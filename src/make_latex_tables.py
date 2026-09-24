"""Emit paper-ready LaTeX tables from the aggregated results.

Writes paper/tables_generated.tex containing:
  * Table 1  -- cost-gradient variance relative to Uniform replay (+ q* floor)
  * Table 2  -- final return / cost per environment, one block per optimizer
  * Table 3  -- cost-violation fraction
Numbers come from results/summary.csv, so the LaTeX never disagrees with the
markdown tables.
"""
import argparse
import csv
import os
from collections import defaultdict

import numpy as np

OPTIMIZERS = [("sac_lag", "SAC-Lagrangian"), ("crpo", "CRPO"), ("pcrpo", "PCRPO")]
SAMPLERS = ["uniform", "td_per", "safety_per", "uncertainty_per", "vosr"]
LABEL = {"uniform": "Uniform", "td_per": "TD-PER", "safety_per": "Safety-PER",
         "uncertainty_per": "Unc.-PER", "vosr": "VOSR"}
SHORT = {
    "SafetyAntVelocity-v1": "Ant", "SafetyHalfCheetahVelocity-v1": "HalfCheetah",
    "SafetyHopperVelocity-v1": "Hopper", "SafetyHumanoidVelocity-v1": "Humanoid",
    "SafetySwimmerVelocity-v1": "Swimmer", "SafetyWalker2dVelocity-v1": "Walker2d",
    "SafetyPointButton1-v0": "PointButton1", "SafetyPointPush1-v0": "PointPush1",
    "SafetyCarGoal1-v0": "CarGoal1$^\\dagger$", "SafetyCarButton1-v0": "CarButton1$^\\dagger$",
    "SafetyPointGoal2-v0": "PointGoal2$^\\dagger$",
}
ORDER = list(SHORT)


def load(path):
    d = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            def g(k):
                try:
                    v = float(r[k])
                    return v if np.isfinite(v) else np.nan
                except (KeyError, TypeError, ValueError):
                    return np.nan
            d[(r["env"], r["method"])] = {
                "ret": g("return_iqm"), "lo": g("return_lo"), "hi": g("return_hi"),
                "cost": g("cost_iqm"), "viol": g("violation"),
                "sc2": g("sigma_c2"), "sc2u": g("sigma_c2_uniform"),
                "sc2q": g("sigma_c2_qstar"), "n": r.get("n_seeds", "?")}
    return d


def _fmt(x, p=2):
    return "--" if x is None or np.isnan(x) else f"{x:.{p}f}"


