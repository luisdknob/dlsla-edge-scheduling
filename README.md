# Enforcing Deployment Latency SLA in Edge Infrastructures through Multi-objective Genetic Scheduler

This repository contains the ContainerSim experiments for UCC 2021. The study evaluates DLSLA, a genetic scheduler that selects an edge node and can reorder its download queue to meet an application's deployment deadline. The experiments compare DLSLA with Kube-scheduler and Infrastructure Aware.

Luis Augusto Dias Knob, Carlos Henrique Kayser, Paulo Silas Severo de Souza, and Tiago Ferreto (2021). *Enforcing Deployment Latency SLA in Edge Infrastructures through Multi-objective Genetic Scheduler*. IEEE/ACM International Conference on Utility and Cloud Computing. [Paper](https://doi.org/10.1145/3468737.3494100)

## Release Note

> [!NOTE]
> This post-publication release is part of an ongoing effort to improve the reproducibility and verifiability of my research. For this paper, I am making the source code and experimental configurations publicly available. I plan to gradually release artifacts from more of my research projects over time.
>
> I used GPT-6.2 Sol and DeepSeek V4.1 Flash 1017 to help prepare this repository, fix minor execution issues, and review the code and results against the published paper. I kept the code here as close as possible to the implementation used in the original experiments.
>
> The archive preserves the original seeds. A fresh run with the same seed can produce different results because UUID generation and the order in which layers are processed also affect the simulation. See [Archived Replay](#archived-replay) for what was reproduced and under which conditions.
>
> I documented minor corrections and clarifications in the [errata](ERRATA.md). The results still support the paper’s main conclusions.

## Simulation Scenario

The simulator uses the 197-node Ipê topology and 24 Docker Hub images. The three schedulers are evaluated under each of the following SLA distributions.

| Scenario | Deployment deadline |
| --- | --- |
| Random | 30–150 s |
| Normal | 30, 60, 90, 120, or 150 s with probabilities of 5%, 20%, 50%, 20%, and 5% |
| 60 seconds | 60 s for every application |

### Dataset

- The [original source archive](archive/ucc-original-source.zip) includes the paper-era Python sources, analysis scripts, and scenario files.
- The [original run reports](archive/reports-090921.7z) contain timing JSON and host-occupation CSV files. The [errata](ERRATA.md#table-3) explains which runs contributed to each block of the published table.
- The runnable copy uses the [scenario files](data/scenarios/) and [seed lists](data/seeds.json). Its compatibility adjustments are documented under [source provenance](expected/README.md#source-provenance).

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

The validator compares the [included run summaries](expected/runs.csv) with the printed SLA and latency values. The [errata](ERRATA.md#table-3) explains the differences.

The `analysis-fixed` branch reconstructs the published SLA and latency statistics from the original reports. It also contains the corrected Table 3 in `expected/table3_corrected_270.md` and commands to recompute its values.

### Archived Replay

The `archive-replay` branch uses the original seeds and recovered layer order to reproduce the tested runs. [Replay notes](expected/README.md#archived-replay)

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
