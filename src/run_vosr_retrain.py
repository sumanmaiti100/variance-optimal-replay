"""VOSR-only retrain with the V2 per-environment tuning.

11 environments x 3 optimizers x 7 seeds = 231 runs, VOSR sampler only.
Baselines (Uniform/TD-PER/Safety-PER/Uncertainty-PER) are NOT touched -- they
stay exactly as recorded in runs_main/. Writes to a separate directory so
runs_main/ is never modified; the two can be aggregated together or compared
directly (same envs, same optimizers, same seeds, same step budgets -- only
VOSR's own tuning differs).

Same step budgets as the main campaign for direct comparability:
velocity=32000, navigation=20000, train_every=6, eval_episodes=2.
"""
import os
import sys

from vosr_iclr.campaign import run_campaign
from vosr_iclr.train import VELOCITY_ENVS, NAVIGATION_ENVS, NEW_ENVS, ALL_ENVS

SEEDS = [0, 1, 2, 3, 4, 5, 6]
OPTIMIZERS = ["sac_lag", "crpo", "pcrpo"]

VELOCITY_STEPS = int(os.environ.get("VOSR_VEL_STEPS", 32_000))
NAV_STEPS = int(os.environ.get("VOSR_NAV_STEPS", 20_000))
NAV_ALL = NAVIGATION_ENVS + NEW_ENVS

STEPS = {**{e: VELOCITY_STEPS for e in VELOCITY_ENVS}, **{e: NAV_STEPS for e in NAV_ALL}}
EVAL_INTERVAL = {**{e: 2_000 for e in VELOCITY_ENVS}, **{e: 1_500 for e in NAV_ALL}}

N_PARALLEL = int(os.environ.get("VOSR_N_PARALLEL", 14))
CONTENTION = float(os.environ.get("VOSR_CONTENTION", 2.8))
SAFETY_MULT = float(os.environ.get("VOSR_SAFETY_MULT", 1.5))
# campaign.py's RATE_SOLO/contention model estimated 7.3h for this workload,
# but an empirical measurement just before launch (the matched V1/V2 tuning
# pilot -- 22 pure-VOSR runs, same 14 workers) measured 467.9 env-steps/s
# aggregate, implying ~3.6h for this retrain's 6.13M steps. Deadline set with
# margin above the empirical estimate, not the stale rate-table one.
DEADLINE_MIN = float(os.environ.get("VOSR_DEADLINE_MIN", 330))
LOG_DIR = os.environ.get("VOSR_LOG_DIR", "runs_vosr_v2")
TRAIN_EVERY = int(os.environ.get("VOSR_TRAIN_EVERY", 6))
EVAL_EPISODES = int(os.environ.get("VOSR_EVAL_EPISODES", 2))

if __name__ == "__main__":
    grid = [{"env": e, "method": f"{o}_vosr", "seed": s}
            for e in ALL_ENVS for o in OPTIMIZERS for s in SEEDS]
    total_steps = sum(STEPS[c["env"]] for c in grid)
    print(f"VOSR-only retrain: {len(grid)} runs (11 envs x 3 optimizers x {len(SEEDS)} seeds)")
    print(f"tuning_version=v2 (per-env, see ENV_TUNING_V2 in train.py) | "
          f"total env-steps {total_steps/1e6:.1f}M | writing to {LOG_DIR}/ (runs_main/ untouched)")
    sys.stdout.flush()
    run_campaign(grid, LOG_DIR, STEPS, EVAL_INTERVAL, N_PARALLEL, CONTENTION,
                 SAFETY_MULT, DEADLINE_MIN, eval_episodes=EVAL_EPISODES,
                 train_every=TRAIN_EVERY, label="vosr_v2", tuning_version="v2")
