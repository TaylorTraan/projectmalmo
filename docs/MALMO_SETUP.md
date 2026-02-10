## Malmo Setup (macOS, zsh) for CS175

This guide walks you through setting up Project Malmo and this repo on macOS with a Python virtual environment, plus a simple smoke test to check everything works.

The goal is **reproducibility**: everyone should be able to follow these steps and get the same behavior.

---

## 1. Prerequisites

- **Operating system / CPU**
  - Tested on recent macOS releases (e.g., 13+).
  - **Apple Silicon (M1/M2/M3, arm64)** needs a small extra setup step (Rosetta + Intel Python); see **Section 2.3 – Recommended Apple Silicon path**.
  - Older versions may also work but are not guaranteed.

- **Homebrew**
  - Install Homebrew if you do not already have it:
    - Follow the instructions at `https://brew.sh`

- **Xcode Command Line Tools**
  - Some dependencies require build tools:
  - In a terminal:
    - `xcode-select --install`

- **Java (JDK 8+)**
  - Malmo is built on top of Minecraft and requires Java.
  - Recommended (LTS) via Homebrew:
    - `brew install --cask temurin@8`
  - Verify:
    - `java -version`

- **Python 3**
  - We use a standard Homebrew Python:
    - `brew install python3`
  - Verify:
    - `python3 --version`

- **Malmo dependencies (from official docs)**
  - Based on the upstream `install_macosx.md`:
    - `brew install ffmpeg boost-python3`
  - These provide video and Boost.Python bindings used by Malmo.

---

## 2. Installing Project Malmo (recommended path for CS175)

For this course we **always** use the official Malmo zip with:

- Java 8 (Temurin),
- a **Rosetta (Intel) shell** on Apple Silicon,
- and **Python 3.7** in a dedicated virtual environment.

`pip install malmo` / wheels are **not** supported or expected to work in this setup.

### 2.1. Get the official Malmo zip

1. **Download Malmo**
   - Go to the official GitHub releases page:
     - `https://github.com/Microsoft/malmo/releases`
   - Download the latest stable release zip for macOS (e.g., `Malmo-0.37.0-Mac-64bit_withBoost_Python3.7.zip`).

2. **Unzip Malmo**
   - Move the zip somewhere stable, e.g. your home directory or Desktop.
   - In a terminal:

   ```bash
     cd ~/Desktop
     mkdir -p MalmoPlatform
     cd MalmoPlatform
     unzip ~/Downloads/Malmo-0.37.0-Mac-64bit_withBoost_Python3.7.zip
     ```

     - Adjust the zip file name if you downloaded a different version.
     - After this, you should have a directory such as:
       - `~/Desktop/MalmoPlatform/Malmo-0.37.0-Mac-64bit_withBoost_Python3.7`

3. **Set MALMO_HOME, MALMO_XSD_PATH, PYTHONPATH**
   - Malmo requires environment variables pointing at its install and XML schemas, plus a `PYTHONPATH` entry for the Python bindings.
   - Add these lines to your `~/.zshrc` (adjust the folder name if needed):

   ```bash
     echo 'export MALMO_HOME="$HOME/Desktop/MalmoPlatform/Malmo-0.37.0-Mac-64bit_withBoost_Python3.7"' >> ~/.zshrc
     echo 'export MALMO_XSD_PATH="$MALMO_HOME/Schemas"' >> ~/.zshrc
     echo 'export PYTHONPATH="$MALMO_HOME/Python_Examples:$PYTHONPATH"' >> ~/.zshrc
     source ~/.zshrc
   ```

4. **Launch the Malmo Minecraft client**
   - In a separate terminal **outside** the venv:

   ```bash
     cd "$MALMO_HOME/Minecraft"
     ./launchClient.sh
   ```

   - Wait for Minecraft to fully load with the Malmo mod. Leave this running while you use the environment.

5. **Verify `MalmoPython`**

   - Back in your project repo (with the venv activated and environment variables loaded), run:

   ```bash
     python -c "import MalmoPython; print('MalmoPython import OK')"
     ```

   - If this fails, double-check:
     - `PYTHONPATH` includes the directory containing `MalmoPython.so`.
     - You are using the same Python **major/minor version and architecture** that Malmo was built for (e.g., Python 3.7 x86_64 in a Rosetta shell).

---

## 3. Python virtual environment (per-repo)

All project work should happen inside a virtual environment in this repo for reproducibility.

From the **repo root** (where the `README.md` lives):

```bash
cd /path/to/projectmalmo

# Create venv (one-time)
# - On Apple Silicon using the official Malmo zip: prefer a Rosetta + Python 3.7 venv.

python3.7 -m venv .venv_malmo37

# Activate (zsh)
source .venv_malmo37/bin/activate

# Upgrade pip (optional but recommended)
pip install --upgrade pip
```

