"""Refined/enlarged variant of make_showcase_figures.py.

Same data and curves as make_showcase_figures.py, restyled for readability:
  - all text (titles, axis labels, tick labels, legend, suptitle) 4x the
    original font size
  - all plotted lines (return/cost curves, cost-limit line) 2x the original
    line width
  - open axis style: top/right spines removed, only the x- and y-axis
    (bottom/left spines) are drawn, made bold enough to read clearly
  - no background grid (kept the look clean now that the box is gone)

Run from the repository root (same working-directory convention as
make_showcase_figures.py) so the default --assignment / runs_main /
runs_vosr_v2 relative paths resolve correctly.
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

# Lines 18x the original width (2x -> 6x -> now x3 more requested again).
LW = {s: 1.5 * 18 for s in SAMPLERS}
LW["vosr"] = 2.6 * 18

# Text 16x the original sizes (4x from the first pass, x4 more requested).
FONT_SCALE = 16
TITLE_FS = 9.5 * FONT_SCALE
XLABEL_FS = 8 * FONT_SCALE
YLABEL_FS = 9 * FONT_SCALE
TICK_FS = 7 * FONT_SCALE
LEGEND_FS = 8.5 * FONT_SCALE
SUPTITLE_FS = 12 * FONT_SCALE

# Canvas grown (independently of FONT_SCALE) so the much bigger text has
# room to sit without crowding the curves; kept a bit below full FONT_SCALE
# growth (dpi lowered to compensate) to keep file sizes/render time sane.
FIG_SCALE = 10
SAVE_DPI = 90

SPINE_LW = 5.2
TICK_WIDTH = 5.2
TICK_LEN = 20
COST_LIMIT_LW = 1.0 * 6

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
        lo = np.clip(lo, clip_lower, None)
    ax.plot(x, mu, color=color, lw=lw, label=label, zorder=3 if "VOSR" in label else 2)
    ax.fill_between(x, lo, hi, color=color, alpha=0.15, lw=0)


def _open_axis(ax):
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(SPINE_LW)
    ax.spines["bottom"].set_linewidth(SPINE_LW)
    ax.tick_params(labelsize=TICK_FS, width=TICK_WIDTH, length=TICK_LEN)


def make_group_figure(opt, envs, assignment_meta, out):
    n = len(envs)
    fig, axes = plt.subplots(2, n, figsize=(3.35 * n * FIG_SCALE, 5.1 * FIG_SCALE), squeeze=False)
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
        ax_c.axhline(COST_LIMIT, ls="--", c="k", lw=COST_LIMIT_LW, zorder=1)
        ax_c.set_ylim(bottom=0)
        tag = " (V2 retune)" if vosr_source == "V2" else ""
        ax_r.set_title(f"{SHORT.get(env, env)}{tag}", fontsize=TITLE_FS)
        ax_c.set_xlabel("Environment steps (k)", fontsize=XLABEL_FS)
        for ax in (ax_r, ax_c):
            _open_axis(ax)
        if j == 0:
            ax_r.set_ylabel("Return", fontsize=YLABEL_FS)
            ax_c.set_ylabel("Cost", fontsize=YLABEL_FS)
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels + ["Cost limit (25)"], loc="upper center",
               ncol=6, fontsize=LEGEND_FS, frameon=False, bbox_to_anchor=(0.5, 1.28))
    fig.suptitle(f"VOSR's showcase environments under {OPT_TITLE[opt]}", y=1.62,
                 fontsize=SUPTITLE_FS, fontweight="bold")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight", dpi=SAVE_DPI)
    plt.close(fig)
    print(f"wrote {out}.pdf ({n} environments)")


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
