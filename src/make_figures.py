"""Paper-ready figures for the ICLR revision.

Produces:
  fig3a_sac_lag.pdf/.png   -- return (top) / cost (bottom) strips, SAC-Lagrangian
  fig3b_crpo_pcrpo.pdf     -- same for CRPO and PCRPO
  fig_new_envs.pdf         -- the three new environments, all three optimizers
  fig_variance.pdf         -- cost-gradient variance vs Uniform, per environment
  fig_xi.pdf               -- density-ratio estimator diagnostics (xi ESS, loss)
  fig_ablation_kappa.pdf / fig_ablation_eta.pdf
  fig_state_correction.pdf -- corrected vs uncorrected (the bug), paired

Curves are the mean over seeds with a +/-1 s.d. band, matching the paper's
existing figure convention, on a shared x-axis per environment.
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

SAMPLERS = ["uniform", "td_per", "safety_per", "uncertainty_per", "vosr"]
LABEL = {"uniform": "Uniform", "td_per": "TD-PER", "safety_per": "Safety-PER",
         "uncertainty_per": "Uncertainty-PER", "vosr": "VOSR (ours)"}
# Colour-blind-safe; VOSR is the bold blue, as in the current paper.
COLOR = {"uniform": "#E69F00", "td_per": "#009E73", "safety_per": "#D55E00",
         "uncertainty_per": "#CC79A7", "vosr": "#0072B2"}
LW = {s: 1.4 for s in SAMPLERS}
LW["vosr"] = 2.4

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


def _f(x):
    try:
        v = float(x)
        return v if np.isfinite(v) else np.nan
    except (TypeError, ValueError):
        return np.nan


def load(log_dir):
    """-> data[env][method] = {"steps": [...], "return": [n_seed, T], "cost": ...}"""
    raw = defaultdict(lambda: defaultdict(list))
    for fn in sorted(os.listdir(log_dir)):
        m = RUN_RE.match(fn)
        if not m:
            continue
        steps, rets, costs, extra = [], [], [], defaultdict(list)
        with open(os.path.join(log_dir, fn), newline="") as f:
            for row in csv.DictReader(f):
                steps.append(_f(row.get("step")))
                rets.append(_f(row.get("eval_return")))
                costs.append(_f(row.get("eval_cost")))
                for k in ("sigma_c2", "sigma_c2_uniform", "sigma_c2_qstar",
                          "xi_ess", "xi_mean", "ratio_loss", "ess_frac"):
                    extra[k].append(_f(row.get(k)))
        if len(steps) < 2:
            continue
        raw[m["env"]][m["method"]].append(
            {"steps": np.array(steps), "return": np.array(rets),
             "cost": np.array(costs), **{k: np.array(v) for k, v in extra.items()}})

    data = {}
    for env, methods in raw.items():
        data[env] = {}
        for method, runs in methods.items():
            T = min(len(r["steps"]) for r in runs)
            d = {"steps": runs[0]["steps"][:T], "n_seeds": len(runs)}
            for k in ("return", "cost", "sigma_c2", "sigma_c2_uniform",
                      "sigma_c2_qstar", "xi_ess", "xi_mean", "ratio_loss", "ess_frac"):
                d[k] = np.vstack([r[k][:T] for r in runs])
            data[env][method] = d
    return data


def _band(ax, steps, mat, color, label, lw):
    mu = np.nanmean(mat, axis=0)
    sd = np.nanstd(mat, axis=0)
    ax.plot(steps, mu, color=color, label=label, lw=lw, zorder=3 if "VOSR" in label else 2)
    ax.fill_between(steps, mu - sd, mu + sd, color=color, alpha=0.16, lw=0)


def strip(data, envs, optimizer, out, title=None):
    """Two-row return/cost strip across environments for one optimizer."""
    envs = [e for e in envs if e in data]
    if not envs:
        return
    n = len(envs)
    fig, axes = plt.subplots(2, n, figsize=(2.55 * n, 4.4), squeeze=False)
    for j, env in enumerate(envs):
        ax_r, ax_c = axes[0][j], axes[1][j]
        for s in SAMPLERS:
            d = data[env].get(f"{optimizer}_{s}")
            if d is None:
                continue
            x = d["steps"] / 1000.0
            _band(ax_r, x, d["return"], COLOR[s], LABEL[s], LW[s])
            _band(ax_c, x, d["cost"], COLOR[s], LABEL[s], LW[s])
        ax_c.axhline(COST_LIMIT, ls="--", c="k", lw=1.0, zorder=1)
        ax_r.set_title(SHORT.get(env, env), fontsize=9)
        ax_c.set_xlabel("Environment steps (k)", fontsize=8)
        for ax in (ax_r, ax_c):
            ax.tick_params(labelsize=7)
            ax.grid(alpha=0.25, lw=0.5)
        if j == 0:
            ax_r.set_ylabel("Return", fontsize=9)
            ax_c.set_ylabel("Cost", fontsize=9)
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels + ["Cost limit (25)"], loc="upper center",
               ncol=6, fontsize=8, frameon=False, bbox_to_anchor=(0.5, 1.06))
    if title:
        fig.suptitle(title, y=1.12, fontsize=10)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  wrote {out}.pdf")


def variance_figure(data, envs, out):
    """Paired within-run ratio sigma_c^2(q) / sigma_c^2(uniform), averaged over
    optimizers and seeds, plus Theorem 1's floor sigma_c^2(q*)/sigma_c^2(b)."""
    envs = [e for e in envs if e in data]
    rows = []
    for env in envs:
        row = {}
        for s in SAMPLERS[1:] + ["qstar"]:
            v = []
            for o in ("sac_lag", "crpo", "pcrpo"):
                key = f"{o}_{'uniform' if s == 'qstar' else s}"
                d = data[env].get(key)
                if d is None:
                    continue
                num = np.nanmean(d["sigma_c2_qstar" if s == "qstar" else "sigma_c2"])
                den = np.nanmean(d["sigma_c2_uniform"])
                if np.isfinite(num) and np.isfinite(den) and den > 0:
                    v.append(num / den)
            row[s] = float(np.mean(v)) if v else np.nan
        if any(np.isfinite(x) for x in row.values()):
            rows.append((env, row))
    if not rows:
        print("  (no sigma_c2 data yet, skipping variance figure)")
        return
    series = SAMPLERS[1:] + ["qstar"]
    lab = {**LABEL, "qstar": r"$q^\star$ (floor)"}
    col = {**COLOR, "qstar": "#555555"}
    fig, ax = plt.subplots(figsize=(1.15 * len(rows) + 3, 3.2))
    width = 0.16
    xs = np.arange(len(rows))
    for i, s in enumerate(series):
        ax.bar(xs + (i - 2.0) * width, [r[1].get(s, np.nan) for r in rows],
               width, label=lab[s], color=col[s])
    ax.axhline(1.0, ls="--", c="k", lw=1.0)
    ax.set_xticks(xs)
    ax.set_xticklabels([SHORT.get(e, e).replace(" (new)", "*") for e, _ in rows],
                       rotation=35, ha="right", fontsize=7)
    ax.set_ylabel(r"$\sigma_c^2$ relative to Uniform", fontsize=9)
    ax.tick_params(labelsize=7)
    ax.grid(alpha=0.25, axis="y", lw=0.5)
    ax.legend(fontsize=7, ncol=2, frameon=False)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  wrote {out}.pdf")


