"""Training harness: algorithm-agnostic episode loop and episode statistics.

Usage:

    from harness import run_episodes, EpisodeStats
    from harness.agents import RandomAgent

    env = MalmoGridEnv(...)
    stats = run_episodes(env, RandomAgent(), num_episodes=5, seed=42)
    for s in stats:
        print(s.episode, s.total_reward, s.steps, s.success, s.termination_reason)

Agent protocol:
- Required: select_action(obs: dict, info: dict) -> int
- Optional: observe(obs, action, reward, next_obs, done, info) -> None
"""

from harness.agent_protocol import has_observe
from harness.logging import (
    create_run_directory,
    save_episode_stats_csv,
    save_episode_stats_json,
)
from harness.loop import EpisodeStats, run_episodes

__all__ = [
    "EpisodeStats",
    "create_run_directory",
    "has_observe",
    "run_episodes",
    "save_episode_stats_csv",
    "save_episode_stats_json",
]
