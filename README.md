# Enforcing Deployment Latency SLA in Edge Infrastructures through Multi-objective Genetic Scheduler

This repository contains the ContainerSim experiments for UCC 2021. The study evaluates DLSLA, a genetic scheduler that selects an edge node and can reorder its download queue to meet an application's deployment deadline. The experiments compare DLSLA with Kube-scheduler and Infrastructure Aware.

Luis Augusto Dias Knob, Carlos Henrique Kayser, Paulo Silas Severo de Souza, and Tiago Ferreto (2021). *Enforcing Deployment Latency SLA in Edge Infrastructures through Multi-objective Genetic Scheduler*. IEEE/ACM International Conference on Utility and Cloud Computing. [Paper](https://doi.org/10.1145/3468737.3494100)

## Simulation Scenario

The simulator uses the 197-node Ipê topology and 24 Docker Hub images. The three schedulers are evaluated under each of the following SLA distributions.

| Scenario | Deployment deadline |
| --- | --- |
| Random | 30–150 s |
| Normal | 30, 60, 90, 120, or 150 s with probabilities of 5%, 20%, 50%, 20%, and 5% |
| 60 seconds | 60 s for every application |

### Dataset

- The original source and run report archives are in `archive/` on `main`. The [errata](ERRATA.md#table-3) explains which reports contributed to the published table.
- The runnable copy uses the [scenario files](data/scenarios/) and [seed lists](data/seeds.json).

### Settings and Execution

From the repository root, install the dependencies with Python 3.9.

```bash
python3.9 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the Random Kube-scheduler scenario with a saved seed.

```bash
python scripts/run_experiment.py \
  --scenario data/scenarios/scenario-1-kubescheduler.json \
  --seed 163295
```

Reports go to `reports/` and simulator logs go to `logs/`. To run the first seed for each scheduler in the Random scenario, run the batch with a one-seed limit.

```bash
python scripts/run_all.py --set random --limit 1
```

### Results

```bash
python scripts/validate.py
```

The validator compares the [included run summaries](expected/runs.csv) with the printed SLA and latency values. Use the `analysis-fixed` branch to reconstruct the published statistics from the archive and recompute the corrected Table 3.

### Archived Replay

The `archive-replay` branch can restore the execution order for a preserved run. Extract `archive/reports-090921.7z` from `main` and keep the timing JSON and host-occupation CSV in the same directory.

```bash
python scripts/replay_archive.py \
  data/scenarios/scenario-2-sla.json \
  /path/to/reports/random_scenario/scenario-2-sla-163295-container_all_times.json
```

The helper uses the archived seed and recovered layer order, recreates the Windows UUID random sequence, and compares both regenerated reports. [Replay audit](expected/README.md#archived-replay)

## Citation

```bibtex
@inproceedings{knob2021ucc,
  author    = {Dias Knob, Luis Augusto and Kayser, Carlos Henrique and Souza, Paulo Silas Severo de and Ferreto, Tiago},
  title     = {Enforcing Deployment Latency SLA in Edge Infrastructures through Multi-objective Genetic Scheduler},
  booktitle = {2021 IEEE/ACM 14th International Conference on Utility and Cloud Computing (UCC)},
  year      = {2021},
  doi       = {10.1145/3468737.3494100}
}
```

## License

The code is released under the [Apache License 2.0](LICENSE). See [NOTICE](NOTICE).
