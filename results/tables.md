# VOSR (ICLR revision) -- aggregate results

Source: `runs_main/`  |  cost budget: 25.0

### sac_lag

| Environment | Uniform | TD-PER | Safety-PER | Unc.-PER | VOSR |
|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | -2565.0 / 0.1 | -2076.7 / 0.1 | -510.2 / 0.7 | -873.1 / 0.8 | -1979.6 / 0.1 |
| SafetyCarButton1-v0 | -0.3 / 112.1 | -2.8 / 62.0 | -0.6 / 62.8 | -4.4 / 21.1 | 0.1 / 39.8 |
| SafetyCarGoal1-v0 | -2.8 / 35.0 | 0.3 / 67.8 | 0.0 / 25.2 | -1.6 / 7.6 | -1.3 / 3.5 |
| SafetyHalfCheetahVelocity-v1 | -371.8 / 1.6 | -405.1 / 0.8 | 19.6 / 1.5 | -131.0 / 0.0 | -474.4 / 0.0 |
| SafetyHopperVelocity-v1 | 122.8 / 3.2 | 58.2 / 4.2 | 77.5 / 6.3 | 38.3 / 0.2 | 40.2 / 9.7 |
| SafetyHumanoidVelocity-v1 | 66.3 / 0.0 | 67.2 / 0.0 | 70.6 / 0.0 | 65.5 / 0.0 | 80.5 / 0.0 |
| SafetyPointButton1-v0 | 0.2 / 20.7 | -0.2 / 40.2 | 0.2 / 62.0 | 0.3 / 42.1 | -1.6 / 27.8 |
| SafetyPointGoal2-v0 | -0.1 / 62.8 | -0.0 / 158.1 | 0.0 / 80.5 | -0.1 / 132.1 | -0.2 / 62.4 |
| SafetyPointPush1-v0 | 0.1 / 0.0 | -0.2 / 8.2 | -0.2 / 0.0 | 0.1 / 0.0 | 0.0 / 1.1 |
| SafetySwimmerVelocity-v1 | 8.5 / 20.8 | 2.8 / 8.9 | -3.4 / 4.1 | -7.3 / 1.5 | -4.9 / 0.1 |
| SafetyWalker2dVelocity-v1 | 17.0 / 0.0 | 8.8 / 0.0 | 89.4 / 1.7 | 28.9 / 0.0 | 35.3 / 0.2 |

_Cells are IQM final return / IQM final cost (budget 25)._

### crpo

| Environment | Uniform | TD-PER | Safety-PER | Unc.-PER | VOSR |
|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | -1319.4 / 0.1 | -1607.8 / 0.2 | -2121.1 / 0.3 | -1157.7 / 0.3 | -1740.9 / 0.3 |
| SafetyCarButton1-v0 | -0.3 / 55.8 | 0.1 / 68.0 | -0.0 / 56.1 | -0.4 / 186.6 | -0.3 / 33.8 |
| SafetyCarGoal1-v0 | 0.7 / 94.0 | 0.1 / 27.1 | 0.6 / 12.2 | 0.0 / 61.8 | -3.0 / 42.4 |
| SafetyHalfCheetahVelocity-v1 | -550.2 / 0.0 | -467.2 / 0.0 | -386.1 / 0.0 | -389.8 / 0.2 | -596.8 / 0.0 |
| SafetyHopperVelocity-v1 | 90.5 / 6.0 | 27.5 / 0.0 | 64.1 / 3.0 | 37.7 / 0.9 | 38.2 / 1.8 |
| SafetyHumanoidVelocity-v1 | 73.2 / 0.0 | 67.7 / 0.0 | 68.7 / 0.0 | 70.7 / 0.0 | 80.6 / 0.0 |
| SafetyPointButton1-v0 | 0.7 / 60.0 | 0.2 / 42.1 | 0.2 / 57.5 | 0.2 / 132.6 | -0.1 / 45.2 |
| SafetyPointGoal2-v0 | 0.1 / 82.2 | 0.2 / 47.2 | -0.2 / 86.4 | -0.1 / 48.3 | -0.5 / 32.0 |
| SafetyPointPush1-v0 | 0.0 / 43.1 | -0.0 / 81.4 | 0.2 / 9.8 | 0.2 / 2.1 | -0.2 / 2.2 |
| SafetySwimmerVelocity-v1 | 1.1 / 14.7 | 3.4 / 10.2 | -8.7 / 4.6 | 0.4 / 11.8 | -5.3 / 2.7 |
| SafetyWalker2dVelocity-v1 | 88.4 / 0.7 | 41.4 / 0.0 | 62.4 / 0.4 | 119.8 / 2.4 | 58.0 / 0.4 |

_Cells are IQM final return / IQM final cost (budget 25)._

### pcrpo

