#!/usr/bin/env python3
"""Run a UCC 2021 scenario set over its archived seed list."""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SEEDS = json.load(open(os.path.join(ROOT, "data", "seeds.json")))
SCENARIOS = {
    "random": [
        ("scenario-1-kubescheduler", "random"),
        ("scenario-2-sla", "random"),
        ("scenario-3-ks-infra", "random"),
    ],
    "normal": [
        ("nd_scenario_1_ks", "normal"),
        ("nd_scenario_2_sla", "normal"),
        ("nd_scenario_3_infra", "normal"),
    ],
    "60sec": [
        ("st_scenario_1_ks", "60sec"),
        ("st_scenario_2_sla", "60sec"),
        ("st_scenario_3_infra", "60sec"),
    ],
}


def run_one(name, group, seed, reports):
    cmd = [
        sys.executable, os.path.join(HERE, "run_experiment.py"),
        "--scenario", os.path.join(ROOT, "data", "scenarios", name + ".json"),
        "--seed", str(seed),
        "--reports", *reports,
    ]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return name, seed, p.returncode, p.stderr[-1000:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["random", "normal", "60sec", "all"], default="random")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--limit", type=int, default=None,
                    help="only the first N seeds of each scenario, for a smoke test")
    ap.add_argument("--reports", nargs="+", default=["containerAllTimes", "hostOccupation"],
                    choices=["containerAllTimes", "hostOccupation", "cacheStatus",
                             "provisionTime", "networkLog", "registryUsage"])
    args = ap.parse_args()

    groups = ["random", "normal", "60sec"] if args.set == "all" else [args.set]
    jobs = []
    for group in groups:
        for name, seed_group in SCENARIOS[group]:
            seeds = SEEDS[seed_group][:args.limit] if args.limit else SEEDS[seed_group]
            for seed in seeds:
                jobs.append((name, seed_group, seed))
    print("jobs", len(jobs), "workers", args.workers)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_one, name, group, seed, args.reports): (name, seed)
                for name, group, seed in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            name, seed = futs[f]
            n, s, rc, err = f.result()
            print(("OK   " if rc == 0 else "FAIL ") + "%s seed=%d (%d/%d)" % (n, s, i, len(jobs)))
            if rc != 0:
                print(err)
    print("reports in", os.path.join(ROOT, "reports"))


if __name__ == "__main__":
    main()
