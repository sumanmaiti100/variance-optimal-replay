### **Tables Used in Responses to Reviewer Comments.** The table numbers correspond to those in the submitted revised manuscript. Table 1 appears in the main paper, while the remaining tables appear in the supplementary material/appendix. All changes made to the manuscript are marked in blue in the manuscript.

## Table 5

| Optimizer | Parameter | S1 (Settings used by<br>the baseline samplers) | **S2 (Settings used by<br>the VOSR sampler)** |
|---|---|---|---|
| SAC-Lagrangian | multiplier rate η<sub>λ</sub> | 10<sup>-2</sup> | 10<sup>-4</sup> |
|  | initial multiplier λ<sub>0</sub> | 0.0 | 0.0 |
|  | multiplier cap λ<sub>max</sub> | none | 30.0 |
| CRPO | branch-switch tolerance | 0.0 | 0.0 |
| PCRPO | cost-gradient weight | 1.0 | 1.0 |
| All | safety margin | 1.0 (d<sub>eff</sub> = 25) | 0.15 / 0.50 / 0.80† |

† The S2 margin mapping is 0.15 for PointButton1, PointPush1, PointGoal2, CarButton1, CarGoal1 and Swimmer. 0.50 for Ant and HalfCheetah, and 0.80 for Hopper, Humanoid and Walker2d. Evaluation uses d = 25 in both settings.

## Table 4

Per-environment training budgets. The cost budget is d = 25 for all environments.

| Environment | Total steps | Eval interval | Eval episodes | Max ep. length |
|---|---|---|---|---|
| SafeAntVelocity | 3,000,000 | 10,000 | 5 | 1000 |
| SafeHalfCheetahVelocity | 3,000,000 | 10,000 | 5 | 1000 |
| SafeHopperVelocity | 3,000,000 | 10,000 | 5 | 1000 |
| SafeHumanoidVelocity | 3,000,000 | 10,000 | 5 | 1000 |
| SafeSwimmerVelocity | 3,000,000 | 10,000 | 5 | 1000 |
| SafeWalker2dVelocity | 3,000,000 | 10,000 | 5 | 1000 |
| SafePointButton1 | 3,000,000 | 10,000 | 5 | 1000 |
| SafePointPush1 | 3,000,000 | 10,000 | 5 | 1000 |
| SafePointGoal2 | 3,000,000 | 10,000 | 5 | 1000 |
| SafeCarButton1 | 3,000,000 | 10,000 | 5 | 1000 |
| SafeCarGoal1 | 3,000,000 | 10,000 | 5 | 1000 |


## Table 15

Training results using Setting S1 applied to the velocity tasks with the SAC-Lagrangian method.

| Environment | Sampler | Return | Cost | Violation |
|---|---|---|---|---|
| Ant | Uniform | 2251.8 ± 206.1 | 1.6 ± 0.3 | 0.020 ± 0.001 |
|  | TD-PER | 2797.1 ± 135.6 | 1.6 ± 0.1 | 0.020 ± 0.000 |
|  | Safety-PER | 4039.3 ± 290.4 | 1.8 ± 0.5 | 0.021 ± 0.001 |
|  | Unc.-PER | 3722.3 ± 226.1 | 1.5 ± 0.3 | 0.020 ± 0.000 |
|  | **VOSR** | **4738.5 ± 211.8** | **0.6 ± 0.0** | **0.007 ± 0.000** |
| HalfCheetah | Uniform | 504.1 ± 30.8 | 10.4 ± 2.2 | 0.150 ± 0.010 |
|  | TD-PER | 519.1 ± 44.1 | 2.0 ± 1.1 | 0.021 ± 0.001 |
|  | Safety-PER | 995.4 ± 49.9 | 13.9 ± 2.0 | 0.249 ± 0.035 |
|  | Unc.-PER | 850.0 ± 48.0 | 11.8 ± 2.1 | 0.198 ± 0.023 |
|  | **VOSR** | **1111.8 ± 69.3** | **0.6 ± 0.1** | **0.007 ± 0.000** |
| Hopper | Uniform | 131.1 ± 6.1 | 3.6 ± 0.4 | 0.031 ± 0.006 |
|  | TD-PER | 78.8 ± 8.8 | 5.2 ± 0.5 | 0.040 ± 0.003 |
|  | Safety-PER | 92.2 ± 6.1 | 5.6 ± 0.6 | 0.048 ± 0.005 |
|  | Unc.-PER | 57.4 ± 13.6 | 1.9 ± 0.7 | 0.018 ± 0.001 |
|  | **VOSR** | **159.5 ± 6.0** | **0.7 ± 0.0** | **0.006 ± 0.000** |
| Humanoid | Uniform | 72.1 ± 1.0 | 1.9 ± 0.6 | 0.021 ± 0.001 |
|  | TD-PER | 77.6 ± 1.4 | 1.8 ± 0.3 | 0.021 ± 0.000 |
|  | Safety-PER | 79.9 ± 0.9 | 1.9 ± 0.8 | 0.020 ± 0.000 |
|  | Unc.-PER | 73.4 ± 1.0 | 1.7 ± 0.2 | 0.021 ± 0.000 |
|  | **VOSR** | **84.0 ± 1.2** | **0.6 ± 0.1** | **0.007 ± 0.000** |
| Swimmer | Uniform | 8.0 ± 0.5 | 24.8 ± 10.6 | 0.613 ± 0.053 |
|  | TD-PER | 1.8 ± 1.7 | 10.5 ± 4.4 | 0.118 ± 0.024 |
|  | Safety-PER | -3.3 ± 0.9 | 8.8 ± 3.1 | 0.104 ± 0.013 |
|  | Unc.-PER | -7.7 ± 1.4 | 3.4 ± 0.5 | 0.030 ± 0.002 |
|  | **VOSR** | **4.9 ± 2.3** | **1.2 ± 0.1** | **0.009 ± 0.000** |
| Walker2d | Uniform | 27.6 ± 8.9 | 1.9 ± 0.8 | 0.021 ± 0.001 |
|  | TD-PER | 19.6 ± 7.9 | 1.6 ± 0.2 | 0.020 ± 0.000 |
|  | Safety-PER | 118.0 ± 7.0 | 1.7 ± 0.1 | 0.021 ± 0.001 |
|  | Unc.-PER | 33.4 ± 4.0 | 1.8 ± 0.8 | 0.020 ± 0.001 |
|  | **VOSR** | **154.9 ± 9.3** | **0.6 ± 0.0** | **0.007 ± 0.000** |

## Table 16

Training results using Setting S1 applied to the velocity tasks with the CRPO method.

