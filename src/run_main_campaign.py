"""Main ICLR campaign: 11 environments x 15 methods x 7 seeds = 1155 runs.

Tiered step budget. The six velocity tasks get 30k steps, the five navigation
tasks 20k: navigation environments are ~1.8x slower per env-step (larger lidar
observations, no early termination), so a flat budget would let them eat the
whole box. Every method within an environment gets an identical budget, which
is what the sampler comparison actually requires.

Wall-clock is bounded three ways:
  * per-run  : --time_budget_sec, so a slow run truncates instead of hanging;
  * campaign : --deadline-min stops launching once the box is nearly full;
  * ordering : seed-major, so a shortfall costs whole seeds, not random cells.
"""
import os
import sys

from vosr_iclr.campaign import run_campaign, main_grid
from vosr_iclr.train import VELOCITY_ENVS, NAVIGATION_ENVS, NEW_ENVS, ALL_ENVS

SEEDS = [0, 1, 2, 3, 4, 5, 6]

# Worker count is held at 14. 16 workers measured 58.6% total CPU on this box
# (Get-Counter \Processor(_Total)\% Processor Time); 14 lands near 50%, which is
# the requested headroom so the desktop stays responsive. An earlier 32-worker
# run on 16 physical cores saturated the box and made it unusable; 16 workers
# is the deliberate cap, not a performance choice.
#
# Sized from the measured 607 env-steps/s aggregate at that worker count
# (train_every=6, eval_episodes=2 -- tests/bench_gpu.py DEV=cpu N=16). The grid
# below is 32.4M env-steps ~= 14.9 h inside a 16 h deadline, leaving room for
# the ragged tail so all 7 seeds complete.
#
# (A GPU port was measured and rejected: 358 env-steps/s at 20 CUDA workers vs
# 1014 on CPU at 32. The nets are 128-wide MLPs at batch 256, so each train step
# is hundreds of tiny kernel launches and the GPU sits launch-bound at 82W/230W
# while every worker serialises through one command queue. MuJoCo physics is
# CPU-only regardless, so GPU workers occupy CPU threads anyway.)
VELOCITY_STEPS = int(os.environ.get("VOSR_VEL_STEPS", 32_000))
NAV_STEPS = int(os.environ.get("VOSR_NAV_STEPS", 20_000))

NAV_ALL = NAVIGATION_ENVS + NEW_ENVS

STEPS = {**{e: VELOCITY_STEPS for e in VELOCITY_ENVS},
         **{e: NAV_STEPS for e in NAV_ALL}}
EVAL_INTERVAL = {**{e: 2_000 for e in VELOCITY_ENVS},
                 **{e: 1_500 for e in NAV_ALL}}

N_PARALLEL = int(os.environ.get("VOSR_N_PARALLEL", 14))
CONTENTION = float(os.environ.get("VOSR_CONTENTION", 2.8))
SAFETY_MULT = float(os.environ.get("VOSR_SAFETY_MULT", 1.5))
DEADLINE_MIN = float(os.environ.get("VOSR_DEADLINE_MIN", 990))
LOG_DIR = os.environ.get("VOSR_LOG_DIR", "runs_main")
TRAIN_EVERY = int(os.environ.get("VOSR_TRAIN_EVERY", 6))
EVAL_EPISODES = int(os.environ.get("VOSR_EVAL_EPISODES", 2))

if __name__ == "__main__":
    grid = main_grid(ALL_ENVS, SEEDS)
    print(f"environments ({len(ALL_ENVS)}): {ALL_ENVS}")
    print(f"seeds: {SEEDS}   methods: 15   runs: {len(grid)}")
    print(f"steps: velocity={VELOCITY_STEPS}  navigation={NAV_STEPS}  "
          f"train_every={TRAIN_EVERY}  eval_episodes={EVAL_EPISODES}")
    total_steps = sum(STEPS[c["env"]] for c in grid)
    print(f"total env-steps to run: {total_steps/1e6:.1f}M")
    sys.stdout.flush()
    run_campaign(grid, LOG_DIR, STEPS, EVAL_INTERVAL, N_PARALLEL, CONTENTION,
                 SAFETY_MULT, DEADLINE_MIN, eval_episodes=EVAL_EPISODES,
                 train_every=TRAIN_EVERY, label="main")
