"""Aggregate the ablation arms into comparison tables.

Each arm lives in its own directory (`runs_ablation/<arm>/`) because train.py
names output files from (env, method, seed) alone. This walks those directories,
summarises each with the same IQM/bootstrap machinery as the main campaign, and
emits one table per ablated parameter plus the paired state-correction table.
"""
import argparse
import os
import re

import numpy as np

from vosr_iclr.aggregate import summarise

KAPPA_RE = re.compile(r"^kappa_(?P<v>[0-9.]+)$")
ETA_RE = re.compile(r"^eta_(?P<v>[0-9.]+)$")


def collect(base):
    arms = {}
    if not os.path.isdir(base):
        return arms
    for d in sorted(os.listdir(base)):
        p = os.path.join(base, d)
        if os.path.isdir(p):
            s = summarise(p)
            if s:
                arms[d] = s
    return arms


def _cell(rec):
    if rec is None:
        return "--"
    return f"{rec['return_iqm']:.1f} / {rec['cost_iqm']:.1f}"


def param_table(arms, regex, title, symbol):
    sel = []
    for name, s in arms.items():
        m = regex.match(name)
        if m:
            sel.append((float(m["v"]), name, s))
    if not sel:
        return ""
    sel.sort()
    envs = sorted({e for _, _, s in sel for e, _ in s})
    lines = [f"### {title}", "",
             "| Environment | " + " | ".join(f"{symbol}={v:g}" for v, _, _ in sel) + " |",
             "|---" * (len(sel) + 1) + "|"]
    seed_counts = set()
    for env in envs:
        cells = []
        for _, _, s in sel:
            rec = next((r for (e, m), r in s.items() if e == env), None)
            if rec is not None:
                seed_counts.add(rec["n_seeds"])
            cells.append(_cell(rec))
        lines.append(f"| {env} | " + " | ".join(cells) + " |")
    # Report the seed count actually present rather than a hardcoded one -- a
    # wrong n in a table caption is exactly the kind of thing that discredits a
    # results section.
    if len(seed_counts) == 1:
        seeds = f"{seed_counts.pop()} seeds per cell"
    elif seed_counts:
        seeds = f"{min(seed_counts)}-{max(seed_counts)} seeds per cell"
    else:
        seeds = "no seeds"
    lines += ["", f"_IQM final return / IQM final cost (budget 25), {seeds}._", ""]
    return "\n".join(lines)


def state_correction_table(arms):
    on, off = arms.get("statecorr_on"), arms.get("statecorr_off")
    if not (on and off):
        return ""
    envs = sorted({e for (e, _) in on} & {e for (e, _) in off})
    lines = ["### State-visitation correction (the bug): paired comparison", "",
             "| Environment | with xi (corrected) | xi == 1 (previous, biased) | "
             "delta return | delta cost |", "|---|---|---|---|---|"]
    dr, dc = [], []
    for env in envs:
        a = next((r for (e, m), r in on.items() if e == env), None)
        b = next((r for (e, m), r in off.items() if e == env), None)
        if a is None or b is None:
            continue
        d_r = a["return_iqm"] - b["return_iqm"]
        d_c = a["cost_iqm"] - b["cost_iqm"]
        dr.append(d_r); dc.append(d_c)
        lines.append(f"| {env} | {_cell(a)} | {_cell(b)} | {d_r:+.1f} | {d_c:+.1f} |")
    if dr:
        lines.append(f"| **Mean** | | | **{np.mean(dr):+.1f}** | **{np.mean(dc):+.1f}** |")
    lines += ["", "_Cells are IQM final return / IQM final cost. Positive delta return "
              "and negative delta cost both favour the corrected estimator._", ""]
    return "\n".join(lines)


def xi_health_table(arms):
    rows = []
    for name, s in sorted(arms.items()):
        vals = [r for r in s.values() if not np.isnan(r.get("xi_ess", np.nan))]
        if not vals:
            continue
        rows.append((name,
                     float(np.mean([r["xi_mean"] for r in vals])),
                     float(np.mean([r["xi_ess"] for r in vals]))))
    if not rows:
        return ""
    lines = ["### Density-ratio estimator health by arm", "",
             "| Arm | mean xi (target 1.0) | xi ESS fraction |", "|---|---|---|"]
    for n, m, e in rows:
        lines.append(f"| {n} | {m:.3f} | {e:.3f} |")
    lines.append("")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--abl-dir", default="runs_ablation")
    p.add_argument("--out", default="results")
    a = p.parse_args()
    arms = collect(a.abl_dir)
    os.makedirs(a.out, exist_ok=True)
    parts = ["# VOSR ablation studies (ICLR revision)", "",
             f"Source: `{a.abl_dir}/`, one directory per arm. "
             f"Arms found: {len(arms)}.", ""]
    parts.append(param_table(arms, KAPPA_RE, "Ablation: kappa (reward/cost blend in the replay score)", "kappa"))
    parts.append(param_table(arms, ETA_RE, "Ablation: eta (trust-region temperature)", "eta"))
    parts.append(state_correction_table(arms))
    parts.append(xi_health_table(arms))
    out = os.path.join(a.out, "ablation_tables.md")
    with open(out, "w") as f:
        f.write("\n".join(x for x in parts if x))
    print(f"aggregated {len(arms)} ablation arms -> {out}")
    for n in sorted(arms):
        print(f"  {n}: {len(arms[n])} cells")


if __name__ == "__main__":
    main()
