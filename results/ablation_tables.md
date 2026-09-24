# VOSR ablation studies (ICLR revision)
Source: `runs_ablation/`, one directory per arm. Arms found: 10.
### Ablation: kappa (reward/cost blend in the replay score)

| Environment | kappa=0 | kappa=0.15 | kappa=0.35 | kappa=0.7 | kappa=1.5 |
|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | -2269.4 / 0.2 | -2959.5 / 0.0 | -2993.3 / 0.0 | -2850.2 / 0.0 | -2022.7 / 0.5 |
| SafetyCarButton1-v0 | -4.7 / 2.8 | -0.7 / 54.7 | -0.5 / 60.5 | -4.9 / 29.2 | -2.2 / 83.8 |
| SafetyHopperVelocity-v1 | 20.1 / 0.0 | 18.3 / 0.0 | 36.1 / 4.3 | 72.7 / 1.0 | 20.4 / 0.0 |
| SafetyWalker2dVelocity-v1 | 68.0 / 0.0 | 109.2 / 1.0 | 110.1 / 0.6 | 101.0 / 0.3 | 42.2 / 0.3 |

_IQM final return / IQM final cost (budget 25), 3 seeds per cell._

### Ablation: eta (trust-region temperature)

| Environment | eta=0.1 | eta=0.5 | eta=1 | eta=2 | eta=5 |
|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | -2511.0 / 0.0 | -1380.9 / 0.1 | -1709.1 / 0.4 | -1027.4 / 0.2 | -2310.1 / 0.1 |
| SafetyCarButton1-v0 | 0.9 / 132.5 | -0.6 / 62.5 | -0.4 / 25.2 | -8.9 / 0.8 | -15.4 / 0.8 |
| SafetyHopperVelocity-v1 | 22.6 / 3.8 | 35.7 / 9.2 | 61.5 / 13.0 | 115.9 / 1.9 | 28.0 / 3.6 |
| SafetyWalker2dVelocity-v1 | -0.3 / 0.0 | 143.3 / 1.6 | 81.5 / 0.2 | 23.1 / 0.0 | 56.9 / 0.2 |

_IQM final return / IQM final cost (budget 25), 3 seeds per cell._

### Density-ratio estimator health by arm

| Arm | mean xi (target 1.0) | xi ESS fraction |
|---|---|---|
| eta_0.1 | 0.904 | 0.447 |
| eta_0.5 | 0.850 | 0.416 |
| eta_1.0 | 0.891 | 0.450 |
| eta_2.0 | 0.892 | 0.444 |
| eta_5.0 | 0.897 | 0.437 |
| kappa_0.0 | 0.913 | 0.454 |
| kappa_0.15 | 0.913 | 0.450 |
| kappa_0.35 | 0.930 | 0.456 |
| kappa_0.7 | 0.914 | 0.450 |
| kappa_1.5 | 0.905 | 0.448 |
