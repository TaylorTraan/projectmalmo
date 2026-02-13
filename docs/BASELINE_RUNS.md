# Random Baseline Runs

The random policy agent selects actions uniformly at random from the discrete action space (0–3) at every time step. It does not use observations, memory, or learning. Running it for a fixed number of episodes produces a **baseline** that can be compared with learning agents to see whether and how learning improves behavior.

---

## Running the baseline

From the repo root (with Malmo client running and environment set up):

```bash
Run the random baseline

PYTHONPATH="/home/malmo/MalmoPlatform/scripts/python-wheel/backwards-compatible-imports:$PYTHONPATH" python3 scripts/run_random_baseline.py --config configs/random_baseline.json

```

This:

- Loads settings from `configs/random_baseline.json` (e.g. `num_episodes`, `seed`, `max_steps`, `mission_xml_path`).
- Creates a timestamped run directory under `runs/`, e.g. `runs/20250212_143022_random_baseline_seed42/`.
- Runs that many episodes with the random agent via the shared training harness.
- Writes `episodes.csv`, `episodes.json`, and a copy of the config as `config.json` in that directory.

Override config from the command line if needed:

```bash
PYTHONPATH="/home/malmo/MalmoPlatform/scripts/python-wheel/backwards-compatible-imports:$PYTHONPATH" python3 scripts/run_random_baseline.py --config configs/random_baseline.json --num-episodes 20 --seed 0
```

---

## Summarizing a run

To compute summary statistics and optionally generate plots for a run directory:

```bash
PYTHONPATH="/home/malmo/MalmoPlatform/scripts/python-wheel/backwards-compatible-imports:$PYTHONPATH" python3 scripts/summarize_run.py runs/02122026_random_baseline_seed42
```

This:

- Reads `episodes.json` (or `episodes.csv`) from the given run directory.
- Computes mean and standard deviation of total reward and steps, success rate (%), and counts per termination reason.
- Writes `summary.json` and `summary.txt` into the same directory.
- If matplotlib is available, also writes `baseline_plots.png` (reward per episode and reward distribution) for comparison with learning agents.

To skip plot generation:

```bash
PYTHONPATH="/home/malmo/MalmoPlatform/scripts/python-wheel/backwards-compatible-imports:$PYTHONPATH" python3 scripts/summarize_run.py runs/20250212_143022_random_baseline_seed42 --no-plot
```

---

## Run directory layout

After a baseline run and summarize step, a run directory contains:

| File | Description |
|------|-------------|
| `episodes.csv` | Episode-level stats (episode, total_reward, steps, success, termination_reason, seed). |
| `episodes.json` | Same data in JSON. |
| `config.json` | Copy of the experiment config used for reproducibility. |
| `summary.json` | Summary statistics (mean/std reward and steps, success rate, termination counts). |
| `summary.txt` | Human-readable summary. |
| `baseline_plots.png` | Optional; reward-per-episode and reward histogram (if matplotlib available). |

Use these artifacts to compare the random baseline with learning agents on the same metrics and environment conditions.
