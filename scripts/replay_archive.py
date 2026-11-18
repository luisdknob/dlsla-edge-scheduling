"""Reconstruct one archived UCC run's execution order and compare its reports."""
import argparse
import json
import os
import runpy
import sys
import tempfile
import uuid
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx


ENTRY = Path(__file__).resolve().parents[1] / "code/main.py"
TIMING = "-container_all_times.json"
PLACEMENT = "-host_occupation.csv"


def layer_order(scenario, rows):
    graph = nx.DiGraph()
    graph.add_nodes_from(layer["digest"] for layer in scenario["layers"])
    downloads = defaultdict(list)
    for row in rows:
        if row["downloaded"] == 1:
            replica, digest = row["name"].rsplit("-sha256:", 1)
            downloads[replica].append("sha256:" + digest)
    for layers in downloads.values():
        graph.add_edges_from(zip(layers, layers[1:]))

    order = list(nx.lexicographical_topological_sort(graph))
    precedence = nx.transitive_closure_dag(graph, order)
    for image in scenario["images"]:
        for version in image["versions"]:
            for a, b in combinations(version["layers"], 2):
                if not (precedence.has_edge(a, b) or precedence.has_edge(b, a)):
                    raise ValueError(f"Incomplete layer order for {image['name']}: {a}, {b}")
    return {digest: index for index, digest in enumerate(order)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path)
    parser.add_argument("archived_timing_report", type=Path)
    args = parser.parse_args()

    scenario = args.scenario.resolve()
    timing = args.archived_timing_report.resolve()
    run = timing.name.removesuffix(TIMING)
    seed = int(run.rsplit("-", 1)[1])
    placement = timing.with_name(run + PLACEMENT)
    original_timing = timing.read_text()
    original_placement = placement.read_text()
    rows = json.loads(original_timing)["containers"]
    order = layer_order(json.loads(scenario.read_text()), rows)

    # Match the RNG calls of the historical Windows CPython 3.9 uuid1 path.
    uuid._generate_time_safe = None
    uuid._node = 0x020000000001
    sys.path.insert(0, str(ENTRY.parent))
    from classes import json as loader

    read_config = loader.configuration_from_JSON

    def read_with_order(config):
        result = read_config(config)
        for image in result[2]:
            for version in image.versions:
                version.layers.sort(key=lambda layer: order[layer.digest])
        return result

    loader.configuration_from_JSON = read_with_order
    sys.argv = [str(ENTRY), "--file", str(scenario), "--seed", str(seed),
                "--reports", "containerAllTimes", "hostOccupation"]

    with tempfile.TemporaryDirectory(prefix="ucc-archive-replay-") as path:
        destination = Path(path)
        for directory in ("logs", "reports"):
            (destination / directory).mkdir()
        cwd = Path.cwd()
        try:
            os.chdir(destination)
            runpy.run_path(str(ENTRY), run_name="__main__")
        finally:
            os.chdir(cwd)

        reports = destination / "reports"
        if (reports / timing.name).read_text() != original_timing:
            raise SystemExit("Timing report differs")
        if (reports / placement.name).read_text() != original_placement:
            raise SystemExit("Placement report differs")
    print(f"Both reports match after newline normalization ({len(rows):,} timing rows).")


if __name__ == "__main__":
    main()
