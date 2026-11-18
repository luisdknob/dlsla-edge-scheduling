#!/usr/bin/env python3
"""Recompute paper or corrected UCC 2021 metrics from container_all_times files."""
import argparse
import csv
import json
import os
import statistics
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SCENARIOS = {
    "random": [
        ("scenario-1-kubescheduler", "Kube"),
        ("scenario-2-sla", "DLSLA"),
        ("scenario-3-ks-infra", "Infrastructure"),
    ],
    "normal": [
        ("nd_scenario_1_ks", "Kube"),
        ("nd_scenario_2_sla", "DLSLA"),
        ("nd_scenario_3_infra", "Infrastructure"),
    ],
    "60sec": [
        ("st_scenario_1_ks", "Kube"),
        ("st_scenario_2_sla", "DLSLA"),
        ("st_scenario_3_infra", "Infrastructure"),
    ],
}
with open(os.path.join(ROOT, "data", "seeds.json")) as f:
    SEEDS = json.load(f)
ARCHIVE_DIRS = {
    "random": "random_scenario",
    "normal": "normal_distribution_scenario",
    "60sec": "todos_60",
}


def app_key(name):
    # Same grouping as the paper's all_times.py (first four dash tokens).
    return "-".join(name.split("-", 5)[:4])


def replica_applications(scenario):
    """Map the names emitted by the simulator to their full application IDs."""
    applications = {app["name"]: app for app in scenario["applications"]}
    images = {image["name"]: image for image in scenario["images"]}
    replicas = {}
    for op in scenario["lifecyleOperations"]:
        if op["type"] != "creation" or op["name"] != "deployment":
            continue
        app = op["application"]
        image = applications[app]["image"].split(":")[0]
        tag = images[image]["versions"][0]["tag"]
        for index in range(op["numReplicas"]):
            replicas[f"{app}-{index}-{image}-{tag}"] = app
    return replicas


def run_metrics(path, replicas=None, host_counts=None):
    with open(path) as f:
        data = json.load(f)["containers"]
    if not data:
        raise ValueError(f"{path} contains no container records")

    values = {}
    expected = {}
    destinations = {}
    for row in data:
        if replicas is None:
            key = app_key(row["name"])
        else:
            replica = row["name"].rsplit("-", 1)[0]
            if replica not in replicas:
                raise ValueError(f"{path} contains an unknown replica: {replica}")
            key = replicas[replica]
            if host_counts is not None:
                destination = row["dst"]
                if destinations.setdefault(replica, destination) != destination:
                    raise ValueError(f"{path} places {replica} on more than one node")
        instantiation = row["instantiation_time"]
        deadline = row["expected_time"]
        values[key] = max(values.get(key, instantiation), instantiation)
        expected[key] = max(expected.get(key, deadline), deadline)

    if host_counts is not None:
        if destinations.keys() != replicas.keys():
            raise ValueError(f"{path} is missing configured replicas")
        host_counts.append(Counter(destinations.values()))

    missed = [key for key, value in values.items() if expected[key] <= value]
    over = statistics.fmean(values[key] - expected[key] for key in missed) if missed else 0.0
    count = 350 if replicas is None else len(values)
    # The original analysis rounded each run before aggregating Table 3.
    places = 2 if replicas is None else 4
    return {
        "n_groups": len(values),
        "missed": len(missed),
        "fulfilled": count - len(missed),
        "over_sla": round(over, places),
        "all_avg": round(statistics.fmean(values.values()), places),
    }


