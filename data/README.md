# Data

## Scenarios

The nine UCC 2021 scenario files are grouped into three SLA distributions:

| Group | Scenario files | Scheduler |
|---|---|---|
| `random` | `scenario-1-kubescheduler.json` | Kube-scheduler |
| `random` | `scenario-2-sla.json` | DLSLA |
| `random` | `scenario-3-ks-infra.json` | Infrastructure Aware |
| `normal` | `nd_scenario_1_ks.json` | Kube-scheduler |
| `normal` | `nd_scenario_2_sla.json` | DLSLA |
| `normal` | `nd_scenario_3_infra.json` | Infrastructure Aware |
| `60sec` | `st_scenario_1_ks.json` | Kube-scheduler |
| `60sec` | `st_scenario_2_sla.json` | DLSLA |
| `60sec` | `st_scenario_3_infra.json` | Infrastructure Aware |

Each scenario uses the 197-node Ipê topology and 24 Docker Hub images. The application counts are 356 (`random`), 353 (`normal`), and 350 (`60sec`); the paper's Table 2 reports 350, which is the value used by the analysis script's SLA convention.

The 30 seeds planned for each group are listed in `seeds.json`. The original Random comparison uses the 29 seeds shared by all three schedulers. Report filenames identify the seed for each preserved run.