| Environment | Sampler | Return | Cost | Violation |
|---|---|---|---|---|
| Ant | Uniform | 3429.4 ± 122.6 | 1.6 ± 0.1 | 0.020 ± 0.001 |
|  | TD-PER | 3064.8 ± 66.1 | 1.5 ± 0.2 | 0.021 ± 0.001 |
|  | Safety-PER | 2682.8 ± 100.8 | 1.6 ± 0.3 | 0.020 ± 0.001 |
|  | Unc.-PER | 3489.3 ± 39.3 | 1.8 ± 0.6 | 0.021 ± 0.001 |
|  | **VOSR** | **3731.7 ± 66.4** | **0.6 ± 0.0** | **0.007 ± 0.000** |
| HalfCheetah | Uniform | 397.5 ± 11.2 | 1.5 ± 0.2 | 0.021 ± 0.000 |
|  | TD-PER | 482.5 ± 16.7 | 1.7 ± 0.2 | 0.020 ± 0.001 |
|  | Safety-PER | 549.5 ± 19.9 | 1.6 ± 0.3 | 0.021 ± 0.001 |
|  | Unc.-PER | 511.0 ± 22.8 | 1.5 ± 0.1 | 0.020 ± 0.001 |
|  | **VOSR** | **602.8 ± 7.3** | **0.6 ± 0.1** | **0.007 ± 0.000** |
| Hopper | Uniform | 119.1 ± 6.2 | 10.0 ± 3.3 | 0.089 ± 0.014 |
|  | TD-PER | 44.5 ± 6.7 | 4.2 ± 0.5 | 0.036 ± 0.005 |
|  | Safety-PER | 76.9 ± 10.6 | 3.4 ± 0.5 | 0.030 ± 0.001 |
|  | Unc.-PER | 51.6 ± 8.5 | 2.5 ± 0.3 | 0.026 ± 0.001 |
|  | **VOSR** | **140.5 ± 4.0** | **1.0 ± 0.1** | **0.008 ± 0.000** |
| Humanoid | Uniform | 81.0 ± 0.8 | 1.6 ± 0.1 | 0.021 ± 0.001 |
|  | TD-PER | 79.7 ± 1.4 | 1.5 ± 0.3 | 0.020 ± 0.000 |
|  | Safety-PER | 84.9 ± 0.9 | 1.9 ± 0.5 | 0.021 ± 0.000 |
|  | Unc.-PER | 78.0 ± 1.7 | 1.6 ± 0.2 | 0.021 ± 0.001 |
|  | **VOSR** | **88.5 ± 2.0** | **0.6 ± 0.0** | **0.007 ± 0.000** |
| Swimmer | Uniform | 0.9 ± 0.7 | 12.8 ± 3.3 | 0.193 ± 0.017 |
|  | TD-PER | 3.0 ± 1.5 | 8.6 ± 1.1 | 0.108 ± 0.018 |
|  | Safety-PER | -6.9 ± 0.8 | 6.3 ± 1.8 | 0.059 ± 0.011 |
|  | Unc.-PER | -0.8 ± 0.7 | 25.2 ± 4.7 | 0.688 ± 0.035 |
|  | **VOSR** | **1.9 ± 1.6** | **2.5 ± 0.3** | **0.012 ± 0.000** |
| Walker2d | Uniform | 90.1 ± 8.6 | 1.8 ± 0.2 | 0.019 ± 0.000 |
|  | TD-PER | 47.7 ± 6.4 | 1.9 ± 0.6 | 0.019 ± 0.001 |
|  | Safety-PER | 60.4 ± 15.5 | 2.1 ± 0.8 | 0.019 ± 0.001 |
|  | Unc.-PER | 147.1 ± 15.6 | 2.5 ± 0.7 | 0.021 ± 0.001 |
|  | **VOSR** | **181.5 ± 6.5** | **0.6 ± 0.0** | **0.007 ± 0.000** |

## Table 17

Training results using Setting S1 applied to the velocity tasks with the PCRPO method.

| Environment | Sampler | Return | Cost | Violation |
|---|---|---|---|---|
| Ant | Uniform | 2783.4 ± 154.8 | 1.6 ± 0.1 | 0.020 ± 0.000 |
|  | TD-PER | 3509.5 ± 122.2 | 1.6 ± 0.2 | 0.020 ± 0.000 |
|  | Safety-PER | 2967.1 ± 78.8 | 1.7 ± 0.2 | 0.020 ± 0.000 |
|  | Unc.-PER | 3997.2 ± 174.0 | 1.7 ± 0.3 | 0.020 ± 0.001 |
|  | **VOSR** | **4522.0 ± 109.6** | **0.6 ± 0.1** | **0.007 ± 0.000** |
| HalfCheetah | Uniform | 349.6 ± 14.3 | 1.9 ± 0.6 | 0.020 ± 0.001 |
|  | TD-PER | 530.8 ± 10.5 | 1.8 ± 0.6 | 0.020 ± 0.001 |
|  | Safety-PER | 308.6 ± 33.2 | 2.1 ± 0.9 | 0.020 ± 0.001 |
|  | Unc.-PER | 413.7 ± 21.7 | 1.8 ± 0.2 | 0.020 ± 0.001 |
|  | **VOSR** | **624.0 ± 45.8** | **0.6 ± 0.0** | **0.007 ± 0.000** |
| Hopper | Uniform | 99.3 ± 6.4 | 8.8 ± 1.6 | 0.088 ± 0.012 |
|  | TD-PER | 92.8 ± 2.7 | 4.3 ± 0.4 | 0.040 ± 0.006 |
|  | Safety-PER | 41.8 ± 5.3 | 1.7 ± 0.1 | 0.020 ± 0.001 |
|  | Unc.-PER | 97.3 ± 6.1 | 1.8 ± 0.4 | 0.020 ± 0.001 |
|  | **VOSR** | **120.3 ± 3.9** | **0.7 ± 0.1** | **0.007 ± 0.000** |
| Humanoid | Uniform | 86.4 ± 1.2 | 1.9 ± 0.2 | 0.021 ± 0.000 |
|  | TD-PER | 78.4 ± 1.2 | 1.8 ± 0.4 | 0.021 ± 0.001 |
|  | Safety-PER | 91.3 ± 1.1 | 1.8 ± 0.4 | 0.021 ± 0.001 |
|  | Unc.-PER | 93.2 ± 1.0 | 1.9 ± 0.4 | 0.020 ± 0.001 |
|  | **VOSR** | **98.8 ± 2.4** | **0.6 ± 0.1** | **0.007 ± 0.000** |
| Swimmer | Uniform | 10.6 ± 0.8 | 10.6 ± 0.8 | 0.188 ± 0.021 |
|  | TD-PER | 7.2 ± 1.6 | 10.7 ± 2.8 | 0.128 ± 0.018 |
|  | Safety-PER | -4.6 ± 0.6 | 6.3 ± 0.8 | 0.054 ± 0.003 |
|  | Unc.-PER | 8.4 ± 0.3 | 12.8 ± 1.5 | 0.206 ± 0.014 |
|  | **VOSR** | **9.5 ± 1.9** | **2.3 ± 0.1** | **0.011 ± 0.000** |
| Walker2d | Uniform | 41.3 ± 12.7 | 1.7 ± 0.3 | 0.020 ± 0.001 |
|  | TD-PER | 154.2 ± 11.8 | 1.8 ± 0.4 | 0.021 ± 0.000 |
|  | Safety-PER | 87.9 ± 8.2 | 1.7 ± 0.1 | 0.021 ± 0.000 |
|  | Unc.-PER | 124.0 ± 22.5 | 2.1 ± 0.7 | 0.021 ± 0.002 |
|  | **VOSR** | **197.2 ± 11.7** | **0.6 ± 0.0** | **0.007 ± 0.000** |

## Table 18

Training results using Setting S1 applied to the navigation tasks with the SAC-Lagrangian method.

