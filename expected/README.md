# Archived UCC 2021 reports

The original report archive (`archive/reports-090921.7z` on `main`) contains 270 complete timing JSON and host-occupation CSV pairs across the three scenario directories, plus earlier experimental files. See the [errata](../ERRATA.md#table-3) for the run sets used in the printed table.

## Per-run summaries

- [`runs.csv`](runs.csv) contains 268 rows from the release snapshot. It includes all 267 archived runs with shared seeds and the Infrastructure Aware Random run for seed `122354`.
- [`table3_verified.csv`](table3_verified.csv) compares the release snapshot with the printed table.

## Metric convention

See [Application Grouping](../ERRATA.md#application-grouping) for how `all_times.py` counted SLA fulfillment.

## Corrected Analysis

Paper mode uses the application grouping described above. Corrected mode maps each report entry to its full application ID using the scenario file. It counts fulfillment against the number of applications in the report.

The [corrected Table 3](table3_corrected_270.md) uses 30 shared seeds per scheduler and scenario. The Random cohort adds the two archived Kube and DLSLA runs for seed `988196` and one [new Infrastructure Aware run](../data/additional-runs/) for that seed. The original Infrastructure Aware run for `122354` remains in the main archive. The corrected cohort contains 269 archived runs and one new run. The new run used the unchanged Random Infrastructure Aware [configuration](../data/scenarios/scenario-3-ks-infra.json).

The following command produced identical timing and host-occupation reports in two runs on macOS arm64 with Python 3.9.6 and the repository dependencies.

```bash
PYTHONHASHSEED=0 python scripts/run_experiment.py \
  --scenario data/scenarios/scenario-3-ks-infra.json --seed 988196
```

To recompute the corrected table, extract the original reports from `main` and pass the extracted `reports/` directory. The analyzer uses the packaged Infrastructure Aware report when the input directory lacks that run.

```bash
python scripts/analyze.py --reports /path/to/reports --mode corrected \
  --cohort complete --summary-out results/table3_corrected_270.csv
```

DLSLA has the most applications fulfilling their SLAs and the lowest mean delay beyond the SLA in all three scenarios. It fulfills 52.6–66.8% more application SLAs than Kube. Infrastructure Aware has the lower mean deployment time across all applications in Normal (24.61 s versus 26.44 s).

For the Figure 7 comparison, a node that receives 15 replicas across 30 runs averages 0.5 replicas and is counted below one. The corrected 270-run analysis gives the following counts out of 140 edge nodes.

| Scenario | DLSLA | Infrastructure Aware |
| --- | ---: | ---: |
| Random | 10 | 4 |
| Normal | 10 | 26 |
| 60 seconds | 16 | 19 |

Infrastructure Aware has fewer edge nodes below one replica per run on average in Random. DLSLA has fewer in the other two scenarios. The [data CSV](table3_corrected_270.csv) also gives the mean number of nodes with zero replicas per execution as a separate metric.

The [comparison of the original and corrected analyses](historical_vs_corrected.tsv) uses the 267 archived runs with shared seeds and records the effect of correcting the analysis on this cohort.

## Source Provenance

The compatibility changes defer the Basemap import, honor seed zero, and remove an unused import. The release keeps one copy of each scheduler and stores the scenario files under `data/scenarios/`.

## Archived Replay

The report filenames preserve seeds from the original runs. The standard run commands use local Python behavior, so a run with the same seed can produce different placements and timings. The `archive-replay` branch documents the verified replay procedure.

## Published Cohorts

The original analysis used 29 shared Random seeds per scheduler. Seed `988196` is present for Kube and DLSLA, and seed `122354` is present only for Infrastructure Aware. Normal and 60 seconds have 30 shared seeds each.

The SLA and latency block used **261 runs**. The archived `graphs_pd.py` assigns the 29 Random rows to an empty pandas DataFrame first. The longer Normal and 60-second series align to this existing index, dropping the last seed of each scheduler (`537105` and `482017`, respectively). Recomputing these 261 runs matches all 54 published means and standard deviations to the printed precision.

## Figure 7 Check

The figure script averages the number of replicas on each edge node across runs, then inspects the nodes whose average is below one. Using the archived Random summaries, 10 nodes are below that threshold with DLSLA and five with Infrastructure Aware. The comparison favors DLSLA in Normal and 60 seconds by the same measure. The published Random values of 4.2 and 5.2 remain unverified.
