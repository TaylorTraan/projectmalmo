"""Lightweight smoke test for MalmoGridEnv.

This script:
- Creates a MalmoGridEnv using the mission at env/mission.xml.
- Runs one or more episodes with random actions.
- Prints total reward and termination reason per episode.

Usage (from repo root, with venv active and Malmo client running):

    python scripts/smoke_test_env.py --episodes 1
"""

import argparse
import random
import sys
from pathlib import Path

from env.malmo_env import MalmoGridEnv


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

    for episode in range(args.episodes):
        print("\n[INFO] Starting episode {}".format(episode))
        try:
            obs = env.reset()
        except Exception as exc:  # pragma: no cover - runtime-specific
            print("[ERROR] reset() failed: {}".format(exc), file=sys.stderr)
            return 1

        print("[INFO] Initial observation: {}".format(obs))

        done = False
        total_reward = 0.0
        last_info = {}

        step = 0
        while not done and step < args.max_steps:
            action = random.randint(0, 3)  # MOVE_NORTH, MOVE_SOUTH, MOVE_WEST, MOVE_EAST
            try:
                obs, reward, done, info = env.step(action)
            except Exception as exc:  # pragma: no cover - runtime-specific
                print("[ERROR] step() failed at step {}: {}".format(step, exc), file=sys.stderr)
                return 1

            total_reward += reward
            last_info = info
            step += 1

            # Keep per-step logging minimal; comment out if noisy.
            print(
                "[STEP {}] action={} obs={} reward={} done={} reason={}".format(
                    step, action, obs, reward, done, info.get("termination_reason")
                )
            )

        term_reason = last_info.get("termination_reason")
        diamond_count = last_info.get("diamond_count")
        position = last_info.get("position")

        print(
            "[EPISODE SUMMARY] episode={} total_reward={} termination_reason={} position={} diamond_count={}".format(
                episode, total_reward, term_reason, position, diamond_count
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