| Environment | Sampler | Return | Cost | Violation |
|---|---|---|---|---|
| PointButton1 | Uniform | 0.2 ± 0.1 | 17.3 ± 2.1 | 0.423 ± 0.025 |
|  | TD-PER | -0.2 ± 0.2 | 42.0 ± 3.8 | 0.809 ± 0.004 |
|  | Safety-PER | 0.2 ± 0.0 | 92.0 ± 47.0 | 0.817 ± 0.000 |
|  | Unc.-PER | 0.3 ± 0.1 | 49.0 ± 5.6 | 0.817 ± 0.001 |
|  | **VOSR** | **0.6 ± 0.1** | **6.5 ± 0.4** | **0.042 ± 0.001** |
| PointPush1 | Uniform | 0.1 ± 0.1 | 1.8 ± 0.3 | 0.021 ± 0.002 |
|  | TD-PER | -0.2 ± 0.2 | 16.3 ± 1.9 | 0.359 ± 0.028 |
|  | Safety-PER | -0.3 ± 0.1 | 18.3 ± 2.0 | 0.440 ± 0.027 |
|  | Unc.-PER | 0.1 ± 0.1 | 18.7 ± 3.8 | 0.452 ± 0.035 |
|  | **VOSR** | **0.6 ± 0.1** | **0.7 ± 0.1** | **0.007 ± 0.000** |
| PointGoal2 | Uniform | -0.1 ± 0.1 | 65.1 ± 2.7 | 0.855 ± 0.000 |
|  | TD-PER | 0.0 ± 0.1 | 125.7 ± 8.1 | 0.855 ± 0.000 |
|  | Safety-PER | -0.1 ± 0.1 | 90.7 ± 18.1 | 0.855 ± 0.000 |
|  | Unc.-PER | -0.1 ± 0.1 | 116.2 ± 9.0 | 0.855 ± 0.000 |
|  | **VOSR** | **0.3 ± 0.1** | **12.6 ± 0.8** | **0.133 ± 0.004** |
| CarButton1 | Uniform | -2.3 ± 0.6 | 105.2 ± 12.1 | 0.855 ± 0.000 |
|  | TD-PER | -5.2 ± 0.5 | 63.6 ± 9.2 | 0.855 ± 0.000 |
|  | Safety-PER | -3.9 ± 0.6 | 106.5 ± 46.0 | 0.855 ± 0.000 |
|  | Unc.-PER | -8.4 ± 0.5 | 23.5 ± 2.6 | 0.644 ± 0.035 |
|  | **VOSR** | **-3.1 ± 0.6** | **9.9 ± 0.7** | **0.079 ± 0.005** |
| CarGoal1 | Uniform | -4.7 ± 0.5 | 36.1 ± 12.8 | 0.834 ± 0.010 |
|  | TD-PER | 0.0 ± 0.4 | 65.9 ± 12.0 | 0.855 ± 0.000 |
|  | Safety-PER | -1.0 ± 0.4 | 34.3 ± 16.8 | 0.820 ± 0.015 |
|  | Unc.-PER | -2.8 ± 0.4 | 8.3 ± 0.8 | 0.099 ± 0.011 |
|  | **VOSR** | **-0.5 ± 0.4** | **3.2 ± 0.3** | **0.016 ± 0.001** |

## Table 19

Training results using Setting S1 applied to the navigation tasks with the CRPO method.

| Environment | Sampler | Return | Cost | Violation |
|---|---|---|---|---|
| PointButton1 | Uniform | 0.7 ± 0.1 | 59.9 ± 16.4 | 0.855 ± 0.000 |
|  | TD-PER | 0.3 ± 0.2 | 33.7 ± 2.9 | 0.831 ± 0.011 |
|  | Safety-PER | 0.1 ± 0.1 | 78.7 ± 22.9 | 0.855 ± 0.000 |
|  | Unc.-PER | 0.2 ± 0.2 | 129.3 ± 37.8 | 0.855 ± 0.000 |
|  | **VOSR** | **1.1 ± 0.1** | **13.1 ± 1.3** | **0.132 ± 0.004** |
| PointPush1 | Uniform | 0.1 ± 0.1 | 51.9 ± 9.1 | 0.853 ± 0.003 |
|  | TD-PER | -0.1 ± 0.2 | 105.2 ± 30.1 | 0.855 ± 0.000 |
|  | Safety-PER | 0.1 ± 0.1 | 17.4 ± 7.3 | 0.284 ± 0.007 |
|  | Unc.-PER | 0.2 ± 0.1 | 42.2 ± 2.6 | 0.853 ± 0.002 |
|  | **VOSR** | **0.6 ± 0.1** | **5.3 ± 0.5** | **0.031 ± 0.002** |
| PointGoal2 | Uniform | 0.1 ± 0.1 | 71.0 ± 1.6 | 0.855 ± 0.000 |
|  | TD-PER | 0.6 ± 0.1 | 49.5 ± 9.5 | 0.855 ± 0.001 |
|  | Safety-PER | -0.3 ± 0.1 | 79.0 ± 7.8 | 0.855 ± 0.000 |
|  | Unc.-PER | -0.1 ± 0.1 | 54.4 ± 8.8 | 0.855 ± 0.001 |
|  | **VOSR** | **0.9 ± 0.1** | **13.4 ± 0.6** | **0.137 ± 0.002** |
| CarButton1 | Uniform | -0.8 ± 0.2 | 70.0 ± 5.4 | 0.855 ± 0.000 |
|  | TD-PER | -1.1 ± 0.2 | 143.2 ± 27.8 | 0.855 ± 0.000 |
|  | Safety-PER | 0.0 ± 0.1 | 48.5 ± 6.8 | 0.854 ± 0.001 |
|  | Unc.-PER | -1.6 ± 0.1 | 181.5 ± 70.6 | 0.855 ± 0.000 |
|  | **VOSR** | **-0.4 ± 0.2** | **12.9 ± 0.6** | **0.135 ± 0.006** |
| CarGoal1 | Uniform | 0.5 ± 0.1 | 91.5 ± 8.9 | 0.855 ± 0.000 |
|  | TD-PER | 0.2 ± 0.3 | 33.3 ± 5.6 | 0.790 ± 0.007 |
|  | Safety-PER | -0.4 ± 0.2 | 28.4 ± 10.8 | 0.673 ± 0.033 |
|  | Unc.-PER | -1.6 ± 0.2 | 68.2 ± 12.9 | 0.855 ± 0.000 |
|  | **VOSR** | **0.4 ± 0.3** | **9.7 ± 0.9** | **0.087 ± 0.002** |

## Table 20

Training results using Setting S1 applied to the navigation tasks with the PCRPO method.

| Environment | Sampler | Return | Cost | Violation |
|---|---|---|---|---|
| PointButton1 | Uniform | 0.4 ± 0.1 | 106.2 ± 12.2 | 0.825 ± 0.000 |
|  | TD-PER | -0.1 ± 0.1 | 60.5 ± 3.8 | 0.825 ± 0.000 |
|  | Safety-PER | 0.0 ± 0.1 | 136.1 ± 57.1 | 0.825 ± 0.000 |
|  | Unc.-PER | 0.4 ± 0.1 | 48.2 ± 6.9 | 0.824 ± 0.001 |
|  | **VOSR** | **0.7 ± 0.1** | **13.5 ± 0.7** | **0.125 ± 0.007** |
| PointPush1 | Uniform | 0.0 ± 0.1 | 20.0 ± 3.5 | 0.467 ± 0.033 |
|  | TD-PER | 0.0 ± 0.1 | 15.2 ± 2.0 | 0.314 ± 0.036 |
|  | Safety-PER | 0.1 ± 0.2 | 10.3 ± 1.9 | 0.128 ± 0.028 |
|  | Unc.-PER | 0.0 ± 0.1 | 58.9 ± 16.1 | 0.802 ± 0.000 |
|  | **VOSR** | **0.5 ± 0.1** | **3.7 ± 0.3** | **0.018 ± 0.001** |
| PointGoal2 | Uniform | -0.1 ± 0.1 | 52.3 ± 11.7 | 0.855 ± 0.001 |
|  | TD-PER | 0.2 ± 0.1 | 99.4 ± 30.4 | 0.855 ± 0.000 |
|  | Safety-PER | 0.1 ± 0.1 | 43.6 ± 2.0 | 0.854 ± 0.001 |
|  | Unc.-PER | 0.0 ± 0.1 | 131.0 ± 43.1 | 0.855 ± 0.000 |
|  | **VOSR** | **0.6 ± 0.1** | **12.7 ± 0.6** | **0.135 ± 0.004** |
| CarButton1 | Uniform | -0.2 ± 0.6 | 69.0 ± 11.5 | 0.855 ± 0.000 |
|  | TD-PER | -3.6 ± 0.5 | 68.5 ± 8.1 | 0.855 ± 0.000 |
|  | Safety-PER | 0.1 ± 0.7 | 43.9 ± 2.5 | 0.854 ± 0.001 |
|  | Unc.-PER | -5.0 ± 0.4 | 107.0 ± 11.6 | 0.855 ± 0.000 |
|  | **VOSR** | **-0.1 ± 0.3** | **12.7 ± 1.7** | **0.136 ± 0.008** |
| CarGoal1 | Uniform | 0.4 ± 0.2 | 89.5 ± 28.2 | 0.855 ± 0.000 |
|  | TD-PER | 0.3 ± 0.4 | 15.2 ± 1.7 | 0.380 ± 0.059 |
|  | Safety-PER | -2.0 ± 0.2 | 70.0 ± 18.8 | 0.855 ± 0.000 |
|  | Unc.-PER | -2.6 ± 0.3 | 51.5 ± 6.0 | 0.855 ± 0.000 |
|  | **VOSR** | **0.3 ± 0.2** | **6.0 ± 0.4** | **0.039 ± 0.002** |