def xi_figure(data, envs, out):
    """Health of the state-visitation ratio estimator: is it doing anything, and
    is it doing something sane? Reviewers will ask both."""
    envs = [e for e in envs if e in data]
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.0))
    for env in envs:
        d = data[env].get("sac_lag_vosr")
        if d is None or not np.any(np.isfinite(d["xi_ess"])):
            continue
        x = d["steps"] / 1000.0
        axes[0].plot(x, np.nanmean(d["xi_ess"], axis=0), lw=1.3,
                     label=SHORT.get(env, env))
        axes[1].plot(x, np.nanmean(d["xi_mean"], axis=0), lw=1.3)
        rl = np.nanmean(d["ratio_loss"], axis=0)
        axes[2].plot(x, np.clip(rl, 1e-12, None), lw=1.3)
    axes[0].set_ylabel(r"ESS fraction of $\xi$", fontsize=9)
    axes[0].set_title(r"Reweighting strength", fontsize=9)
    axes[1].set_title(r"$\mathbb{E}_{d^b}[\xi]$  (should be $\approx 1$)", fontsize=9)
    axes[1].axhline(1.0, ls="--", c="k", lw=1.0)
    axes[2].set_title("Minimax estimator loss", fontsize=9)
    axes[2].set_yscale("log")
    for ax in axes:
        ax.set_xlabel("Environment steps (k)", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.25, lw=0.5)
    axes[0].legend(fontsize=6, ncol=2, frameon=False)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  wrote {out}.pdf")


def ablation_figure(base_dir, prefix, values, out, param_label):
    """One panel pair (return, cost) per environment, one curve per value."""
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
            _band(axes[0][j], x, d["return"], c, f"{param_label}={v}", 1.5)
            _band(axes[1][j], x, d["cost"], c, f"{param_label}={v}", 1.5)
        axes[1][j].axhline(COST_LIMIT, ls="--", c="k", lw=1.0)
        axes[0][j].set_title(SHORT.get(env, env), fontsize=9)
        axes[1][j].set_xlabel("Environment steps (k)", fontsize=8)
        for ax in (axes[0][j], axes[1][j]):
            ax.tick_params(labelsize=7); ax.grid(alpha=0.25, lw=0.5)
    axes[0][0].set_ylabel("Return", fontsize=9)
    axes[1][0].set_ylabel("Cost", fontsize=9)
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=len(values), fontsize=8,
               frameon=False, bbox_to_anchor=(0.5, 1.07))
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  wrote {out}.pdf")


