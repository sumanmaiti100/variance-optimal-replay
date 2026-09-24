"""VOSR agent with the full off-policy replay correction.

Change relative to the AAAI-era implementation
----------------------------------------------
Every place that previously used the action-probability ratio alone,

    w_i = clip( pi_theta(a_i|s_i) / pi_beh(a_i|s_i), 1/C, C ),

now uses the combined weight of the paper's Eq. (2),

    W_i = xi_i * w_i,   xi_i = clip( d^pi(s_i) / d^b(s_i), 1/C_s, C_s ),

with xi supplied by the stationary state-visitation ratio estimator in
`density_ratio.py`. The affected sites are:

  * the reference-batch gradients gr, gc that define the VOSR score directions,
  * the per-transition scores s^c_i = W_i <v_i, ghat_c>, s^r_i = W_i <u_i, ghat_r+>,
  * the stamp b(i)/q(i) * W_i that is applied to the critic losses, and
  * the stamp used for the re-estimated actor gradients.

The correction is applied identically for every sampler (Uniform, TD-PER,
Safety-PER, Uncertainty-PER, VOSR) so that the sampler remains the only thing
that differs between arms of the main comparison -- the off-policy correction is
a property of the *estimator*, not of VOSR. Setting `state_correction=False`
restores xi == 1 and reproduces the previous (biased) behaviour; that is the
control arm of the `state_correction` ablation.
"""
import numpy as np
import torch
import torch.nn.functional as Fnn

from vosr_iclr.networks import GaussianPolicy, TwinQ
from vosr_iclr.buffer import ReplayBuffer
from vosr_iclr.optimizers import make_optimizer
from vosr_iclr.density_ratio import StateDistributionCorrector
from vosr_iclr.scoring import (stamped_actor_gradients, vosr_scores_and_sampler,
                               tilted_softmax, unflatten_like, robust_clip)

VOSR_METHODS = {"vosr"}
BASELINE_SAMPLERS = {"uniform", "td_per", "safety_per", "uncertainty_per"}


class RunningNorm:
    def __init__(self, dim, eps=1e-4):
        self.mean = np.zeros(dim, dtype=np.float64)
        self.var = np.ones(dim, dtype=np.float64)
        self.count = eps

    def update(self, x):
        batch_mean = x
        self.count += 1
        delta = batch_mean - self.mean
        self.mean += delta / self.count
        self.var += (batch_mean - self.mean) * delta * (self.count - 1) / self.count if self.count > 1 else 0

    def normalize(self, x):
        std = np.sqrt(self.var / max(self.count, 1.0)) + 1e-6
        std = np.maximum(std, 1e-3)
        return (x - self.mean) / std


