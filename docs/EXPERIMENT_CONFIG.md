# Experiment Configuration and Reproducibility

All experiments in this project are driven by configuration files. Configs specify experimental parameters such as reward function, state representation, learning algorithm, number of episodes, and random seeds. This ensures that all experiments run under consistent conditions, so differences in learning behavior can be attributed solely to the design choices under study.

---

## Schema Reference

See [configs/SCHEMA.md](../configs/SCHEMA.md) for the full config structure. Summary:

- **Common fields** (all configs): `config_name`, `num_episodes`, `seed`, `max_steps`, `mission_xml_path`, `env_version`, `obs_version`, `action_version`, `reward_scheme`, `reward_params`, `log_reward_components`
- **Tabular Q-learning** adds: `learning_rate`, `discount`, `epsilon_schedule`, `epsilon`, `epsilon_start`, `epsilon_end`, `epsilon_decay_episodes`

---

## How to Run Experiments Reproducibly

1. **Start Docker and Minecraft** – See [docs/MALMO_SETUP.md](MALMO_SETUP.md) for setup. From the project root:

   ```bash
   docker run -it --rm --platform=linux/amd64 -p 5901:5901 -p 6901:6901 -p 10000:10000 -p 8888:8888 -v "$PWD":/workspace andkram/malmo
   ```

2. **Open Minecraft** in noVNC at http://127.0.0.1:6901 and wait for it to load.

3. **Use the shared PYTHONPATH** when running scripts inside the container:

   ```bash
   PYTHONPATH="/home/malmo/MalmoPlatform/scripts/python-wheel/backwards-compatible-imports:$PYTHONPATH"
   ```

4. **Always pass `--config`** to use a config file. Override `--num-episodes` and `--seed` for exploratory runs only.

5. **Each run produces** a timestamped directory `runs/YYYYMMDD_HHMMSS_{config_name}_seed{seed}/` with `config.json` (the exact config used) plus episode logs. This enables full reproducibility.

---

## Calibration Workflow

We first implemented baseline agents and conducted preliminary runs to calibrate episode length, exploration schedules, and reward magnitudes. After establishing reasonable defaults, we fixed these parameters across all experiments to ensure fair and controlled comparisons.

**Calibration checklist:**

1. Run the random baseline with default config; observe variance and termination reasons.
2. Run tabular Q-learning informally (e.g. 50–100 episodes); check whether the learning curve improves.
3. Note reasonable values for `max_steps`, `num_episodes`, `learning_rate`, and `epsilon_schedule`.
4. Update configs with these values.
5. Treat configs as **locked** for formal comparisons; vary only the factor under study.

---

## Change One Variable at a Time

When comparing experiments, derive new configs from a baseline and change **only one factor** (e.g. reward shape, observation richness, algorithm). Do not simultaneously change env, reward, and algorithm; this makes results uninterpretable. See `.cursor/rules/30-experiments-repro.mdc` for the full guideline.

---

## Quick Reference

| Script | Config | Example Command |
|--------|--------|-----------------|
| Random baseline | `configs/random_baseline.json` | `python3 -m scripts.run_random_baseline --config configs/random_baseline.json` |
| Tabular Q-learning | `configs/tabular_q_baseline.json` | `python3 -m scripts.run_tabular_q --config configs/tabular_q_baseline.json` |
| Summarize run | (run directory path) | `python3 -m scripts.summarize_run runs/YYYYMMDD_HHMMSS_config_seed42` |

All commands run from `/workspace` inside the container with PYTHONPATH set. For baseline details, see [docs/BASELINE_RUNS.md](BASELINE_RUNS.md).
