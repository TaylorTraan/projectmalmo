"""Minimal Project Malmo grid environment wrapper.

This module defines `MalmoGridEnv`, a small Gym-like environment for a
discrete grid platform task where the agent must pick up a diamond
without falling off.

The wrapper isolates all direct Malmo SDK usage and exposes a simple
Python API:

- `reset(seed: int | None = None) -> dict`
- `step(action_id: int) -> tuple[dict, float, bool, dict]`

This implementation intentionally aims to be:
- Minimal - only the features needed for CS175 experiments.
- Interpretable - clear termination reasons and reward logic.
- Robust - handles missing observations without crashing.

Dependencies:
- MalmoPython (from Project Malmo)
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

try:
    import MalmoPython  # type: ignore[import]
except ImportError as exc:  # pragma: no cover - import path depends on local install
    raise ImportError(
        "MalmoPython could not be imported. "
        "Make sure Project Malmo is installed and available on PYTHONPATH."
    ) from exc


Termination = Tuple[bool, Optional[str]]


@dataclass
class Position:
    """Simple container for agent position."""

    x: int
    z: int
    y: float

    def as_dict(self) -> Dict[str, float]:
        return {"x": self.x, "z": self.z, "y": self.y}


class MalmoGridEnv:
    """Minimal grid-world wrapper around a Malmo mission.

    Parameters
    ----------
    mission_xml_path:
        Path to the mission XML file.
    max_steps:
        Maximum number of environment steps per episode.
    move_ticks:
        Number of ticks to apply each movement command before stopping.
    platform_y:
        Y-level of the platform. Falling below `platform_y - 1` is treated
        as falling off. This may need adjustment for different missions.
    timeout:
        Optional wall-clock timeout (in seconds) for mission start waits.
        If None, a reasonable default is used.
    seed:
        Optional seed for experiment bookkeeping. Currently passed through
        to `_start_mission` but not all missions support seeding cleanly.
    """

    # Action IDs for v0
    MOVE_NORTH = 0
    MOVE_SOUTH = 1
    MOVE_WEST = 2
    MOVE_EAST = 3

    def __init__(
        self,
        mission_xml_path: str,
        max_steps: int = 200,
        move_ticks: int = 4,
        platform_y: float = 4.0,
        timeout: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> None:
        self.mission_xml_path = mission_xml_path
        self.max_steps = max_steps
        self.move_ticks = move_ticks
        self.platform_y = platform_y
        self.timeout = timeout or 60.0  # seconds
        self._seed = seed

        self._agent_host = MalmoPython.AgentHost()
        self._client_pool = MalmoPython.ClientPool()
        # Default to a single local client on the standard Malmo port.
        self._client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10000))

        self._mission_spec: Optional[MalmoPython.MissionSpec] = None
        self._mission_record_spec: Optional[MalmoPython.MissionRecordSpec] = None

        self._step_count = 0
        self._prev_diamond_count = 0
        self._last_obs: Optional[Position] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self, seed: Optional[int] = None) -> Dict[str, float]:
        """Start a new Malmo mission and return the initial observation.

        The `seed` is currently stored and forwarded into `_start_mission`,
        but not all mission XMLs expose a seeding mechanism. This is here
        primarily for experiment bookkeeping and future extension.
        """
        if seed is not None:
            self._seed = seed

        self._start_mission(self._seed)
        self._wait_for_mission_start()

        self._step_count = 0
        self._prev_diamond_count = 0
        self._last_obs = None

        # Wait for the first valid observation so that we don't return a
        # None position and explode with an attribute error. This also
        # mirrors the smoke-test guidance that the mission should be
        # fully started before training begins.
        start_time = time.time()
        position: Optional[Position] = None
        while True:
            world_state = self._agent_host.getWorldState()
            obs_json = self._get_obs_json(world_state)
            position = self._encode_obs(obs_json)

            if position is not None:
                break

            if not world_state.is_mission_running:
                raise RuntimeError("Mission ended before any observation was received.")

            if time.time() - start_time > self.timeout:
                raise RuntimeError("Timed out waiting for the first observation after mission start.")

            time.sleep(0.1)

        self._last_obs = position

        return position.as_dict()

    def step(self, action_id: int) -> Tuple[Dict[str, float], float, bool, Dict]:
        """Apply an action and advance the environment by a fixed number of ticks."""
        if self._mission_spec is None:
            raise RuntimeError("Cannot call step() before reset() has been called.")

        self._step_count += 1

        # Map discrete action to Malmo movement commands.
        action_cmds = self._action_id_to_commands(action_id)

        # Send movement command(s) for `move_ticks`, then stop.
        for cmd in action_cmds:
            self._send_command(cmd)
        world_state = self._wait_ticks(self.move_ticks)
        # Explicitly stop motion to avoid continuous drift.
        self._send_command("move 0")
        self._send_command("strafe 0")

        obs_json = self._get_obs_json(world_state)
        position = self._encode_obs(obs_json)

        diamond_count = self._get_diamond_count(obs_json) if obs_json is not None else 0
        diamond_increase = diamond_count > self._prev_diamond_count
        if diamond_increase:
            self._prev_diamond_count = diamond_count

        done, reason = self._check_done(
            obs_json=obs_json,
            diamond_increase=diamond_increase,
            world_state=world_state,
        )
        # Handle the "no observation yet" case explicitly when the mission
        # is still running: reuse last observation, zero reward, not done,
        # and mark the info dict accordingly.
        if obs_json is None and world_state.is_mission_running and not done:
            reason = "no_observation_yet"

        reward = self._compute_reward(done, reason)

        # Fallback for missing observations: reuse the last valid one.
        if position is None and self._last_obs is not None:
            position = self._last_obs
        elif position is not None:
            self._last_obs = position

        info = {
            "termination_reason": reason,
            "diamond_count": diamond_count,
            "position": (position or self._last_obs).as_dict() if (position or self._last_obs) else None,
            "step_index": self._step_count,
        }

        # By construction, reward is 0.0 and done is False when reason is
        # "no_observation_yet", so callers can safely ignore those steps if
        # desired.

        return (position.as_dict() if position else self._last_obs.as_dict()), reward, done, info

    # ------------------------------------------------------------------
    # Internal helpers: mission lifecycle and ticking
    # ------------------------------------------------------------------

    def _start_mission(self, seed: Optional[int]) -> None:
        """Load mission XML, construct MissionSpec, and start the mission.

        Seeding:
            Some missions may expose a seeding mechanism via XML.
            For now we just store `seed` and leave integration with
            specific mission templates as a TODO.
        """
        with open(self.mission_xml_path, "r", encoding="utf-8") as f:
            mission_xml = f.read()

        # TODO: If the mission template supports a seed placeholder,
        # apply it here (e.g., mission_xml.format(seed=seed)).

        self._mission_spec = MalmoPython.MissionSpec(mission_xml, True)
        # Request full stats so we can read inventory/position.
        self._mission_spec.requestVideo(320, 240)  # harmless even if unused
        self._mission_spec.timeLimitInSeconds(float(self.max_steps * 0.1))

        self._mission_record_spec = MalmoPython.MissionRecordSpec()

        experiment_id = str(uuid.uuid4())
        max_retries = 3
        for retry in range(max_retries):
            try:
                self._agent_host.startMission(
                    self._mission_spec,
                    self._client_pool,
                    self._mission_record_spec,
                    0,
                    experiment_id,
                )
                break
            except RuntimeError as exc:
                if retry == max_retries - 1:
                    raise RuntimeError(f"Error starting mission: {exc}") from exc
                time.sleep(2.0)

    def _wait_for_mission_start(self) -> None:
        """Block until the mission has begun or timeout is reached."""
        start_time = time.time()
        world_state = self._agent_host.getWorldState()
        while not world_state.has_mission_begun:
            if time.time() - start_time > self.timeout:
                raise RuntimeError("Timed out waiting for mission to begin.")
            time.sleep(0.1)
            world_state = self._agent_host.getWorldState()
            if world_state.errors:
                # Collect errors for easier debugging.
                messages = ", ".join(e.text for e in world_state.errors)
                raise RuntimeError(f"Mission failed to start due to errors: {messages}")

    def _send_command(self, cmd: str) -> None:
        """Thin wrapper around AgentHost.sendCommand."""
        self._agent_host.sendCommand(cmd)

    def _wait_ticks(self, n: int) -> MalmoPython.WorldState:
        """Wait approximately `n` ticks, polling world_state."""
        # Tick duration is mission-specific; we use a small sleep and
        # just poll a fixed number of times as a minimal approach.
        world_state = self._agent_host.getWorldState()
        for _ in range(n):
            time.sleep(0.1)
            world_state = self._agent_host.getWorldState()
        return world_state

    # ------------------------------------------------------------------
    # Internal helpers: observations and termination
    # ------------------------------------------------------------------

    def _get_obs_json(
        self, world_state: Optional[MalmoPython.WorldState] = None
    ) -> Optional[Dict]:
        """Return the latest observation JSON dict, or None if missing.

        Handles several edge cases:
        - If no observations yet but mission is running: returns None.
        - If mission ended and no observations: returns None; caller
          should check world_state flags and termination reason.
        """
        if world_state is None:
            world_state = self._agent_host.getWorldState()

        if not world_state.observations:
            # No new observation yet.
            return None

        latest = world_state.observations[-1]
        try:
            return json.loads(latest.text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Failed to decode Malmo observation JSON: {exc}") from exc

    def _encode_obs(self, obs_json: Optional[Dict]) -> Optional[Position]:
        """Encode raw observation JSON into a Position.

        Assumes standard Malmo keys:
        - 'XPos', 'YPos', 'ZPos'

        If these are missing, this function raises a RuntimeError so
        that environment issues are caught clearly rather than silently
        producing invalid observations.
        """
        if obs_json is None:
            return None

        try:
            x = int(round(float(obs_json["XPos"])))
            y = float(obs_json["YPos"])
            z = int(round(float(obs_json["ZPos"])))
        except KeyError as exc:
            raise RuntimeError(
                f"Expected position keys 'XPos', 'YPos', 'ZPos' in observation, "
                f"but they were missing: {exc}"
            ) from exc

        return Position(x=x, z=z, y=y)

    def _get_diamond_count(self, obs_json: Dict) -> int:
        """Scan inventory slots and count the number of diamonds.

        Requires that the mission enables `ObservationFromFullStats` or
        similar so that inventory slots are exposed in the observation.
        Keys typically look like:
        - 'InventorySlot_0_item' = 'diamond'
        - 'InventorySlot_0_size' = 1
        """
        if obs_json is None:
            return 0

        total = 0
        for key, value in obs_json.items():
            if not key.startswith("InventorySlot_") or not key.endswith("_item"):
                continue
            slot_prefix = key[:-5]  # strip '_item'
            if value == "diamond":
                size_key = f"{slot_prefix}_size"
                size = int(obs_json.get(size_key, 1))
                total += size
        return total

    def _check_done(
        self,
        obs_json: Optional[Dict],
        diamond_increase: bool,
        world_state: MalmoPython.WorldState,
    ) -> Termination:
        """Return (done, termination_reason) based on env rules."""
        # Success: diamond picked up.
        if diamond_increase:
            return True, "success_diamond_picked_up"

        # Timeout on step count.
        if self._step_count >= self.max_steps:
            return True, "timeout_max_steps_reached"

        # Fall detection based on y-coordinate.
        if obs_json is not None:
            try:
                y = float(obs_json["YPos"])
                if y < self.platform_y - 1.0:
                    return True, "failure_fell_off_platform"
            except KeyError:
                # If YPos is missing we cannot make a fall decision here.
                pass

        # Mission ended unexpectedly before other conditions.
        if not world_state.is_mission_running:
            return True, "malmo_mission_ended_early"

        return False, None

    def _compute_reward(self, done: bool, reason: Optional[str]) -> float:
        """Compute scalar reward based on termination reason."""
        if not done:
            return 0.0

        if reason == "success_diamond_picked_up":
            return 1.0
        if reason == "failure_fell_off_platform":
            return -1.0

        # Timeout or unexpected mission end: neutral reward.
        return 0.0


