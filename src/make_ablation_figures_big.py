"""Refined/enlarged variant of the kappa/eta ablation figures from make_figures.py.

Same data as make_figures.py's ablation_figure() (sac_lag_vosr runs under
runs_ablation/<param>_<value>/), restyled:
  - all text 4x the original font size
  - all plotted lines 2x the original line width
  - open axis style: only bottom/left spines are drawn (no box), no grid
  - single-hue colour scheme per figure instead of viridis: the value
    actually used in the paper (kappa=1.5, eta=1.0) gets a deep/dark shade;
    every other value gets a lighter shade of that same hue, so the paper's
    configuration visually stands out among its sweep.

Run from the repository root so the default --abl-dir relative path
resolves the same way it does for make_figures.py.
"""
import argparse
import csv
import os
import re
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RUN_RE = re.compile(r"^(?P<env>.+?)__(?P<method>.+?)__seed(?P<seed>\d+)\.csv$")

SHORT = {
    "SafetyAntVelocity-v1": "AntVelocity",
    "SafetyHalfCheetahVelocity-v1": "HalfCheetahVelocity",
    "SafetyHopperVelocity-v1": "HopperVelocity",
    "SafetyHumanoidVelocity-v1": "HumanoidVelocity",
    "SafetySwimmerVelocity-v1": "SwimmerVelocity",
    "SafetyWalker2dVelocity-v1": "Walker2dVelocity",
    "SafetyPointButton1-v0": "PointButton1",
    "SafetyPointPush1-v0": "PointPush1",
    "SafetyCarGoal1-v0": "CarGoal1 (new)",
    "SafetyCarButton1-v0": "CarButton1 (new)",
    "SafetyPointGoal2-v0": "PointGoal2 (new)",
}
COST_LIMIT = 25.0

# Lines 18x the original ablation width (2x -> 6x -> now x3 more requested again).
CURVE_LW = 1.5 * 18
COST_LIMIT_LW = 1.0 * 6

# Text 16x the original sizes (4x from the first pass, x4 more requested).
FONT_SCALE = 16
TITLE_FS = 9 * FONT_SCALE
XLABEL_FS = 8 * FONT_SCALE
YLABEL_FS = 9 * FONT_SCALE
TICK_FS = 7 * FONT_SCALE
LEGEND_FS = 8 * FONT_SCALE

# Canvas grown independently of FONT_SCALE (dpi lowered to compensate) so
# the much bigger text has room without ballooning file size/render time.
FIG_SCALE = 10
SAVE_DPI = 90

SPINE_LW = 5.2
TICK_WIDTH = 5.2
TICK_LEN = 20

# The configuration actually used in the paper -- gets the deep shade.
PAPER_VALUE = {"kappa": 1.5, "eta": 1.0}
# Single-hue colormap per parameter: kappa stays blue, eta is green.
CMAP_NAME = {"kappa": "Blues", "eta": "Greens"}


def _f(x):
    try:
        v = float(x)
        return v if np.isfinite(v) else np.nan
    except (TypeError, ValueError):
        return np.nan


def load(log_dir):
    raw = defaultdict(lambda: defaultdict(list))
    for fn in sorted(os.listdir(log_dir)):
        m = RUN_RE.match(fn)
        if not m:
            continue
        steps, rets, costs = [], [], []
        with open(os.path.join(log_dir, fn), newline="") as f:
            for row in csv.DictReader(f):
                steps.append(_f(row.get("step")))
                rets.append(_f(row.get("eval_return")))
                costs.append(_f(row.get("eval_cost")))
        if len(steps) < 2:
            continue
        raw[m["env"]][m["method"]].append(
            {"steps": np.array(steps), "return": np.array(rets), "cost": np.array(costs)})

    data = {}
    for env, methods in raw.items():
        data[env] = {}
        for method, runs in methods.items():
            T = min(len(r["steps"]) for r in runs)
            d = {"steps": runs[0]["steps"][:T]}
            for k in ("return", "cost"):
                d[k] = np.vstack([r[k][:T] for r in runs])
            data[env][method] = d
    return data


