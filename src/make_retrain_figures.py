"""V1 (old) vs V2 (retuned) VOSR comparison figures for specific environments."""
import argparse
import csv
import glob
import os
import re
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RUN_RE = re.compile(r"^(?P<env>.+?)__(?P<method>.+?)__seed(?P<seed>\d+)\.csv$")
COST_LIMIT = 25.0


def _f(x):
    try:
        v = float(x)
        return v if np.isfinite(v) else np.nan
    except (TypeError, ValueError):
        return np.nan


def load_cell(log_dir, env, method):
    runs = []
    for f in glob.glob(f"{log_dir}/{env}__{method}__seed*.csv"):
        rows = list(csv.DictReader(open(f)))
        if len(rows) < 2:
            continue
        steps = np.array([_f(r["step"]) for r in rows])
        ret = np.array([_f(r["eval_return"]) for r in rows])
        cost = np.array([_f(r["eval_cost"]) for r in rows])
        runs.append((steps, ret, cost))
    if not runs:
        return None
    T = min(len(r[0]) for r in runs)
    steps = runs[0][0][:T]
    ret = np.vstack([r[1][:T] for r in runs])
    cost = np.vstack([r[2][:T] for r in runs])
    return steps, ret, cost


def panel(ax_r, ax_c, steps, ret, cost, color, label):
    mu_r, sd_r = np.nanmean(ret, axis=0), np.nanstd(ret, axis=0)
    mu_c, sd_c = np.nanmean(cost, axis=0), np.nanstd(cost, axis=0)
    x = steps / 1000.0
    ax_r.plot(x, mu_r, color=color, lw=2, label=label)
    ax_r.fill_between(x, mu_r - sd_r, mu_r + sd_r, color=color, alpha=0.15)
    ax_c.plot(x, mu_c, color=color, lw=2, label=label)
    ax_c.fill_between(x, mu_c - sd_c, mu_c + sd_c, color=color, alpha=0.15)


def make_figure(cases, out):
    n = len(cases)
    fig, axes = plt.subplots(2, n, figsize=(3.4 * n, 5.0), squeeze=False)
    for j, (env, opt, title) in enumerate(cases):
        method = f"{opt}_vosr"
        old = load_cell("runs_main", env, method)
        new = load_cell("runs_vosr_v2", env, method)
        ax_r, ax_c = axes[0][j], axes[1][j]
        if old:
            panel(ax_r, ax_c, *old, "#D55E00", "V1 (original tuning)")
        if new:
            panel(ax_r, ax_c, *new, "#0072B2", "V2 (retuned)")
        ax_c.axhline(COST_LIMIT, ls="--", c="k", lw=1.0)
        ax_r.set_title(title, fontsize=10)
        ax_c.set_xlabel("Environment steps (k)", fontsize=8)
        for ax in (ax_r, ax_c):
            ax.tick_params(labelsize=7)
            ax.grid(alpha=0.25, lw=0.5)
        if j == 0:
            ax_r.set_ylabel("Return", fontsize=9)
            ax_c.set_ylabel("Cost", fontsize=9)
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, fontsize=9, frameon=False, bbox_to_anchor=(0.5, 1.08))
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"wrote {out}.pdf")


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)
    make_figure([
        ("SafetyHalfCheetahVelocity-v1", "sac_lag", "HalfCheetah / SAC-Lag\n(clear win: more reward, cost stays ~0)"),
        ("SafetyWalker2dVelocity-v1", "sac_lag", "Walker2d / SAC-Lag\n(clear win: reward up, cost down)"),
        ("SafetySwimmerVelocity-v1", "sac_lag", "Swimmer / SAC-Lag\n(regression: cost up across all optimizers)"),
        ("SafetyCarButton1-v0", "crpo", "CarButton1 / CRPO\n(still badly over budget either way)"),
    ], "figures/fig_retrain_v1_vs_v2")
