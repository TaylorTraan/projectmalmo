"""Random agent: no-learning baseline for comparison with learning algorithms.

This agent selects actions uniformly at random from the defined discrete
action space (0=North, 1=South, 2=West, 3=East) at every time step. It does
not use observations, memory, or learning. Use it to establish a baseline
representing behavior with no learning.
"""

import random
from typing import Any, Dict, Optional

# Number of discrete actions (must match env action space: N, S, W, E).
NUM_ACTIONS = 4


class RandomAgent:
    """Agent that selects actions uniformly at random from the discrete action space.

    Implements the agent protocol: select_action(obs, info) -> int.
    Does not implement observe; it is the canonical no-learning baseline for
    comparison with learning agents.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        """Create a random agent.

        Parameters
        ----------
        seed:
            Optional seed for reproducibility. If None, uses global RNG state.
        """
        self._rng = random.Random(seed)

    def select_action(self, obs: Dict[str, float], info: Dict[str, Any]) -> int:
        """Return a random action ID from 0 (North) to 3 (East)."""
        return self._rng.randint(0, NUM_ACTIONS - 1)
