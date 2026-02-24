"""Tabular Q-learning agent: learns action-value table via Bellman updates.

This agent uses epsilon-greedy exploration and updates Q-values at each step
using the standard Q-learning rule. It integrates with the training harness
via select_action and observe. Use it to test whether the environment
provides a meaningful learning signal.
"""

import random
from typing import Any, Dict, Optional, Tuple

# Number of discrete actions (must match env action space: N, S, W, E).
NUM_ACTIONS = 4


def _obs_to_state(obs: Dict[str, float]) -> Tuple[int, int]:
    """Discretize observation to grid state (x, z).

    Parameters
    ----------
    obs : dict
        Observation with keys "x", "z", "y" (agent position).

    Returns
    -------
    tuple of (int, int)
        Discretized (x, z) cell.

    Raises
    ------
    KeyError
        If obs is missing "x" or "z".
    """
    try:
        x = int(round(float(obs["x"])))
        z = int(round(float(obs["z"])))
    except KeyError as exc:
        raise KeyError(
            "Observation must contain 'x' and 'z' for tabular state. "
            "Missing: {}".format(exc)
        ) from exc
    return (x, z)


def _get_q(q_table: Dict[Tuple[int, int], Dict[int, float]], state: Tuple[int, int], action: int) -> float:
    """Return Q(s, a); 0.0 if unseen."""
    if state not in q_table:
        return 0.0
    return q_table[state].get(action, 0.0)


def _max_q(q_table: Dict[Tuple[int, int], Dict[int, float]], state: Tuple[int, int]) -> float:
    """Return max_a Q(s, a); 0.0 if state unseen."""
    if state not in q_table:
        return 0.0
    vals = q_table[state]
    if not vals:
        return 0.0
    return max(vals.values())


class TabularQLearningAgent:
    """Tabular Q-learning agent with epsilon-greedy exploration and Bellman updates.

    Implements the agent protocol: select_action(obs, info) -> int and
    observe(obs, action, reward, next_obs, done, info) for learning.
    """

    def __init__(
        self,
        learning_rate: float = 0.1,
        discount: float = 0.99,
        seed: Optional[int] = None,
        epsilon_schedule: str = "constant",
        epsilon: Optional[float] = None,
        epsilon_start: Optional[float] = None,
        epsilon_end: Optional[float] = None,
        epsilon_decay_episodes: Optional[int] = None,
    ) -> None:
        """Create a tabular Q-learning agent.

        Parameters
        ----------
        learning_rate : float
            Step size for Q-updates (alpha).
        discount : float
            Discount factor (gamma).
        seed : int or None
            Seed for RNG (exploration). None uses global state.
        epsilon_schedule : str
            "constant" or "linear_decay".
        epsilon : float or None
            Used when epsilon_schedule == "constant".
        epsilon_start : float or None
            Starting epsilon for linear_decay.
        epsilon_end : float or None
            Final epsilon for linear_decay.
        epsilon_decay_episodes : int or None
            Episodes over which epsilon decays linearly.
        """
        self._alpha = learning_rate
        self._gamma = discount
        self._rng = random.Random(seed)
        self._epsilon_schedule = epsilon_schedule
        self._epsilon = epsilon if epsilon is not None else 0.1
        self._epsilon_start = epsilon_start if epsilon_start is not None else 0.5
        self._epsilon_end = epsilon_end if epsilon_end is not None else 0.05
        self._epsilon_decay_episodes = epsilon_decay_episodes if epsilon_decay_episodes is not None else 150
        self._q_table = {}  # type: Dict[Tuple[int, int], Dict[int, float]]
        self._episode_count = 0

    def _current_epsilon(self) -> float:
        """Return epsilon for the current episode."""
        if self._epsilon_schedule == "constant":
            return self._epsilon
        if self._epsilon_schedule == "linear_decay":
            if self._episode_count >= self._epsilon_decay_episodes:
                return self._epsilon_end
            frac = self._episode_count / float(self._epsilon_decay_episodes)
            return self._epsilon_start + frac * (self._epsilon_end - self._epsilon_start)
        return self._epsilon

    def select_action(self, obs: Dict[str, float], info: Dict[str, Any]) -> int:
        """Return action 0-3 via epsilon-greedy policy over Q(s, a)."""
        state = _obs_to_state(obs)
        eps = self._current_epsilon()
        if self._rng.random() < eps:
            return self._rng.randint(0, NUM_ACTIONS - 1)
        best_q = float("-inf")
        best_actions = []
        for a in range(NUM_ACTIONS):
            q = _get_q(self._q_table, state, a)
            if q > best_q:
                best_q = q
                best_actions = [a]
            elif q == best_q:
                best_actions.append(a)
        return self._rng.choice(best_actions)

    def observe(
        self,
        obs: Dict[str, float],
        action: int,
        reward: float,
        next_obs: Dict[str, float],
        done: bool,
        info: Dict[str, Any],
    ) -> None:
        """Update Q(s, a) using Bellman rule."""
        state = _obs_to_state(obs)
        next_state = _obs_to_state(next_obs)
        if state not in self._q_table:
            self._q_table[state] = {}
        if action not in self._q_table[state]:
            self._q_table[state][action] = 0.0
        if done:
            target = reward
        else:
            target = reward + self._gamma * _max_q(self._q_table, next_state)
        td_error = target - self._q_table[state][action]
        self._q_table[state][action] += self._alpha * td_error
        if done:
            self._episode_count += 1
