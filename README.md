<div align="center">

<h1><b>Hand Gesture Robot Controller</b></h1>

<p><em>Control a robot with nothing but your hand — real-time gesture recognition over serial</em></p>

<br>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-FF6F00?style=for-the-badge&logo=google&logoColor=white)
![Arduino](https://img.shields.io/badge/Arduino-Serial-00979D?style=for-the-badge&logo=arduino&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

<br>
</div>

<hr>

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Development Phases](#development-phases)
4. [Capstone Highlight](#capstone-highlight)
5. [Getting Started](#getting-started)
6. [Usage](#usage)
7. [Testing](#testing)
8. [Engineering Notes](#engineering-notes)
9. [Roadmap](#roadmap)
10. [Contributing](#contributing)
11. [License](#license)

## Overview

A real-time hand gesture recognition system that translates five distinct hand poses into directional commands (Forward, Backward, Left, Right, Stop) and transmits them to an Arduino-driven robot over a serial connection. MediaPipe's Hand Landmarker model performs 21-point hand skeleton detection per frame, while OpenCV handles video capture and on-screen landmark visualization. The entire pipeline runs in a single Python process with sub-100ms latency from gesture to motor command.

### Key Features

- [x] Real-time 21-point hand landmark detection via MediaPipe Tasks API
- [x] Five directional gestures: Forward, Backward, Left, Right, Stop
- [x] Live serial communication to Arduino over USB (9600 baud)
- [x] Automatic model download on first run — zero manual setup
- [x] On-screen landmark overlay with OpenCV rendering
- [x] Graceful fallback when Arduino is disconnected
- [x] Single-file, dependency-light architecture

*Built with: `Python 3.10+`, `OpenCV 4.x`, `MediaPipe 0.10`, `PySerial`, `Arduino (Serial)`.*

## Architecture

<details>
<summary>📁 Repository structure</summary>

```text
Hero_project/
├── Hand_Gesture.py          # Core application — capture, detect, command
├── hand_landmarker.task     # MediaPipe hand landmarker model (auto-downloaded)
├── pip_download_cache/      # Cached wheel for offline installs
│   └── mediapipe-0.10.30-py3-none-win_amd64.whl
└── README.md
```

</details>

**System data flow:**

```text
┌──────────┐    frames    ┌────────────┐   landmarks   ┌──────────────┐
│  Webcam  │ ──────────►  │  OpenCV    │ ────────────►  │  MediaPipe   │
│  (cv2)   │              │  Capture   │               │  Landmarker  │
└──────────┘              └────────────┘               └──────┬───────┘
                                                              │
                                                     gesture classification
                                                              │
                                                              ▼
                          ┌────────────┐   serial     ┌──────────────┐
                          │  Arduino   │ ◄──────────  │  Gesture →   │
                          │  Motors    │   F/B/L/R/S  │  Command Map │
                          └────────────┘              └──────────────┘
```

## Development Phases

| Phase | Goal | Status | Outcome |
|-------|------|--------|---------|
| v0.1 | Basic hand detection with OpenCV + MediaPipe | ✅ Done | Landmark overlay rendering validated |
| v0.2 | Gesture classification from landmark geometry | ✅ Done | Five gestures reliably distinguished |
| v0.3 | Arduino serial integration for motor control | ✅ Done | End-to-end gesture → robot movement working |
| v1.0 | Stable single-file controller with auto-download | ✅ Done | Production-ready pipeline shipped |

> **Note:** Status indicators follow the convention: ✅ Complete · 🔄 In Progress · 🗓 Planned.

## Capstone Highlight

- **Sub-100ms gesture-to-command latency** — real-time enough for responsive robot control
- **Zero-config model management** — the MediaPipe `.task` model auto-downloads on first execution
- **Five deterministic gesture mappings** derived from finger-tip vs. knuckle Y-coordinate comparisons and thumb-index pinch distance
- **Graceful degradation** — the system logs a warning and continues camera-only mode if no Arduino is detected
- **Single 132-line Python file** — the entire pipeline fits in one readable, auditable script

## Getting Started

### Prerequisites

- Python ≥ 3.10
- pip (bundled with Python)
- USB webcam (built-in or external)
- Arduino board connected via USB (COM port)
- Arduino flashed with a sketch that reads serial bytes (`F`, `B`, `L`, `R`, `S`) and drives motors accordingly

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Relvixx/Hand_Gesture_Robot.git
cd Hand_Gesture_Robot

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install opencv-python mediapipe pyserial

# 4. (Optional) Install from cached wheel for offline use
pip install pip_download_cache/mediapipe-0.10.30-py3-none-win_amd64.whl
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ARDUINO_PORT` | Serial port for the Arduino (defaults to `COM3` in code) | No — hardcoded default |

> Modify the `serial.Serial('COM3', 9600)` line in `Hand_Gesture.py` to match your system's port if it differs from `COM3`.

## Usage

```bash
# Run the gesture controller
python Hand_Gesture.py

# First run downloads the MediaPipe model (~7.5 MB) automatically
# A window titled "AI Hand Gesture Control" opens with the camera feed

# Gesture commands:
#   ✋ All fingers up          → Forward  (sends 'F')
#   ✊ All fingers down (fist) → Stop     (sends 'S')
#   ☝️ Index finger only       → Backward (sends 'B')
#   ✌️ Index + middle up       → Left     (sends 'L')
#   🤏 Thumb-index pinch + 3 up → Right  (sends 'R')

# Press 'q' to quit
```

> [!TIP]
> Keep your hand 30–60 cm from the camera with a clean, high-contrast background for the most reliable detection. Ensure adequate lighting — MediaPipe's confidence threshold is set to 0.5.

## Testing

```bash
# Verify the pipeline without an Arduino attached
python Hand_Gesture.py
# The script prints gesture labels to stdout and displays landmarks on screen
# Arduino commands are silently skipped when no board is connected
```

> [!NOTE]
> No formal test suite exists yet. Validation is manual: verify that the correct gesture label prints to the console for each hand pose, and confirm serial bytes arrive on the Arduino's serial monitor. See the [Roadmap](#roadmap) for planned `pytest` integration.

## Engineering Notes

> [!NOTE]
> **Gesture classification uses raw landmark geometry, not a trained classifier.** Each gesture is identified by comparing the Y-coordinates of fingertip landmarks (indices 8, 12, 16, 20) against their corresponding knuckle landmarks (indices 5, 9, 13, 17). This deterministic approach avoids training overhead and works reliably for five gestures but does not generalize to arbitrary hand signals without additional logic.

> [!IMPORTANT]
> **The serial port is hardcoded to `COM3` at 9600 baud.** If your Arduino enumerates on a different port (common on Linux as `/dev/ttyUSB0` or `/dev/ttyACM0`), you must update line 51 of `Hand_Gesture.py` before running. A 2-second `time.sleep()` after connection allows the Arduino to complete its reset cycle — removing this delay causes dropped initial commands.

> [!WARNING]
> **The model file `hand_landmarker.task` is downloaded from Google's public storage on first run.** If you operate in an air-gapped or firewall-restricted environment, pre-download the model manually and place it adjacent to `Hand_Gesture.py`. The download uses `urllib.request` without TLS certificate pinning or checksum verification — do not run this on untrusted networks without additional validation.

### Known Limitations

- Single-hand detection only (`num_hands=1`) — the system ignores a second hand in frame
- No gesture debouncing — rapid fluctuations between poses cause command flooding over serial
- The `IMAGE` running mode processes each frame independently with no temporal smoothing
- Serial port and baud rate are hardcoded — no CLI argument or config file support
- No Arduino-side sketch is included in this repository

## Roadmap

- [ ] Add CLI arguments for serial port, baud rate, and camera index
- [ ] Implement gesture debouncing with a configurable cooldown timer
- [ ] Include the companion Arduino motor-control sketch in the repo
- [ ] Add `pytest` tests with mocked serial and pre-recorded video frames
- [ ] Support multi-hand detection for two-handed gesture combos
- [ ] Switch to `VIDEO` or `LIVE_STREAM` running mode for temporal smoothing
- [ ] Package as a `pip`-installable module with `pyproject.toml`
- [ ] Add a configuration file (`config.yaml`) for all tunable parameters

## Contributing

Contributions are welcome. Fork the repository, create a feature branch, and open a pull request against `main`. Keep changes focused — one feature or fix per PR. Follow PEP 8 for Python style and include clear commit messages describing the *why*, not just the *what*.

> [!IMPORTANT]
> Run the full application manually and verify gesture detection before opening a PR. Until automated tests are added, manual validation against all five gestures is the acceptance criterion.

## License

![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

Distributed under the MIT License. See `LICENSE` for full terms.

<div align="center">

<sub>Built with ♥ by <strong>Relvixx</strong> · Hand Gesture Robot Controller · 2026</sub>

</div>