def summarize(scenario, scheduler, rows, host_counts, config):
    result = {
        "scenario": scenario, "scheduler": scheduler, "runs": len(rows),
        "applications": rows[0]["n_groups"],
        "replicas": sum(host_counts[0].values()),
    }
    for column in ("fulfilled", "missed", "over_sla", "all_avg"):
        values = [row[column] for row in rows]
        result[column + "_mean"] = statistics.mean(values)
        result[column + "_std"] = statistics.stdev(values)
    result["fulfilled_pct"] = 100 * result["fulfilled_mean"] / result["applications"]

    totals = sum(host_counts, Counter())
    for kind in ("worker", "edge"):
        hosts = [node["name"] for node in config["nodes"]
                 if node["type"] == "chost" and node["name"].startswith(kind)]
        mean = sum(totals[host] for host in hosts) / len(rows)
        result[kind + "_replicas_mean"] = mean
        result[kind + "_replica_pct"] = 100 * mean / result["replicas"]
        result[kind + "_replicas_per_node_mean"] = mean / len(hosts)
        result[kind + "_replica_pct_per_node"] = result[kind + "_replica_pct"] / len(hosts)
        if kind == "edge":
            result["edge_nodes_without_replica_mean"] = statistics.mean(
                sum(host not in counts for host in hosts) for counts in host_counts)
            result["edge_nodes_with_mean_below_one_replica"] = sum(
                totals[host] < len(rows) for host in hosts)
    return {key: round(value, 4) if isinstance(value, float) else value
            for key, value in result.items()}


def collect(reports_dir, mode="paper", cohort="paper", summary=None):
    rows = []
    for scenario, entries in SCENARIOS.items():
        seeds = SEEDS[scenario]
        if cohort == "paper":
            # The original statistics used the first 29 rows of each series.
            seeds = seeds[:29]
        if cohort == "complete" and scenario == "random":
            seeds = seeds[:29] + [988196]
        for name, scheduler in entries:
            replicas = None
            host_counts = [] if summary is not None else None
            group = []
            if mode == "corrected":
                with open(os.path.join(ROOT, "data", "scenarios", name + ".json")) as f:
                    config = json.load(f)
                    replicas = replica_applications(config)
            for seed in seeds:
                filename = "%s-%d-container_all_times.json" % (name, seed)
                paths = (
                    os.path.join(reports_dir, ARCHIVE_DIRS[scenario], filename),
                    os.path.join(reports_dir, scenario, filename),
                    os.path.join(reports_dir, filename),
                )
                if cohort == "complete":
                    paths += (os.path.join(ROOT, "data", "additional-runs", filename),)
                path = next((p for p in paths if os.path.isfile(p)), None)
                if path is None:
                    if cohort == "complete":
                        raise ValueError(f"missing timing report: {filename}")
                    continue
                row = {"scenario": scenario, "scheduler": scheduler, "seed": seed}
                row.update(run_metrics(path, replicas, host_counts))
                group.append(row)
            rows.extend(group)
            if summary is not None:
                summary.append(summarize(scenario, scheduler, group, host_counts, config))
    return rows


def write_csv(path, rows):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print("wrote", path, "rows", len(rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", default=os.path.join(ROOT, "reports"),
                    help="extracted reports directory or flat simulator output")
    ap.add_argument("--mode", choices=["paper", "corrected"], default="paper",
                    help="published convention or full application IDs")
    ap.add_argument("--cohort", choices=["paper", "planned", "complete"], default="paper",
                    help="published SLA cohort, planned seeds, or 30 shared seeds per scenario")
    ap.add_argument("--out", help="output CSV (default: results/runs_<mode>.csv)")
    ap.add_argument("--summary-out", help="write corrected SLA, latency and placement aggregates")
    args = ap.parse_args()

    summary = [] if args.summary_out else None
    if summary is not None and (args.mode, args.cohort) != ("corrected", "complete"):
        ap.error("--summary-out requires --mode corrected --cohort complete")
    try:
        rows = collect(args.reports, args.mode, args.cohort, summary)
    except ValueError as error:
        ap.error(str(error))
    if not rows:
        ap.error(f"no matching timing reports in {args.reports}")

    out = args.out or os.path.join(ROOT, "results", f"runs_{args.mode}.csv")
    write_csv(out, rows)
    if summary is not None:
        write_csv(args.summary_out, summary)


if __name__ == "__main__":
    main()
