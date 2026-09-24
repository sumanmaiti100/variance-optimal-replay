"""Stationary state-visitation density-ratio estimator xi(s) = d^pi(s) / d^b(s).

This module is the fix for the bug in the AAAI-era implementation: the replay
correction there applied ONLY the per-step action ratio

    w_i = pi_theta(a_i | s_i) / pi_beh(a_i | s_i),

which corrects the conditional action distribution but leaves the mismatch
between the *state* distribution of the buffer, d^b, and the discounted state
visitation of the current policy, d^pi, entirely uncorrected. Liu et al. (2020),
"Off-Policy Policy Gradient with State Distribution Correction" (OPPOSD), show
that ignoring exactly this term makes the off-policy policy gradient biased --
in their hard example the Off-PAC gradient vanishes at every policy in a family,
so the estimator can be arbitrarily sub-optimal no matter how good the critic is.

Our paper's Lemma 1 (unbiasedness of the replay estimator under any sampler q)
needs the *combined* weight

    W_i = xi_i * w_i,   xi_i = d^pi(s_i) / d^b(s_i),

because only then does E_{i~b}[W_i u_i] = E_{s~d^pi} E_{a~pi_theta}[Q_r phi] = g_r.
With w_i alone the expectation is E_{s~d^b} E_{a~pi_theta}[.], i.e. the right
action distribution over the wrong states.

Estimation follows Liu et al. (2018a) "Breaking the Curse of Horizon", which is
the estimator OPPOSD itself uses (their Algorithm 2, discounted case). For a
candidate ratio function w and test function f define

    Delta(w; s, a, s') = w(s) rho(s, a) - w(s'),      rho(s,a) = pi(a|s)/pi_beh(a|s)
    L(w, f) = gamma * E_{(s,a,s') ~ d^b}[ Delta(w; s,a,s') f(s') ]
              + (1 - gamma) * E_{s0 ~ p0}[ (1 - w(s0)) f(s0) ].

Then L(w, f) = 0 for every measurable f iff w = d^pi/d^b. Maximising over f in
the unit ball of an RKHS H with kernel k has the closed form

    max_{||f||_H <= 1} L(w, f) = || sum_k c_k k(z_k, .) ||_H = sqrt( c^T K c ),

so we minimise the quadratic form c^T K c over the parameters of w. Here the
evaluation points z_k are the next-states s'_i (with coefficients gamma*Delta_i)
stacked with sampled initial states s0_j (with coefficients (1-gamma)(1-w(s0_j))).
This is a proper minimax objective, not a heuristic surrogate, and it costs one
small kernel matrix per update -- the "lightweight stationary-distribution-ratio
network updated alongside the critics" of the paper's Section 5.

At use time the raw network output is self-normalised over the sampled pool so
that E_{s~d^b}[xi(s)] = 1 (the z_w normalisation of OPPOSD's Algorithm 1, line
17) and then clipped to [1/C_s, C_s], giving the bounded xi_i that Assumption 1
of the paper guarantees exists.
"""
import math

import torch
import torch.nn as nn
import torch.nn.functional as Fnn


class StateRatioNet(nn.Module):
    """w_psi(s) > 0. Softplus output head, exactly as in OPPOSD's implementation
    ("we use a neural network with ReLU hidden layers, with the last activation
    function log(1+exp(x)) to guarantee that w(s) > 0 for any input")."""

    def __init__(self, obs_dim, hidden=64):
        super().__init__()
        self.l0 = nn.Linear(obs_dim, hidden)
        self.l1 = nn.Linear(hidden, hidden)
        self.l2 = nn.Linear(hidden, 1)
        # Start near w = 1 everywhere: the head bias is set so softplus(b) ~ 1
        # and the output weights start small. Before the estimator has seen any
        # data the correction is then the identity, which is the correct
        # "no information yet" prior and avoids a large spurious reweighting in
        # the first few hundred updates.
        nn.init.zeros_(self.l2.weight)
        nn.init.constant_(self.l2.bias, math.log(math.e - 1.0))  # softplus(b)=1

    def forward(self, s):
        h = Fnn.relu(self.l0(s))
        h = Fnn.relu(self.l1(h))
        return Fnn.softplus(self.l2(h)).squeeze(-1) + 1e-4


def _median_bandwidth(z, max_n=256):
    """Median heuristic for the RBF bandwidth, computed on (a subsample of) the
    evaluation points so the kernel adapts to the current state scale."""
    n = z.shape[0]
    if n > max_n:
        idx = torch.randperm(n, device=z.device)[:max_n]
        z = z[idx]
    with torch.no_grad():
        d2 = torch.cdist(z, z).pow(2)
        med = d2.flatten().median().clamp_min(1e-6)
    return med


