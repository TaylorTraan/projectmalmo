# Training Harness

The training harness provides a shared, algorithm-agnostic loop for running episodes, stepping agents through the environment, and recording episode-level statistics. Any agent that implements the protocol can be plugged in without changing the core loop.

---

## Quick Start

```python
from env.malmo_env import MalmoGridEnv
from harness import run_episodes, EpisodeStats
from harness.agents import RandomAgent

env = MalmoGridEnv(mission_xml_path="env/mission.xml", max_steps=200)
agent = RandomAgent(seed=42)
stats = run_episodes(env, agent, num_episodes=5, seed=42)

for s in stats:
    print(s.episode, s.total_reward, s.steps, s.success, s.termination_reason)
```

---

## Agent Protocol

To plug in a new agent, implement the following interface.

### Required

- **`select_action(obs: dict, info: dict) -> int`**  
  Return an action ID from 0 to 3 (North, South, West, East) given the current observation and info dict.

### Optional

- **`observe(obs, action, reward, next_obs, done, info)`**  
  Called after each step. Implement this for learning agents (e.g., Q-learning) that need to update on each transition. The harness calls this only if the agent has the method.

---

## Example: Random Agent

```python
import random
from typing import Any, Dict, Optional


class RandomAgent:
    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def select_action(self, obs: Dict[str, float], info: Dict[str, Any]) -> int:
        return self._rng.randint(0, 3)
```

This agent does not implement `observe`; it is suitable for non-learning baselines.

---

## Example: Q-Learning Agent Skeleton

A learning agent needs both `select_action` and `observe`:

```python
from typing import Any, Dict, Optional


class QLearningAgent:
    def __init__(self, learning_rate: float = 0.1, epsilon: float = 0.1, seed: Optional[int] = None) -> None:
        # Initialize Q-table, RNG, etc.
        pass

    def select_action(self, obs: Dict[str, float], info: Dict[str, Any]) -> int:
        # Epsilon-greedy or other policy; return 0-3.
        pass

    def observe(
        self,
        obs: Dict[str, float],
        action: int,
        reward: float,
        next_obs: Dict[str, float],
        done: bool,
        info: Dict[str, Any],
    ) -> None:
        # Update Q(s, a) using the transition (obs, action, reward, next_obs, done).
        pass
```

Fill in the implementation; the harness will call `observe` after each step.

---

## run_episodes API

```python
def run_episodes(
    env: MalmoGridEnv,
    agent,
    num_episodes: int,
    seed: int | None = None,
) -> list[EpisodeStats]:
```

- **env**: MalmoGridEnv instance (must support `reset(seed)` and `step(action)`).
- **agent**: Object with `select_action(obs, info) -> int`; optionally has `observe(...)`.
- **num_episodes**: Number of episodes to run.
- **seed**: Optional seed passed to `env.reset(seed=seed)`.

Returns a list of `EpisodeStats`, one per episode.

---

## EpisodeStats

Each `EpisodeStats` has:

| Field | Type | Description |
|-------|------|-------------|
| `episode` | int | Episode index (0-based). |
| `total_reward` | float | Sum of rewards in the episode. |
| `steps` | int | Number of environment steps. |
| `success` | int | 1 if `termination_reason == "success_diamond_picked_up"`, else 0. |
| `termination_reason` | str \| None | From env info, e.g. `success_diamond_picked_up`, `timeout_max_steps_reached`, `failure_fell_off_platform`. |
| `seed` | int \| None | Seed used for this episode. |

---

## Termination Reasons

The environment sets `info["termination_reason"]`; common values:

- `success_diamond_picked_up` — agent collected the diamond.
- `failure_fell_off_platform` — agent fell off.
- `timeout_max_steps_reached` — episode hit max steps.
- `malmo_mission_ended_early` — Malmo mission ended unexpectedly.

---

## Observation and Action Space

- **Observation**: dict with `x`, `z`, `y` (agent position).
- **Actions**: 0=North, 1=South, 2=West, 3=East.

See [MALMO_SETUP.md](MALMO_SETUP.md) for environment details.
