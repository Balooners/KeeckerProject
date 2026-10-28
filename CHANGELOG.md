# Changelog

## 2026-10-28 — License

### Changed

* License decided by Harold: **Apache License 2.0** (official text from apache.org, SHA256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`). `NOTICE` added: the license covers the original work in this repository, not Keecker material, which is never redistributed. README badge and section, ROADMAP, SPDX headers on scripts

## 2026-10-28 — Robot-side protocol and open test client

### Added

* `scripts/remote-client/keecker_remote.py`: open client for the companion-app protocol (mDNS discovery, handshake, libsodium encryption, projector status, LED and tilt; no movement commands), with an offline self-test against a simulated robot
* `docs/10-Operations/remote-client.md`: test procedure for the client

### Changed

* `docs/05-Interfaces/remote-app-protocol.md`: robot-side evidence. Jetty server on port 8080 with a local-socket bridge, one message per WebSocket frame, `0xAA` keep-alive, TXT fields `uuid`/`v`/`vn`, `type_name` format, full handshake, pairing rules, UDP port 43045, security observations
* `README.md`: `remote-api` is published without a license (read and documented, not copied); only `services-api` is Apache 2.0

## 2026-10-28 — Public home page and device session kit

### Added

* `docs/10-Operations/adb-runbook.md` and `scripts/robot-readonly-snapshot.ps1`: one read-only ADB session that answers the bootloader, partition, kernel, STM node, port and DRM questions
* `docs/02-Acquisition/Prior-Sessions-Review.md`: review of the earlier ADB and network sessions (observed, assumed, unknown)
* `docs/assets/banner.svg`: project banner (original artwork, no Keecker logo or photo)

### Changed

* `README.md` rewritten as the public home page: community and non-commercial purpose, Android TV target, progress, architecture diagram, roadmap, principles, non-affiliation notice

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