def _rbf(z, bw):
    d2 = torch.cdist(z, z).pow(2)
    return torch.exp(-d2 / bw.clamp_min(1e-6))


def ratio_minimax_loss(ratio_net, s, s2, rho, s0, gamma):
    """c^T K c for the Liu et al. (2018a) discounted objective.

    Args:
        s, s2: [B, obs_dim] transition states / next states drawn from the buffer.
        rho:   [B] action-probability ratio pi_theta(a|s)/pi_beh(a|s) (already clipped).
        s0:    [M, obs_dim] initial states drawn from the buffer's p0 store.
        gamma: discount.
    Returns:
        scalar loss, and the batch-mean of w(s) for diagnostics.
    """
    w_s = ratio_net(s)
    w_s2 = ratio_net(s2)
    w_s0 = ratio_net(s0)

    B = s.shape[0]
    M = s0.shape[0]
    # Coefficients on f(.) at each evaluation point.
    c_trans = gamma * (w_s * rho - w_s2) / B          # evaluated at s2
    c_init = (1.0 - gamma) * (1.0 - w_s0) / M          # evaluated at s0
    c = torch.cat([c_trans, c_init], dim=0)            # [B+M]

    z = torch.cat([s2, s0], dim=0)                     # [B+M, obs_dim]
    bw = _median_bandwidth(z)
    K = _rbf(z, bw)
    # Normalising the kernel by its mean entry makes the loss scale (and hence
    # the usable learning rate) insensitive to the kernel hyper-parameter, as
    # recommended in OPPOSD's experimental section.
    K = K / K.mean().clamp_min(1e-8)

    loss = torch.dot(c, K @ c)
    return loss, w_s.mean().detach()


class StateDistributionCorrector:
    """Owns the ratio network, its optimiser, and the use-time normalisation.

    `enabled=False` reproduces the buggy AAAI-era behaviour (xi == 1) and is the
    control arm of the `state_correction` ablation.
    """

    def __init__(self, obs_dim, device, gamma=0.99, lr=1e-3, hidden=64,
                 clip_s=5.0, n_updates=1, batch=128, init_batch=64,
                 warmup_updates=250, enabled=True):
        self.enabled = enabled
        self.device = device
        self.gamma = gamma
        self.clip_s = clip_s
        self.n_updates = n_updates
        self.batch = batch
        self.init_batch = init_batch
        self.warmup_updates = warmup_updates
        self.updates = 0
        self.last_loss = 0.0
        self.last_w_mean = 1.0
        if enabled:
            self.net = StateRatioNet(obs_dim, hidden).to(device)
            self.opt = torch.optim.Adam(self.net.parameters(), lr=lr)
        else:
            self.net = None
            self.opt = None

    @property
    def active(self):
        """True once the estimator has had enough updates to be trusted."""
        return self.enabled and self.updates >= self.warmup_updates

    def update(self, buffer, action_ratio_fn):
        """One (or `n_updates`) minimax steps on the ratio network.

        `action_ratio_fn(s, a, logp_beh) -> rho` is supplied by the agent so the
        estimator always uses the *current* policy's action ratio, matching the
        d^pi it is supposed to be tracking.
        """
        if not self.enabled:
            return
        if buffer.size < self.batch + 10 or buffer.n_init < 2:
            return
        for _ in range(self.n_updates):
            idx = buffer.sample_uniform_idx(self.batch)
            s, a, _, _, s2, done, logp_beh = buffer.to_torch(idx)
            with torch.no_grad():
                rho = action_ratio_fn(s, a, logp_beh)
            s0 = buffer.sample_initial(min(self.init_batch, buffer.n_init))
            loss, w_mean = ratio_minimax_loss(self.net, s, s2, rho, s0, self.gamma)
            self.opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.net.parameters(), 10.0)
            self.opt.step()
            self.updates += 1
            self.last_loss = float(loss.item())
            self.last_w_mean = float(w_mean.item())

    @torch.no_grad()
    def xi(self, s):
        """Self-normalised, clipped state-visitation ratio for a batch of states.

        Self-normalisation is over the batch actually being reweighted, which is
        drawn uniformly from the buffer, so it is a consistent estimate of
        E_{s~d^b}[w(s)] -- the normaliser z_w in OPPOSD Algorithm 1.
        """
        if not self.active:
            return torch.ones(s.shape[0], device=s.device)
        raw = self.net(s)
        z = raw.mean().clamp_min(1e-6)
        xi = raw / z
        return xi.clamp(1.0 / self.clip_s, self.clip_s)

    def diagnostics(self):
        return {"ratio_loss": self.last_loss, "ratio_w_mean": self.last_w_mean,
                "ratio_updates": self.updates}