def _band(ax, steps, mat, color, label, lw, zorder=2):
    mu = np.nanmean(mat, axis=0)
    sd = np.nanstd(mat, axis=0)
    ax.plot(steps, mu, color=color, label=label, lw=lw, zorder=zorder)
    ax.fill_between(steps, mu - sd, mu + sd, color=color, alpha=0.16, lw=0)


def _open_axis(ax):
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(SPINE_LW)
    ax.spines["bottom"].set_linewidth(SPINE_LW)
    ax.tick_params(labelsize=TICK_FS, width=TICK_WIDTH, length=TICK_LEN)


def value_colors(values, highlight, cmap_name="Blues"):
    """Deep shade for `highlight`, progressively lighter shades of the same
    hue for everything else (ordered as given, not by distance)."""
    cmap = plt.get_cmap(cmap_name)
    others = [v for v in values if v != highlight]
    colors = {}
    n_other = len(others)
    for idx, v in enumerate(others):
        w = 0.28 if n_other <= 1 else 0.28 + 0.32 * idx / (n_other - 1)
        colors[v] = cmap(w)
    colors[highlight] = cmap(0.88)
    return colors


def ablation_figure(base_dir, prefix, values, out, param_label):
    arms = {}
    for v in values:
        d = os.path.join(base_dir, f"{prefix}_{v}")
        if os.path.isdir(d):
            arms[v] = load(d)
    if not arms:
        print(f"  (no {prefix} ablation data, skipping)")
        return
    envs = sorted({e for a in arms.values() for e in a})
    n = len(envs)
    highlight = PAPER_VALUE.get(prefix)
    colors = value_colors(values, highlight, cmap_name=CMAP_NAME.get(prefix, "Blues"))

    fig, axes = plt.subplots(2, n, figsize=(2.7 * n * FIG_SCALE, 4.4 * FIG_SCALE), squeeze=False)
    for j, env in enumerate(envs):
        for v in values:
            a = arms.get(v)
            if not a or env not in a:
                continue
            d = a[env].get("sac_lag_vosr")
            if d is None:
                continue
            c = colors[v]
            is_paper = (v == highlight)
            x = d["steps"] / 1000.0
            lab = f"{param_label}={v}" + ("  (used in paper)" if is_paper else "")
            _band(axes[0][j], x, d["return"], c, lab, CURVE_LW, zorder=3 if is_paper else 2)
            _band(axes[1][j], x, d["cost"], c, lab, CURVE_LW, zorder=3 if is_paper else 2)
        axes[1][j].axhline(COST_LIMIT, ls="--", c="k", lw=COST_LIMIT_LW, zorder=1)
        axes[0][j].set_title(SHORT.get(env, env), fontsize=TITLE_FS)
        axes[1][j].set_xlabel("Environment steps (k)", fontsize=XLABEL_FS)
        for ax in (axes[0][j], axes[1][j]):
            _open_axis(ax)
    axes[0][0].set_ylabel("Return", fontsize=YLABEL_FS)
    axes[1][0].set_ylabel("Cost", fontsize=YLABEL_FS)
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=3, fontsize=LEGEND_FS,
               frameon=False, bbox_to_anchor=(0.5, 1.32))
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight", dpi=SAVE_DPI)
    plt.close(fig)
    print(f"  wrote {out}.pdf")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--abl-dir", default="runs_ablation")
    p.add_argument("--out", default="figures_showcase")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)

    ablation_figure(a.abl_dir, "kappa", [0.0, 0.15, 0.35, 0.7, 1.5],
                    f"{a.out}/fig_ablation_kappa", r"$\kappa$")
    ablation_figure(a.abl_dir, "eta", [0.1, 0.5, 1.0, 2.0, 5.0],
                    f"{a.out}/fig_ablation_eta", r"$\eta$")
    print("ablation figures done.")
