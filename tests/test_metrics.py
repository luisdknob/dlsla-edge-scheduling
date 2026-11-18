import csv
import os
import sys
import unittest

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
        rows = list(csv.DictReader(open(os.path.join(ROOT, "expected", "runs.csv"))))
        agg = validate.aggregate(rows)
        a = agg[("random", "Infrastructure")]
        self.assertEqual(a["n"], 30)
        self.assertAlmostEqual(a["fulfilled"], 313.23, places=2)
        self.assertAlmostEqual(a["over"], 29.92, places=2)
        self.assertAlmostEqual(a["all"], 26.43, places=2)

    def test_aggregate_dlsla(self):
        rows = list(csv.DictReader(open(os.path.join(ROOT, "expected", "runs.csv"))))
        agg = validate.aggregate(rows)
        a = agg[("60sec", "DLSLA")]
        self.assertEqual(a["n"], 30)
        self.assertAlmostEqual(a["fulfilled"], 326.17, places=2)
        self.assertAlmostEqual(a["over"], 36.73, places=2)
        self.assertAlmostEqual(a["all"], 24.92, places=2)


if __name__ == "__main__":
    unittest.main()
