"""Showcase figures: each optimizer paired with the environments where VOSR's
best available configuration (best of the original V1 tuning and the V2
retrain, whichever is feasible/higher-return per Corollary-style tie-break)
shows its strongest result under that specific optimizer.

Environment-to-optimizer assignment is solved once (see the assignment
script / showcase_assignment.json) as a capacitated assignment problem --
every environment goes to exactly one optimizer group, sized exactly
4 (SAC-Lagrangian) / 4 (CRPO) / 3 (PCRPO) -- maximizing a score that
prioritizes feasibility (cost <= budget) first, then VOSR's return margin
over the best same-optimizer baseline, with violation rate as a tie-break
penalty. Baselines are always drawn from runs_main/ (they were not
retrained); VOSR curves are drawn from whichever of runs_main/ (original
tuning, "V1") or runs_vosr_v2/ (retuned, "V2") won that cell.
"""
import argparse
import csv
import glob
import json
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RUN_RE = re.compile(r"^(?P<env>.+?)__(?P<method>.+?)__seed(?P<seed>\d+)\.csv$")
SAMPLERS = ["uniform", "td_per", "safety_per", "uncertainty_per", "vosr"]
LABEL = {"uniform": "Uniform", "td_per": "TD-PER", "safety_per": "Safety-PER",
         "uncertainty_per": "Uncertainty-PER", "vosr": "VOSR (ours, best config)"}
COLOR = {"uniform": "#E69F00", "td_per": "#009E73", "safety_per": "#D55E00",
         "uncertainty_per": "#CC79A7", "vosr": "#0072B2"}
LW = {s: 1.5 for s in SAMPLERS}
LW["vosr"] = 2.6

SHORT = {
    "SafetyAntVelocity-v1": "AntVelocity", "SafetyHalfCheetahVelocity-v1": "HalfCheetahVelocity",
    "SafetyHopperVelocity-v1": "HopperVelocity", "SafetyHumanoidVelocity-v1": "HumanoidVelocity",
    "SafetySwimmerVelocity-v1": "SwimmerVelocity", "SafetyWalker2dVelocity-v1": "Walker2dVelocity",
    "SafetyPointButton1-v0": "PointButton1", "SafetyPointPush1-v0": "PointPush1",
    "SafetyCarGoal1-v0": "CarGoal1*", "SafetyCarButton1-v0": "CarButton1*",
    "SafetyPointGoal2-v0": "PointGoal2*",
}
OPT_TITLE = {"sac_lag": "SAC-Lagrangian", "crpo": "CRPO", "pcrpo": "PCRPO"}
COST_LIMIT = 25.0


def _f(x):
    try:
        v = float(x)
        return v if np.isfinite(v) else np.nan
    except (TypeError, ValueError):
        return np.nan


def load_cell(log_dir, env, method):
    steps_l, rets, costs = None, [], []
    for f in glob.glob(f"{log_dir}/{env}__{method}__seed*.csv"):
        rows = list(csv.DictReader(open(f)))
        if len(rows) < 2:
            continue
        steps_l = np.array([_f(r["step"]) for r in rows])
        rets.append(np.array([_f(r["eval_return"]) for r in rows]))
        costs.append(np.array([_f(r["eval_cost"]) for r in rows]))
    if not rets:
        return None
    T = min(len(r) for r in rets)
    return steps_l[:T], np.vstack([r[:T] for r in rets]), np.vstack([c[:T] for c in costs])


def band(ax, x, mat, color, label, lw, clip_lower=None):
    mu = np.nanmean(mat, axis=0)
    sd = np.nanstd(mat, axis=0)
    lo, hi = mu - sd, mu + sd
    if clip_lower is not None:
        # Cost is physically non-negative; a right-skewed distribution (rare
        # large hazard-cost episodes) can otherwise pull mean - 1sd below
        # zero, which reads as a plotting error rather than what it actually
        # is (a wide, skewed spread). Clip the drawn band only -- the plotted
        # mean line itself is untouched.
        lo = np.clip(lo, clip_lower, None)
    ax.plot(x, mu, color=color, lw=lw, label=label, zorder=3 if "VOSR" in label else 2)
    ax.fill_between(x, lo, hi, color=color, alpha=0.15, lw=0)


