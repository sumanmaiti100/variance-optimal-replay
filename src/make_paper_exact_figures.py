"""Figures restricted to exactly what ICLR_3.pdf reports.

The main showcase scripts (make_showcase_figures.py / make_figures.py)
produce panels for every environment we have data for. The submitted draft
is narrower:
  - Figure 4's PCRPO column only shows Point Goal and Point Push (no
    Hopper, even though we have PCRPO data for it).
  - Figure 5 evaluates kappa only on {AntVelocity, CarButton1} and eta only
    on {HopperVelocity, Walker2dVelocity} -- not all four envs for both.

This script reuses the existing plotting code (imported, not duplicated)
but restricts the environment lists to match the draft precisely. Figures
3 and 4's CRPO column already match 1:1 with make_showcase_figures.py's
output, so those are just copied by the packaging step, not regenerated
here.

Run from the repository root.
"""
import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import make_showcase_figures as sc
import make_figures as mf


def ablation_figure_restricted(base_dir, prefix, values, out, param_label, envs):
    """Same as make_figures.ablation_figure, but panels are restricted to
    `envs` (in the given order) instead of auto-discovering every env the
    ablation happens to have run data for."""
    arms = {}
    for v in values:
        d = os.path.join(base_dir, f"{prefix}_{v}")
        if os.path.isdir(d):
            arms[v] = mf.load(d)
    if not arms:
        print(f"  (no {prefix} ablation data, skipping)")
        return
    n = len(envs)
    fig, axes = plt.subplots(2, n, figsize=(2.7 * n, 4.4), squeeze=False)
    cmap = plt.get_cmap("viridis")
    for j, env in enumerate(envs):
        for i, v in enumerate(values):
            a = arms.get(v)
            if not a or env not in a:
                continue
            d = a[env].get("sac_lag_vosr")
            if d is None:
                continue
            c = cmap(i / max(1, len(values) - 1))
            x = d["steps"] / 1000.0
            mf._band(axes[0][j], x, d["return"], c, f"{param_label}={v}", 1.5)
            mf._band(axes[1][j], x, d["cost"], c, f"{param_label}={v}", 1.5)
        axes[1][j].axhline(mf.COST_LIMIT, ls="--", c="k", lw=1.0)
        axes[0][j].set_title(mf.SHORT.get(env, env), fontsize=9)
        axes[1][j].set_xlabel("Environment steps (k)", fontsize=8)
        for ax in (axes[0][j], axes[1][j]):
            ax.tick_params(labelsize=7)
            ax.grid(alpha=0.25, lw=0.5)
    axes[0][0].set_ylabel("Return", fontsize=9)
    axes[1][0].set_ylabel("Cost", fontsize=9)
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=len(values), fontsize=8,
               frameon=False, bbox_to_anchor=(0.5, 1.07))
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  wrote {out}.pdf ({n} environments)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--assignment", default="showcase_assignment.json")
    p.add_argument("--abl-dir", default="runs_ablation")
    p.add_argument("--out", default="figures_paper_exact")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)

    data = json.load(open(a.assignment))

    # Figure 4, PCRPO column: Point Goal, Point Push only.
    pcrpo_envs = ["SafetyPointGoal2-v0", "SafetyPointPush1-v0"]
    sc.make_group_figure("pcrpo", pcrpo_envs,
                          {e: data["vosr_best"][f"{e}|pcrpo"] for e in pcrpo_envs},
                          os.path.join(a.out, "fig4_pcrpo_point_goal_push"))

    # Figure 5: kappa on {Ant, CarButton1}, eta on {Hopper, Walker2d}.
    ablation_figure_restricted(a.abl_dir, "kappa", [0.0, 0.15, 0.35, 0.7, 1.5],
                                os.path.join(a.out, "fig5_ablation_kappa"), r"$\kappa$",
                                ["SafetyAntVelocity-v1", "SafetyCarButton1-v0"])
    ablation_figure_restricted(a.abl_dir, "eta", [0.1, 0.5, 1.0, 2.0, 5.0],
                                os.path.join(a.out, "fig5_ablation_eta"), r"$\eta$",
                                ["SafetyHopperVelocity-v1", "SafetyWalker2dVelocity-v1"])
    print("paper-exact figures done.")


if __name__ == "__main__":
    main()
