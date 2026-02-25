"""Straight agent: baseline that always takes the same fixed direction.

This agent selects a single action every step (e.g. 0=North). It does not
use observations or learning. Use it as a baseline to compare with random
and learning agents (e.g. to see effect of always moving in one direction).
"""

from typing import Any, Dict

# Action space: 0=North, 1=South, 2=West, 3=East (must match env).
NUM_ACTIONS = 4


class StraightAgent:
    """Agent that always returns the same action (go straight in one direction).

    Implements the agent protocol: select_action(obs, info) -> int.
    Direction is fixed at construction (default North=0).
    """

    def __init__(self, direction: int = 0) -> None:
        """Create a straight agent.

        Parameters
        ----------
        direction : int
            Action ID to take every step: 0=North, 1=South, 2=West, 3=East.
            Default 0 (North). Clamped to [0, NUM_ACTIONS-1].
        """
        self._action = max(0, min(direction, NUM_ACTIONS - 1))

    def select_action(self, obs: Dict[str, float], info: Dict[str, Any]) -> int:
        """Return the fixed direction action."""
        return self._action
