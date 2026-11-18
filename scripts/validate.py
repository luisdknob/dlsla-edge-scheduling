#!/usr/bin/env python3
"""Summarize UCC 2021 runs or compare them with Table 3."""
import argparse
import csv
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Paper Table 3: fulfilled avg/std, over-SLA avg/std, all-apps avg/std.
PAPER = {
    ("random", "Kube"): (211.90, 5.00, 97.25, 5.65, 82.91, 2.91),
    ("random", "Infrastructure"): (313.21, 1.15, 29.99, 1.60, 26.47, 0.40),
    ("random", "DLSLA"): (325.79, 2.30, 25.48, 3.50, 25.42, 0.59),
    ("normal", "Kube"): (221.24, 6.10, 91.52, 7.37, 84.48, 3.80),
    ("normal", "Infrastructure"): (331.69, 1.20, 34.55, 1.86, 25.04, 0.30),
    ("normal", "DLSLA"): (338.93, 1.83, 33.97, 7.76, 26.89, 0.65),
    ("60sec", "Kube"): (195.76, 4.86, 109.94, 6.14, 88.68, 3.38),
    ("60sec", "Infrastructure"): (309.76, 2.29, 40.71, 3.46, 26.84, 0.85),
    ("60sec", "DLSLA"): (326.17, 2.35, 36.22, 7.58, 24.87, 0.88),
}
ORDER = {"random": 0, "normal": 1, "60sec": 2}
SCHED = {"Kube": 0, "Infrastructure": 1, "DLSLA": 2}


def aggregate(rows):
    out = {}
    for scen in ORDER:
        for sched in SCHED:
            rr = [r for r in rows if r["scenario"] == scen and r["scheduler"] == sched]
            if not rr:
                continue
            metrics = {
                "n": len(rr),
                "groups": statistics.fmean(float(r["n_groups"]) for r in rr),
            }
            for metric, column in [("fulfilled", "fulfilled"), ("over", "over_sla"), ("all", "all_avg")]:
                values = [float(r[column]) for r in rr]
                metrics[metric] = statistics.fmean(values)
                metrics[metric + "_std"] = statistics.stdev(values) if len(values) > 1 else None
            out[(scen, sched)] = metrics
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=os.path.join(ROOT, "expected", "runs.csv"))
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--summary", action="store_true",
                    help="summarize results without comparing with the paper")
    args = ap.parse_args()

    if args.summary and args.strict:
        ap.error("--strict requires comparison with Table 3")
    with open(args.runs, newline="") as f:
        rows = list(csv.DictReader(f))
    agg = aggregate(rows)
    if not agg:
        ap.error(f"no matching runs in {args.runs}")
    seeds = {(r["scenario"], r["scheduler"], r["seed"]) for r in rows}
    if len(seeds) != len(rows):
        ap.error(f"duplicate scenario, scheduler and seed in {args.runs}")

    if args.summary:
        print(f"{'scenario':8s} {'scheduler':15s} {'runs':>4s} {'groups':>8s} "
              f"{'fulfilled':>10s} {'over (s)':>9s} {'all (s)':>9s}")
        for (scenario, scheduler), a in agg.items():
            print(f"{scenario:8s} {scheduler:15s} {a['n']:4d} {a['groups']:8.2f} "
                  f"{a['fulfilled']:10.2f} {a['over']:9.2f} {a['all']:9.2f}")
        return

    print(f"{'scenario':8s} {'scheduler':15s} {'n':>3s} "
          f"{'fulfilled':>10s} {'paper':>8s} {'over':>8s} {'paper':>8s} "
          f"{'all':>8s} {'paper':>8s}")
    failed = False
    if args.strict:
        for key in PAPER:
            n = agg.get(key, {}).get("n", 0)
            required = 29
            if n < required:
                print("FAIL", key, f"only {n} of {required} required runs", file=sys.stderr)
                failed = True
    for key in sorted(agg, key=lambda k: (ORDER[k[0]], SCHED[k[1]])):
        a = agg[key]
        p = PAPER[key]
        print(f"{key[0]:8s} {key[1]:15s} {a['n']:3d} "
              f"{a['fulfilled']:10.2f} {p[0]:8.2f} {a['over']:8.2f} {p[2]:8.2f} "
              f"{a['all']:8.2f} {p[4]:8.2f}")
        for got, want, name in [
            (a["fulfilled"], p[0], "fulfilled"),
            (a["fulfilled_std"], p[1], "fulfilled std"),
            (a["over"], p[2], "over SLA"),
            (a["over_std"], p[3], "over SLA std"),
            (a["all"], p[4], "all apps"),
            (a["all_std"], p[5], "all apps std"),
        ]:
            if got is not None and abs(got - want) > 1.0:
                print("FAIL", key, name, got, want, file=sys.stderr)
                failed = True
    if args.strict and failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
