# Archived UCC 2021 reports

The original report archive (`archive/reports-090921.7z` on `main`) contains 270 complete timing JSON and host-occupation CSV pairs across the three scenario directories, plus earlier experimental files. See the [errata](../ERRATA.md#table-3) for the run sets used in the printed table.

## Per-run summaries

- [`runs.csv`](runs.csv) contains 268 rows from the release snapshot. It includes all 267 archived runs with shared seeds and the Infrastructure Aware Random run for seed `122354`.
- [`table3_verified.csv`](table3_verified.csv) compares the release snapshot with the printed table.

## Metric convention

See [Application Grouping](../ERRATA.md#application-grouping) for how `all_times.py` counted SLA fulfillment.

The `analysis-fixed` branch reconstructs the published SLA and latency statistics and provides the corrected Table 3.

## Release Analyzer

The release analyzer uses the last deadline it reads. This affects the reconstruction for some Random runs. The `analysis-fixed` branch reproduces the published SLA and latency cohort and includes a corrected 270-run analysis.

## Source Provenance

The compatibility changes defer the Basemap import, honor seed zero, and remove an unused import. The release keeps one copy of each scheduler and stores the scenario files under `data/scenarios/`.

## Archived Replay

A standard macOS run with an archived seed can differ in two ways. The Windows CPython 3.9 implementation of `uuid1()` takes draws from the same random stream as the scheduler. The macOS native path skips those draws. The scenario loader also deduplicates layers with a set, whose iteration order determines the download queue.

The helper uses the archived seed, restores the Windows-style random draws for UUID generation, and infers the layer order from each replica's original successful downloads. The layer order was recoverable for all 270 archived runs in the audit. Node choices and timing values are computed by the simulator.

The timing JSON and host-occupation CSV matched exactly after line-ending normalization in ten tested runs covering all nine scheduler and SLA combinations. The timing reports contained 109,860 rows.

## Published Cohorts

The original analysis used 29 shared Random seeds per scheduler. Seed `988196` is present for Kube and DLSLA, and seed `122354` is present only for Infrastructure Aware. Normal and 60 seconds have 30 shared seeds each.

The SLA and latency block used **261 runs**. The archived `graphs_pd.py` assigns the 29 Random rows to an empty pandas DataFrame first. The longer Normal and 60-second series align to this existing index, dropping the last seed of each scheduler (`537105` and `482017`, respectively). Recomputing these 261 runs matches all 54 published means and standard deviations to the printed precision.

## Figure 7 Check

The figure script averages the number of replicas on each edge node across runs, then inspects the nodes whose average is below one. Using the archived Random summaries, 10 nodes are below that threshold with DLSLA and five with Infrastructure Aware. The comparison favors DLSLA in Normal and 60 seconds by the same measure. The published Random values of 4.2 and 5.2 remain unverified.
