"""Summarize a training run: compute episode-level statistics and optionally plot.

Reads episodes.json (or episodes.csv) from a run directory, computes mean/std
of total_reward and steps, success rate, and termination_reason counts, then
writes summary.json and summary.txt into the same directory. If matplotlib is
available (optional; not imported at top level), also writes baseline_plots.png
for comparison with learning agents. Install matplotlib if you want the plot.

Usage (from repo root):

    PYTHONPATH="/home/malmo/MalmoPlatform/scripts/python-wheel/backwards-compatible-imports:$PYTHONPATH" python3 scripts/summarize_run.py runs/20260213_051253_random_baseline_seed42
"""

import argparse
import csv
import json
import sys
from pathlib import Path

# Repo root is parent of scripts/
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def load_episodes_json(path: Path) -> list:
    """Load episode records from JSON. Uses str(path) for Python 3.5 open() compatibility."""
    with open(str(path), encoding="utf-8") as f:
        return json.load(f)


def load_episodes_csv(path: Path) -> list:
    """Load episode records from CSV (normalize to same dict shape as JSON). Uses str(path) for Python 3.5."""
    rows = []
    with open(str(path), newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "episode": int(row["episode"]),
                "total_reward": float(row["total_reward"]),
                "steps": int(row["steps"]),
                "success": int(row["success"]),
                "termination_reason": row["termination_reason"] or "",
                "seed": row["seed"] or "",
            })
    return rows


def compute_summary(episodes: list) -> dict:
    """Compute summary statistics from a list of episode dicts."""
    if not episodes:
        return {
            "num_episodes": 0,
            "total_reward_mean": None,
            "total_reward_std": None,
            "steps_mean": None,
            "steps_std": None,
            "success_rate_pct": None,
            "termination_reason_counts": {},
        }

    n = len(episodes)
    rewards = [e["total_reward"] for e in episodes]
    steps_list = [e["steps"] for e in episodes]
    successes = [e["success"] for e in episodes]

    mean_reward = sum(rewards) / n
    variance_reward = sum((r - mean_reward) ** 2 for r in rewards) / n if n > 1 else 0.0
    std_reward = variance_reward ** 0.5

    mean_steps = sum(steps_list) / n
    variance_steps = sum((s - mean_steps) ** 2 for s in steps_list) / n if n > 1 else 0.0
    std_steps = variance_steps ** 0.5

    success_rate_pct = 100.0 * sum(successes) / n

    reason_counts = {}
    for e in episodes:
        r = e.get("termination_reason") or ""
        reason_counts[r] = reason_counts.get(r, 0) + 1

    return {
        "num_episodes": n,
        "total_reward_mean": mean_reward,
        "total_reward_std": std_reward,
        "steps_mean": mean_steps,
        "steps_std": std_steps,
        "success_rate_pct": success_rate_pct,
        "termination_reason_counts": reason_counts,
    }


def write_summary_txt(summary: dict, path: Path) -> None:
    """Write human-readable summary to a text file."""
    lines = [
        "Summary statistics",
        "==================",
        "num_episodes: {}".format(summary["num_episodes"]),
        "total_reward: mean = {:.4f}, std = {:.4f}".format(
            summary["total_reward_mean"] or 0,
            summary["total_reward_std"] or 0,
        ),
        "steps: mean = {:.2f}, std = {:.2f}".format(
            summary["steps_mean"] or 0,
            summary["steps_std"] or 0,
        ),
        "success_rate_pct: {:.2f}".format(summary["success_rate_pct"] or 0),
        "",
        "termination_reason counts:",
    ]
    for reason, count in sorted(summary["termination_reason_counts"].items(), key=lambda x: -x[1]):
        lines.append("  {}: {}".format(reason or "(empty)", count))
    with open(str(path), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def try_plot(run_dir: Path, episodes: list) -> None:
    """If matplotlib is available, save reward-per-episode and reward histogram.

    matplotlib is imported here (not at top level) so the script runs without it;
    install matplotlib to generate baseline_plots.png.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[INFO] matplotlib not found; skipping plots. Install matplotlib to generate baseline_plots.png.")
        return

    if not episodes:
        return

    rewards = [e["total_reward"] for e in episodes]
    episodes_idx = [e["episode"] for e in episodes]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.plot(episodes_idx, rewards, "b.", markersize=4, alpha=0.7)
    ax1.set_xlabel("Episode")
    ax1.set_ylabel("Total reward")
    ax1.set_title("Total reward per episode")
    ax1.grid(True, alpha=0.3)

    ax2.hist(rewards, bins=min(20, max(1, len(set(rewards)))), edgecolor="black", alpha=0.7)
    ax2.set_xlabel("Total reward")
    ax2.set_ylabel("Count")
    ax2.set_title("Distribution of total reward")

    plt.tight_layout()
    plot_path = run_dir / "baseline_plots.png"
    plt.savefig(str(plot_path), dpi=100)
    plt.close()
    print("[INFO] Wrote {}".format(plot_path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize a run directory and optionally generate plots.",
    )
    parser.add_argument(
        "run_dir",
        type=Path,
        help="Path to run directory (e.g. runs/20250212_143022_random_baseline_seed42).",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip generating plots even if matplotlib is available.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.resolve()

    if not run_dir.is_dir():
        print("[ERROR] Run directory not found: {}".format(run_dir), file=sys.stderr)
        return 1

    json_path = run_dir / "episodes.json"
    csv_path = run_dir / "episodes.csv"

    if json_path.is_file():
        episodes = load_episodes_json(json_path)
    elif csv_path.is_file():
        episodes = load_episodes_csv(csv_path)
    else:
        print("[ERROR] No episodes.json or episodes.csv in {}".format(run_dir), file=sys.stderr)
        return 1

    summary = compute_summary(episodes)

    summary_json_path = run_dir / "summary.json"
    summary_txt_path = run_dir / "summary.txt"

    with open(str(summary_json_path), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    write_summary_txt(summary, summary_txt_path)

    print("[INFO] Wrote {} and {}".format(summary_json_path, summary_txt_path))
    print(summary_txt_path.read_text())

    if not args.no_plot:
        try_plot(run_dir, episodes)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
