"""Run the random policy baseline for a fixed number of episodes and log results.

Uses the shared training harness and writes episode-level metrics to a
timestamped run directory under runs/. A copy of the config is saved in the
run directory for reproducibility.

Usage (from repo root):

    python3 scripts/run_random_baseline.py --config configs/random_baseline.json
    python3 scripts/run_random_baseline.py --config configs/random_baseline.json --num-episodes 20 --seed 0
"""

import sys
if sys.version_info < (3, 5):
    sys.exit("This script requires Python 3.5 or later. Run with: python3 scripts/run_random_baseline.py ...")

import argparse
import json
import os
import sys
from pathlib import Path

# Repo root is parent of scripts/
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from env.malmo_env import MalmoGridEnv
from harness import (
    create_run_directory,
    run_episodes,
    save_episode_stats_csv,
    save_episode_stats_json,
)
from harness.agents import RandomAgent


DEFAULT_CONFIG_PATH = _REPO_ROOT / "configs" / "random_baseline.json"


def load_config(path: Path) -> dict:
    """Load JSON config from path. Uses str(path) for Python 3.5 open() compatibility."""
    with open(str(path), encoding="utf-8") as f:
        return json.load(f)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run random baseline and log episode stats to runs/.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to experiment config JSON (default: configs/random_baseline.json).",
    )
    parser.add_argument(
        "--num-episodes",
        type=int,
        default=None,
        metavar="N",
        help="Override num_episodes from config.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="S",
        help="Override seed from config.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.config.is_file():
        print("[ERROR] Config file not found: {}".format(args.config), file=sys.stderr)
        return 1

    config = load_config(args.config)
    if args.num_episodes is not None:
        config["num_episodes"] = args.num_episodes
    if args.seed is not None:
        config["seed"] = args.seed

    config_name = config.get("config_name", "random_baseline")
    num_episodes = config["num_episodes"]
    seed = config["seed"]
    max_steps = config["max_steps"]
    reward_scheme = config.get("reward_scheme", "sparse_v0")
    reward_params = config.get("reward_params", {})
    log_reward_components = bool(config.get("log_reward_components", False))
    mission_path = Path(config["mission_xml_path"])
    if not mission_path.is_absolute():
        mission_path = _REPO_ROOT / mission_path

    if not mission_path.is_file():
        print("[ERROR] Mission file not found: {}".format(mission_path), file=sys.stderr)
        return 1

    print("[INFO] config_name={} num_episodes={} seed={} max_steps={}".format(
        config_name, num_episodes, seed, max_steps,
    ))
    print("[INFO] reward_scheme={} log_reward_components={}".format(
        reward_scheme, log_reward_components,
    ))

    try:
        env = MalmoGridEnv(
            mission_xml_path=str(mission_path),
            max_steps=max_steps,
            reward_scheme=reward_scheme,
            reward_params=reward_params,
            log_reward_components=log_reward_components,
        )
    except ImportError as exc:
        print("[ERROR] MalmoPython not available: {}".format(exc), file=sys.stderr)
        return 1

    agent = RandomAgent(seed=seed)
    run_dir = create_run_directory(config_name=config_name, seed=seed)

    try:
        stats_list = run_episodes(
            env=env,
            agent=agent,
            num_episodes=num_episodes,
            seed=seed,
        )
    except Exception as exc:
        print("[ERROR] run_episodes failed: {}".format(exc), file=sys.stderr)
        return 1

    csv_path = os.path.join(run_dir, "episodes.csv")
    json_path = os.path.join(run_dir, "episodes.json")
    config_copy_path = os.path.join(run_dir, "config.json")

    save_episode_stats_csv(stats_list, csv_path)
    save_episode_stats_json(stats_list, json_path)
    with open(config_copy_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print("[INFO] Run directory: {}".format(run_dir))
    print("[INFO] Wrote episodes.csv, episodes.json, config.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
