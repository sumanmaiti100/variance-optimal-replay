"""Time-budgeted, resumable parallel campaign runner.

Design notes
------------
* Every child run is launched with `--time_budget_sec`, so it exits cleanly and
  flushes its CSV even if it is slower than predicted. A run that hits its cap
  still yields a usable (shorter) learning curve rather than nothing.
* Runs are scheduled longest-estimate-first, which minimises the ragged tail at
  the end of the campaign.
* A campaign-level `--deadline-min` stops launching new work once the remaining
  time cannot fit another run, so the whole thing lands inside a wall-clock box.
* `--skip-existing` (default) makes the campaign resumable after an interruption.
"""
import argparse
import itertools
import json
import os
import subprocess
import sys
import time

OPTIMIZERS = ["sac_lag", "crpo", "pcrpo"]
SAMPLERS = ["uniform", "td_per", "safety_per", "uncertainty_per", "vosr"]

# Measured single-process seconds per 1e4 env steps (solo, this machine), from
# tests/smoke.py. Parallel contention is folded in separately by CONTENTION.
RATE_SOLO = {
    "SafetyAntVelocity-v1": (95.0, 190.0),
    "SafetyHalfCheetahVelocity-v1": (88.0, 178.0),
    "SafetyHopperVelocity-v1": (83.0, 173.0),
    "SafetyHumanoidVelocity-v1": (150.0, 260.0),
    "SafetySwimmerVelocity-v1": (80.0, 168.0),
    "SafetyWalker2dVelocity-v1": (88.0, 178.0),
    "SafetyPointButton1-v0": (150.0, 250.0),
    "SafetyPointPush1-v0": (150.0, 250.0),
    "SafetyCarGoal1-v0": (152.0, 255.0),
    "SafetyCarButton1-v0": (170.0, 275.0),
    "SafetyPointGoal2-v0": (165.0, 264.0),
}


def rate(env, method, contention):
    base, vosr = RATE_SOLO[env]
    return (vosr if method.endswith("_vosr") else base) * contention


def estimated_seconds(cfg, steps_map, contention):
    return steps_map[cfg["env"]] / 1e4 * rate(cfg["env"], cfg["method"], contention)


def run_name(cfg):
    tag = cfg.get("tag")
    base = f"{cfg['env']}__{cfg['method']}__seed{cfg['seed']}"
    return f"{tag}__{base}" if tag else base


def already_done(cfg, log_dir):
    return os.path.exists(os.path.join(log_dir, run_name(cfg) + ".csv"))


