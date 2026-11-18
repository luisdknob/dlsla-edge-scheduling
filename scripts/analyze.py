#!/usr/bin/env python3
"""Recompute UCC 2021 per-run metrics from archived container_all_times files.

The paper's Table 3 was produced by ``reports/all_times.py``.  That script
groups an application by the first four dash-separated tokens of the container
name and reports the number of SLA misses; the paper reports fulfillment as
350 - misses.  We keep the same convention so the aggregate reproduces Table 3.
"""
import argparse
import csv
import json
import os
import statistics
import sys

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
SEEDS = json.load(open(os.path.join(ROOT, "data", "seeds.json")))
SCENARIO_LABELS = {
    "random_scenario": "random",
    "normal_distribution_scenario": "normal",
    "todos_60": "60sec",
}


def app_key(name):
    # Same grouping as the paper's all_times.py (first four dash tokens).
    return "-".join(name.split("-", 5)[:4])


def run_metrics(path):
    data = json.load(open(path))["containers"]
    groups = {}
    expected = {}
    for row in data:
        key = app_key(row["name"])
        groups.setdefault(key, []).append(row["instantiation_time"])
        expected[key] = row["expected_time"]
    values = {key: max(vals) for key, vals in groups.items()}
    missed = [key for key, value in values.items() if expected[key] <= value]
    over = statistics.fmean(values[key] - expected[key] for key in missed) if missed else 0.0
    return {
        "n_groups": len(values),
        "missed": len(missed),
        "fulfilled": 350 - len(missed),
        "over_sla": over,
        "all_avg": statistics.fmean(values.values()),
    }


def collect(reports_dir):
    rows = []
    for scenario, entries in SCENARIOS.items():
        for name, scheduler in entries:
            for seed in SEEDS[scenario]:
                filename = "%s-%d-container_all_times.json" % (name, seed)
                path = os.path.join(reports_dir, scenario, filename)
                if not os.path.exists(path):
                    path = os.path.join(reports_dir, filename)
                if not os.path.exists(path):
                    print("missing", path, file=sys.stderr)
                    continue
                row = {"scenario": SCENARIO_LABELS[scenario], "scheduler": scheduler, "seed": seed}
                row.update(run_metrics(path))
                rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", default=os.path.join(ROOT, "reports"),
                    help="directory containing random/, normal/, 60sec/ reports")
    ap.add_argument("--out", default=os.path.join(ROOT, "expected", "runs.csv"))
    args = ap.parse_args()

    rows = collect(args.reports)
    fields = ["scenario", "scheduler", "seed", "n_groups", "missed", "fulfilled", "over_sla", "all_avg"]
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            out = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}
            w.writerow(out)
    print("wrote", args.out, "rows", len(rows))


if __name__ == "__main__":
    main()
