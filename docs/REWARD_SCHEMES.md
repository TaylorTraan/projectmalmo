## Reward Schemes (Feedback Variants)

This project studies how **reward design** (amount and type of feedback) affects learning on the Malmo “diamond pickup” task.

### Task recap (what the reward is trying to produce)

- **Goal**: pick up the diamond.
- **Failure**: fall off the platform (into lava).
- **Timeout**: hit `max_steps` without success.
- **Termination reasons** are surfaced as `info["termination_reason"]` (see `docs/TRAINING_HARNESS.md`).

### How reward schemes are selected

Reward is computed inside the environment and returned through the standard Gym-like API:

- `obs, reward, done, info = env.step(action)`

To change reward shaping **without changing agent code**, set these config fields:

- `reward_scheme`: string name of the reward design variant
- `reward_params`: object of scheme-specific parameters (optional)
- `log_reward_components`: if `true`, adds `info["reward_components"]` (optional per-step breakdown)

Reward schemes are implemented in `env/reward_schemes.py`.

### Implemented reward variants

#### `sparse_v0` (terminal-only; baseline)

- **Definition**:
  - If `done` and `termination_reason == "success_diamond_picked_up"`: \(+1\)
  - If `done` and `termination_reason == "failure_fell_off_platform"`: \(-1\)
  - Else: \(0\)
- **Intended effect**: minimal feedback; learning depends heavily on exploration reaching the diamond.
- **Notes**: This is designed to match the historical reward behavior from `env/malmo_env.py` exactly.

#### `sparse_neutral_fall_v1` (terminal-only; no negative fall)

- **Definition**:
  - Success: \(+1\)
  - Fall/timeout/early termination: \(0\)
- **Intended effect**: isolates the impact of **negative punishment** on exploration vs. learning stability.

#### `step_penalty_v1` (sparse + per-step cost)

- **Parameters** (`reward_params`):
  - `step_penalty` (float, default `0.01`)
- **Definition**:
  - Terminal reward uses the same success/fall values as `sparse_v0`
  - Each **non-terminal** step adds \(-\texttt{step_penalty}\)
- **Intended effect**: encourages shorter paths and reduces dithering; can make “doing nothing” expensive.
- **Caution**: if the step penalty is too large relative to terminal reward, the agent may prefer ending episodes quickly (including risky moves).

#### `fall_penalty_v1` (sparse + stronger fall penalty)

- **Parameters** (`reward_params`):
  - `fall_penalty` (float, default `2.0`)
- **Definition**:
  - Success: \(+1\)
  - Fall: \(-\texttt{fall_penalty}\)
  - Timeout/early termination: \(0\)
- **Intended effect**: discourages risky edge behavior; can change exploration by making falls much more costly.

#### `distance_shaping_v1` (terminal + distance-to-goal shaping)

- **Parameters** (`reward_params`):
  - `goal_x` (int, default `0`)
  - `goal_z` (int, default `9`)
  - `distance_scale` (float, default `0.05`)
  - `distance_metric` (`"manhattan"` or `"euclidean"`, default `"manhattan"`)
  - `clip_abs` (float or null, default null) — optional clip for shaping magnitude per step
- **Definition**:
  - Terminal reward uses `sparse_v0`
  - If position is available on consecutive steps, define distance \(d_t\) from agent \((x_t,z_t)\) to \((goal_x,goal_z)\)
  - Shaping reward: \(r_{shape} = \texttt{distance_scale} \cdot (d_{t-1} - d_t)\)
    - Moving **closer** gives positive reward; moving away gives negative reward.
  - Total reward: \(r_t = r_{terminal} + r_{shape}\)
- **Intended effect**: dense guidance toward the diamond; typically improves early learning speed.
- **Caution**: shaping can bias policies; compare against `sparse_v0` under the same seeds and environment versions.

### Example config snippets

Sparse (baseline):

```json
{
  "reward_scheme": "sparse_v0",
  "reward_params": {},
  "log_reward_components": false
}
```

Step penalty:

```json
{
  "reward_scheme": "step_penalty_v1",
  "reward_params": { "step_penalty": 0.01 },
  "log_reward_components": true
}
```

Distance shaping (using the default diamond location from `env/mission.xml`):

```json
{
  "reward_scheme": "distance_shaping_v1",
  "reward_params": {
    "goal_x": 0,
    "goal_z": 9,
    "distance_scale": 0.05,
    "distance_metric": "manhattan",
    "clip_abs": 0.2
  },
  "log_reward_components": true
}
```

