import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scripts import analyze, validate  # noqa: E402


class MetricsTest(unittest.TestCase):

    def test_app_key_matches_paper_script(self):
        self.assertEqual(
            analyze.app_key("hello-world-app-3-10-0-hello-world-latest-sha256:abc"),
            "hello-world-app-3",
        )
        self.assertEqual(
            analyze.app_key("influxdb-app-3-0-0-influxdb-latest-sha256:abc"),
            "influxdb-app-3-0",
        )

    def test_aggregate_random(self):
        with open(os.path.join(ROOT, "expected", "runs.csv")) as f:
            rows = list(csv.DictReader(f))
        agg = validate.aggregate(rows)
        a = agg[("random", "Infrastructure")]
        self.assertEqual(a["n"], 30)
        self.assertAlmostEqual(a["fulfilled"], 313.23, places=2)
        self.assertAlmostEqual(a["over"], 29.92, places=2)
        self.assertAlmostEqual(a["all"], 26.43, places=2)

    def test_aggregate_dlsla(self):
        with open(os.path.join(ROOT, "expected", "runs.csv")) as f:
            rows = list(csv.DictReader(f))
        agg = validate.aggregate(rows)
        a = agg[("60sec", "DLSLA")]
        self.assertEqual(a["n"], 30)
        self.assertAlmostEqual(a["fulfilled"], 326.17, places=2)
        self.assertAlmostEqual(a["over"], 36.73, places=2)
        self.assertAlmostEqual(a["all"], 24.92, places=2)

    def test_paper_and_corrected_application_grouping(self):
        name = "hello-world"
        apps = ["hello-world-app-3-10", "hello-world-app-3-20"]
        scenario = {
            "applications": [{"name": app, "image": name} for app in apps],
            "images": [{"name": name, "versions": [{"tag": "latest"}]}],
            "lifecyleOperations": [
                {"type": "creation", "name": "deployment", "application": app, "numReplicas": 1}
                for app in apps
            ],
        }
        records = [
            {"name": f"{apps[1]}-0-hello-world-latest-sha256:abc",
             "expected_time": 20, "instantiation_time": 10},
            {"name": f"{apps[0]}-0-hello-world-latest-sha256:abc",
             "expected_time": 10, "instantiation_time": 15},
        ]
        with tempfile.TemporaryDirectory() as path:
            report = Path(path) / "timings.json"
            report.write_text(json.dumps({"containers": records}))
            paper = analyze.run_metrics(report)
            corrected = analyze.run_metrics(report, analyze.replica_applications(scenario))
            report.write_text(json.dumps({"containers": list(reversed(records))}))
            self.assertEqual(analyze.run_metrics(report), paper)

        self.assertEqual((paper["n_groups"], paper["fulfilled"]), (1, 350))
        self.assertEqual((corrected["n_groups"], corrected["fulfilled"]), (2, 1))
        self.assertEqual(corrected["over_sla"], 5)

    def test_collect_historical_archive_cohort(self):
        with tempfile.TemporaryDirectory() as path:
            reports = Path(path) / "random_scenario"
            reports.mkdir()
            for seed in (163295, 122354):
                report = reports / f"scenario-3-ks-infra-{seed}-container_all_times.json"
                report.write_text(json.dumps({"containers": [{
                    "name": "influxdb-app-3-0-0-influxdb-latest-sha256:abc",
                    "expected_time": 20, "instantiation_time": 10,
                }]}))
            self.assertEqual(
                [(r["scenario"], r["seed"]) for r in analyze.collect(path)],
                [("random", 163295)],
            )
            self.assertEqual(
                {r["seed"] for r in analyze.collect(path, cohort="planned")},
                {163295, 122354},
            )

    def test_analyze_empty_input_preserves_output(self):
        with tempfile.TemporaryDirectory() as path:
            output = Path(path) / "runs.csv"
            output.write_text("existing results\n")
            result = subprocess.run(
                [sys.executable, os.path.join(ROOT, "scripts", "analyze.py"),
                 "--reports", path, "--out", str(output)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no matching timing reports", result.stderr)
            self.assertEqual(output.read_text(), "existing results\n")

    def test_validate_rejects_empty_and_incomplete_strict_results(self):
        with tempfile.TemporaryDirectory() as path:
            runs = Path(path) / "runs.csv"
            cmd = [sys.executable, os.path.join(ROOT, "scripts", "validate.py"),
                   "--strict", "--runs", str(runs)]
            header = "scenario,scheduler,seed,n_groups,missed,fulfilled,over_sla,all_avg\n"
            runs.write_text(header)
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no matching runs", result.stderr)

            runs.write_text(header + "random,Kube,163295,350,138,212,97.25,82.91\n")
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("only 1 of 29 required runs", result.stderr)


if __name__ == "__main__":
    unittest.main()
