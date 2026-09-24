# A Variance-Optimal Replay Framework for Safe Off-Policy Reinforcement Learning

Training code and result figures for an ICLR submission under double-blind review.

## Summary

Off-policy safe RL methods inherit replay sampling strategies built for
unconstrained settings, so replay stays optimized for reward rather than
safety. This work treats the replay distribution itself as a control
variable: we prove that importance-weighted replay sampling preserves the
*expected* constrained policy update and affects only its variance, then
derive the closed-form sampler — **VOSR** (Variance-Optimal Sampler for
Replay) — that minimizes that variance across minibatches. VOSR wraps any
gradient-based safe optimizer (SAC-Lagrangian, CRPO, PCRPO) without changing
its constrained solution, and reduces cost-gradient variance and safety
violations across the Safety Gymnasium benchmark suite.

## Repository structure

```
src/                 Training code and figure/table generation scripts
results/             Aggregated per-(environment, method) result summaries
figures/paper/       Reproductions matching Figures 3-5 of the paper exactly
figures/extended/    Supplementary plots beyond what's shown in the paper
```

### `src/`

- `train.py`, `agent.py`, `networks.py`, `buffer.py` — actor/critic
  training loop and replay buffer.
- `density_ratio.py` — the state-visitation ratio estimator used for the
  state-visitation correction.
- `optimizers.py` — the gradient-based safe optimizers wrapped by VOSR
  (SAC-Lagrangian, CRPO, PCRPO).
- `scoring.py` — the variance-optimal sampling scores and the closed-form
  sampler (Theorem 1 / Proposition 2).
- `campaign.py`, `run_main_campaign.py`, `run_ablations.py`,
  `run_kappa_eta_ablations.py`, `run_vosr_retrain.py` — experiment drivers.
- `aggregate.py`, `aggregate_ablations.py`, `pipeline_after_main.py` —
  turn per-seed training logs into the tables in `results/`.
- `make_figures.py`, `make_showcase_figures.py`, `make_paper_exact_figures.py`,
  `make_showcase_figures_big.py`, `make_ablation_figures_big.py`,
  `make_retrain_figures.py`, `make_latex_tables.py` — generate every plot
  and table under `figures/` and `results/`.

### `results/`

- `summary.csv`, `summary.json`, `tables.md`, `ablation_tables.md` — the
  main experiment campaign: three optimizers x five replay samplers across
  eleven Safety Gymnasium environments, seven seeds each.
- `summary_retuned.csv`, `summary_retuned.json`, `tables_retuned.md` — a
  second VOSR configuration with retuned hyperparameters, evaluated on the
  same protocol. Figures under `figures/paper/` use whichever configuration
  (original or retuned) performs better in each environment, matching the
  selection described in the paper.

### `figures/paper/`

Exact reproductions of Figures 3-5: the SAC-Lagrangian and CRPO showcase
panels, the PCRPO panel restricted to Point Goal and Point Push, and the
kappa/eta ablations restricted to the environment pairs they are evaluated
on in the paper (kappa: Ant Velocity, Car Button 1; eta: Hopper Velocity,
Walker 2d Velocity).

### `figures/extended/`

- `showcase_full/` — larger-format renderings of the showcase and ablation
  figures, including the PCRPO panel's full environment set.
- `additional_analyses/` — per-environment result strips by task type,
  cost-gradient-variance and density-ratio diagnostics, and the comparison
  between the original and retuned VOSR configurations.
- `environment_optimizer_assignment.md` — the environment-to-optimizer
  assignment used to build the showcase figures, solved as a capacitated
  assignment problem (Section 5 of the paper).

## Hyperparameters

Shared agent/network settings, per-environment training budgets, and
per-optimizer settings are implemented in `src/train.py`, `src/campaign.py`,
and `src/optimizers.py`. The ablation sweep values are set in
`src/run_kappa_eta_ablations.py`: `kappa in {0.0, 0.15, 0.35, 0.7, 1.5}`,
`eta in {0.1, 0.5, 1.0, 2.0, 5.0}`. The configuration used throughout the
main results is `kappa = 1.5`, `eta = 1.0`.
