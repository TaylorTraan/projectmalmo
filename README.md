---

## Project Overview

This project investigates how reinforcement learning (RL) systems behave under different design choices, rather than focusing on achieving the best possible task performance. We use **Project Malmo** as a simplified, controlled Minecraft-based environment where an agent must navigate a small platform and collect a diamond without falling off.

The environment serves as a *testbed* for studying learning dynamics. Task success is not the primary goal; instead, it provides a concrete setting in which learning behavior can be observed, measured, and explained.

---

## High-Level Research Goal

The central goal of this project is to understand **how and why learning changes** when we modify key reinforcement learning design decisions. We are interested in questions such as:

* What information does the agent need to learn effectively?
* How does reward feedback shape learning speed and stability?
* Under what conditions does learning fail, and why?

By answering these questions, we emphasize reinforcement learning as an experimental and analytical discipline rather than a black-box optimization problem.

---

## Learning Algorithms as Objects of Study

Rather than comparing many complex algorithms, we begin with simple and interpretable baselines, including a random policy and tabular Q-learning. These baselines allow us to clearly distinguish *no learning* from *learning* and to verify that the environment provides a meaningful learning signal.

More complex methods are introduced only when they help answer new research questions, such as how richer representations or function approximation affect learning behavior.

---

## Experimental Design and Methodology

Our experiments are structured to isolate variables. After calibrating baseline behavior, we lock experimental configurations and vary **one factor at a time**, such as:

* reward structure (sparse vs. shaped),
* state representation (minimal vs. richer observations),
* or learning algorithm.

All experiments are run with consistent environments, episode limits, and random seeds to ensure fair comparisons. We evaluate learning using metrics such as episode reward, success rate, steps per episode, and termination causes.

---

## Analysis Focus

Evaluation focuses on **learning behavior**, not just final outcomes. We analyze:

* learning curves and convergence patterns,
* stability and variance across runs,
* common failure modes (e.g., falling off the platform),
* and how design choices influence these behaviors.

Even cases where the agent fails to learn are treated as meaningful results that reveal limitations or tradeoffs in the chosen design.

---

## Project Philosophy

The success of this project is measured by **insight and explanation**, not by building the strongest possible agent. Our objective is to demonstrate understanding through careful experimentation, comparison, and interpretation, aligning directly with the goals of CS175.

---

## Minimal Malmo Environment Wrapper

We provide a small Gym-like wrapper around a Project Malmo mission for a discrete grid platform task where the agent must pick up a diamond without falling off.

- **Wrapper class**: `MalmoGridEnv` in `env/malmo_env.py`
- **Mission XML**: `env/mission.xml` (simple platform; includes TODOs where course-specific diamond placement can be added)
- **Smoke test script**: `scripts/smoke_test_env.py`

### Example usage

From the repo root, with your virtual environment active and the Malmo Minecraft client running:

```python
from env.malmo_env import MalmoGridEnv

env = MalmoGridEnv(mission_xml_path="env/mission.xml", max_steps=200)

obs = env.reset()  # initial observation: {"x": int, "z": int, "y": float}
done = False
total_reward = 0.0

while not done:
    # v0 discrete actions: 0=N, 1=S, 2=W, 3=E
    action = 0  # e.g., always move north; replace with a policy / random
    obs, reward, done, info = env.step(action)
    total_reward += reward

print("Episode finished.")
print("Total reward:", total_reward)
print("Termination reason:", info.get("termination_reason"))
print("Final position:", info.get("position"))
print("Diamond count:", info.get("diamond_count"))
```

To run the full smoke test (random policy, small number of episodes):

```bash
python scripts/smoke_test_env.py --episodes 1
```

For detailed setup instructions (Malmo install, virtualenv, troubleshooting), see `docs/MALMO_SETUP.md`.

