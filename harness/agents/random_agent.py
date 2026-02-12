"""Random agent for smoke-testing and as a template for new agents."""

import random
from typing import Any, Dict, Optional


class RandomAgent:
    """Agent that selects actions uniformly at random from 0-3.

    Implements the agent protocol: select_action(obs, info) -> int.
    Does not implement observe; suitable for non-learning baselines.
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
        return self._rng.randint(0, 3)
