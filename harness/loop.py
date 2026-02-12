"""Core training loop for running episodes with any agent."""

from collections import namedtuple
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from env.malmo_env import MalmoGridEnv


EpisodeStats = namedtuple(
    "EpisodeStats",
    ["episode", "total_reward", "steps", "success", "termination_reason", "seed"],
)
EpisodeStats.__doc__ = "Episode-level statistics recorded by run_episodes."


def run_episodes(
    env: "MalmoGridEnv",
    agent: Any,
    num_episodes: int,
    seed: Optional[int] = None,
) -> List[EpisodeStats]:
    """Run episodes with the given agent and record per-episode statistics.

    Parameters
    ----------
    env:
        MalmoGridEnv instance (must support reset(seed) and step(action)).
    agent:
        Object with select_action(obs, info) -> int. Optionally has
        observe(obs, action, reward, next_obs, done, info) for learning.
    num_episodes:
        Number of episodes to run.
    seed:
        Optional seed passed to env.reset(seed=seed).

    Returns
    -------
    List of EpisodeStats, one per episode.
    """
    agent_observe = getattr(agent, "observe", None)
    use_observe = agent_observe is not None and callable(agent_observe)

    stats_list = []

    for episode in range(num_episodes):
        obs = env.reset(seed=seed)
        done = False
        total_reward = 0.0
        step_count = 0
        info = {}
        termination_reason = None

        while not done:
            action = agent.select_action(obs, info)
            next_obs, reward, done, info = env.step(action)
            total_reward += reward
            step_count += 1
            termination_reason = info.get("termination_reason")

            if use_observe:
                agent_observe(obs, action, reward, next_obs, done, info)

            obs = next_obs

        success = (
            1
            if termination_reason == "success_diamond_picked_up"
            else 0
        )
        stats_list.append(
            EpisodeStats(
                episode=episode,
                total_reward=total_reward,
                steps=step_count,
                success=success,
                termination_reason=termination_reason,
                seed=seed,
            )
        )

    return stats_list