def state_correction_figure(base_dir, out):
    on_d = os.path.join(base_dir, "statecorr_on")
    off_d = os.path.join(base_dir, "statecorr_off")
    if not (os.path.isdir(on_d) and os.path.isdir(off_d)):
        print("  (no state-correction ablation data, skipping)")
        return
    on, off = load(on_d), load(off_d)
    envs = sorted(set(on) & set(off))
    if not envs:
        return
    n = len(envs)
    fig, axes = plt.subplots(2, n, figsize=(2.7 * n, 4.4), squeeze=False)
    for j, env in enumerate(envs):
        for d, c, lab in ((on.get(env, {}).get("sac_lag_vosr"), "#0072B2",
                           r"with $\xi$ (corrected)"),
                          (off.get(env, {}).get("sac_lag_vosr"), "#D55E00",
                           r"$\xi \equiv 1$ (previous, biased)")):
            if d is None:
                continue
            x = d["steps"] / 1000.0
            _band(axes[0][j], x, d["return"], c, lab, 2.0)
            _band(axes[1][j], x, d["cost"], c, lab, 2.0)
        axes[1][j].axhline(COST_LIMIT, ls="--", c="k", lw=1.0)
        axes[0][j].set_title(SHORT.get(env, env), fontsize=9)
        axes[1][j].set_xlabel("Environment steps (k)", fontsize=8)
        for ax in (axes[0][j], axes[1][j]):
            ax.tick_params(labelsize=7); ax.grid(alpha=0.25, lw=0.5)
    axes[0][0].set_ylabel("Return", fontsize=9)
    axes[1][0].set_ylabel("Cost", fontsize=9)
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, fontsize=9, frameon=False,
               bbox_to_anchor=(0.5, 1.07))
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  wrote {out}.pdf")


VEL = ["SafetyAntVelocity-v1", "SafetyHalfCheetahVelocity-v1", "SafetyHopperVelocity-v1",
       "SafetyHumanoidVelocity-v1", "SafetySwimmerVelocity-v1", "SafetyWalker2dVelocity-v1"]
NAV = ["SafetyPointButton1-v0", "SafetyPointPush1-v0"]
NEW = ["SafetyCarGoal1-v0", "SafetyCarButton1-v0", "SafetyPointGoal2-v0"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--log-dir", default="runs_main")
    p.add_argument("--abl-dir", default="runs_ablation")
    p.add_argument("--out", default="figures")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)

    print(f"loading {a.log_dir}/ ...")
    data = load(a.log_dir)
    print(f"  {len(data)} environments, "
          f"{sum(len(v) for v in data.values())} (env, method) cells")

    o = a.out
    strip(data, VEL, "sac_lag", f"{o}/fig3a_sac_lag_velocity", "SAC-Lagrangian")
    strip(data, NAV + NEW, "sac_lag", f"{o}/fig3a_sac_lag_navigation", "SAC-Lagrangian")
    strip(data, VEL, "crpo", f"{o}/fig3b_crpo_velocity", "CRPO")
    strip(data, NAV + NEW, "crpo", f"{o}/fig3b_crpo_navigation", "CRPO")
    strip(data, VEL, "pcrpo", f"{o}/fig3c_pcrpo_velocity", "PCRPO")
    strip(data, NAV + NEW, "pcrpo", f"{o}/fig3c_pcrpo_navigation", "PCRPO")
    for opt in ("sac_lag", "crpo", "pcrpo"):
        strip(data, NEW, opt, f"{o}/fig_new_envs_{opt}",
              f"New environments -- {opt}")
    variance_figure(data, VEL + NAV + NEW, f"{o}/fig_variance")
    xi_figure(data, VEL + NAV + NEW, f"{o}/fig_xi_diagnostics")

    print(f"loading ablations from {a.abl_dir}/ ...")
    ablation_figure(a.abl_dir, "kappa", [0.0, 0.15, 0.35, 0.7, 1.5],
                    f"{o}/fig_ablation_kappa", r"$\kappa$")
    ablation_figure(a.abl_dir, "eta", [0.1, 0.5, 1.0, 2.0, 5.0],
                    f"{o}/fig_ablation_eta", r"$\eta$")
    state_correction_figure(a.abl_dir, f"{o}/fig_state_correction")
    print("figures done.")


if __name__ == "__main__":
    main()