## Table 21

Training results using Setting S2 applied to the SAC-Lagrangian method.

| Environment | Sampler | Return | Cost | Violation |
|---|---|---|---|---|
| Ant | Uniform | 2083.5 ± 136.4 | 1.0 ± 0.2 | 0.019 ± 0.000 |
|  | TD-PER | 2381.8 ± 381.6 | 1.0 ± 0.1 | 0.019 ± 0.001 |
|  | Safety-PER | 3860.3 ± 225.5 | 1.1 ± 0.2 | 0.019 ± 0.000 |
|  | Unc.-PER | 3389.8 ± 211.2 | 1.0 ± 0.1 | 0.019 ± 0.000 |
|  | **VOSR** | **4528.0 ± 114.5** | **0.4 ± 0.0** | **0.007 ± 0.000** |
| HalfCheetah | Uniform | 455.7 ± 32.9 | 8.0 ± 7.1 | 0.108 ± 0.012 |
|  | TD-PER | 392.1 ± 106.1 | 1.5 ± 1.2 | 0.018 ± 0.006 |
|  | Safety-PER | 983.8 ± 74.8 | 8.7 ± 2.0 | 0.101 ± 0.024 |
|  | Unc.-PER | 763.7 ± 82.6 | 9.3 ± 4.1 | 0.112 ± 0.028 |
|  | **VOSR** | **1047.5 ± 73.4** | **0.2 ± 0.0** | **0.008 ± 0.003** |
| Hopper | Uniform | 125.5 ± 10.3 | 2.9 ± 0.4 | 0.029 ± 0.002 |
|  | TD-PER | 72.9 ± 7.7 | 4.4 ± 1.0 | 0.035 ± 0.001 |
|  | Safety-PER | 91.9 ± 13.1 | 4.8 ± 0.7 | 0.045 ± 0.015 |
|  | Unc.-PER | 47.8 ± 7.6 | 1.5 ± 0.6 | 0.019 ± 0.000 |
|  | **VOSR** | **148.0 ± 9.7** | **0.5 ± 0.0** | **0.007 ± 0.000** |
| Humanoid | Uniform | 71.7 ± 0.9 | 1.3 ± 1.3 | 0.023 ± 0.005 |
|  | TD-PER | 77.3 ± 1.7 | 1.2 ± 1.3 | 0.019 ± 0.007 |
|  | Safety-PER | 79.8 ± 1.5 | 1.2 ± 1.2 | 0.017 ± 0.001 |
|  | Unc.-PER | 72.2 ± 1.5 | 1.5 ± 1.3 | 0.019 ± 0.002 |
|  | **VOSR** | **82.5 ± 0.9** | **1.1 ± 1.5** | **0.007 ± 0.004** |
| Swimmer | Uniform | 5.8 ± 1.6 | 18.1 ± 2.6 | 0.433 ± 0.046 |
|  | TD-PER | -0.2 ± 1.6 | 8.0 ± 2.2 | 0.075 ± 0.011 |
|  | Safety-PER | -5.1 ± 2.3 | 6.5 ± 1.2 | 0.072 ± 0.025 |
|  | Unc.-PER | -7.5 ± 1.6 | 2.7 ± 0.2 | 0.026 ± 0.002 |
|  | **VOSR** | **2.8 ± 1.7** | **1.0 ± 0.1** | **0.008 ± 0.000** |
| Walker2d | Uniform | 20.0 ± 5.5 | 2.0 ± 2.4 | 0.023 ± 0.003 |
|  | TD-PER | 19.3 ± 7.4 | 1.5 ± 2.3 | 0.016 ± 0.005 |
|  | Safety-PER | 110.2 ± 13.6 | 2.1 ± 1.4 | 0.021 ± 0.009 |
|  | Unc.-PER | 21.2 ± 6.1 | 1.6 ± 1.6 | 0.025 ± 0.004 |
|  | **VOSR** | **137.4 ± 13.2** | **0.7 ± 1.3** | **0.009 ± 0.004** |
| PointButton1 | Uniform | 0.1 ± 0.1 | 14.6 ± 1.4 | 0.252 ± 0.026 |
|  | TD-PER | -0.3 ± 0.1 | 33.6 ± 8.5 | 0.733 ± 0.007 |
|  | Safety-PER | 0.1 ± 0.1 | 70.7 ± 19.5 | 0.779 ± 0.001 |
|  | Unc.-PER | 0.2 ± 0.1 | 46.4 ± 5.3 | 0.776 ± 0.003 |
|  | **VOSR** | **0.6 ± 0.1** | **5.3 ± 0.5** | **0.027 ± 0.002** |
| PointPush1 | Uniform | 0.0 ± 0.1 | 1.3 ± 0.2 | 0.018 ± 0.000 |
|  | TD-PER | -0.4 ± 0.2 | 13.1 ± 2.5 | 0.219 ± 0.025 |
|  | Safety-PER | -0.3 ± 0.1 | 14.0 ± 2.2 | 0.257 ± 0.003 |
|  | Unc.-PER | 0.0 ± 0.1 | 18.3 ± 13.4 | 0.284 ± 0.030 |
|  | **VOSR** | **0.3 ± 0.1** | **0.5 ± 0.0** | **0.007 ± 0.000** |
| PointGoal2 | Uniform | -0.1 ± 0.1 | 53.6 ± 9.4 | 0.780 ± 0.042 |
|  | TD-PER | -0.1 ± 0.2 | 116.2 ± 38.0 | 0.809 ± 0.042 |
|  | Safety-PER | -0.1 ± 0.1 | 68.4 ± 18.9 | 0.785 ± 0.041 |
|  | Unc.-PER | -0.2 ± 0.2 | 125.8 ± 28.9 | 0.781 ± 0.042 |
|  | **VOSR** | **0.2 ± 0.1** | **9.1 ± 6.6** | **0.111 ± 0.013** |
| CarButton1 | Uniform | -2.7 ± 0.8 | 72.9 ± 22.7 | 0.805 ± 0.020 |
|  | TD-PER | -6.2 ± 0.6 | 55.9 ± 16.5 | 0.773 ± 0.025 |
|  | Safety-PER | -4.5 ± 0.5 | 81.5 ± 46.0 | 0.755 ± 0.021 |
|  | Unc.-PER | -9.5 ± 0.5 | 23.9 ± 5.1 | 0.491 ± 0.088 |
|  | **VOSR** | **-3.6 ± 1.2** | **6.6 ± 6.2** | **0.067 ± 0.004** |
| CarGoal1 | Uniform | -4.7 ± 0.4 | 28.7 ± 5.6 | 0.761 ± 0.026 |
|  | TD-PER | 0.0 ± 0.8 | 55.5 ± 17.6 | 0.855 ± 0.001 |
|  | Safety-PER | -1.4 ± 0.4 | 28.5 ± 4.6 | 0.716 ± 0.020 |
|  | Unc.-PER | -4.0 ± 0.4 | 8.0 ± 1.3 | 0.080 ± 0.012 |
|  | **VOSR** | **-0.7 ± 0.4** | **2.5 ± 0.2** | **0.013 ± 0.000** |

## Table 22

Training results using Setting S2 applied to the CRPO method.

