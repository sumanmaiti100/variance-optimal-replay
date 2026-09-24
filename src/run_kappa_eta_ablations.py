"""Resume/run just the kappa and eta ablation arms (the paper's Figure 4
sweep), skipping the state-correction control arm.

Reuses run_ablations.py's environments, seeds, and step budgets so results
are directly comparable to the arms already completed there (5/5 kappa
arms, 4/5 eta arms as of this script's creation -- run_campaign's
skip_existing=True default detects and skips those instantly, so this only
actually trains whatever is still missing, e.g. eta_5.0).
"""
import os
import sys
import time

from vosr_iclr.campaign import run_campaign
from vosr_iclr.run_ablations import (ABL_ENVS, ABL_SEEDS, ABL_METHOD, STEPS,
                                     EVAL_INTERVAL, KAPPAS, ETAS, BASE,
                                     N_PARALLEL, CONTENTION, SAFETY_MULT,
                                     TRAIN_EVERY, EVAL_EPISODES, arm)

TOTAL_DEADLINE_MIN = float(os.environ.get("VOSR_ABL_DEADLINE_MIN", 60))

if __name__ == "__main__":
    arms = ([arm(f"kappa_{k}", {"VOSR_ABLATION_KAPPA": str(k)}) for k in KAPPAS] +
            [arm(f"eta_{e}", {"VOSR_ABLATION_ETA": str(e)}) for e in ETAS])
    n_runs = sum(len(g) for _, g in arms)
    print(f"kappa/eta ablation arms: {len(arms)}  runs: {n_runs}  "
          f"envs: {ABL_ENVS}  seeds: {ABL_SEEDS}")
    sys.stdout.flush()

    t_start = time.time()
    for name, grid in arms:
        remaining_min = TOTAL_DEADLINE_MIN - (time.time() - t_start) / 60
        if remaining_min <= 2:
            print(f"[kappa_eta] out of budget, skipping remaining arms from {name}")
            break
        run_campaign(grid, os.path.join(BASE, name), STEPS, EVAL_INTERVAL,
                     N_PARALLEL, CONTENTION, SAFETY_MULT, remaining_min,
                     eval_episodes=EVAL_EPISODES, train_every=TRAIN_EVERY,
                     label=f"kappa_eta:{name}")
    print(f"[kappa_eta] all arms done in {(time.time()-t_start)/60:.1f} min")
