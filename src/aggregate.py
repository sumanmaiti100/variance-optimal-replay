"""Aggregate campaign CSVs into the paper's tables.

Reports, per (environment, method):
  * final return and final cost -- mean over the last 20% of eval points of each
    run, then IQM across seeds with a stratified bootstrap 95% CI;
  * cost-violation fraction -- fraction of eval points with eval_cost > budget,
    which is the quantity the paper's "Violation" row reports;
  * normalised cost-gradient variance -- sigma_c^2 of a method divided by
    Uniform's, matching Table 1.

IQM (interquartile mean) with bootstrap CIs follows the reliable-RL evaluation
protocol; with 7 seeds it is far more robust than a plain mean, which is why the
seed count matters more than the horizon for this comparison.
"""
import argparse
import csv
import json
import os
import re
from collections import defaultdict

import numpy as np

RUN_RE = re.compile(r"^(?P<env>.+?)__(?P<method>.+?)__seed(?P<seed>\d+)\.csv$")
OPTIMIZERS = ["sac_lag", "crpo", "pcrpo"]
SAMPLERS = ["uniform", "td_per", "safety_per", "uncertainty_per", "vosr"]
SAMPLER_LABEL = {"uniform": "Uniform", "td_per": "TD-PER", "safety_per": "Safety-PER",
                 "uncertainty_per": "Unc.-PER", "vosr": "VOSR"}


def _f(x):
    try:
        v = float(x)
        return v if np.isfinite(v) else np.nan
    except (TypeError, ValueError):
        return np.nan


def load_runs(log_dir):
    runs = defaultdict(list)
    for fn in sorted(os.listdir(log_dir)):
        m = RUN_RE.match(fn)
        if not m:
            continue
        rows = []
        with open(os.path.join(log_dir, fn), newline="") as f:
            for row in csv.DictReader(f):
                rows.append(row)
        if not rows:
            continue
        runs[(m["env"], m["method"])].append({"seed": int(m["seed"]), "rows": rows})
    return runs


def tail_mean(rows, key, frac=0.2):
    vals = [_f(r.get(key)) for r in rows]
    vals = [v for v in vals if not np.isnan(v)]
    if not vals:
        return np.nan
    k = max(1, int(len(vals) * frac))
    return float(np.mean(vals[-k:]))


def violation_fraction(rows, cost_limit):
    vals = [_f(r.get("eval_cost")) for r in rows]
    vals = [v for v in vals if not np.isnan(v)]
    if not vals:
        return np.nan
    return float(np.mean([1.0 if v > cost_limit else 0.0 for v in vals]))


def iqm(x):
    x = np.asarray([v for v in x if not np.isnan(v)], dtype=float)
    if x.size == 0:
        return np.nan
    if x.size < 4:
        return float(np.mean(x))
    x = np.sort(x)
    lo, hi = int(np.floor(x.size * 0.25)), int(np.ceil(x.size * 0.75))
    return float(np.mean(x[lo:hi]))


def bootstrap_ci(x, stat=iqm, n_boot=2000, alpha=0.05, seed=0):
    x = np.asarray([v for v in x if not np.isnan(v)], dtype=float)
    if x.size < 2:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    boots = [stat(rng.choice(x, size=x.size, replace=True)) for _ in range(n_boot)]
    return (float(np.percentile(boots, 100 * alpha / 2)),
            float(np.percentile(boots, 100 * (1 - alpha / 2))))


def summarise(log_dir, cost_limit=25.0):
    runs = load_runs(log_dir)
    out = {}
    for (env, method), lst in runs.items():
        rec = {"n_seeds": len(lst), "seeds": sorted(r["seed"] for r in lst)}
        for key, label in (("eval_return", "return"), ("eval_cost", "cost")):
            per_seed = [tail_mean(r["rows"], key) for r in lst]
            rec[f"{label}_iqm"] = iqm(per_seed)
            rec[f"{label}_ci"] = bootstrap_ci(per_seed)
            rec[f"{label}_per_seed"] = per_seed
        rec["violation"] = float(np.nanmean([violation_fraction(r["rows"], cost_limit)
                                             for r in lst]))
        for k in ("sigma_c2", "sigma_r2", "sigma_c2_uniform", "sigma_c2_qstar"):
            v = [tail_mean(r["rows"], k, frac=1.0) for r in lst]
            rec[k] = float(np.nanmean(v)) if np.any(~np.isnan(v)) else np.nan
        for k in ("xi_mean", "xi_ess", "ess_frac"):
            v = [tail_mean(r["rows"], k, frac=1.0) for r in lst]
            rec[k] = float(np.nanmean(v)) if np.any(~np.isnan(v)) else np.nan
        rec["steps"] = max((len(r["rows"]) for r in lst), default=0)
        out[(env, method)] = rec
    return out