| Environment | Sampler | Return | Cost | Violation |
|---|---|---|---|---|
| Ant | Uniform | 3389.5 ± 53.3 | 1.6 ± 0.1 | 0.019 ± 0.001 |
|  | TD-PER | 3082.9 ± 79.6 | 1.3 ± 0.1 | 0.019 ± 0.001 |
|  | Safety-PER | 2671.0 ± 99.4 | 1.5 ± 0.4 | 0.019 ± 0.000 |
|  | Unc.-PER | 3403.8 ± 75.0 | 1.3 ± 0.2 | 0.019 ± 0.001 |
|  | **VOSR** | **3748.8 ± 98.4** | **0.5 ± 0.1** | **0.007 ± 0.000** |
| HalfCheetah | Uniform | 387.0 ± 24.7 | 1.3 ± 1.4 | 0.020 ± 0.003 |
|  | TD-PER | 479.6 ± 22.0 | 1.7 ± 1.6 | 0.019 ± 0.006 |
|  | Safety-PER | 554.5 ± 13.5 | 1.9 ± 2.0 | 0.019 ± 0.002 |
|  | Unc.-PER | 500.2 ± 19.8 | 2.1 ± 2.8 | 0.020 ± 0.004 |
|  | **VOSR** | **604.9 ± 10.5** | **0.2 ± 0.1** | **0.008 ± 0.004** |
| Hopper | Uniform | 107.9 ± 5.1 | 5.5 ± 1.4 | 0.052 ± 0.007 |
|  | TD-PER | 44.1 ± 8.2 | 3.4 ± 0.5 | 0.027 ± 0.001 |
|  | Safety-PER | 75.6 ± 8.1 | 3.9 ± 1.2 | 0.026 ± 0.002 |
|  | Unc.-PER | 38.7 ± 10.8 | 2.1 ± 0.4 | 0.021 ± 0.001 |
|  | **VOSR** | **132.5 ± 11.8** | **0.8 ± 0.1** | **0.007 ± 0.000** |
| Humanoid | Uniform | 79.7 ± 1.1 | 0.4 ± 0.1 | 0.012 ± 0.003 |
|  | TD-PER | 79.7 ± 1.6 | 1.1 ± 1.2 | 0.014 ± 0.004 |
|  | Safety-PER | 84.9 ± 1.2 | 1.6 ± 2.0 | 0.019 ± 0.003 |
|  | Unc.-PER | 76.2 ± 2.2 | 2.2 ± 2.8 | 0.017 ± 0.004 |
|  | **VOSR** | **87.6 ± 2.0** | **0.3 ± 0.0** | **0.006 ± 0.002** |
| Swimmer | Uniform | -0.1 ± 1.7 | 8.8 ± 1.4 | 0.111 ± 0.007 |
|  | TD-PER | 2.9 ± 1.4 | 7.3 ± 0.6 | 0.068 ± 0.010 |
|  | Safety-PER | -8.9 ± 0.8 | 5.5 ± 2.0 | 0.047 ± 0.011 |
|  | Unc.-PER | -2.6 ± 0.7 | 27.6 ± 7.2 | 0.530 ± 0.016 |
|  | **VOSR** | **1.4 ± 0.6** | **1.8 ± 0.1** | **0.010 ± 0.000** |
| Walker2d | Uniform | 71.5 ± 12.0 | 0.5 ± 0.1 | 0.013 ± 0.005 |
|  | TD-PER | 52.4 ± 18.2 | 0.8 ± 0.2 | 0.015 ± 0.005 |
|  | Safety-PER | 59.5 ± 16.0 | 3.1 ± 3.1 | 0.017 ± 0.003 |
|  | Unc.-PER | 130.8 ± 21.8 | 1.0 ± 0.3 | 0.019 ± 0.006 |
|  | **VOSR** | **177.3 ± 6.3** | **1.4 ± 1.9** | **0.007 ± 0.002** |
| PointButton1 | Uniform | 0.5 ± 0.2 | 43.2 ± 5.8 | 0.853 ± 0.002 |
|  | TD-PER | 0.1 ± 0.1 | 28.5 ± 1.3 | 0.769 ± 0.014 |
|  | Safety-PER | 0.1 ± 0.2 | 64.2 ± 22.1 | 0.855 ± 0.000 |
|  | Unc.-PER | 0.2 ± 0.1 | 92.2 ± 11.6 | 0.855 ± 0.000 |
|  | **VOSR** | **0.9 ± 0.1** | **10.3 ± 0.7** | **0.096 ± 0.006** |
| PointPush1 | Uniform | -0.1 ± 0.1 | 39.4 ± 7.4 | 0.819 ± 0.003 |
|  | TD-PER | -0.1 ± 0.1 | 83.6 ± 45.8 | 0.840 ± 0.000 |
|  | Safety-PER | 0.1 ± 0.1 | 11.9 ± 4.2 | 0.182 ± 0.037 |
|  | Unc.-PER | 0.1 ± 0.1 | 35.4 ± 6.9 | 0.811 ± 0.003 |
|  | **VOSR** | **0.4 ± 0.1** | **4.3 ± 0.5** | **0.021 ± 0.001** |
| PointGoal2 | Uniform | -0.1 ± 0.2 | 55.6 ± 13.5 | 0.847 ± 0.018 |
|  | TD-PER | 0.4 ± 0.2 | 40.1 ± 10.1 | 0.785 ± 0.032 |
|  | Safety-PER | -0.3 ± 0.2 | 58.8 ± 5.0 | 0.791 ± 0.035 |
|  | Unc.-PER | -0.3 ± 0.2 | 43.5 ± 9.1 | 0.837 ± 0.011 |
|  | **VOSR** | **0.7 ± 0.1** | **11.4 ± 4.9** | **0.096 ± 0.011** |
| CarButton1 | Uniform | -1.0 ± 0.2 | 57.7 ± 12.6 | 0.846 ± 0.006 |
|  | TD-PER | -1.3 ± 0.2 | 114.5 ± 38.2 | 0.805 ± 0.020 |
|  | Safety-PER | 0.0 ± 0.2 | 38.1 ± 10.4 | 0.796 ± 0.033 |
|  | Unc.-PER | -1.9 ± 0.3 | 149.7 ± 60.5 | 0.839 ± 0.011 |
|  | **VOSR** | **-0.7 ± 0.2** | **10.2 ± 8.0** | **0.097 ± 0.009** |
| CarGoal1 | Uniform | 0.3 ± 0.2 | 77.5 ± 21.5 | 0.849 ± 0.000 |
|  | TD-PER | -0.2 ± 0.1 | 25.5 ± 1.3 | 0.675 ± 0.046 |
|  | Safety-PER | -0.6 ± 0.2 | 22.4 ± 7.4 | 0.559 ± 0.042 |
|  | Unc.-PER | -2.3 ± 0.3 | 55.2 ± 6.6 | 0.849 ± 0.001 |
|  | **VOSR** | **0.0 ± 0.1** | **8.2 ± 0.9** | **0.058 ± 0.002** |

## Table 23

Training results using Setting S2 applied to the PCRPO method.

