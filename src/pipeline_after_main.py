"""Chain the remaining pipeline behind the main campaign so no CPU sits idle.

Waits for `[main] COMPLETE` in the campaign log, then runs, in order:
  1. the ablation suite (kappa, eta, state-correction control),
  2. aggregation of the main campaign into tables,
  3. figure generation for both the main campaign and the ablations.

Each stage is logged separately under logs/ so a failure in one does not hide
the others. Safe to start at any time -- it only waits and then runs.
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "logs", "main_campaign.log")
POLL = 60
MAX_WAIT_H = float(os.environ.get("VOSR_CHAIN_MAX_WAIT_H", 18))


def main_done():
    try:
        with open(LOG, errors="ignore") as f:
            return "[main] COMPLETE" in f.read()
    except OSError:
        return False


def stage(name, args, logfile):
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT
    env["OMP_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"
    path = os.path.join(ROOT, "logs", logfile)
    print(f"[chain] === {name} -> logs/{logfile}", flush=True)
    t = time.time()
    with open(path, "w") as f:
        rc = subprocess.call([sys.executable, "-u"] + args, cwd=ROOT, env=env,
                             stdout=f, stderr=subprocess.STDOUT)
    print(f"[chain] {name} finished rc={rc} in {(time.time()-t)/60:.1f} min", flush=True)
    return rc


if __name__ == "__main__":
    t0 = time.time()
    print("[chain] waiting for main campaign to complete ...", flush=True)
    while not main_done():
        if (time.time() - t0) / 3600 > MAX_WAIT_H:
            print("[chain] max wait exceeded; proceeding with whatever exists", flush=True)
            break
        time.sleep(POLL)
    print(f"[chain] main campaign done after {(time.time()-t0)/3600:.2f} h of waiting", flush=True)

    stage("ablations", ["-m", "vosr_iclr.run_ablations"], "ablations.log")
    stage("aggregate-main", ["-m", "vosr_iclr.aggregate",
                             "--log-dir", "runs_main", "--out", "results"], "aggregate.log")
    stage("aggregate-ablations", ["-m", "vosr_iclr.aggregate_ablations",
                                  "--abl-dir", "runs_ablation", "--out", "results"],
          "aggregate_ablations.log")
    stage("figures", ["-m", "vosr_iclr.make_figures", "--log-dir", "runs_main",
                      "--abl-dir", "runs_ablation", "--out", "figures"], "figures.log")
    stage("latex-tables", ["-m", "vosr_iclr.make_latex_tables",
                           "--summary", "results/summary.csv",
                           "--out", "paper/tables_generated.tex"], "latex_tables.log")
    print(f"[chain] ALL STAGES COMPLETE in {(time.time()-t0)/3600:.2f} h", flush=True)