You should now see something like `(.venv_malmo37)` at the start of your shell prompt.

Install Python dependencies inside the venv:

```bash
# Do NOT install Malmo with pip in this setup.
# Malmo is provided by the zip + MALMO_HOME / PYTHONPATH configuration.

# Any other minimal utilities used by this repo
# (currently the core wrapper aims to be pure Python with stdlib only)
```

To deactivate the venv:

```bash
deactivate
```

---

## 4. Running the project smoke test

Once:

- Java + Malmo are installed,
- the Minecraft client with Malmo mod is running,
- your virtual environment is activated,

you can run the project-level smoke test.

> Note: The script `scripts/smoke_test_env.py` expects a mission XML at `env/mission.xml`. The mission in this repo is intentionally simple and focused on a small platform + diamond task.

From the repo root:

```bash
source .venv/bin/activate   # if not already active
python scripts/smoke_test_env.py --episodes 1
```

You should see output resembling:

- The script printing that it created `MalmoGridEnv`.
- Per-episode summary lines such as:
  - `Episode 0: total_reward=0.0 termination_reason=timeout_max_steps_reached position={'x': ..., 'z': ..., 'y': ...} diamond_count=0`

Exact numbers will vary because the smoke test uses random actions, but **you should see a clear termination reason** at the end of the run.

If the script fails, scroll up to find the first traceback or error message and consult the **Common errors** section below.

---

## 5. Minimal manual Malmo smoke test (outside this repo)

If you just want to verify that your Malmo install is basically working (before touching this repo’s code):

1. Ensure the Malmo Minecraft client is running (`launchClient.sh`).
2. In another terminal (with any Python that has access to `MalmoPython`):

   ```bash
   python -c "import MalmoPython; print('MalmoPython import OK')"
   ```

3. Optionally run one of the official Malmo Python examples (paths vary by release; see the Malmo docs / course starter).

---

## 6. Common errors & fixes

### 6.1 `ModuleNotFoundError: No module named 'MalmoPython'`

Possible causes and fixes:

- **You are not in the Malmo venv**
  - Make sure you ran (or equivalent):

    ```bash
    source .venv_malmo37/bin/activate
    ```

- **Malmo is not on this Python’s `sys.path`**
  - Confirm that `PYTHONPATH` includes the directory containing the Malmo Python bindings (`MalmoPython.so`):

    ```bash
    python -c "import sys, os; print([p for p in sys.path if 'Malmo' in p])"
    ```

  - If needed, re-add the env var and reload your shell:

    ```bash
    echo 'export PYTHONPATH="$MALMO_HOME/Python_Examples:$PYTHONPATH"' >> ~/.zshrc
    source ~/.zshrc
    ```

- **Python version / architecture mismatch**
  - The official Malmo zip used here ships binaries for **Python 3.7 on Intel (x86_64)**.
  - Make sure:
    - `python --version` shows `3.7.x`, **and**
    - `arch` prints `i386` or `x86_64` (not `arm64`).

### 6.2 `Please set the MALMO_XSD_PATH environment variable`

- This usually comes from the official Malmo examples or some mission code.
- Fix:

  ```bash
  echo 'export MALMO_XSD_PATH="$HOME/MalmoPlatform/Schemas"' >> ~/.zshrc
  source ~/.zshrc
  ```

  (Adjust the path if you installed Malmo elsewhere.)

### 6.3 Mission fails to start or times out connecting to client

Symptoms:

- The env hangs on “Waiting for the mission to start…”.
- The world state never shows `has_mission_begun=True`.

Checklist:

- **Is the Minecraft client with Malmo mod running?**
  - You should have launched it via `./launchClient.sh` in the `Minecraft` folder of your Malmo install.
- **Is the host/port correct?**
  - By default this repo uses `127.0.0.1:10000`. If your client is configured differently, update the env constructor call or mission/client config accordingly.
- **Did you start multiple conflicting missions?**
  - Close extra Minecraft windows and try again.

### 6.4 Miscellaneous Java / graphics errors

- Ensure you are using a supported Java version (e.g., Temurin 8).
- If the Minecraft client crashes on startup, try:
  - Updating your GPU drivers (via macOS updates).
  - Redownloading the Malmo zip in case of corruption.

---

## 7. Reproducibility tips for teammates

- Always:
  - Work inside the repo’s Malmo venv (e.g., `.venv_malmo37`) or clearly document if you are using a different environment.
  - Record the exact commit hash of Malmo you installed (or the release tag).
  - Write down any deviations from this guide and why.

- When something breaks:
  - Save the full error message and context.
  - Note:
    - macOS version,
    - Python version,
    - Java version,
    - where Malmo is installed (`MALMO_HOME` path) and which zip you used.
  - Share those details when asking for help so we can reproduce your setup.

