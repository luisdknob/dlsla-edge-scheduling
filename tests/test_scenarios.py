import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCEN = os.path.join(ROOT, "data", "scenarios")


class ScenarioTest(unittest.TestCase):

    def test_scenarios(self):
        expected = {
            "scenario-1-kubescheduler.json": (356, "KubeScheduler"),
            "scenario-2-sla.json": (356, "SLADeploymentLatencyScheduler"),
            "scenario-3-ks-infra.json": (356, "KubeScheduler"),
            "nd_scenario_1_ks.json": (353, "KubeScheduler"),
            "nd_scenario_2_sla.json": (353, "SLADeploymentLatencyScheduler"),
            "nd_scenario_3_infra.json": (353, "KubeScheduler"),
            "st_scenario_1_ks.json": (350, "KubeScheduler"),
            "st_scenario_2_sla.json": (350, "SLADeploymentLatencyScheduler"),
            "st_scenario_3_infra.json": (350, "KubeScheduler"),
        }
        for name, (n_apps, scheduler) in expected.items():
            with open(os.path.join(SCEN, name)) as f:
                d = json.load(f)
            self.assertEqual(len(d["applications"]), n_apps, name)
            self.assertEqual(len(d["images"]), 24, name)
            self.assertEqual(len(d["nodes"]), 197, name)
            self.assertEqual(d["infrastructure"]["scheduler"]["name"], scheduler, name)

    def test_seeds(self):
        with open(os.path.join(ROOT, "data", "seeds.json")) as f:
            seeds = json.load(f)
        self.assertEqual(set(seeds), {"random", "normal", "60sec"})
        for key, values in seeds.items():
            self.assertEqual(len(values), 30, key)
            self.assertEqual(len(set(values)), 30, key)


if __name__ == "__main__":
    unittest.main()