def launch(cfg, log_dir, steps_map, eval_map, contention, safety_mult,
           eval_episodes, train_every, hard_cap=None, tuning_version="v1"):
    name = run_name(cfg)
    est = estimated_seconds(cfg, steps_map, contention)
    budget = est * safety_mult
    if hard_cap is not None:
        budget = min(budget, hard_cap)
    cmd = [sys.executable, "-m", "vosr_iclr.train",
           "--env", cfg["env"], "--method", cfg["method"], "--seed", str(cfg["seed"]),
           "--total_steps", str(steps_map[cfg["env"]]),
           "--eval_interval", str(eval_map[cfg["env"]]),
           "--eval_episodes", str(eval_episodes),
           "--start_steps", "1000",
           "--log_dir", log_dir,
           "--device", "cpu",
           "--train_every", str(train_every),
           "--tuning_version", tuning_version,
           "--time_budget_sec", str(int(budget))]
    env_vars = os.environ.copy()
    env_vars["OMP_NUM_THREADS"] = "1"
    env_vars["MKL_NUM_THREADS"] = "1"
    env_vars["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_vars.update(cfg.get("env_overrides", {}))
    # Child runs write under the campaign's own run name; train.py names files
    # from (env, method, seed), so tagged ablation arms go to separate dirs.
    out_f = open(os.path.join(log_dir, name + ".stdout.log"), "w")
    p = subprocess.Popen(cmd, cwd=env_vars["PYTHONPATH"], env=env_vars,
                         stdout=out_f, stderr=subprocess.STDOUT)
    return {"proc": p, "out_f": out_f, "name": name, "cfg": cfg,
            "start": time.time(), "deadline": time.time() + budget + 180}


def run_campaign(grid, log_dir, steps_map, eval_map, n_parallel, contention,
                 safety_mult, deadline_min, eval_episodes=3, train_every=4,
                 skip_existing=True, label="campaign", tuning_version="v1"):
    os.makedirs(log_dir, exist_ok=True)
    if skip_existing:
        before = len(grid)
        grid = [c for c in grid if not already_done(c, log_dir)]
        print(f"[{label}] skipping {before - len(grid)} runs already in {log_dir}/")

    # Seed-major ordering. If the campaign runs out of wall-clock, what is lost
    # is whole *seeds* (the tail of the seed list) rather than a scatter of
    # random (env, method) cells -- so the resulting dataset stays a complete,
    # balanced grid at a smaller seed count, which is reportable. Within a seed
    # block, longest-first keeps the tail tight.
    seed_order = {s: i for i, s in enumerate(sorted({c["seed"] for c in grid}))}
    grid.sort(key=lambda c: (seed_order[c["seed"]],
                             -estimated_seconds(c, steps_map, contention)))
    total_est = sum(estimated_seconds(c, steps_map, contention) for c in grid)
    print(f"[{label}] {len(grid)} runs | est compute {total_est/3600:.1f} proc-h | "
          f"parallelism {n_parallel} | est wall {total_est/n_parallel/3600:.2f} h | "
          f"deadline {deadline_min} min | -> {log_dir}/")
    sys.stdout.flush()

    t0 = time.time()
    hard_deadline = t0 + deadline_min * 60
    manifest = open(os.path.join(log_dir, f"manifest_{label}.jsonl"), "a")
    running, pending = [], list(grid)
    done_ct, killed_ct = 0, 0

    while pending or running:
        now = time.time()
        while pending and len(running) < n_parallel and now < hard_deadline:
            cfg = pending.pop(0)
            remaining = hard_deadline - time.time()
            running.append(launch(cfg, log_dir, steps_map, eval_map, contention,
                                  safety_mult, eval_episodes, train_every,
                                  hard_cap=max(60.0, remaining - 60),
                                  tuning_version=tuning_version))
        if pending and time.time() >= hard_deadline:
            print(f"[{label}] deadline reached, dropping {len(pending)} unstarted runs")
            manifest.write(json.dumps({"event": "deadline_drop", "n": len(pending),
                                       "runs": [run_name(c) for c in pending]}) + "\n")
            manifest.flush()
            pending = []
        time.sleep(3)
        still = []
        for r in running:
            rc = r["proc"].poll()
            timed_out = time.time() > r["deadline"] and rc is None
            if rc is not None or timed_out:
                if timed_out:
                    r["proc"].kill(); r["proc"].wait(); status = "killed_timeout"; killed_ct += 1
                else:
                    status = "ok" if rc == 0 else f"exit_{rc}"
                    done_ct += 1
                r["out_f"].close()
                manifest.write(json.dumps({"run": r["name"], "status": status,
                                           "wall_time": time.time() - r["start"],
                                           **{k: v for k, v in r["cfg"].items()
                                              if k != "env_overrides"}}) + "\n")
                manifest.flush()
                el = (time.time() - t0) / 60
                print(f"[{label}][{el:6.1f}m] {r['name']} -> {status} "
                      f"({len(pending)} pending, {len(running)-1} running)")
                sys.stdout.flush()
            else:
                still.append(r)
        running = still

    manifest.close()
    print(f"[{label}] COMPLETE in {(time.time()-t0)/60:.1f} min "
          f"({done_ct} finished, {killed_ct} hit their cap)")
    return time.time() - t0


def main_grid(envs, seeds, optimizers=OPTIMIZERS, samplers=SAMPLERS):
    return [{"env": e, "method": f"{o}_{s}", "seed": sd}
            for e in envs for o, s in itertools.product(optimizers, samplers) for sd in seeds]


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--envs", nargs="+", required=True)
    p.add_argument("--seeds", nargs="+", type=int, required=True)
    p.add_argument("--steps", type=int, required=True)
    p.add_argument("--eval-interval", type=int, required=True)
    p.add_argument("--log-dir", required=True)
    p.add_argument("--n-parallel", type=int, default=26)
    p.add_argument("--contention", type=float, default=1.8)
    p.add_argument("--safety-mult", type=float, default=1.6)
    p.add_argument("--deadline-min", type=float, default=600)
    p.add_argument("--eval-episodes", type=int, default=3)
    p.add_argument("--label", default="campaign")
    a = p.parse_args()
    grid = main_grid(a.envs, a.seeds)
    run_campaign(grid, a.log_dir, {e: a.steps for e in a.envs},
                 {e: a.eval_interval for e in a.envs}, a.n_parallel, a.contention,
                 a.safety_mult, a.deadline_min, a.eval_episodes, label=a.label)
