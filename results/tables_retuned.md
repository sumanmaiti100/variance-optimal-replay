# VOSR (ICLR revision) -- aggregate results

Source: `runs_vosr_v2/`  |  cost budget: 25.0

### sac_lag

| Environment | Uniform | TD-PER | Safety-PER | Unc.-PER | VOSR |
|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | -- | -- | -- | -- | -2122.2 / 0.3 |
| SafetyCarButton1-v0 | -- | -- | -- | -- | -4.7 / 44.2 |
| SafetyCarGoal1-v0 | -- | -- | -- | -- | -0.6 / 46.2 |
| SafetyHalfCheetahVelocity-v1 | -- | -- | -- | -- | -298.7 / 0.0 |
| SafetyHopperVelocity-v1 | -- | -- | -- | -- | 31.5 / 5.2 |
| SafetyHumanoidVelocity-v1 | -- | -- | -- | -- | 65.4 / 0.0 |
| SafetyPointButton1-v0 | -- | -- | -- | -- | -0.7 / 61.8 |
| SafetyPointGoal2-v0 | -- | -- | -- | -- | 0.1 / 60.5 |
| SafetyPointPush1-v0 | -- | -- | -- | -- | -0.3 / 0.8 |
| SafetySwimmerVelocity-v1 | -- | -- | -- | -- | -7.9 / 2.4 |
| SafetyWalker2dVelocity-v1 | -- | -- | -- | -- | 60.6 / 0.1 |

_Cells are IQM final return / IQM final cost (budget 25)._

### crpo

| Environment | Uniform | TD-PER | Safety-PER | Unc.-PER | VOSR |
|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | -- | -- | -- | -- | -2040.6 / 0.2 |
| SafetyCarButton1-v0 | -- | -- | -- | -- | -1.7 / 62.6 |
| SafetyCarGoal1-v0 | -- | -- | -- | -- | -3.7 / 21.1 |
| SafetyHalfCheetahVelocity-v1 | -- | -- | -- | -- | -317.8 / 0.0 |
| SafetyHopperVelocity-v1 | -- | -- | -- | -- | 32.8 / 5.4 |
| SafetyHumanoidVelocity-v1 | -- | -- | -- | -- | 67.9 / 0.0 |
| SafetyPointButton1-v0 | -- | -- | -- | -- | -0.6 / 48.6 |
| SafetyPointGoal2-v0 | -- | -- | -- | -- | -1.0 / 42.1 |
| SafetyPointPush1-v0 | -- | -- | -- | -- | 0.0 / 5.0 |
| SafetySwimmerVelocity-v1 | -- | -- | -- | -- | -7.4 / 7.4 |
| SafetyWalker2dVelocity-v1 | -- | -- | -- | -- | 13.5 / 0.0 |

_Cells are IQM final return / IQM final cost (budget 25)._

### pcrpo

| Environment | Uniform | TD-PER | Safety-PER | Unc.-PER | VOSR |
|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | -- | -- | -- | -- | -1476.8 / 0.1 |
| SafetyCarButton1-v0 | -- | -- | -- | -- | -1.8 / 47.9 |
| SafetyCarGoal1-v0 | -- | -- | -- | -- | -0.9 / 10.6 |
| SafetyHalfCheetahVelocity-v1 | -- | -- | -- | -- | -595.3 / 0.0 |
| SafetyHopperVelocity-v1 | -- | -- | -- | -- | 49.3 / 0.8 |
| SafetyHumanoidVelocity-v1 | -- | -- | -- | -- | 69.4 / 0.0 |
| SafetyPointButton1-v0 | -- | -- | -- | -- | -1.0 / 27.2 |
| SafetyPointGoal2-v0 | -- | -- | -- | -- | -0.3 / 38.5 |
| SafetyPointPush1-v0 | -- | -- | -- | -- | 0.0 / 3.3 |
| SafetySwimmerVelocity-v1 | -- | -- | -- | -- | -7.7 / 8.9 |
| SafetyWalker2dVelocity-v1 | -- | -- | -- | -- | 119.1 / 0.4 |

_Cells are IQM final return / IQM final cost (budget 25)._

### Cost-gradient variance relative to Uniform replay (lower is better)

| Environment | Uniform | TD-PER | Safety-PER | Unc.-PER | VOSR | q* (floor) |
|---|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | -- | -- | -- | -- | **0.91** | -- |
| SafetyCarButton1-v0 | -- | -- | -- | -- | **0.27** | -- |
| SafetyCarGoal1-v0 | -- | -- | -- | -- | **0.36** | -- |
| SafetyHalfCheetahVelocity-v1 | -- | -- | -- | -- | **1.49** | -- |
| SafetyHopperVelocity-v1 | -- | -- | -- | -- | **0.35** | -- |
| SafetyHumanoidVelocity-v1 | -- | -- | -- | -- | **0.82** | -- |
| SafetyPointButton1-v0 | -- | -- | -- | -- | **0.41** | -- |
| SafetyPointGoal2-v0 | -- | -- | -- | -- | **0.34** | -- |
| SafetyPointPush1-v0 | -- | -- | -- | -- | **0.32** | -- |
| SafetySwimmerVelocity-v1 | -- | -- | -- | -- | **0.24** | -- |
| SafetyWalker2dVelocity-v1 | -- | -- | -- | -- | **1.15** | -- |
| **Average** | -- | -- | -- | -- | **0.61** | -- |

_Measured by the closed-form Theorem 1 probe, paired within each run (same pool, same policy, both samplers). Uniform is 1.00 by construction._

### Cost-violation fraction (lower is better)

| Environment | Uniform | TD-PER | Safety-PER | Unc.-PER | VOSR |
|---|---|---|---|---|---|
| SafetyAntVelocity-v1 | -- | -- | -- | -- | 0.000 |
| SafetyCarButton1-v0 | -- | -- | -- | -- | 0.465 |
| SafetyCarGoal1-v0 | -- | -- | -- | -- | 0.352 |
| SafetyHalfCheetahVelocity-v1 | -- | -- | -- | -- | 0.000 |
| SafetyHopperVelocity-v1 | -- | -- | -- | -- | 0.000 |
| SafetyHumanoidVelocity-v1 | -- | -- | -- | -- | 0.000 |
| SafetyPointButton1-v0 | -- | -- | -- | -- | 0.516 |
| SafetyPointGoal2-v0 | -- | -- | -- | -- | 0.473 |
| SafetyPointPush1-v0 | -- | -- | -- | -- | 0.106 |
| SafetySwimmerVelocity-v1 | -- | -- | -- | -- | 0.033 |
| SafetyWalker2dVelocity-v1 | -- | -- | -- | -- | 0.000 |
| **Average** | -- | -- | -- | -- | **0.177** |
