# Experiment Config Schema

All experiment configurations in this project share a common structure. This document defines the schema so that experiments run under consistent conditions and differences in learning behavior can be attributed solely to the design choices under study.

---

## Common Fields (All Configs)

| Field | Type | Description |
|-------|------|-------------|
| `config_name` | string | Experiment identifier; used in run directory names and logs |
| `num_episodes` | int | Number of episodes to run |
| `seed` | int | Random seed for reproducibility |
| `max_steps` | int | Maximum environment steps per episode |
| `mission_xml_path` | string | Path to mission XML (e.g. `env/mission.xml`) |
| `env_version` | string | Version tag for mission + termination semantics (e.g. `v0`); see env/malmo_env.py |
| `obs_version` | string | Version tag for observation format (e.g. `v0`); see docs/TRAINING_HARNESS.md |
| `action_version` | string | Version tag for action mapping (e.g. `v0`); 0=N, 1=S, 2=W, 3=E |
| `reward_scheme` | string | Reward variant name (e.g. `sparse_v0`, `step_penalty_v1`, `distance_shaping_v1`); see env/reward_schemes.py |
| `reward_params` | object | Optional scheme-specific parameters (e.g. `step_penalty`, `fall_penalty`, `distance_scale`) |
| `log_reward_components` | bool | If true, env adds `info["reward_components"]` (per-step) with a breakdown of reward terms |

---

## Algorithm-Specific Fields (Tabular Q-Learning)

| Field | Type | Description |
|-------|------|-------------|
| `learning_rate` | float | Step size for Q-updates (alpha) |
| `discount` | float | Discount factor (gamma) |
| `epsilon_schedule` | string | `constant` or `linear_decay` |
| `epsilon` | float | Used when `epsilon_schedule` is `constant` |
| `epsilon_start` | float | Starting epsilon for `linear_decay` |
| `epsilon_end` | float | Final epsilon for `linear_decay` |
| `epsilon_decay_episodes` | int | Episodes over which epsilon decays linearly |

---

## Locked vs Variable Parameters

**Locked** (fixed across all experiments for fair comparison):

- `max_steps` – same step limit for all runs
- `mission_xml_path` – same environment
- `env_version`, `obs_version`, `action_version` – same reward, observation, and action semantics

**Variable** (may differ per algorithm or run):

- `num_episodes` – learning algorithms may need more episodes than baselines
- `seed` – vary for multiple runs or statistical comparison
- Algorithm-specific params (e.g. `learning_rate`, `epsilon_schedule`) – only when comparing algorithms

When comparing experiments, change **one variable at a time**; derive new configs from a baseline and modify only the factor under study.

---

## Example Configs

- `configs/random_baseline.json` – random policy baseline
- `configs/tabular_q_baseline.json` – tabular Q-learning baseline

Copy one of these when creating a new experiment config and adjust only the fields you intend to vary.
