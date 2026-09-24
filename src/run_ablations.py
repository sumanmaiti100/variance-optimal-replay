"""Ablation suite.

Primary (user-selected): kappa and eta, the two VOSR design constants from the
paper's Figure 4, rerun under the corrected estimator so that figure remains
valid for the revision.

Also included, small: state-correction on/off. This is the control arm that
measures what the bug actually cost -- xi == 1 reproduces the AAAI-era
behaviour exactly -- and the revision needs that number in it.

Each arm writes to its own directory because train.py names output files from
(env, method, seed) alone, so arms would otherwise collide.
"""
import os
import sys

from vosr_iclr.campaign import run_campaign

# SAC-Lagrangian, matching the paper's Figure 4. Four environments spanning the
# tiers: two reward-max velocity tasks (the paper's own choices), one mild-tier
# velocity task, and one new severe-tier navigation task.
ABL_ENVS = ["SafetyHopperVelocity-v1", "SafetyWalker2dVelocity-v1",
            "SafetyAntVelocity-v1", "SafetyCarButton1-v0"]
ABL_SEEDS = [0, 1, 2]
ABL_METHOD = "sac_lag_vosr"

VEL_STEPS = int(os.environ.get("ABL_VEL_STEPS", 24_000))
NAV_STEPS = int(os.environ.get("ABL_NAV_STEPS", 16_000))
STEPS = {e: (NAV_STEPS if e.startswith("SafetyCar") or e.startswith("SafetyPoint")
             else VEL_STEPS) for e in ABL_ENVS}
EVAL_INTERVAL = {e: 2_000 for e in ABL_ENVS}

KAPPAS = [0.0, 0.15, 0.35, 0.7, 1.5]
ETAS = [0.1, 0.5, 1.0, 2.0, 5.0]

BASE = os.environ.get("VOSR_ABL_DIR", "runs_ablation")
N_PARALLEL = int(os.environ.get("VOSR_N_PARALLEL", 14))
CONTENTION = float(os.environ.get("VOSR_CONTENTION", 2.8))
SAFETY_MULT = float(os.environ.get("VOSR_SAFETY_MULT", 1.5))
TRAIN_EVERY = int(os.environ.get("VOSR_TRAIN_EVERY", 6))
EVAL_EPISODES = int(os.environ.get("VOSR_EVAL_EPISODES", 2))
TOTAL_DEADLINE_MIN = float(os.environ.get("VOSR_ABL_DEADLINE_MIN", 210))


def arm(name, overrides):
    grid = [{"env": e, "method": ABL_METHOD, "seed": s, "env_overrides": overrides}
            for e in ABL_ENVS for s in ABL_SEEDS]
    return name, grid


def build_arms():
    arms = []
    for k in KAPPAS:
        arms.append(arm(f"kappa_{k}", {"VOSR_ABLATION_KAPPA": str(k)}))
    for e in ETAS:
        arms.append(arm(f"eta_{e}", {"VOSR_ABLATION_ETA": str(e)}))
    # Control arm for the bug: xi == 1. The paired "on" arm is kappa's / eta's
    # deployed setting, which is already run above (kappa=0.15/0.35/0.7 by tier
    # and eta=1.0), so we only need the "off" side plus a matched "on" side at
    # identical settings for a clean pair.
    arms.append(arm("statecorr_on", {"VOSR_STATE_CORRECTION": "1"}))
    arms.append(arm("statecorr_off", {"VOSR_STATE_CORRECTION": "0"}))
    return arms


if __name__ == "__main__":
    arms = build_arms()
    n_runs = sum(len(g) for _, g in arms)
    total_steps = sum(STEPS[c["env"]] for _, g in arms for c in g)
    print(f"ablation arms: {len(arms)}  runs: {n_runs}  env-steps: {total_steps/1e6:.2f}M")
    sys.stdout.flush()

    import time
    t_start = time.time()
    for name, grid in arms:
        remaining_min = TOTAL_DEADLINE_MIN - (time.time() - t_start) / 60
        if remaining_min <= 2:
            print(f"[ablation] out of budget, skipping remaining arms from {name}")
            break
        run_campaign(grid, os.path.join(BASE, name), STEPS, EVAL_INTERVAL,
                     N_PARALLEL, CONTENTION, SAFETY_MULT, remaining_min,
                     eval_episodes=EVAL_EPISODES, train_every=TRAIN_EVERY,
                     label=f"abl:{name}")
    print(f"[ablation] all arms done in {(time.time()-t_start)/60:.1f} min")