def md_main_table(summary, envs, optimizer):
    lines = [f"### {optimizer}", "",
             "| Environment | " + " | ".join(SAMPLER_LABEL[s] for s in SAMPLERS) + " |",
             "|---" * (len(SAMPLERS) + 1) + "|"]
    for env in envs:
        cells = []
        for s in SAMPLERS:
            rec = summary.get((env, f"{optimizer}_{s}"))
            if rec is None:
                cells.append("--")
            else:
                cells.append(f"{rec['return_iqm']:.1f} / {rec['cost_iqm']:.1f}")
        lines.append(f"| {env} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("_Cells are IQM final return / IQM final cost (budget 25)._")
    lines.append("")
    return "\n".join(lines)


def md_variance_table(summary, envs):
    """Table 1: cost-gradient variance relative to Uniform replay.

    The normaliser is measured *within each run*: `variance_probe` evaluates
    sigma_c^2 both under the run's own sampler and under uniform sampling on the
    identical pool, at the same policy. That makes the ratio a paired
    measurement rather than a comparison across two separate training runs, and
    it gives a free sanity check -- the Uniform column must come out at 1.00.
    The q* column is Theorem 1's variance floor on the same pool.
    """
    cols = SAMPLERS + ["qstar"]
    header = [SAMPLER_LABEL[s] for s in SAMPLERS] + ["q* (floor)"]
    lines = ["### Cost-gradient variance relative to Uniform replay (lower is better)", "",
             "| Environment | " + " | ".join(header) + " |",
             "|---" * (len(cols) + 1) + "|"]
    acc = defaultdict(list)
    for env in envs:
        cells = []
        for s in cols:
            vals = []
            for o in OPTIMIZERS:
                key = (env, f"{o}_{'uniform' if s == 'qstar' else s}")
                r = summary.get(key)
                if r is None:
                    continue
                num = r["sigma_c2_qstar"] if s == "qstar" else r["sigma_c2"]
                den = r["sigma_c2_uniform"]
                if np.isnan(num) or np.isnan(den) or den <= 0:
                    continue
                vals.append(num / den)
            if vals:
                m = float(np.mean(vals))
                acc[s].append(m)
                cells.append(f"**{m:.2f}**" if s == "vosr" else f"{m:.2f}")
            else:
                cells.append("--")
        lines.append(f"| {env} | " + " | ".join(cells) + " |")
    lines.append("| **Average** | " + " | ".join(
        f"**{np.mean(acc[s]):.2f}**" if acc[s] else "--" for s in cols) + " |")
    lines.append("")
    lines.append("_Measured by the closed-form Theorem 1 probe, paired within each run "
                 "(same pool, same policy, both samplers). Uniform is 1.00 by construction._")
    lines.append("")
    return "\n".join(lines)


def md_violation_table(summary, envs):
    lines = ["### Cost-violation fraction (lower is better)", "",
             "| Environment | " + " | ".join(SAMPLER_LABEL[s] for s in SAMPLERS) + " |",
             "|---" * (len(SAMPLERS) + 1) + "|"]
    totals = defaultdict(list)
    for env in envs:
        cells = []
        for s in SAMPLERS:
            vals = [summary[(env, f"{o}_{s}")]["violation"] for o in OPTIMIZERS
                    if (env, f"{o}_{s}") in summary]
            vals = [v for v in vals if not np.isnan(v)]
            if vals:
                m = float(np.mean(vals))
                totals[s].append(m)
                cells.append(f"{m:.3f}")
            else:
                cells.append("--")
        lines.append(f"| {env} | " + " | ".join(cells) + " |")
    lines.append("| **Average** | " + " | ".join(
        f"**{np.mean(totals[s]):.3f}**" if totals[s] else "--" for s in SAMPLERS) + " |")
    lines.append("")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--log-dir", default="runs_main")
    p.add_argument("--out", default="results")
    p.add_argument("--cost-limit", type=float, default=25.0)
    a = p.parse_args()

    summary = summarise(a.log_dir, a.cost_limit)
    envs = sorted({e for e, _ in summary})
    os.makedirs(a.out, exist_ok=True)

    with open(os.path.join(a.out, "summary.json"), "w") as f:
        json.dump({f"{e}|{m}": {k: (v if not isinstance(v, tuple) else list(v))
                                for k, v in rec.items()}
                   for (e, m), rec in summary.items()}, f, indent=2, default=str)

    with open(os.path.join(a.out, "summary.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["env", "method", "n_seeds", "return_iqm", "return_lo", "return_hi",
                    "cost_iqm", "cost_lo", "cost_hi", "violation", "sigma_c2",
                    "sigma_r2", "sigma_c2_uniform", "sigma_c2_qstar",
                    "xi_mean", "xi_ess", "ess_frac", "eval_points"])
        for (e, m), r in sorted(summary.items()):
            w.writerow([e, m, r["n_seeds"], r["return_iqm"], r["return_ci"][0], r["return_ci"][1],
                        r["cost_iqm"], r["cost_ci"][0], r["cost_ci"][1], r["violation"],
                        r["sigma_c2"], r.get("sigma_r2"), r.get("sigma_c2_uniform"),
                        r.get("sigma_c2_qstar"), r["xi_mean"], r["xi_ess"], r["ess_frac"], r["steps"]])

    parts = ["# VOSR (ICLR revision) -- aggregate results", "",
             f"Source: `{a.log_dir}/`  |  cost budget: {a.cost_limit}", ""]
    for o in OPTIMIZERS:
        parts.append(md_main_table(summary, envs, o))
    parts.append(md_variance_table(summary, envs))
    parts.append(md_violation_table(summary, envs))
    with open(os.path.join(a.out, "tables.md"), "w") as f:
        f.write("\n".join(parts))

    n = len(summary)
    seeds = [r["n_seeds"] for r in summary.values()]
    print(f"aggregated {n} (env, method) cells from {a.log_dir}/")
    print(f"seeds per cell: min={min(seeds) if seeds else 0} max={max(seeds) if seeds else 0}")
    print(f"wrote {a.out}/tables.md, summary.csv, summary.json")


if __name__ == "__main__":
    main()
