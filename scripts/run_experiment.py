#!/usr/bin/env python3
"""Run one UCC 2021 scenario/seed with the paper-era ContainerSim code."""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True,
                    help="scenario JSON, e.g. data/scenarios/scenario-1-kubescheduler.json")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--reports", nargs="+",
                    default=["containerAllTimes", "hostOccupation"],
                    choices=["containerAllTimes", "hostOccupation", "cacheStatus",
                             "provisionTime", "networkLog", "registryUsage"])
    args = ap.parse_args()

    scenario = args.scenario if os.path.isabs(args.scenario) else os.path.join(ROOT, args.scenario)
    for d in ("logs", "reports"):
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    cmd = [
        sys.executable, os.path.join(ROOT, "code", "main.py"),
        "--file", scenario,
        "--seed", str(args.seed),
        "--reports", *args.reports,
    ]
    print(" ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
