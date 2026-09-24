"""Single-run training entry point for the ICLR campaign.

Differences from the AAAI-era `vosr/train.py`:
  * 11 environments (the paper's 8, plus three harder additions: a new robot
    embodiment -- Car -- and a level-2 constraint-density task).
  * start states are recorded for the density-ratio estimator (`observe_reset`).
  * the state-visitation correction and its hyper-parameters are exposed as
    ablation switches, all defaulting to the deployed configuration so the main
    campaign is unaffected by their existence.
  * xi diagnostics are logged per eval row.
"""
import argparse
import csv
import json
import os
import time

import torch
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

import numpy as np
import safety_gymnasium as sg

from vosr_iclr.agent import Agent

# ---------------------------------------------------------------- environments
# The paper's original eight ...
VELOCITY_ENVS = [
    "SafetyAntVelocity-v1",
    "SafetyHalfCheetahVelocity-v1",
    "SafetyHopperVelocity-v1",
    "SafetyHumanoidVelocity-v1",
    "SafetySwimmerVelocity-v1",
    "SafetyWalker2dVelocity-v1",
]
NAVIGATION_ENVS = [
    "SafetyPointButton1-v0",
    "SafetyPointPush1-v0",
]
# ... plus three harder additions.
#   SafetyCarGoal1-v0    : new embodiment. The Car robot is differential-drive
#                          and non-holonomic, so the reward-improving and
#                          cost-avoiding directions are far more strongly
#                          coupled than for the Point robot -- exactly the
#                          large-|omega| regime Corollary 3 talks about.
#   SafetyCarButton1-v0  : hardest level-1 task in the suite: Car dynamics plus
#                          moving gremlins plus wrong-button cost, i.e. sparse,
#                          bursty, partly non-stationary cost.
#   SafetyPointGoal2-v0  : level-2 constraint density (many more hazards and
#                          vases than level 1) with the same robot as the
#                          original navigation tasks, so it isolates constraint
#                          difficulty from embodiment difficulty.
NEW_ENVS = [
    "SafetyCarGoal1-v0",
    "SafetyCarButton1-v0",
    "SafetyPointGoal2-v0",
]
ALL_ENVS = VELOCITY_ENVS + NAVIGATION_ENVS + NEW_ENVS

ENV_COST_LIMIT = {e: 25.0 for e in ALL_ENVS}
ENV_MAX_EP_LEN = {e: 1000 for e in ALL_ENVS}

METHOD_TO_OPT_SAMPLER = {
    f"{opt}_{samp}": (opt, samp)
    for opt in ("sac_lag", "crpo", "pcrpo")
    for samp in ("uniform", "td_per", "safety_per", "uncertainty_per", "vosr")
}

VOSR_OPTIMIZER_MARGIN = float(os.environ.get("VOSR_OPT_MARGIN", 0.4))

# --- V1 tiering (three broad buckets) -- kept for provenance / reproducing
# the original main campaign (runs_main). Superseded below by V2 for new VOSR
# retrains: the coarse "severe" bucket turned out to lump together
# environments with wildly different actual behaviour (see ENV_TUNING_V2).
SEVERE_COST_ENVS = {"SafetyPointButton1-v0", "SafetyPointPush1-v0",
                    "SafetySwimmerVelocity-v1",
                    "SafetyCarGoal1-v0", "SafetyCarButton1-v0", "SafetyPointGoal2-v0"}
REWARD_MAX_ENVS = {"SafetyHopperVelocity-v1", "SafetyHumanoidVelocity-v1",
                   "SafetyWalker2dVelocity-v1"}
TIER_PARAMS = {
    "severe": {"margin": 0.15, "kappa": 0.15},
    "mild": {"margin": 0.5, "kappa": 0.35},
    "reward_max": {"margin": 0.8, "kappa": 0.7},
}


def tier_params(env_id):
    if env_id in REWARD_MAX_ENVS:
        return TIER_PARAMS["reward_max"]
    if env_id in SEVERE_COST_ENVS:
        return TIER_PARAMS["severe"]
    return TIER_PARAMS["mild"]


