# Environment -> optimizer showcase assignment

Each environment is assigned to exactly one optimizer -- the one under which VOSR's best available configuration (best of the original tuning and the retune, whichever is feasible / higher-return) performs best relative to that optimizer's own baselines. Solved as a capacitated assignment problem with fixed group sizes (SAC-Lagrangian: 4, CRPO: 4, PCRPO: 3), not by naive per-environment top-pick, though in this case every environment did land in its own top choice.

| Environment | Optimizer | VOSR config used | Return | Cost | Violation | Score |
|---|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | CRPO | V1 | -1740.90 | 0.33 | 0% | 416.8 |
| SafetyHalfCheetahVelocity-v1 | CRPO | V2 | -317.81 | 0.00 | 0% | 1068.3 |
| SafetyHumanoidVelocity-v1 | CRPO | V1 | 80.57 | 0.00 | 0% | 1007.3 |
| SafetySwimmerVelocity-v1 | CRPO | V1 | -5.25 | 2.73 | 2% | 990.4 |
| SafetyHopperVelocity-v1 | PCRPO | V2 | 49.25 | 0.80 | 0% | 964.4 |
| SafetyPointGoal2-v0 | PCRPO | V2 | -0.28 | 38.55 | 45% | -22.8 |
| SafetyPointPush1-v0 | PCRPO | V2 | 0.03 | 3.30 | 12% | 993.9 |
| SafetyCarButton1-v0 | SAC-Lagrangian | V1 | 0.12 | 39.75 | 54% | -22.4 |
| SafetyCarGoal1-v0 | SAC-Lagrangian | V1 | -1.26 | 3.45 | 29% | 986.1 |
| SafetyPointButton1-v0 | SAC-Lagrangian | V1 | -1.58 | 27.80 | 43% | -23.3 |
| SafetyWalker2dVelocity-v1 | SAC-Lagrangian | V2 | 60.57 | 0.07 | 0% | 971.2 |

_Score = 1000 x feasible(cost<=25) + (VOSR return - best same-optimizer baseline's return) - 50 x VOSR violation rate. 'VOSR config used' names whether the original (V1) or retuned (V2) configuration won that cell._