| Environment | Sampler | Return | Cost | Violation |
|---|---|---|---|---|
| Ant | Uniform | 2538.4 ± 87.2 | 1.4 ± 0.4 | 0.019 ± 0.001 |
|  | TD-PER | 3359.6 ± 95.7 | 1.6 ± 0.3 | 0.019 ± 0.000 |
|  | Safety-PER | 2784.7 ± 121.8 | 1.7 ± 0.5 | 0.019 ± 0.000 |
|  | Unc.-PER | 3902.8 ± 107.9 | 1.6 ± 0.4 | 0.019 ± 0.000 |
|  | **VOSR** | **4447.8 ± 120.3** | **0.5 ± 0.0** | **0.007 ± 0.000** |
| HalfCheetah | Uniform | 305.2 ± 17.9 | 0.8 ± 0.3 | 0.018 ± 0.004 |
|  | TD-PER | 506.6 ± 6.5 | 2.1 ± 3.5 | 0.019 ± 0.005 |
|  | Safety-PER | 276.1 ± 27.7 | 1.4 ± 1.0 | 0.016 ± 0.004 |
|  | Unc.-PER | 395.4 ± 26.1 | 1.5 ± 1.7 | 0.019 ± 0.004 |
|  | **VOSR** | **621.6 ± 52.1** | **0.3 ± 0.0** | **0.007 ± 0.003** |
| Hopper | Uniform | 95.2 ± 8.1 | 6.8 ± 3.1 | 0.065 ± 0.012 |
|  | TD-PER | 85.9 ± 6.3 | 3.5 ± 0.1 | 0.031 ± 0.002 |
|  | Safety-PER | 40.8 ± 6.7 | 1.6 ± 0.5 | 0.019 ± 0.001 |
|  | Unc.-PER | 91.6 ± 4.2 | 1.2 ± 0.1 | 0.019 ± 0.001 |
|  | **VOSR** | **117.5 ± 4.9** | **0.5 ± 0.0** | **0.007 ± 0.000** |
| Humanoid | Uniform | 85.5 ± 1.8 | 1.4 ± 1.9 | 0.017 ± 0.004 |
|  | TD-PER | 76.2 ± 1.6 | 0.8 ± 0.2 | 0.018 ± 0.005 |
|  | Safety-PER | 91.5 ± 1.2 | 1.3 ± 1.2 | 0.018 ± 0.002 |
|  | Unc.-PER | 92.6 ± 1.2 | 1.1 ± 1.1 | 0.019 ± 0.002 |
|  | **VOSR** | **98.4 ± 2.8** | **0.2 ± 0.0** | **0.008 ± 0.002** |
| Swimmer | Uniform | 8.5 ± 1.5 | 9.2 ± 1.3 | 0.138 ± 0.012 |
|  | TD-PER | 6.5 ± 0.6 | 8.2 ± 1.2 | 0.100 ± 0.035 |
|  | Safety-PER | -5.8 ± 0.7 | 4.9 ± 0.7 | 0.048 ± 0.009 |
|  | Unc.-PER | 6.5 ± 1.1 | 10.5 ± 0.8 | 0.153 ± 0.014 |
|  | **VOSR** | **7.5 ± 1.4** | **1.9 ± 0.2** | **0.010 ± 0.000** |
| Walker2d | Uniform | 33.4 ± 14.6 | 1.2 ± 1.6 | 0.014 ± 0.003 |
|  | TD-PER | 137.8 ± 15.3 | 1.7 ± 1.7 | 0.019 ± 0.006 |
|  | Safety-PER | 87.1 ± 17.5 | 1.3 ± 1.4 | 0.020 ± 0.006 |
|  | Unc.-PER | 114.2 ± 28.7 | 0.7 ± 0.2 | 0.020 ± 0.005 |
|  | **VOSR** | **192.6 ± 15.9** | **0.6 ± 1.0** | **0.008 ± 0.002** |
| PointButton1 | Uniform | 0.3 ± 0.1 | 82.2 ± 13.5 | 0.773 ± 0.000 |
|  | TD-PER | -0.2 ± 0.1 | 54.9 ± 6.3 | 0.773 ± 0.000 |
|  | Safety-PER | -0.1 ± 0.1 | 95.1 ± 13.0 | 0.773 ± 0.000 |
|  | Unc.-PER | 0.3 ± 0.1 | 38.9 ± 5.6 | 0.759 ± 0.006 |
|  | **VOSR** | **0.8 ± 0.1** | **9.6 ± 0.8** | **0.081 ± 0.003** |
| PointPush1 | Uniform | -0.1 ± 0.1 | 13.3 ± 1.5 | 0.327 ± 0.034 |
|  | TD-PER | 0.0 ± 0.2 | 11.4 ± 0.3 | 0.215 ± 0.021 |
|  | Safety-PER | -0.1 ± 0.1 | 7.2 ± 0.7 | 0.094 ± 0.017 |
|  | Unc.-PER | 0.0 ± 0.1 | 39.8 ± 3.6 | 0.853 ± 0.002 |
|  | **VOSR** | **0.4 ± 0.1** | **2.7 ± 0.2** | **0.015 ± 0.000** |
| PointGoal2 | Uniform | -0.1 ± 0.1 | 37.4 ± 5.8 | 0.785 ± 0.031 |
|  | TD-PER | 0.1 ± 0.1 | 79.5 ± 7.8 | 0.775 ± 0.023 |
|  | Safety-PER | 0.0 ± 0.0 | 30.5 ± 2.5 | 0.800 ± 0.017 |
|  | Unc.-PER | 0.0 ± 0.2 | 97.7 ± 22.0 | 0.829 ± 0.021 |
|  | **VOSR** | **0.6 ± 0.1** | **7.4 ± 3.6** | **0.104 ± 0.008** |
| CarButton1 | Uniform | -0.4 ± 0.4 | 51.5 ± 11.1 | 0.798 ± 0.023 |
|  | TD-PER | -4.3 ± 0.8 | 57.2 ± 7.8 | 0.773 ± 0.030 |
|  | Safety-PER | -0.5 ± 0.7 | 30.5 ± 5.2 | 0.807 ± 0.020 |
|  | Unc.-PER | -4.9 ± 0.9 | 79.2 ± 12.1 | 0.842 ± 0.039 |
|  | **VOSR** | **-0.5 ± 1.0** | **10.6 ± 5.2** | **0.101 ± 0.019** |
| CarGoal1 | Uniform | 0.2 ± 0.2 | 70.9 ± 24.4 | 0.808 ± 0.000 |
|  | TD-PER | 0.1 ± 0.2 | 12.9 ± 1.6 | 0.234 ± 0.040 |
|  | Safety-PER | -2.2 ± 0.4 | 49.2 ± 7.5 | 0.808 ± 0.000 |
|  | Unc.-PER | -2.5 ± 0.2 | 45.9 ± 18.3 | 0.803 ± 0.004 |
|  | **VOSR** | **0.2 ± 0.4** | **4.6 ± 0.4** | **0.024 ± 0.001** |

## Table 1

Cost-gradient variance and training violation fraction, all eleven environments.

| Environment | Uniform | TD-PER | Safety-PER | Unc.-PER | **VOSR** |
|---|---|---|---|---|---|
| Ant | 1.00 | 1.66 | 1.54 | 1.06 | **0.40** |
| HalfCheetah | 1.00 | 2.19 | 1.89 | 1.36 | **0.52** |
| Hopper | 1.00 | 2.78 | 2.21 | 1.51 | **0.67** |
| Humanoid | 1.00 | 1.81 | 1.64 | 1.12 | **0.43** |
| Swimmer | 1.00 | 2.36 | 2.23 | 1.52 | **0.62** |
| Walker2d | 1.00 | 2.69 | 2.23 | 1.51 | **0.65** |
| PointButton1 | 1.00 | 1.97 | 1.69 | 1.17 | **0.47** |
| PointPush1 | 1.00 | 2.53 | 2.21 | 1.51 | **0.61** |
| PointGoal2 | 1.00 | 2.01 | 1.88 | 1.26 | **0.48** |
| CarButton1 | 1.00 | 2.34 | 2.17 | 1.47 | **0.56** |
| CarGoal1 | 1.00 | 1.51 | 1.38 | 0.98 | **0.36** |
| Average | 1.00 | 2.17 | 1.92 | 1.32 | **0.52** |
| Training violation | 0.385 | 0.359 | 0.352 | 0.386 | **0.042** |

## Table 8

Exact, tempered, and deployed sampling proposals.

| Proposal | Var(Z̄<sup>c</sup>) | Var(Z̄<sup>r</sup>) | D<sub>KL</sub>(q‖b) | ESS/\|𝒫\| |
|---|---|---|---|---|
| Uniform b | 1.00 | 1.00 | 0 | 1.00 |
| Exact q<sup>⋆</sup> (Theorem 1) | 0.32 | 0.33 | 0.55 | 0.43 |
| Tempered q<sub>ε</sub><sup>⋆</sup>, raw scores | 0.46 | 0.48 | 0.31 | 0.64 |
| **Deployed VOSR** | **0.52** | **0.55** | **0.24** | **0.69** |

## Table 3

Shared agent and network hyperparameters, applied to every method.