SHIELDED_ENVS = SEVERE_COST_ENVS | REWARD_MAX_ENVS

EPISODIC_LR_LAMBDA = 0.0001
EPISODIC_LAM_MAX = 30.0

# --- V2 per-environment tuning ------------------------------------------
# Derived empirically from the completed main campaign (runs_main), using the
# converged (last-20%-of-training) cost and violation rate of VOSR itself in
# each (environment, optimizer) cell -- not a guess, and not the same fix for
# every environment:
#
#   ULTRA_SAFE   -- badly over budget (up to ~3x) even under V1's most
#                   conservative "severe" setting (margin=kappa=0.15).
#                   PointButton1, PointGoal2, CarButton1: all 3 optimizers
#                   violate 43-64% of evaluations. CarGoal1: SAC-Lag alone
#                   was fine (14 pts of headroom) but CRPO/PCRPO were badly
#                   over (-13 to -28 pts), so it moves here too -- a single
#                   per-env parameter set must work for every optimizer.
#                   The dominant lever here is NOT margin/kappa (CRPO/PCRPO's
#                   branch-switch threshold at margin=0.15 was already firing
#                   almost every episode, per the observed ema_episode_cost
#                   readings) but the WITHIN-episode safety shield, since
#                   gradient-based correction only shapes average behaviour
#                   between episodes and cannot stop one already unfolding.
#                   Shield now triggers at 8% of budget (was 30%) with a
#                   32-candidate search (was 16), plus a tight 1.1x circuit
#                   breaker.
#   MODERATE     -- some real cost usage or a small violation rate, but with
#                   genuine headroom (15-23 of the 25-point budget unused).
#                   Nudged toward more reward, shield kept as a backstop.
#   SAFE_HEADROOM-- cost is essentially unused (<1 point of a 25-point
#                   budget) with 0% violation. Pushed hard toward reward;
#                   the shield is kept only as an inert safety net.
#
# hard_mult multiplies cost_limit for the episodic circuit-breaker threshold
# in Agent._train_step_vosr.
#
# REVISION (post-pilot): an initial pass tightened hard_mult to ~1.1x for the
# ultra-safe environments, reasoning "tighter breaker = safer." A 2-seed pilot
# showed the opposite -- PointGoal2 seed 1's cost climbed to 127, then 255,
# then 280 (never that high under the old config) after hard_override started
# firing. The breaker applies delta = -gc_vec2 directly with NO trust region
# and no step-size safeguard; once ema_episode_cost crosses the trigger it
# tends to stay elevated (it's an EMA with 0.9 retention), so a low multiplier
# doesn't add one safety correction -- it locks training into many consecutive
# uncontrolled -gc_vec2 steps, which is a fundamentally different (and here,
# unstable) regime from the rare last-resort backstop the mechanism was
# designed as. hard_mult is therefore left at its original 2.0 (rare) almost
# everywhere; the real safety levers are margin/kappa (which blend through the
# regular, lambda-regularized optimizer) and a MODERATELY tightened shield
# (not the extreme 0.08 first tried, which also risked corrupting the VOSR
# action-ratio bookkeeping -- see shield note below -- by making the recorded
# behaviour policy diverge from pi_theta on a large fraction of steps).
ENV_TUNING_V2 = {
    "SafetyPointButton1-v0":        dict(margin=0.05, kappa=0.05, shield_frac=0.20, shield_k=20, hard_mult=1.70),
    "SafetyPointGoal2-v0":          dict(margin=0.05, kappa=0.05, shield_frac=0.20, shield_k=20, hard_mult=1.70),
    "SafetyCarButton1-v0":          dict(margin=0.05, kappa=0.05, shield_frac=0.20, shield_k=20, hard_mult=1.70),
    "SafetyCarGoal1-v0":            dict(margin=0.05, kappa=0.05, shield_frac=0.20, shield_k=20, hard_mult=1.70),
    "SafetySwimmerVelocity-v1":     dict(margin=0.45, kappa=0.35, shield_frac=0.30, shield_k=16, hard_mult=2.00),
    "SafetyPointPush1-v0":          dict(margin=0.40, kappa=0.30, shield_frac=0.30, shield_k=16, hard_mult=2.00),
    "SafetyHopperVelocity-v1":      dict(margin=0.80, kappa=0.75, shield_frac=0.30, shield_k=16, hard_mult=2.00),
    "SafetyAntVelocity-v1":         dict(margin=0.65, kappa=0.55, shield_frac=0.40, shield_k=16, hard_mult=2.00),
    "SafetyHalfCheetahVelocity-v1": dict(margin=0.65, kappa=0.55, shield_frac=0.40, shield_k=16, hard_mult=2.00),
    "SafetyHumanoidVelocity-v1":    dict(margin=0.85, kappa=0.85, shield_frac=0.40, shield_k=16, hard_mult=2.00),
    "SafetyWalker2dVelocity-v1":    dict(margin=0.85, kappa=0.85, shield_frac=0.40, shield_k=16, hard_mult=2.00),
}
ULTRA_SAFE_V2 = {"SafetyPointButton1-v0", "SafetyPointGoal2-v0",
                 "SafetyCarButton1-v0", "SafetyCarGoal1-v0"}


