"""Logging utilities for episode-level statistics (CSV/JSON) and run directories."""

import csv
import json
import os
from datetime import datetime

# EpisodeStats is defined in harness.loop; avoid circular import by duck-typing stats_list
# stats_list elements have: episode, total_reward, steps, success, termination_reason, seed


def _stats_to_dict(s):
    """Convert an EpisodeStats-like namedtuple to a dict for serialization."""
    return {
        "episode": s.episode,
        "total_reward": s.total_reward,
        "steps": s.steps,
        "success": s.success,
        "termination_reason": s.termination_reason if s.termination_reason is not None else "",
        "seed": s.seed if s.seed is not None else "",
    }


def save_episode_stats_csv(stats_list, filepath):
    """Write a list of EpisodeStats to a CSV file.

    Parameters
    ----------
    stats_list : list
        List of EpisodeStats (or objects with episode, total_reward, steps, success, termination_reason, seed).
    filepath : str
        Path to the output CSV file.
    """
    if not stats_list:
        return
    fieldnames = ["episode", "total_reward", "steps", "success", "termination_reason", "seed"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in stats_list:
            writer.writerow(_stats_to_dict(s))


def save_episode_stats_json(stats_list, filepath):
    """Write a list of EpisodeStats to a JSON file (list of dicts).

    Parameters
    ----------
    stats_list : list
        List of EpisodeStats (or objects with episode, total_reward, steps, success, termination_reason, seed).
    filepath : str
        Path to the output JSON file.
    """
    data = [_stats_to_dict(s) for s in stats_list]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def create_run_directory(config_name=None, seed=None):
    """Create a timestamped run directory under runs/ and return its path.

    Directory name format: runs/YYYYMMDD_HHMMSS_{config_name}_seed{seed}/
    If config_name or seed is None, that part is omitted or replaced with a placeholder.

    Parameters
    ----------
    config_name : str or None
        Optional config identifier (e.g. 'random_agent').
    seed : int or None
        Optional seed (e.g. 42).

    Returns
    -------
    str
        Path to the created directory (e.g. runs/20250212_143022_random_agent_seed42).
    """
    now = datetime.now()
    stamp = now.strftime("%Y%m%d_%H%M%S")
    parts = [stamp]
    if config_name is not None:
        parts.append(str(config_name))
    if seed is not None:
        parts.append("seed{}".format(seed))
    dirname = "_".join(parts)
    base = "runs"
    path = os.path.join(base, dirname)
    os.makedirs(path, exist_ok=True)
    return path
