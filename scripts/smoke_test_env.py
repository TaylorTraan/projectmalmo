"""Lightweight smoke test for MalmoGridEnv.

This script:
- Creates a MalmoGridEnv using the mission at env/mission.xml.
- Runs one or more episodes with random actions via the training harness.
- Prints total reward and termination reason per episode.

Usage (from repo root, with venv active and Malmo client running):

    python scripts/smoke_test_env.py --episodes 1
"""

import argparse
import sys
from pathlib import Path

from env.malmo_env import MalmoGridEnv
from harness import run_episodes
from harness.agents import RandomAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test for MalmoGridEnv.")
    parser.add_argument(
        "--mission",
        type=str,
        default="env/mission.xml",
        help="Path to mission XML file (default: env/mission.xml).",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=1,
        help="Number of episodes to run (default: 1).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=200,
        help="Maximum steps per episode (default: 200).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    mission_path = Path(args.mission)
    if not mission_path.is_file():
        print("[ERROR] Mission file not found: {}".format(mission_path), file=sys.stderr)
        return 1

    print("[INFO] Using mission: {}".format(mission_path))

    try:
        env = MalmoGridEnv(mission_xml_path=str(mission_path), max_steps=args.max_steps)
    except ImportError as exc:
        print("[ERROR] Failed to import MalmoPython: {}".format(exc), file=sys.stderr)
        print("Hint: ensure Project Malmo is installed and accessible in this venv.")
        return 1
    except Exception as exc:  # pragma: no cover - smoke test entrypoint
        print("[ERROR] Failed to construct MalmoGridEnv: {}".format(exc), file=sys.stderr)
        return 1

    agent = RandomAgent(seed=args.seed)

    try:
        stats_list = run_episodes(
            env=env,
            agent=agent,
            num_episodes=args.episodes,
            seed=args.seed,
        )
    except Exception as exc:  # pragma: no cover - runtime-specific
        print("[ERROR] run_episodes failed: {}".format(exc), file=sys.stderr)
        return 1

    for s in stats_list:
        print(
            "\n[EPISODE SUMMARY] episode={} total_reward={} steps={} success={} termination_reason={} seed={}".format(
                s.episode, s.total_reward, s.steps, s.success, s.termination_reason, s.seed
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