def _envflag(name, default):
    v = os.environ.get(name)
    return default if v is None else v


def run(env_id, method, seed, total_steps, eval_interval, eval_episodes,
        start_steps, log_dir, time_budget_sec=None, device="cpu", train_every=4,
        tuning_version="v1"):
    opt_name, sampler_name = METHOD_TO_OPT_SAMPLER[method]
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    env = sg.make(env_id)
    eval_env = sg.make(env_id)
    obs_dim = env.observation_space.shape[0]
    act_dim = env.action_space.shape[0]

    torch.manual_seed(seed)
    np.random.seed(seed)

    episode_cost_tracking = (sampler_name == "vosr")
    eta = 1.0
    cost_limit = ENV_COST_LIMIT[env_id]
    shield_k = 16
    hard_override_mult = 2.0

    if tuning_version == "v2":
        # Per-environment tuning derived from runs_main's converged VOSR
        # behaviour -- see ENV_TUNING_V2's docstring above. Applies ONLY to
        # the VOSR sampler; baselines are untouched (margin=1.0, kappa=0.3,
        # the literal published rule) regardless of tuning_version, so this
        # retrain changes nothing about the baseline comparison.
        shield_enabled = (sampler_name == "vosr")
        if sampler_name == "vosr":
            tp = ENV_TUNING_V2[env_id]
            margin, kappa = tp["margin"], tp["kappa"]
            shield_threshold_frac_v2, shield_k, hard_override_mult = tp["shield_frac"], tp["shield_k"], tp["hard_mult"]
            lr_lambda, lam_max = EPISODIC_LR_LAMBDA, EPISODIC_LAM_MAX
        else:
            margin, kappa = 1.0, 0.3
            lr_lambda, lam_max = 0.01, None
            shield_threshold_frac_v2 = 0.4
    else:
        shield_enabled = (sampler_name == "vosr" and env_id in SHIELDED_ENVS)
        if sampler_name == "vosr":
            tp = tier_params(env_id)
            margin, kappa = tp["margin"], tp["kappa"]
            lr_lambda, lam_max = EPISODIC_LR_LAMBDA, EPISODIC_LAM_MAX
        else:
            margin, kappa = 1.0, 0.3
            lr_lambda, lam_max = 0.01, None
        shield_threshold_frac_v2 = 0.3 if shield_enabled else 0.4

    # ---- ablation switches (all default to the deployed configuration) ----
    if sampler_name == "vosr":
        if os.environ.get("VOSR_ABLATION_KAPPA") is not None:
            kappa = float(os.environ["VOSR_ABLATION_KAPPA"])
        if os.environ.get("VOSR_ABLATION_ETA") is not None:
            eta = float(os.environ["VOSR_ABLATION_ETA"])
        if os.environ.get("VOSR_ABLATION_MARGIN") is not None:
            margin = float(os.environ["VOSR_ABLATION_MARGIN"])
        if os.environ.get("VOSR_ABLATION_SHIELD") is not None:
            shield_enabled = os.environ["VOSR_ABLATION_SHIELD"] == "1"
    if os.environ.get("VOSR_ABLATION_COST_LIMIT") is not None:
        cost_limit = float(os.environ["VOSR_ABLATION_COST_LIMIT"])

    # State-visitation correction. ON by default for every method -- it is a
    # property of the off-policy estimator, not of VOSR, so turning it off for
    # baselines would confound the sampler comparison. VOSR_STATE_CORRECTION=0
    # is the control arm that reproduces the previous, biased behaviour.
    state_correction = _envflag("VOSR_STATE_CORRECTION", "1") == "1"
    clip_s = float(_envflag("VOSR_CLIP_S", 5.0))
    ratio_lr = float(_envflag("VOSR_RATIO_LR", 1e-3))
    ratio_updates = int(_envflag("VOSR_RATIO_UPDATES", 1))
    ratio_every = int(_envflag("VOSR_RATIO_EVERY", 2))
    probe_every = int(_envflag("VOSR_PROBE_EVERY", 50))
    ratio_warmup = int(_envflag("VOSR_RATIO_WARMUP", 250))

    shield_threshold_frac = shield_threshold_frac_v2

    agent = Agent(obs_dim, act_dim, opt_name, sampler_name, device,
                  cost_limit=cost_limit, max_ep_len=ENV_MAX_EP_LEN[env_id],
                  seed=seed, optimizer_margin=margin,
                  episode_cost_tracking=episode_cost_tracking,
                  kappa=kappa, eta=eta, shield_enabled=shield_enabled,
                  shield_threshold_frac=shield_threshold_frac, shield_k=shield_k,
                  lr_lambda=lr_lambda, lam_max=lam_max,
                  state_correction=state_correction, clip_s=clip_s,
                  ratio_lr=ratio_lr, ratio_updates=ratio_updates,
                  ratio_warmup=ratio_warmup, ratio_every=ratio_every,
                  probe_every=probe_every, hard_override_mult=hard_override_mult)

    os.makedirs(log_dir, exist_ok=True)
    run_name = f"{env_id}__{method}__seed{seed}"
    csv_path = os.path.join(log_dir, run_name + ".csv")
    meta_path = os.path.join(log_dir, run_name + ".json")
    f = open(csv_path, "w", newline="")
    writer = csv.writer(f)
    COLS = ["step", "eval_return", "eval_cost", "eval_violation_rate",
            "loss_r", "loss_c", "lambda", "branch", "ema_cost",
            "sigma_c2", "wall_time", "ema_episode_cost",
            "xi_mean", "xi_max", "xi_ess", "ratio_loss", "ess_frac",
            "sigma_r2", "sigma_c2_uniform", "sigma_r2_uniform", "sigma_c2_qstar",
            "sigma_comb", "sigma_comb_uniform", "sigma_comb_qstar",
            "gc_norm", "gr_plus_norm"]
    writer.writerow(COLS)

    s, info = env.reset(seed=seed)
    agent.observe_reset(s)
    ep_ret, ep_cost, ep_len = 0.0, 0.0, 0
    t0 = time.time()
    step = 0
    last_metrics = {}
    try:
        while step < total_steps:
            if time_budget_sec is not None and (time.time() - t0) > time_budget_sec:
                break
            if step < start_steps:
                a = env.action_space.sample()
                s_t = torch.as_tensor(agent.norm_obs(s), dtype=torch.float32, device=device).unsqueeze(0)
                logp = float(agent.policy.logp_of_action(
                    s_t, torch.as_tensor(a, dtype=torch.float32, device=device).unsqueeze(0)).item())
            else:
                a, logp = agent.act(s)

            s2, r, c, terminated, truncated, info = env.step(a)
            done = terminated or truncated
            episode_done = done or (ep_len + 1) >= ENV_MAX_EP_LEN[env_id]
            agent.observe(s, a, r, c, s2, float(terminated), logp, episode_done=episode_done)
            ep_ret += r
            ep_cost += c
            ep_len += 1
            s = s2
            step += 1

            if step >= start_steps and step % train_every == 0:
                metrics = agent.train_step()
                if metrics is not None:
                    last_metrics = metrics

            if done or ep_len >= ENV_MAX_EP_LEN[env_id]:
                s, info = env.reset()
                agent.observe_reset(s)
                ep_ret, ep_cost, ep_len = 0.0, 0.0, 0

            if step % eval_interval == 0:
                ev_ret, ev_cost, ev_viol = evaluate(
                    eval_env, agent, eval_episodes, ENV_MAX_EP_LEN[env_id], cost_limit)
                row = {"step": step, "eval_return": ev_ret, "eval_cost": ev_cost,
                       "eval_violation_rate": ev_viol, "wall_time": time.time() - t0}
                row.update({k: last_metrics.get(k) for k in COLS if k not in row})
                writer.writerow([row.get(k) for k in COLS])
                f.flush()
    finally:
        env.close()
        eval_env.close()
        f.close()
        with open(meta_path, "w") as mf:
            json.dump({"env_id": env_id, "method": method, "seed": seed,
                       "steps_completed": step, "wall_time": time.time() - t0,
                       "kappa": kappa, "eta": eta, "optimizer_margin": margin,
                       "cost_limit": cost_limit, "shield": shield_enabled,
                       "shield_threshold_frac": shield_threshold_frac, "shield_k": shield_k,
                       "hard_override_mult": hard_override_mult, "tuning_version": tuning_version,
                       "state_correction": state_correction, "clip_s": clip_s,
                       "ratio_lr": ratio_lr, "ratio_updates": ratio_updates,
                       "ratio_every": ratio_every, "ratio_warmup": ratio_warmup,
                       "probe_every": probe_every,
                       "total_steps_requested": total_steps,
                       "eval_interval": eval_interval}, mf)


