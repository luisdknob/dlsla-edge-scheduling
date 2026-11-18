# Table 3 — Corrected UCC 2021 results

The analysis uses 270 runs, with 30 shared seeds per scenario and scheduler. The cohort contains 269 archived runs and one new Infrastructure Aware run in Random. See the [analysis notes](README.md#corrected-analysis) for the run and aggregation commands.

## Container placement

Worker and edge totals are mean replica counts per run. Shares are percentages of all replicas.

| Scenario | Scheduler | Worker total | Edge total | Worker / edge share (%) | Worker replicas per node | Worker share per node (%) | Edge replicas per node | Edge share per node (%) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Random | Kube-scheduler | 214.47 | 1069.53 | 16.70 / 83.30 | 7.66 | 0.60 | 7.64 | 0.59 |
| Random | Infrastructure Aware | 401.40 | 882.60 | 31.26 / 68.74 | 14.34 | 1.12 | 6.30 | 0.49 |
| Random | DLSLA | 434.80 | 849.20 | 33.86 / 66.14 | 15.53 | 1.21 | 6.07 | 0.47 |
| Normal | Kube-scheduler | 208.40 | 1044.60 | 16.63 / 83.37 | 7.44 | 0.59 | 7.46 | 0.60 |
| Normal | Infrastructure Aware | 418.20 | 834.80 | 33.38 / 66.62 | 14.94 | 1.19 | 5.96 | 0.48 |
| Normal | DLSLA | 433.50 | 819.50 | 34.60 / 65.40 | 15.48 | 1.24 | 5.85 | 0.47 |
| 60 seconds | Kube-scheduler | 208.30 | 1041.70 | 16.66 / 83.34 | 7.44 | 0.60 | 7.44 | 0.60 |
| 60 seconds | Infrastructure Aware | 407.97 | 842.03 | 32.64 / 67.36 | 14.57 | 1.17 | 6.01 | 0.48 |
| 60 seconds | DLSLA | 435.60 | 814.40 | 34.85 / 65.15 | 15.56 | 1.24 | 5.82 | 0.47 |

## SLA fulfillment and application deployment latency

Time over SLA covers applications that missed their deadlines. Deployment time covers all applications. SD is the sample standard deviation across runs.

| Scenario | Scheduler | SLAs met, mean | SLAs met, SD | Time over SLA, mean (s) | Time over SLA, SD (s) | Deployment time, mean (s) | Deployment time, SD (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Random | Kube-scheduler | 217.33 | 5.24 | 97.38 | 5.50 | 81.60 | 2.89 |
| Random | Infrastructure Aware | 319.20 | 1.13 | 29.98 | 1.58 | 26.01 | 0.39 |
| Random | DLSLA | 331.80 | 2.30 | 25.60 | 3.48 | 25.02 | 0.57 |
| Normal | Kube-scheduler | 224.10 | 6.22 | 91.90 | 7.80 | 83.25 | 3.78 |
| Normal | Infrastructure Aware | 334.70 | 1.18 | 34.55 | 1.83 | 24.61 | 0.29 |
| Normal | DLSLA | 341.90 | 1.81 | 34.03 | 7.63 | 26.44 | 0.63 |
| 60 seconds | Kube-scheduler | 195.50 | 4.90 | 109.71 | 6.18 | 86.42 | 3.21 |
| 60 seconds | Infrastructure Aware | 309.90 | 2.38 | 40.67 | 3.40 | 26.13 | 0.83 |
| 60 seconds | DLSLA | 326.17 | 2.31 | 36.73 | 7.96 | 24.28 | 0.88 |

[Data CSV](table3_corrected_270.csv)