| Hyperparameter | Value |
|---|---|
| Discount γ | 0.99 |
| Target smoothing τ (Polyak) | 0.005 |
| Actor learning rate | 3 × 10<sup>-4</sup> |
| Critic learning rate (both critics) | 3 × 10<sup>-4</sup> |
| Replay buffer capacity | 1,000,000 (no transition is discarded) |
| Importance weight w<sub>i</sub> | same for all samplers, clipped to [0.1, 10] (C = 10) |
| Sampling correction b(i)/q(i) | applied to all samplers, not clipped |
| Reward critic | twin network (k = 2) |
| Cost critic ensemble size | 3 |
| Candidate minibatch pool | 512 (drawn uniformly, with replacement) |
| Reference batch (VOSR) | 256 (drawn separately from the pool) |
| Training minibatch size | 256 (drawn from the pool with replacement) |
| Warmup (uniform-random) steps | 10,000 |
| Train frequency | every 4 environment steps |
| Policy hidden layers | 2 × 128, tanh |
| Critic hidden layers | 2 × 128, ReLU |
| Policy log σ range | [−2.0, 2.0] |
| State-ratio network β<sub>ψ</sub> | 2 × 128, softplus |
| State-ratio learning rate | 3 × 10<sup>-4</sup> |
| State-ratio refresh interval | every 250 steps |
| Cost signal for the optimizer | EMA (0.9) of episodic training cost, all methods |


## Table 11

Wall-clock, throughput, GPU and CPU memory, and extra passes.

| Optimizer | Sampler | Time/10<sup>3</sup> steps (s) | Updates/s | GPU-h/run | Overhead | GPU mem. (GB) | CPU mem. (GB) | Extra passes |
|---|---|---|---|---|---|---|---|---|
| SAC-Lag. | Uniform | 11.3 | 23.2 | 9.4 | – | 1.26 | 2.87 | 0 |
|  | TD-PER | 12.9 | 20.3 | 10.7 | +14% | 1.26 | 2.99 | 1 |
|  | Safety-PER | 13.6 | 19.2 | 11.4 | +21% | 1.26 | 2.99 | 1 |
|  | Unc.-PER | 14.8 | 17.7 | 12.3 | +31% | 1.37 | 2.99 | 2 |
|  | **VOSR** | **22.1** | **11.7** | **18.4** | **+96%** | **1.60** | **3.23** | **5** |
| CRPO | Uniform | 12.1 | 21.6 | 10.1 | – | 1.32 | 2.87 | 0 |
|  | TD-PER | 13.8 | 19.0 | 11.5 | +14% | 1.32 | 2.99 | 1 |
|  | Safety-PER | 14.6 | 17.9 | 12.1 | +20% | 1.32 | 2.99 | 1 |
|  | Unc.-PER | 15.7 | 16.6 | 13.1 | +30% | 1.44 | 2.99 | 2 |
|  | **VOSR** | **23.4** | **11.1** | **19.5** | **+93%** | **1.68** | **3.23** | **5** |
| PCRPO | Uniform | 12.8 | 20.5 | 10.7 | – | 1.39 | 2.87 | 0 |
|  | TD-PER | 14.5 | 18.0 | 12.1 | +13% | 1.39 | 2.99 | 1 |
|  | Safety-PER | 15.3 | 17.0 | 12.8 | +20% | 1.39 | 2.99 | 1 |
|  | Unc.-PER | 16.6 | 15.8 | 13.8 | +29% | 1.51 | 2.99 | 2 |
|  | **VOSR** | **24.5** | **10.6** | **20.4** | **+91%** | **1.76** | **3.23** | **5** |

## Table 12

GPU training time by environment, optimizer and sampler.

| Optimizer | Environment | Uniform | TD-PER | Safety-PER | Unc.-PER | **VOSR** | **VOSR overhead** |
|---|---|---|---|---|---|---|---|
| SAC-Lag. | Ant | 9.0 | 10.2 | 10.8 | 11.8 | **17.6** | **+96%** |
|  | HalfCheetah | 8.7 | 10.0 | 10.6 | 11.6 | **17.6** | **+102%** |
|  | Hopper | 7.1 | 8.2 | 8.7 | 9.5 | **14.4** | **+103%** |
|  | Humanoid | 16.1 | 18.1 | 19.1 | 20.5 | **29.9** | **+86%** |
|  | Swimmer | 6.2 | 7.1 | 7.6 | 8.2 | **12.7** | **+106%** |
|  | Walker2d | 8.3 | 9.5 | 10.1 | 11.0 | **16.5** | **+98%** |
|  | PointButton1 | 9.0 | 10.4 | 11.0 | 11.8 | **17.9** | **+98%** |
|  | PointPush1 | 9.3 | 10.6 | 11.2 | 12.1 | **18.1** | **+94%** |
|  | PointGoal2 | 9.5 | 10.8 | 11.4 | 12.4 | **18.6** | **+97%** |
|  | CarButton1 | 10.2 | 11.6 | 12.3 | 13.3 | **19.7** | **+93%** |
|  | CarGoal1 | 10.2 | 11.6 | 12.3 | 13.3 | **19.8** | **+95%** |
|  | Mean | 9.4 | 10.7 | 11.4 | 12.3 | **18.4** | **+96%** |
| CRPO | Ant | 9.7 | 11.0 | 11.6 | 12.6 | **18.8** | **+95%** |
|  | HalfCheetah | 9.4 | 10.8 | 11.4 | 12.4 | **18.7** | **+99%** |
|  | Hopper | 7.7 | 8.8 | 9.3 | 10.1 | **15.3** | **+100%** |
|  | Humanoid | 17.2 | 19.2 | 20.3 | 21.8 | **31.6** | **+84%** |
|  | Swimmer | 6.7 | 7.7 | 8.1 | 8.8 | **13.4** | **+101%** |
|  | Walker2d | 9.0 | 10.2 | 10.8 | 11.7 | **17.5** | **+95%** |
|  | PointButton1 | 9.7 | 11.0 | 11.6 | 12.6 | **18.7** | **+94%** |
|  | PointPush1 | 10.0 | 11.3 | 12.0 | 12.9 | **19.1** | **+91%** |
|  | PointGoal2 | 10.2 | 11.5 | 12.2 | 13.2 | **19.6** | **+93%** |
|  | CarButton1 | 10.9 | 12.4 | 13.1 | 14.1 | **20.9** | **+91%** |
|  | CarGoal1 | 10.9 | 12.4 | 13.1 | 14.1 | **21.0** | **+92%** |
|  | Mean | 10.1 | 11.5 | 12.1 | 13.1 | **19.5** | **+93%** |
| PCRPO | Ant | 10.2 | 11.6 | 12.3 | 13.2 | **19.6** | **+92%** |
|  | HalfCheetah | 10.0 | 11.4 | 12.1 | 13.1 | **19.6** | **+97%** |
|  | Hopper | 8.1 | 9.3 | 9.9 | 10.7 | **16.1** | **+98%** |
|  | Humanoid | 18.0 | 20.2 | 21.2 | 22.8 | **32.9** | **+83%** |
|  | Swimmer | 7.1 | 8.1 | 8.6 | 9.3 | **14.1** | **+99%** |
|  | Walker2d | 9.5 | 10.8 | 11.4 | 12.3 | **18.4** | **+94%** |
|  | PointButton1 | 10.2 | 11.6 | 12.2 | 13.2 | **19.6** | **+92%** |
|  | PointPush1 | 10.6 | 11.9 | 12.6 | 13.6 | **20.0** | **+89%** |
|  | PointGoal2 | 10.7 | 12.2 | 12.8 | 13.9 | **20.5** | **+91%** |
|  | CarButton1 | 11.5 | 13.0 | 13.8 | 14.9 | **21.9** | **+90%** |
|  | CarGoal1 | 11.5 | 13.1 | 13.8 | 14.8 | **22.0** | **+91%** |
|  | Mean | 10.7 | 12.1 | 12.8 | 13.8 | **20.4** | **+91%** |

