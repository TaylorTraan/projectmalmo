"""Agent protocol for the training harness.

Any object implementing `select_action` can be used as an agent.
Learning agents may additionally implement `observe` to receive
transitions and update internal state (e.g., Q-values).

Required: select_action(obs, info) -> int
Optional (duck-typed; harness calls only if present): observe(obs, action, reward, next_obs, done, info) -> None
"""

from typing import Any


def has_observe(agent: Any) -> bool:
    """Return True if the agent implements observe for learning updates."""
    return hasattr(agent, "observe") and callable(getattr(agent, "observe"))