| Environment | Uniform | TD-PER | Safety-PER | Unc.-PER | VOSR |
|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | -2103.1 / 0.4 | -1191.6 / 0.8 | -1850.2 / 0.3 | -435.0 / 0.4 | -1570.7 / 0.1 |
| SafetyCarButton1-v0 | -0.1 / 72.1 | -2.5 / 73.6 | -0.1 / 28.1 | -3.9 / 99.6 | -1.4 / 42.9 |
| SafetyCarGoal1-v0 | 0.3 / 83.1 | 0.3 / 13.3 | -1.3 / 63.0 | -1.3 / 53.5 | -0.9 / 31.4 |
| SafetyHalfCheetahVelocity-v1 | -596.9 / 0.0 | -365.2 / 0.0 | -529.5 / 0.1 | -491.3 / 0.2 | -309.5 / 0.0 |
| SafetyHopperVelocity-v1 | 84.9 / 2.8 | 74.5 / 3.1 | 35.9 / 0.0 | 54.7 / 1.1 | 29.7 / 2.7 |
| SafetyHumanoidVelocity-v1 | 78.0 / 0.0 | 72.6 / 0.0 | 76.5 / 0.0 | 79.5 / 0.0 | 66.6 / 0.0 |
| SafetyPointButton1-v0 | 0.4 / 93.2 | -0.1 / 73.5 | 0.1 / 100.0 | 0.4 / 56.1 | -0.4 / 33.9 |
| SafetyPointGoal2-v0 | 0.0 / 51.0 | 0.0 / 119.8 | 0.0 / 44.4 | 0.0 / 151.4 | 0.4 / 49.3 |
| SafetyPointPush1-v0 | -0.0 / 0.0 | 0.0 / 1.2 | 0.0 / 2.9 | 0.0 / 48.5 | -0.4 / 1.0 |
| SafetySwimmerVelocity-v1 | 10.6 / 15.2 | 7.0 / 12.3 | -1.4 / 6.4 | 7.9 / 16.9 | -4.3 / 0.2 |
| SafetyWalker2dVelocity-v1 | 22.6 / 0.0 | 154.9 / 2.0 | 65.7 / 0.8 | 110.3 / 1.3 | 114.9 / 0.7 |

_Cells are IQM final return / IQM final cost (budget 25)._

### Cost-gradient variance relative to Uniform replay (lower is better)

| Environment | Uniform | TD-PER | Safety-PER | Unc.-PER | VOSR | q* (floor) |
|---|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | 1.00 | 2.43 | 2.14 | 1.44 | **0.80** | 0.16 |
| SafetyCarButton1-v0 | 1.00 | 1.39 | 1.77 | 1.24 | **0.39** | 0.24 |
| SafetyCarGoal1-v0 | 1.00 | 1.43 | 1.68 | 1.19 | **0.36** | 0.23 |
| SafetyHalfCheetahVelocity-v1 | 1.00 | 7.28 | 2.01 | 1.65 | **1.85** | 0.06 |
| SafetyHopperVelocity-v1 | 1.00 | 2.15 | 1.77 | 1.26 | **0.28** | 0.31 |
| SafetyHumanoidVelocity-v1 | 1.00 | 2.41 | 3.06 | 1.67 | **0.99** | 0.39 |
| SafetyPointButton1-v0 | 1.00 | 1.35 | 1.80 | 1.25 | **0.38** | 0.28 |
| SafetyPointGoal2-v0 | 1.00 | 1.37 | 1.87 | 1.38 | **0.40** | 0.24 |
| SafetyPointPush1-v0 | 1.00 | 1.43 | 1.45 | 1.22 | **0.35** | 0.35 |
| SafetySwimmerVelocity-v1 | 1.00 | 2.51 | 2.90 | 1.69 | **0.40** | 0.16 |
| SafetyWalker2dVelocity-v1 | 1.00 | 2.12 | 1.25 | 1.06 | **1.52** | 0.32 |
| **Average** | **1.00** | **2.35** | **1.97** | **1.37** | **0.70** | **0.25** |

_Measured by the closed-form Theorem 1 probe, paired within each run (same pool, same policy, both samplers). Uniform is 1.00 by construction._

### Cost-violation fraction (lower is better)

| Environment | Uniform | TD-PER | Safety-PER | Unc.-PER | VOSR |
|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| SafetyCarButton1-v0 | 0.557 | 0.674 | 0.542 | 0.597 | 0.527 |
| SafetyCarGoal1-v0 | 0.473 | 0.385 | 0.403 | 0.377 | 0.293 |
| SafetyHalfCheetahVelocity-v1 | 0.009 | 0.003 | 0.042 | 0.036 | 0.030 |
| SafetyHopperVelocity-v1 | 0.071 | 0.054 | 0.054 | 0.006 | 0.000 |
| SafetyHumanoidVelocity-v1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| SafetyPointButton1-v0 | 0.590 | 0.498 | 0.531 | 0.549 | 0.505 |
| SafetyPointGoal2-v0 | 0.454 | 0.491 | 0.443 | 0.447 | 0.487 |
| SafetyPointPush1-v0 | 0.168 | 0.165 | 0.125 | 0.176 | 0.095 |
| SafetySwimmerVelocity-v1 | 0.098 | 0.107 | 0.110 | 0.092 | 0.012 |
| SafetyWalker2dVelocity-v1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| **Average** | **0.220** | **0.216** | **0.204** | **0.207** | **0.177** |