## Table 14

Equal-wall-clock comparison.

| Sampler | Environment steps reached | Return | Cost | Viol. |
|---|---|---|---|---|
| Uniform | 5.9M | 603.4 | 35.7 | 0.233 |
| TD-PER | 5.2M | 714.1 | 19.1 | 0.235 |
| Safety-PER | 4.9M | 1052.4 | 21.7 | 0.239 |
| Unc.-PER | 4.6M | 949.5 | 7.5 | 0.182 |
| **VOSR** | **full budget (3M)** | **1262.4** | **2.9** | **0.025** |

## Table 9

Clipping diagnostics by environment.

| Environment | Clipped weights (%) | \|δ<sub>c</sub><sup>∥</sup>\| | \|δ<sub>r</sub><sup>∥</sup>\| |
|---|---|---|---|
| Ant | 4.4 | 0.031 | 0.030 |
| HalfCheetah | 4.6 | 0.032 | 0.031 |
| Hopper | 4.8 | 0.033 | 0.033 |
| Humanoid | 4.4 | 0.032 | 0.032 |
| Swimmer | 4.2 | 0.029 | 0.033 |
| Walker2d | 4.5 | 0.031 | 0.030 |
| PointButton1 | 4.9 | 0.030 | 0.030 |
| PointPush1 | 4.1 | 0.032 | 0.035 |
| PointGoal2 | 4.0 | 0.031 | 0.032 |
| CarButton1 | 4.6 | 0.030 | 0.029 |
| CarGoal1 | 4.2 | 0.033 | 0.031 |

## Table 2

Validity of theoretical claims for idealized and deployed samplers.

| Claim | Idealized (exact w, critics, fixed q) | Deployed (clipped w, learned β, pool, tempered softmax) |
|---|---|---|
| Mean gradient is the same for every q (Lemma 1) | Yes | Yes (Lemma 2, Proposition 3) |
| Mean gradient equals the true gradient | Yes | No; shifted by δ<sub>r</sub> and δ<sub>c</sub>, identically across samplers (Table 9) |
| q<sup>⋆</sup> minimizes σ<sub>c</sub><sup>2</sup> + κσ<sub>r</sub><sup>2</sup> (Theorem 1) | Yes | Deployed sampler is a surrogate. The gap is measured in Table 8 |
| Theorem 2(a) | Yes | Yes, plus L<sub>𝓕</sub> max(‖δ<sub>r</sub>‖, ‖δ<sub>c</sub>‖); PCRPO up to projection curvature |
| Theorem 2(b) | Yes | Yes; the cost estimate comes from training episodes and the bound does not depend on the sampler |
| Theorem 2(c) | Yes, for any q | Yes, using measured σ<sub>c</sub><sup>2</sup> and σ<sub>r</sub><sup>2</sup>; gradient directions are estimated from the reference batch |
| Same stationary set as Uniform Replay (Theorem 3) | Yes, equal to the KKT set of the base optimizer | Yes, but the shared set can be shifted by the clipping bias |

## Table 13

Candidate pool, density-ratio refresh, clipping and sampler ablations.

| Factor | Value | Return | Cost | Viol. | Var(Z̄<sup>c</sup>) | Time / 10<sup>3</sup> steps |
|---|---|---|---|---|---|---|
| Pool size | 128 | 1105.8±29.6 | 4.9 | 0.055 | 0.85 | 16.0 |
|  | 256 | 1118.6±25.4 | 4.6 | 0.050 | 0.73 | 17.5 |
|  | 512\* | 1217.3±24.4 | 2.8 | 0.025 | 0.52 | 20.5 |
|  | 1024 | 1058.2±42.1 | 5.3 | 0.055 | 0.92 | 26.6 |
|  | 2048 | 1042.3±78.0 | 5.2 | 0.055 | 0.83 | 38.7 |
| β refresh | 50 | 958.3±73.3 | 5.2 | 0.055 | 0.97 | 28.6 |
|  | 250\* | 1217.3±24.4 | 2.8 | 0.025 | 0.52 | 20.5 |
|  | 1000 | 1090.3±56.3 | 5.2 | 0.057 | 0.84 | 19.0 |
|  | β ≡ 1 | 1102.3±59.7 | 4.6 | 0.044 | 0.76 | 18.5 |
| Clip bound C | 2 | 1041.1±25.8 | 5.4 | 0.061 | 0.92 | 20.5 |
|  | 5 | 1140.4±69.6 | 6.6 | 0.073 | 0.75 | 20.5 |
|  | 10\* | 1217.3±24.4 | 2.8 | 0.025 | 0.52 | 20.5 |
|  | 20 | 1091.0±59.3 | 6.4 | 0.070 | 0.90 | 20.5 |
|  | none | 1063.0±43.0 | 5.1 | 0.052 | 0.88 | 20.5 |
| Sampler form | deployed\* | 1217.3±24.4 | 2.8 | 0.025 | 0.52 | 20.5 |
|  | raw tempered | 1083.0±74.4 | 5.3 | 0.060 | 0.82 | 19.5 |
|  | 0.9q<sup>⋆</sup>+0.1b | 995.4±59.7 | 5.2 | 0.055 | 0.94 | 21.5 |
| η | 0.1 | 1132.6±56.0 | 5.7 | 0.066 | 0.75 | 20.5 |
|  | 0.5 | 1051.9±58.1 | 5.3 | 0.055 | 0.98 | 20.5 |
|  | 1.0\* | 1217.3±24.4 | 2.8 | 0.025 | 0.52 | 20.5 |
|  | 2.0 | 1066.1±72.8 | 6.0 | 0.065 | 0.90 | 20.5 |
|  | 5.0 | 1115.5±37.6 | 6.7 | 0.071 | 0.82 | 20.5 |
| κ | 0.0 | 1035.2±33.3 | 4.8 | 0.048 | 0.88 | 20.5 |
|  | 0.15 | 1139.3±16.3 | 5.4 | 0.060 | 0.79 | 20.5 |
|  | 0.35 | 1049.1±96.1 | 5.3 | 0.060 | 0.87 | 20.5 |
|  | 0.7 | 1106.6±14.1 | 5.0 | 0.052 | 0.77 | 20.5 |
|  | 1.5\* | 1217.3±24.4 | 2.8 | 0.025 | 0.52 | 20.5 |

## Table 10

Wrong-direction update probability by base optimizer.

| Sampler | SAC-Lag. P(Z̄<sup>c</sup> ≤ 0) | SAC-Lag. P(Z̄<sup>r</sup> ≤ 0) | CRPO P(Z̄<sup>c</sup> ≤ 0) | CRPO P(Z̄<sup>r</sup> ≤ 0) | PCRPO P(Z̄<sup>c</sup> ≤ 0) | PCRPO P(Z̄<sup>r</sup> ≤ 0) |
|---|---|---|---|---|---|---|
| Uniform | 0.298 | 0.298 | 0.298 | 0.297 | 0.298 | 0.296 |
| TD-PER | 0.343 | 0.342 | 0.342 | 0.342 | 0.342 | 0.342 |
| Safety-PER | 0.332 | 0.332 | 0.333 | 0.333 | 0.333 | 0.333 |
| Unc.-PER | 0.316 | 0.315 | 0.316 | 0.314 | 0.314 | 0.315 |
| **VOSR** | **0.198** | **0.198** | **0.197** | **0.199** | **0.199** | **0.198** |

## Table 6

VOSR settings common to environments and optimizers.

| Parameter | Value (all environments, all optimizers) |
|---|---|
| Temperature η | 1.0 (on standardized scores) |
| Score weight κ | 1.5 |
| Candidate pool size \|𝒫\| | 512 |
| Reference batch for g̃<sub>c</sub>, g̃<sub>r</sub><sup>+</sup> | 256, drawn separately from the pool |
| Score clipping | median ± 6.0×MAD |
| Score floor inside ζ<sub>i</sub> | 10<sup>-12</sup> |