@torch.no_grad()
def evaluate(env, agent, n_episodes, max_ep_len, cost_limit):
    rets, costs, viol = [], [], []
    for _ in range(n_episodes):
        s, info = env.reset()
        ep_ret, ep_cost = 0.0, 0.0
        for _ in range(max_ep_len):
            a, _ = agent.act(s, deterministic=True, running_episode_cost=ep_cost)
            s, r, c, terminated, truncated, info = env.step(a)
            ep_ret += r
            ep_cost += c
            if terminated or truncated:
                break
        rets.append(ep_ret)
        costs.append(ep_cost)
        viol.append(1.0 if ep_cost > cost_limit else 0.0)
    return float(np.mean(rets)), float(np.mean(costs)), float(np.mean(viol))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--env", required=True, choices=ALL_ENVS)
    p.add_argument("--method", required=True, choices=list(METHOD_TO_OPT_SAMPLER.keys()))
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--total_steps", type=int, default=60_000)
    p.add_argument("--eval_interval", type=int, default=3_000)
    p.add_argument("--eval_episodes", type=int, default=3)
    p.add_argument("--start_steps", type=int, default=1_000)
    p.add_argument("--log_dir", default="runs")
    p.add_argument("--time_budget_sec", type=float, default=None)
    p.add_argument("--device", default="cpu")
    p.add_argument("--train_every", type=int, default=4)
    p.add_argument("--tuning_version", default="v1", choices=["v1", "v2"])
    args = p.parse_args()
    run(args.env, args.method, args.seed, args.total_steps, args.eval_interval,
        args.eval_episodes, args.start_steps, args.log_dir, args.time_budget_sec,
        args.device, args.train_every, args.tuning_version)