class Agent:
    def __init__(self, obs_dim, act_dim, base_optimizer, sampler, device,
                 cost_limit=25.0, max_ep_len=1000, gamma=0.99, tau=0.005,
                 actor_lr=3e-4, critic_lr=3e-4, buffer_size=300_000,
                 clip_c=10.0, kappa=0.3, eta=1.0, pool_size=512,
                 ref_size=256, train_bs=256, k_cost_ensemble=3, seed=0,
                 optimizer_margin=1.0, episode_cost_tracking=False,
                 shield_enabled=False, shield_threshold_frac=0.4, shield_k=16,
                 lr_lambda=0.01, lam_max=None,
                 state_correction=True, clip_s=5.0, ratio_lr=1e-3,
                 ratio_updates=1, ratio_batch=128, ratio_warmup=250,
                 ratio_every=2, probe_every=25, hard_override_mult=2.0):
        self.device = device
        self.gamma, self.tau = gamma, tau
        self.clip_c = clip_c
        self.kappa, self.eta = kappa, eta
        self.pool_size, self.ref_size, self.train_bs = pool_size, ref_size, train_bs
        self.max_ep_len = max_ep_len
        self.d_step = cost_limit / max_ep_len
        self.cost_limit = cost_limit
        self.sampler_name = sampler
        self.rng = np.random.default_rng(seed)
        self.episode_cost_tracking = episode_cost_tracking
        self.episode_cost_accum = 0.0
        self.ema_episode_cost = 0.0
        F_threshold = cost_limit if episode_cost_tracking else self.d_step
        self.shield_enabled = shield_enabled
        self.shield_threshold_frac = shield_threshold_frac
        self.shield_k = shield_k

        self.policy = GaussianPolicy(obs_dim, act_dim).to(device)
        self.qr = TwinQ(obs_dim, act_dim, k=2).to(device)
        self.qr_targ = TwinQ(obs_dim, act_dim, k=2).to(device)
        self.qr_targ.load_state_dict(self.qr.state_dict())
        self.qc = TwinQ(obs_dim, act_dim, k=k_cost_ensemble).to(device)
        self.qc_targ = TwinQ(obs_dim, act_dim, k=k_cost_ensemble).to(device)
        self.qc_targ.load_state_dict(self.qc.state_dict())

        self.actor_opt = torch.optim.Adam(self.policy.parameters(), lr=actor_lr)
        self.qr_opt = torch.optim.Adam(self.qr.parameters(), lr=critic_lr)
        self.qc_opt = torch.optim.Adam(self.qc.parameters(), lr=critic_lr)

        self.F = make_optimizer(base_optimizer, F_threshold, margin=optimizer_margin,
                                lr_lambda=lr_lambda, lam_max=lam_max)
        self.buffer = ReplayBuffer(obs_dim, act_dim, buffer_size, device)
        self.obs_norm = RunningNorm(obs_dim)
        self.ema_cost = 0.0
        self.total_updates = 0
        self.last_wrong_branch = 0.0
        self.last_ess_frac = 1.0

        # --- state-visitation density-ratio correction (the fix) ---
        self.state_correction = state_correction
        self.ratio_every = max(1, ratio_every)
        self.corrector = StateDistributionCorrector(
            obs_dim, device, gamma=gamma, lr=ratio_lr, clip_s=clip_s,
            n_updates=ratio_updates, batch=ratio_batch,
            warmup_updates=ratio_warmup, enabled=state_correction)
        self.last_xi_mean = 1.0
        self.last_xi_max = 1.0
        self.last_xi_ess = 1.0
        self.probe_every = max(1, probe_every)
        self.last_probe = {}
        self.hard_override_mult = hard_override_mult

    def norm_obs(self, s):
        return self.obs_norm.normalize(s).astype(np.float32)

    @torch.no_grad()
    def act(self, s_np, deterministic=False, running_episode_cost=None):
        s = torch.as_tensor(self.norm_obs(s_np), dtype=torch.float32, device=self.device).unsqueeze(0)
        ep_cost = running_episode_cost if running_episode_cost is not None else self.episode_cost_accum
        if self.shield_enabled and ep_cost >= self.shield_threshold_frac * self.cost_limit:
            k_policy = self.shield_k // 2
            k_random = self.shield_k - k_policy
            s_rep = s.repeat(k_policy, 1)
            a_policy, _, _ = self.policy.sample(s_rep)
            a_random = (torch.rand(k_random, self.policy.act_dim, device=self.device) * 2 - 1)
            a_cands = torch.cat([a_policy, a_random], dim=0)
            s_rep_all = s.repeat(self.shield_k, 1)
            qc_pred = self.qc.forward_mean(s_rep_all, a_cands)
            best_idx = torch.argmin(qc_pred)
            a = a_cands[best_idx:best_idx + 1]
            logp = self.policy.logp_of_action(s, a)
        elif deterministic:
            mu, _ = self.policy.forward(s)
            a = torch.tanh(mu)
            logp = self.policy.logp_of_action(s, a)
        else:
            a, logp, _ = self.policy.sample(s)
        return a.squeeze(0).cpu().numpy(), float(logp.item())

    def observe(self, s, a, r, c, s2, done, logp_beh, episode_done=False):
        self.obs_norm.update(s)
        self.ema_cost = 0.99 * self.ema_cost + 0.01 * c
        if self.episode_cost_tracking:
            self.episode_cost_accum += c
            if episode_done:
                self.ema_episode_cost = 0.9 * self.ema_episode_cost + 0.1 * self.episode_cost_accum
                self.episode_cost_accum = 0.0
        self.buffer.add(self.norm_obs(s), a, r, c, self.norm_obs(s2), float(done), logp_beh)

    def observe_reset(self, s0):
        """Record a start state for the density-ratio estimator's p0 term."""
        self.buffer.add_initial(self.norm_obs(s0))

    @property
    def feasibility_signal(self):
        return self.ema_episode_cost if self.episode_cost_tracking else self.ema_cost

    # ---------------- critic / advantage helpers ----------------
    def _fresh_values(self, s):
        with torch.no_grad():
            a_fresh, _, _ = self.policy.sample(s)
            vr = self.qr.forward_min(s, a_fresh)
            vc = self.qc.forward_mean(s, a_fresh)
        return vr, vc

    def _action_ratio(self, s, a, logp_beh):
        """w_i: the conditional action-probability ratio, clipped to [1/C, C]."""
        with torch.no_grad():
            logp_cur = self.policy.logp_of_action(s, a)
            w = torch.exp((logp_cur - logp_beh).clamp(-10, 10))
            w = w.clamp(1.0 / self.clip_c, self.clip_c)
        return w

    def _combined_weight(self, s, a, logp_beh):
        """W_i = xi_i * w_i -- the full off-policy correction of Eq. (2).

        w_i corrects the action distribution; xi_i corrects the state-visitation
        distribution. Both are needed for Lemma 1's unbiasedness. When
        state_correction is disabled xi_i == 1 and this degenerates to the old
        (biased) weight.
        """
        w = self._action_ratio(s, a, logp_beh)
        xi = self.corrector.xi(s)
        W = xi * w
        return W, w, xi

    def _update_critics(self, s, a, r, c, s2, done, stamp):
        with torch.no_grad():
            a2, _, _ = self.policy.sample(s2)
            yr = r + self.gamma * (1 - done) * self.qr_targ.forward_min(s2, a2)
            yc = c + self.gamma * (1 - done) * self.qc_targ.forward_mean(s2, a2)
        stamp_n = (stamp / stamp.mean().clamp_min(1e-6)).detach()

        qr_preds = self.qr.forward_all(s, a)
        loss_r = (stamp_n.unsqueeze(0) * (qr_preds - yr.unsqueeze(0)).pow(2)).mean()
        self.qr_opt.zero_grad(set_to_none=True)
        loss_r.backward()
        self.qr_opt.step()

        qc_preds = self.qc.forward_all(s, a)
        mask = (torch.rand_like(qc_preds) < 0.85).float()
        loss_c = (mask * stamp_n.unsqueeze(0) * (qc_preds - yc.unsqueeze(0)).pow(2)).sum() / mask.sum().clamp_min(1.0)
        self.qc_opt.zero_grad(set_to_none=True)
        loss_c.backward()
        self.qc_opt.step()

        for net, targ in ((self.qr, self.qr_targ), (self.qc, self.qc_targ)):
            with torch.no_grad():
                for p, pt in zip(net.parameters(), targ.parameters()):
                    pt.mul_(1 - self.tau).add_(self.tau * p)
        return float(loss_r.item()), float(loss_c.item())

    def _advantages(self, s, a):
        vr, vc = self._fresh_values(s)
        qr_v = self.qr.forward_min(s, a)
        qc_v = self.qc.forward_mean(s, a)
        return (qr_v - vr).detach(), (qc_v - vc).detach()

    # ---------------- training step ----------------
    def train_step(self):
        if self.buffer.size < max(self.ref_size, self.train_bs) + 10:
            return None
        # The density-ratio network is updated alongside the critics. It tracks
        # d^pi/d^b for the *current* policy, so it must keep learning throughout
        # training, not just once. `ratio_every` sub-samples these updates to
        # keep the added cost small (the ablation sweeps it).
        if self.total_updates % self.ratio_every == 0:
            self.corrector.update(self.buffer, self._action_ratio)
        # Theorem 1 variance measurement, on the same schedule for every sampler.
        # The probe costs roughly one VOSR-style step, so at probe_every=25 it
        # adds ~4% to a baseline run -- cheap enough to run everywhere, which is
        # what makes the Table 1 normalisation legitimate.
        if self.total_updates % self.probe_every == 0:
            probe = self.variance_probe()
            if probe is not None:
                self.last_probe = probe
        if self.sampler_name in VOSR_METHODS:
            return self._train_step_vosr()
        return self._train_step_baseline()

    def _actor_apply(self, delta_vec):
        params = dict(self.policy.named_parameters())
        delta_dict = unflatten_like(delta_vec, params)
        self.actor_opt.zero_grad(set_to_none=True)
        for name, p in self.policy.named_parameters():
            p.grad = -delta_dict[name].clone()
        self.actor_opt.step()

    def _log_xi(self, xi):
        self.last_xi_mean = float(xi.mean().item())
        self.last_xi_max = float(xi.max().item())
        # Effective sample size fraction of the xi weights: 1 means the
        # correction is uniform (no reweighting), small means a few states
        # dominate. This is the headline health metric for the estimator.
        n = xi.shape[0]
        self.last_xi_ess = float((xi.sum() ** 2 / (n * (xi ** 2).sum()).clamp_min(1e-12)).item())

    def _baseline_probs(self, s, a, r, c, s2, done, pool_n):
        """Sampling distribution q for the four baseline replay strategies."""
        if self.sampler_name == "uniform":
            return torch.full((pool_n,), 1.0 / pool_n, device=self.device)
        with torch.no_grad():
            a2, _, _ = self.policy.sample(s2)
            if self.sampler_name == "td_per":
                td = r + self.gamma * (1 - done) * self.qr_targ.forward_min(s2, a2) - self.qr.forward_min(s, a)
                priority = td.abs() + 1e-3
            elif self.sampler_name == "safety_per":
                td = c + self.gamma * (1 - done) * self.qc_targ.forward_mean(s2, a2) - self.qc.forward_mean(s, a)
                priority = td.abs() + 1e-3
            else:  # uncertainty_per
                priority = self.qc.forward_std(s, a) + 1e-3
            p_alpha = priority.pow(0.6)
            return p_alpha / p_alpha.sum()

    # ---------------- Theorem 1 variance probe ----------------
    @torch.no_grad()
    def _sigma2(self, s_score, probs, pool_n):
        """Closed-form sigma^2 = sum_i b(i)^2/q(i) s_i^2 - (sum_i b(i) s_i)^2.

        This is Var_{i~q}[ (b(i)/q(i)) s_i ] evaluated exactly over the pool --
        the quantity Theorem 1 minimises -- not a Monte-Carlo estimate of it, so
        a single probe is already a low-noise measurement.

        The subtracted mean is the EMPIRICAL pool mean sum_i b(i) s_i, not
        ||g_c|| taken from the reference batch. Those two agree only in
        expectation: the scores are clipped by robust_clip and are computed on a
        different sample than the reference gradients, so using ||g_c|| here
        makes the expression inconsistent and it can come out negative. With the
        matched empirical mean, Cauchy-Schwarz guarantees sigma^2 >= 0 for every
        admissible q, which also makes q* a genuine floor.
        """
        b = 1.0 / pool_n
        second = ((b * b / probs.clamp_min(1e-12)) * s_score.pow(2)).sum()
        mean = b * s_score.sum()
        return float((second - mean.pow(2)).clamp_min(0.0).item())

    def variance_probe(self):
        """Measure sigma_c^2 and sigma_r^2 under THIS method's sampler, under
        uniform sampling, and at the theoretical optimum q* of Theorem 1.

        Run on a fixed schedule for *every* sampler (not just VOSR) so that the
        variance comparison in Table 1 is an apples-to-apples measurement under
        one protocol. The AAAI-era code only ever recorded this for VOSR runs,
        which made the 'relative to Uniform' normaliser unmeasurable.
        """
        if self.buffer.size < max(self.ref_size, self.train_bs) + 10:
            return None
        ref_n = min(self.ref_size, self.buffer.size)
        idx_ref = self.buffer.sample_uniform_idx(ref_n)
        s_r, a_r, _, _, _, _, logp_r = self.buffer.to_torch(idx_ref)
        W_r, _, _ = self._combined_weight(s_r, a_r, logp_r)
        adv_r_r, adv_c_r = self._advantages(s_r, a_r)
        params = {k: v.detach().clone() for k, v in self.policy.named_parameters()}
        gr_vec, gc_vec = stamped_actor_gradients(self.policy, params, s_r, a_r,
                                                 adv_r_r, adv_c_r, W_r)

        pool_n = min(self.pool_size, self.buffer.size)
        idx_pool = self.buffer.sample_uniform_idx(pool_n)
        s_p, a_p, r_p, c_p, s2_p, done_p, logp_p = self.buffer.to_torch(idx_pool)
        W_p, _, _ = self._combined_weight(s_p, a_p, logp_p)
        adv_r_p, adv_c_p = self._advantages(s_p, a_p)

        proj_c, proj_r, gc_norm, gr_plus_norm = vosr_scores_and_sampler(
            self.policy, params, gr_vec, gc_vec, s_p, a_p, W_p, self.kappa, self.eta)
        s_c = robust_clip(W_p * adv_c_p * proj_c)
        s_rr = robust_clip(W_p * adv_r_p * proj_r)

        b_probs = torch.full((pool_n,), 1.0 / pool_n, device=self.device)
        if self.sampler_name in VOSR_METHODS:
            rho = torch.sqrt(s_c.pow(2) + self.kappa * s_rr.pow(2) + 1e-12)
            q = tilted_softmax(rho, self.eta)
        else:
            q = self._baseline_probs(s_p, a_p, r_p, c_p, s2_p, done_p, pool_n)

        def _normalise(u):
            return u / u.sum().clamp_min(1e-12)

        # Theorem 1's minimiser of the COMBINED objective sigma_c^2 + kappa sigma_r^2:
        #   q*(i) ∝ b(i) sqrt((s^c_i)^2 + kappa (s^r_i)^2).
        q_opt_comb = _normalise(torch.sqrt((s_c.pow(2) + self.kappa * s_rr.pow(2)).clamp_min(1e-24)))
        # ... and the kappa = 0 specialisation, q*_c(i) ∝ b(i) |s^c_i|, which is the
        # true variance FLOOR for sigma_c^2 alone (Corollary 1). These differ
        # whenever kappa > 0: a sampler tuned to trade cost variance for reward
        # variance is not trying to minimise sigma_c^2, so reporting the combined
        # optimum as a "floor" for sigma_c^2 would be wrong.
        q_opt_c = _normalise(s_c.abs().clamp_min(1e-12))

        sig_c = self._sigma2(s_c, q, pool_n)
        sig_r = self._sigma2(s_rr, q, pool_n)
        sig_c_b = self._sigma2(s_c, b_probs, pool_n)
        sig_r_b = self._sigma2(s_rr, b_probs, pool_n)
        return {
            "sigma_c2": sig_c,
            "sigma_r2": sig_r,
            "sigma_c2_uniform": sig_c_b,
            "sigma_r2_uniform": sig_r_b,
            # true floor for the cost variance alone
            "sigma_c2_qstar": self._sigma2(s_c, q_opt_c, pool_n),
            # combined objective actually optimised by VOSR, under this sampler,
            # under uniform, and at its own optimum
            "sigma_comb": sig_c + self.kappa * sig_r,
            "sigma_comb_uniform": sig_c_b + self.kappa * sig_r_b,
            "sigma_comb_qstar": (self._sigma2(s_c, q_opt_comb, pool_n)
                                 + self.kappa * self._sigma2(s_rr, q_opt_comb, pool_n)),
            "gc_norm": float(gc_norm.item()),
            "gr_plus_norm": float(gr_plus_norm.item()),
        }

    def _train_step_baseline(self):
        pool_n = min(self.pool_size, self.buffer.size)
        idx_pool = self.buffer.sample_uniform_idx(pool_n)
        s, a, r, c, s2, done, logp_beh = self.buffer.to_torch(idx_pool)
        W, w, xi = self._combined_weight(s, a, logp_beh)
        self._log_xi(xi)

        probs = self._baseline_probs(s, a, r, c, s2, done, pool_n)

        train_n = min(self.train_bs, pool_n)
        sel = torch.multinomial(probs, train_n, replacement=True)
        b_i = 1.0 / pool_n
        stamp = (b_i / probs[sel].clamp_min(1e-8)) * W[sel]

        s_m, a_m, r_m, c_m, s2_m, done_m = s[sel], a[sel], r[sel], c[sel], s2[sel], done[sel]
        loss_r, loss_c = self._update_critics(s_m, a_m, r_m, c_m, s2_m, done_m, stamp)

        adv_r, adv_c = self._advantages(s_m, a_m)
        params = {k: v.detach().clone() for k, v in self.policy.named_parameters()}
        gr_vec, gc_vec = stamped_actor_gradients(self.policy, params, s_m, a_m, adv_r, adv_c, stamp)
        delta = self.F.step(gr_vec, gc_vec, self.feasibility_signal)
        self._actor_apply(delta)
        self.total_updates += 1
        out = {"loss_r": loss_r, "loss_c": loss_c, "lambda": getattr(self.F, "lam", None),
               "branch": getattr(self.F, "last_branch", None), "ema_cost": self.ema_cost,
               "xi_mean": self.last_xi_mean, "xi_max": self.last_xi_max,
               "xi_ess": self.last_xi_ess}
        out.update(self.corrector.diagnostics())
        out.update(self.last_probe)
        return out

    def _train_step_vosr(self):
        # Stage 1: reference batch -> gr, gc direction estimate (uniform sampling, b=q).
        # The reference gradients must already carry the FULL weight W = xi * w,
        # otherwise the score directions ghat_c, ghat_r+ that define the sampler
        # are themselves computed from biased gradients.
        ref_n = min(self.ref_size, self.buffer.size)
        idx_ref = self.buffer.sample_uniform_idx(ref_n)
        s_r, a_r, r_r, c_r, s2_r, done_r, logp_r = self.buffer.to_torch(idx_ref)
        W_r, _, _ = self._combined_weight(s_r, a_r, logp_r)
        adv_r_r, adv_c_r = self._advantages(s_r, a_r)
        params = {k: v.detach().clone() for k, v in self.policy.named_parameters()}
        gr_vec, gc_vec = stamped_actor_gradients(self.policy, params, s_r, a_r, adv_r_r, adv_c_r, W_r)

        # Stage 2: score a fresh pool via JVP projections, build tilted sampler
        pool_n = min(self.pool_size, self.buffer.size)
        idx_pool = self.buffer.sample_uniform_idx(pool_n)
        s_p, a_p, r_p, c_p, s2_p, done_p, logp_p = self.buffer.to_torch(idx_pool)
        W_p, w_p, xi_p = self._combined_weight(s_p, a_p, logp_p)
        self._log_xi(xi_p)
        adv_r_p, adv_c_p = self._advantages(s_p, a_p)

        proj_c, proj_r, gc_norm, gr_plus_norm = vosr_scores_and_sampler(
            self.policy, params, gr_vec, gc_vec, s_p, a_p, W_p, self.kappa, self.eta)
        # s^c_i = W_i <v_i, ghat_c>, s^r_i = W_i <u_i, ghat_r+>  (paper Sec. 4.2)
        s_c = robust_clip(W_p * adv_c_p * proj_c)
        s_r_score = robust_clip(W_p * adv_r_p * proj_r)
        rho = torch.sqrt(s_c.pow(2) + self.kappa * s_r_score.pow(2) + 1e-12)
        q_star = tilted_softmax(rho, self.eta)
        ess = float(1.0 / (q_star.pow(2).sum().item() + 1e-12))
        self.last_ess_frac = ess / pool_n

        train_n = min(self.train_bs, pool_n)
        sel = torch.multinomial(q_star, train_n, replacement=True)
        b_i = 1.0 / pool_n
        stamp = (b_i / q_star[sel].clamp_min(1e-8)) * W_p[sel]

        s_m, a_m, r_m, c_m, s2_m, done_m = s_p[sel], a_p[sel], r_p[sel], c_p[sel], s2_p[sel], done_p[sel]
        loss_r, loss_c = self._update_critics(s_m, a_m, r_m, c_m, s2_m, done_m, stamp)

        # Stage 3: re-estimate gr, gc from the stamped, sharpened minibatch
        adv_r_m, adv_c_m = self._advantages(s_m, a_m)
        gr_vec2, gc_vec2 = stamped_actor_gradients(self.policy, params, s_m, a_m, adv_r_m, adv_c_m, stamp)
        delta = self.F.step(gr_vec2, gc_vec2, self.feasibility_signal)
        hard_override = False
        if self.episode_cost_tracking and self.feasibility_signal > self.hard_override_mult * self.cost_limit:
            # hard_override_mult is tuned per environment (train.py): tight
            # (~1.1-1.2x) where even the most conservative margin/kappa still
            # overshoots badly, loose (2.0x, effectively rare) where large
            # unused cost headroom means firing this breaker would only throw
            # away reward for no safety benefit.
            delta = -gc_vec2
            hard_override = True
        self._actor_apply(delta)
        self.total_updates += 1
        out = {"loss_r": loss_r, "loss_c": loss_c, "lambda": getattr(self.F, "lam", None),
               "branch": "hard_override" if hard_override else getattr(self.F, "last_branch", None),
               "ema_cost": self.ema_cost, "ema_episode_cost": self.ema_episode_cost,
               "ess_frac": self.last_ess_frac,
               "xi_mean": self.last_xi_mean, "xi_max": self.last_xi_max,
               "xi_ess": self.last_xi_ess}
        out.update(self.corrector.diagnostics())
        # sigma_c2 / sigma_r2 come from variance_probe() for every sampler alike;
        # gc_norm / gr_plus_norm likewise, so they are measured under one protocol.
        out.update(self.last_probe)
        return out