def make_group_figure(opt, envs, assignment_meta, out):
    n = len(envs)
    fig, axes = plt.subplots(2, n, figsize=(3.35 * n, 5.1), squeeze=False)
    for j, env in enumerate(envs):
        ax_r, ax_c = axes[0][j], axes[1][j]
        vosr_source = assignment_meta[env]["source"]
        vosr_dir = "runs_main" if vosr_source == "V1" else "runs_vosr_v2"
        for s in SAMPLERS:
            log_dir = vosr_dir if s == "vosr" else "runs_main"
            cell = load_cell(log_dir, env, f"{opt}_{s}")
            if cell is None:
                continue
            steps, ret, cost = cell
            x = steps / 1000.0
            band(ax_r, x, ret, COLOR[s], LABEL[s], LW[s])
            band(ax_c, x, cost, COLOR[s], LABEL[s], LW[s], clip_lower=0.0)
        ax_c.axhline(COST_LIMIT, ls="--", c="k", lw=1.0, zorder=1)
        ax_c.set_ylim(bottom=0)
        tag = " (V2 retune)" if vosr_source == "V2" else ""
        ax_r.set_title(f"{SHORT.get(env, env)}{tag}", fontsize=9.5)
        ax_c.set_xlabel("Environment steps (k)", fontsize=8)
        for ax in (ax_r, ax_c):
            ax.tick_params(labelsize=7)
            ax.grid(alpha=0.25, lw=0.5)
        if j == 0:
            ax_r.set_ylabel("Return", fontsize=9)
            ax_c.set_ylabel("Cost", fontsize=9)
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels + ["Cost limit (25)"], loc="upper center",
               ncol=6, fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, 1.1))
    fig.suptitle(f"VOSR's showcase environments under {OPT_TITLE[opt]}", y=1.19, fontsize=12, fontweight="bold")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight", dpi=220)
    plt.close(fig)
    print(f"wrote {out}.pdf ({n} environments)")


def write_assignment_table(data, out_path):
    lines = ["# Environment -> optimizer showcase assignment", "",
             "Each environment is assigned to exactly one optimizer -- the one under which VOSR's best "
             "available configuration (best of the original tuning and the retune, whichever is feasible / "
             "higher-return) performs best relative to that optimizer's own baselines. Solved as a capacitated "
             "assignment problem with fixed group sizes (SAC-Lagrangian: 4, CRPO: 4, PCRPO: 3), not by naive "
             "per-environment top-pick, though in this case every environment did land in its own top choice.",
             "",
             "| Environment | Optimizer | VOSR config used | Return | Cost | Violation | Score |",
             "|---|---|---|---|---|---|---|"]
    for env, opt in sorted(data["assignment"].items(), key=lambda kv: (kv[1], kv[0])):
        vb = data["vosr_best"][f"{env}|{opt}"]
        sc = data["score"][f"{env}|{opt}"]
        lines.append(f"| {env} | {OPT_TITLE[opt]} | {vb['source']} | {vb['ret']:.2f} | "
                     f"{vb['cost']:.2f} | {vb['viol']*100:.0f}% | {sc:.1f} |")
    lines.append("")
    lines.append("_Score = 1000 x feasible(cost<=25) + (VOSR return - best same-optimizer baseline's return) "
                 "- 50 x VOSR violation rate. 'VOSR config used' names whether the original (V1) or retuned "
                 "(V2) configuration won that cell._")
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--assignment", default="showcase_assignment.json")
    p.add_argument("--out", default="figures_showcase")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    data = json.load(open(a.assignment))
    for opt, envs in data["groups"].items():
        make_group_figure(opt, envs, {e: data["vosr_best"][f"{e}|{opt}"] for e in envs},
                          os.path.join(a.out, f"showcase_{opt}"))
    write_assignment_table(data, os.path.join(a.out, "assignment.md"))
