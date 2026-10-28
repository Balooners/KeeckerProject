# Changelog

## 2026-10-28 — Companion app protocol and robot Java code

### Added

* `docs/05-Interfaces/stm32-protocol.md`: STM UART settings, reset sequence, 7-byte command frame and command IDs
* `docs/05-Interfaces/remote-app-protocol.md`: discovery (`_keecker._tcp`), WebSocket `/remote/keecker.ws`, Bluetooth RFCOMM UUID, authentication, from the official app analysed with REA
* `docs/10-Operations/Reverse-Environment.md`: method to recover the robot DEX files from the ODEX and load them in REA/JADX

## 2026-10-28 — OS target decision

### Changed

* OS target decided by Harold: recent Android TV (LineageOS ATV on msm8996-common, Android 11 first) instead of mainline Linux. `CLAUDE.md` and SESSION_STATE updated.

## 2026-10-28 — Product understanding and reverse environment

### Added

* `docs/02-Acquisition/Public-Sources.md`: public Keecker repositories, archived keecker.com documents, end-of-life documents, with SHA256 of local copies (not redistributed)
* `docs/07-Hardware/platform.md`: K1 hardware overview (Open-Q 820 module, motion microcontroller, sensors, projector, power)
* `docs/04-Analysis/FEATURES.md`: feature inventory with cloud dependency, end-of-life status and KeeckerOS strategy
* `docs/07-Hardware/stm32.md`: SoC to STM link identified as UART `/dev/ttyHSL1`, with the list of functions owned by the STM
* `docs/10-Operations/Reverse-Environment.md`: REA 6.8.0, Ghidra 12.1.4 (ARM64 decompiler built locally), JADX bridge in WSL2

## 2026-10-28 — Mission 0: Repository hygiene

### Added

* `CLAUDE.md`: product vision, OS target options and working rules for Claude Code (imports `AGENTS.md` and `SESSION_STATE.md`)
* `.claude/settings.json`: hard deny rules for `adb reboot/root/remount/install/uninstall/push/sideload`, `adb shell su` and `fastboot`
* SESSION_STATE: decisions since 2026-06-28 (official `keecker/services-api` SDK, OS target track, tooling) and mission plan

### Changed

* `.gitignore`: everything under `firmware/` is ignored except `*.md`; work outputs (`work/`, `framework/`) and proprietary formats (`*.apk`, `*.odex`, `*.oat`, `*.vdex`, `*.dex`, `*.smali`, `*.so`, `*.img`, `*.pb`, `*.tflite`) are ignored repository-wide
* ODEX recovery method corrected: baksmali/smali on the OAT container; vdexExtractor does not apply to Android 7

### Removed

* Local history: unreachable commit `bf8b007`, which contained proprietary binaries, purged from the local object store (no branch or tag referenced it; the GitHub API returns "No commit found" for its SHA, so it was never published)


## 2026-06-28 — Phase II: ADB Exploration

### Added

* Confirmed ADB over USB
* Confirmed ADB over Wi-Fi
* Identified Android platform (Android 7.0 / API 24)
* Confirmed Qualcomm Snapdragon 820 (MSM8996)
* Enumerated 133 Binder services
* Identified proprietary Keecker Binder services
* Extracted proprietary APKs
* Extracted main ODEX (`com.keecker.services.odex`)
* Extracted Android boot image (`boot.oat`)
* Identified native robotics libraries
* Confirmed ROS components
* Confirmed OpenCV integration
* Confirmed TensorFlow integration
* Started technical documentation structure

### Changed

* Reverse engineering strategy changed from network-first to ADB-first.

### Notes

No modification has been made to the robot.

All operations performed were read-only.
