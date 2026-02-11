## Malmo Setup (Docker) for CS175

This guide uses **Docker only** to run Project Malmo. The container provides a Linux desktop (noVNC), Minecraft with the Malmo mod, Python/Malmo bindings, and Jupyter. No native macOS install of Malmo or Java is required.

The goal is **reproducibility**: everyone can use the same image and run command to get the same behavior.

---

## 1. Prerequisites

- **Docker** installed on your machine (Docker Desktop on Mac/Windows, or Docker Engine on Linux).
- On **Apple Silicon (M1/M2/M3) Macs**, use `--platform=linux/amd64` so the image runs correctly (the commands below include it).

---

## 2. Pull and run the Malmo container

From a terminal, pull the image (one-time or when you want to update):

```bash
docker pull --platform=linux/amd64 andkram/malmo
```

From your **project repo directory** (the one that contains `env/`, `scripts/`, etc.), start the container:

```bash
docker run -it --rm \
  --platform=linux/amd64 \
  -p 5901:5901 \
  -p 6901:6901 \
  -p 10000:10000 \
  -p 8888:8888 \
  -v "$PWD":/workspace \
  andkram/malmo
```

**What the flags do:**

| Flag | Purpose |
|------|--------|
| `--platform=linux/amd64` | Use x86 image (required on Apple Silicon Macs). |
| `-p 6901:6901` | noVNC — view the desktop and Minecraft in your browser. |
| `-p 5901:5901` | Raw VNC (optional; noVNC is enough for most use). |
| `-p 8888:8888` | Jupyter Notebook — run Python agent code. |
| `-p 10000:10000` | Malmo — Python connects to Minecraft on this port. |
| `-v "$PWD":/workspace` | Mount your project into the container so you can edit code locally and run it inside. |

When the container starts, it launches the desktop, VNC/noVNC, Minecraft with the Malmo mod, and Jupyter. No manual startup steps are needed.

---

## 3. Access noVNC and Jupyter

- **Minecraft (desktop UI)**  
  In your browser, open: **http://127.0.0.1:6901**  
  When prompted for a password, try: **`vncpassword`** or **`malmo`** (image-dependent).

- **Jupyter Notebook**  
  Open the URL printed in the container logs (it includes a token), e.g.:  
  **http://127.0.0.1:8888/?token=...**

You run Python agent code in Jupyter; Minecraft runs visually in the noVNC window. When you start a mission from Python, the agent connects to Minecraft on port 10000.

---

## 4. Example usage from Jupyter (env wrapper + training harness)

1. In Jupyter, go to `/workspace` (your mounted project). Open **notebooks/run_malmo_agent.ipynb**.
2. Run the first cell to add `/workspace` to `sys.path` and set `mission_path` to `/workspace/env/mission.xml`.
3. Run the remaining cells to create `MalmoGridEnv` and run a few episodes with a minimal training loop (random actions). This demonstrates the standardized `reset`/`step` interface.

The first time you call `env.reset()`, a mission starts and Python connects to Minecraft on port 10000; the game will load in the noVNC window.

---

## 5. Running the smoke test (inside the container)

If you open a **shell inside the running container** (e.g. from Jupyter: New → Terminal, or `docker exec` from the host), you can run the project smoke test from the workspace:

```bash
cd /workspace
python scripts/smoke_test_env.py --episodes 1
```

You should see the script create `MalmoGridEnv`, run one episode (e.g. with random actions), and print a termination reason. Minecraft must be running in the noVNC desktop for the mission to start.

---

## 6. Common issues & fixes

### “Nothing is listening on port 10000”

This is **normal until a mission is started**. Minecraft listens on port 10000 only after it has loaded and a mission is launched. Run the “Run episodes” cell in the notebook; the first `env.reset()` starts the mission and establishes the connection.

### Timeout waiting for mission to begin

- Ensure Minecraft is running in the noVNC window (http://127.0.0.1:6901). If the desktop or Minecraft didn’t start, try restarting the container.
- Don’t start a second mission while one is already active; close extra Minecraft windows if needed.

### “Mission ended before any observation was received”

This means the mission started from Python’s side but the game closed or never sent observations. **Do this first:**

1. Open noVNC in your browser: http://127.0.0.1:6901 and log in (password often `vncpassword` or `malmo`).
2. In the desktop, make sure **Minecraft is running** and has **fully loaded** (main menu or world visible, Malmo mod loaded). If it isn’t running, start it from the desktop (e.g. double‑click the Minecraft launcher or icon).
3. Wait until Minecraft is idle and ready (no “Loading…” or crash).
4. From the terminal (with `PYTHONPATH` set as before), run the smoke test again:  
   `python3 -m scripts.smoke_test_env --episodes 1`

If Minecraft was already running, try closing any in‑game world, returning to the main menu, then running the script again. Only one mission can use the client at a time.

### Can’t log in to noVNC

Try the VNC password **`vncpassword`** or **`malmo`** (depends on the image).

### Import errors for `env` in Jupyter

Run the first notebook cell that sets `workspace` and does `sys.path.insert(0, workspace)`. Ensure your project (with `env/`) is the directory mounted at `/workspace` when you started the container (i.e. you ran `docker run ... -v "$PWD":/workspace` from the repo root).

---

## 7. Reproducibility

- Use the same image: **andkram/malmo** (and note the tag if you pull a specific version).
- Use the same run command and ports above so teammates get identical port mapping and workspace mount.
- For experiments, record the image name/tag and the config (e.g. seed, mission XML path) so runs can be reproduced.
