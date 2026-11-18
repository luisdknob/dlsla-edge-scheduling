# UCC 2021 Errata

These corrections refer to the published version of [Enforcing Deployment Latency SLA in Edge Infrastructures through Multi-objective Genetic Scheduler](https://doi.org/10.1145/3468737.3494100).

## Simulation Results

### Workload Sizes

Table 2 gives one workload size of 350 applications and 1,258 replicas. The [scenario files](data/scenarios/) specify different workloads for the three SLA distributions.

| Scenario | Configured applications | Configured replicas | Groups in the original analysis |
| --- | ---: | ---: | ---: |
| Random | 356 | 1,284 | 350 |
| Normal | 353 | 1,253 | 347 |
| 60 seconds | 350 | 1,250 | 341 |

### Application Grouping

The original analysis groups containers by the first four dash-separated tokens in their names, which can merge applications whose image names contain a dash. It counts a group as missing its SLA when its longest instantiation time is at least its largest deadline. The paper reports `350 - misses` as the fulfillment count for all three workloads.

### Table 3

Section 5.3 describes 30 runs per scenario and scheduler. The SLA and latency block of Table 3 averages **261 runs**, or 29 for each combination. The Table 3 script takes the 29 Random rows as its index and drops the last row from each Normal and 60-second series. [Published cohorts](expected/README.md#published-cohorts)

The placement block uses **267 runs**. Its edge totals match the archived per-node summaries using all 30 available Normal and 60-second runs and 29 Random runs per scheduler. The “Worker Nodes (total)” and “Edge Nodes (total)” headings are reversed. The printed worker totals mostly match 1,258 minus the archived edge total, which inflates the Normal and 60-second values. For the Normal workload, Table 3 gives mean worker totals of 238.40 for Kube and 459.93 for DLSLA. The archived means are 208.40 and 426.93, respectively.

Both latency standard-deviation columns have units of seconds. Section 5.4 gives 71.55% as Kube's best SLA fulfillment rate. Its Normal row in the published table implies 63.21% (221.24 out of 350). Section 6 describes SLA fulfillment as “almost 200% better”. The published counts give a 53–67% increase over Kube across the three scenarios.

### Figure 7

Section 5.4 describes the values as counts of edge nodes with zero scheduled containers. The Figure 7 script counts nodes averaging fewer than one replica over the runs. [Figure 7 check](expected/README.md#figure-7-check)

## Simulator

### Queue Changes

Section 4.4 describes the objective as the number of changes. Algorithm 1 measures how far entries move by summing their indices as they are removed from the original queue.

## Conclusion

These corrections leave the paper’s main conclusion intact. Across all three scenarios, DLSLA met the most application SLAs and had the lowest mean delay among applications that missed their SLAs.