def variance_table(d, envs):
    rows = []
    acc = defaultdict(list)
    for env in envs:
        cells = {}
        for s in SAMPLERS + ["qstar"]:
            vals = []
            for o, _ in OPTIMIZERS:
                r = d.get((env, f"{o}_{'uniform' if s == 'qstar' else s}"))
                if not r:
                    continue
                num = r["sc2q"] if s == "qstar" else r["sc2"]
                den = r["sc2u"]
                if np.isfinite(num) and np.isfinite(den) and den > 0:
                    vals.append(num / den)
            cells[s] = float(np.mean(vals)) if vals else np.nan
            if vals:
                acc[s].append(cells[s])
        if any(np.isfinite(v) for v in cells.values()):
            rows.append((env, cells))
    if not rows:
        return "% (no variance data)\n"

    head = " & ".join(LABEL[s] for s in SAMPLERS) + " & $q^\\star_c$"
    out = ["\\begin{table}[t]", "\\centering", "\\small",
           "\\caption{Cost-gradient variance relative to Uniform replay (lower is "
           "better), measured by the closed-form Theorem~1 probe paired within each "
           "run. Uniform is $1.00$ by construction. $q^\\star_c$ is the true "
           "$\\sigma_c^2$ floor ($\\kappa=0$ specialisation of Corollary~1). "
           "$\\dagger$ marks environments new in this revision.}",
           "\\label{tab:variance}",
           "\\begin{tabular}{l" + "c" * (len(SAMPLERS) + 1) + "}", "\\toprule",
           "Environment & " + head + " \\\\", "\\midrule"]
    for env, c in rows:
        cs = []
        for s in SAMPLERS:
            v = _fmt(c.get(s))
            cs.append(f"\\textbf{{{v}}}" if s == "vosr" and v != "--" else v)
        cs.append(_fmt(c.get("qstar")))
        out.append(f"{SHORT.get(env, env)} & " + " & ".join(cs) + " \\\\")
    out.append("\\midrule")
    avg = []
    for s in SAMPLERS:
        v = _fmt(np.mean(acc[s])) if acc[s] else "--"
        avg.append(f"\\textbf{{{v}}}" if s == "vosr" and v != "--" else v)
    avg.append(_fmt(np.mean(acc["qstar"])) if acc["qstar"] else "--")
    out += ["Average & " + " & ".join(avg) + " \\\\", "\\bottomrule",
            "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(out)


def main_table(d, envs):
    out = ["\\begin{table}[t]", "\\centering", "\\small",
           "\\caption{Final return and cost (IQM over 7 seeds, mean of the last "
           "20\\% of evaluations). Cost budget is $25$; cells at or below budget "
           "are feasible. $\\dagger$ marks environments new in this revision.}",
           "\\label{tab:main}",
           "\\begin{tabular}{ll" + "c" * len(SAMPLERS) + "}", "\\toprule",
           "Optimizer & Environment & " + " & ".join(LABEL[s] for s in SAMPLERS) + " \\\\"]
    for o, oname in OPTIMIZERS:
        out.append("\\midrule")
        out.append(f"\\multirow{{{len(envs)}}}{{*}}{{{oname}}}")
        for env in envs:
            cells = []
            for s in SAMPLERS:
                r = d.get((env, f"{o}_{s}"))
                cells.append("--" if not r else
                             f"{_fmt(r['ret'], 1)} / {_fmt(r['cost'], 1)}")
            out.append(f" & {SHORT.get(env, env)} & " + " & ".join(cells) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(out)


def violation_table(d, envs):
    out = ["\\begin{table}[t]", "\\centering", "\\small",
           "\\caption{Cost-violation fraction: proportion of evaluations whose "
           "episodic cost exceeds the budget, averaged over the three optimizers "
           "and seven seeds. Lower is better.}",
           "\\label{tab:violation}",
           "\\begin{tabular}{l" + "c" * len(SAMPLERS) + "}", "\\toprule",
           "Environment & " + " & ".join(LABEL[s] for s in SAMPLERS) + " \\\\",
           "\\midrule"]
    acc = defaultdict(list)
    for env in envs:
        cells = []
        for s in SAMPLERS:
            v = [d[(env, f"{o}_{s}")]["viol"] for o, _ in OPTIMIZERS
                 if (env, f"{o}_{s}") in d and np.isfinite(d[(env, f"{o}_{s}")]["viol"])]
            if v:
                m = float(np.mean(v)); acc[s].append(m)
                cells.append(f"\\textbf{{{m:.3f}}}" if s == "vosr" else f"{m:.3f}")
            else:
                cells.append("--")
        out.append(f"{SHORT.get(env, env)} & " + " & ".join(cells) + " \\\\")
    out.append("\\midrule")
    out.append("Average & " + " & ".join(
        (f"\\textbf{{{np.mean(acc[s]):.3f}}}" if s == "vosr" else f"{np.mean(acc[s]):.3f}")
        if acc[s] else "--" for s in SAMPLERS) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--summary", default="results/summary.csv")
    p.add_argument("--out", default="paper/tables_generated.tex")
    a = p.parse_args()
    if not os.path.exists(a.summary):
        print(f"no summary at {a.summary}; run vosr_iclr.aggregate first")
        return
    d = load(a.summary)
    envs = [e for e in ORDER if any(k[0] == e for k in d)]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        f.write("% Auto-generated by vosr_iclr/make_latex_tables.py -- do not hand-edit.\n")
        f.write("% Requires \\usepackage{booktabs, multirow}\n\n")
        f.write(variance_table(d, envs))
        f.write("\n")
        f.write(main_table(d, envs))
        f.write("\n")
        f.write(violation_table(d, envs))
    print(f"wrote {a.out} ({len(d)} cells, {len(envs)} environments)")


if __name__ == "__main__":
    main()
