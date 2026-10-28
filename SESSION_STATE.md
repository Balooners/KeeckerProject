# SESSION_STATE.md

Last update: 2026-10-28

## Current phase

Phase II — Android / ADB Reverse Engineering

## Completed

### Network phase

- TCP scan completed.
- HTTP crawl completed.
- React assets downloaded.
- JavaScript analysis completed.
- Google Cast / Eureka API discovered.
- OTA endpoint identified.

### Android acquisition

- ADB USB confirmed.
- ADB Wi-Fi confirmed.
- Android 7.0 / SDK 24 confirmed.
- Qualcomm Snapdragon 820 / MSM8996 confirmed.
- ARM64 confirmed.
- 133 Binder services listed.
- Keecker proprietary Binder services identified:
  - KeeckerRegistryService
  - IhmService
  - RecoveryService

### APK extraction

Extracted Keecker/K1 APKs:

- com.keecker.services.apk
- com.keecker.services.ota.apk
- com.keecker.apps.data.apk
- com.keecker.apps.diagnostic.apk
- com.keecker.apps.launcher_netflix.apk
- K1_TvSetupCustomizer.apk
- K1_LeanbackCustomizer.apk
- KeeckerLeanbackWidget.apk

### Main service analysis

- AndroidManifest.xml analysed.
- `com.keecker.services` confirmed as main system service APK.
- Version confirmed: 1.14.6.
- Runs as `android.uid.system`.
- Persistent privileged app.
- Main robot services identified:
  - HwRobotService
  - ProjectorService
  - CameraService
  - ZcamService
  - SlamService
  - MovementPlannerService
  - MovementPerceptionService
  - PerceptionService
  - FollowMeService
  - ApiService
  - RemoteService
  - HttpServerService
  - OptimizedService

### Native libraries

Confirmed native stack includes:

- ROS
- OpenCV
- TensorFlow
- SLAM
- Navigation
- Perception
- Object detection
- Object tracking
- Native camera
- JNI robot control

Important libraries identified:

- libhw_robot_jni.so
- libslam.so
- libslam_jni.so
- libmovement_planner.so
- libmovement_planner_jni.so
- libmovement_perception_jni.so
- libperception.so
- libperception_jni.so
- liblocalizer.so
- liblocalizer_jni.so
- libnative_camera_jni.so
- libobject_detector_jni.so
- libobject_tracker_jni.so
- libtensorflow_inference.so
- libtf2.so
- libroscpp_serialization.so
- librostime.so

### ODEX / OAT

- `com.keecker.services.apk` does not expose Java classes directly in JADX.
- Main Java bytecode appears to be in ODEX.
- Extracted:

`firmware/odex/com.keecker.services.odex`

Size:

`70,189,776 bytes`

SHA256:

`ABA15779A89B2A429D71A541119BD70062FABBFD09233F6274914DD92097FBDC`

Format:

- ELF
- ARM64
- Android ART/OAT optimized dex container

- `boot.oat` extracted for future ODEX reconstruction.

### Repository

- KeeckerOS project direction established.
- Documentation structure created.
- Governance structure started.
- Artifact register started.
- AGENTS.md created.
- SESSION_STATE.md created.
- Codex extension installed in VS Code and used for repository audit/restructuring.

## Current blockers

- JADX cannot directly decompile `com.keecker.services.odex`.
- Need Android 7 ODEX/OAT reconstruction workflow.
- Method corrected on 2026-10-28: on Android 7 the ODEX is an OAT container that embeds the DEX.
  vdexExtractor does not apply (VDEX only exists from Android 8). Planned chain:
  `baksmali list dex` → `baksmali x -d <bootclasspath>` → `smali a` → JADX/REA, all inside `work/` (git-ignored).
  If `firmware/oat/boot.oat` alone is an incomplete bootclasspath, a read-only `adb pull /system/framework`
  will be needed (robot + Harold's approval).

## Next objective

Recover Java classes from:

`firmware/odex/com.keecker.services.odex`

Then search for:

- HwRobotService
- ProjectorService
- ApiService
- SlamService
- MovementPlannerService
- Binder interfaces
- JNI bindings
- System.loadLibrary usage
- Native method declarations

## Decisions and findings since 2026-06-28

Recorded on 2026-10-28; product vision and OS target options are in `CLAUDE.md`.

- Project goal extended: an open-source OS any K1 owner can install without Keecker servers.
  Must work on every unit (hardware revisions, per-robot calibration backup).
- ✅ OS target decided by Harold on 2026-10-28: **recent Android TV** (LineageOS ATV, msm8996-common, Android 11 first).
  Reason: the wanted apps (myCANAL, Molotov, Free TV, Jellyfin, IPTV, Netflix, Disney+) and phone casting are Android TV
  features, and Android 7 (API 24) is below several app minimums. Linux + ROS 2 is no longer the target (see `CLAUDE.md`).
- ✅ Official Keecker SDK found: https://github.com/keecker/services-api (Apache 2.0, KEECKER SAS,
  last commit March 2019). 36 AIDL files describe Binder contracts (projector, perception, movement
  planner/perception, API service). Reusable with attribution, unlike ODEX and binaries.
  - 🟡 Probable: an STM32 microcontroller handles at least the movement safeties
    (`embedded/stm`, `MovementSafetiesStatus`, 12 proximity sensors).
  - 🔴 Hypothesis: motors and sensors go through a serial or USB link to that MCU.
  - Consequence: ODEX reconstruction becomes verification for SDK-covered services; services without
    public AIDL (HwRobotService, SlamService, ZcamService, FollowMeService, CameraService, RemoteService)
    become priority targets. To be confirmed by mission 1.
- Tooling decided: REA MCP (official `morluto/rea` only) and Ghidra (official NSA repository), both in WSL2
  (Harold's workstation is Windows 11 ARM64).
- Legal rule restated: nothing proprietary in the repository; proprietary parts will be extracted from each
  owner's robot by a script. The "Keecker OS" name is provisional.

### Product understanding (2026-10-28, public sources)

- ✅ Compute module is a commercial Intrinsyc **Open-Q 820** SOM (official certification text: "Radio Module: ITCNFA324
  Integrated on Open Q-820"). 🟡 SoC probably APQ8096, same as the DragonBoard 820c (mainline Linux).
- ✅ A dedicated microcontroller executes motion commands and reads the 12 proximity sensors in real time
  (Keecker navigation blog post; SDK `NB_OF_PROXIMITY_SENSORS = 12`).
- ✅ Sensors: forward ToF depth camera, 12 proximity sensors, wheel magnetic encoders, IMU, 13 MP 360° fisheye top camera,
  5 MP front camera, temperature/humidity/light, 2 microphones.
- ✅ `keecker/remote-api` holds the full companion-app protocol (~180 protobuf messages).
- ✅ End of life: the final release removed every server-backed feature (remote camera, programs, analytics, video call,
  diagnostics, Alexa/Google Home) and added offline pairing (press the top button 6 times).
- ✅ SoC ↔ STM link is a UART, `/dev/ttyHSL1`, opened with termios by `libhw_robot_jni.so`. The STM owns propulsion,
  IR proximity sensors, IMU, light sensor, fans, projector focus/tilt and safeties (`docs/07-Hardware/stm32.md`).
- ✅ Official companion app `com.keecker.remote` 2.0.3 analysed with REA (genuine Keecker signature). Discovery: mDNS
  `_keecker._tcp`; transport: WebSocket `ws://<host>:<port>/remote/keecker.ws` or Bluetooth RFCOMM
  `7fdc2820-6bc9-11e3-981f-0800200c9a66`; messages: `remote-api` protobuf over libsodium (`docs/05-Interfaces/remote-app-protocol.md`).
- ✅ STM command protocol decoded: `/dev/ttyHSL1` 115200 8N1, 7-byte frames `0xBE, cmd, 4-byte value (MSB first), XOR`;
  velocity `0x02`, focus `0x03`, tilt `0x04`, fans `0x09`, PWM `0x17`, PIDs, wheels `0x31` (`docs/05-Interfaces/stm32-protocol.md`).
- ✅ Robot Java code recovered from the ODEX (3 DEX, 18,136 classes) and readable in REA/JADX.
- ✅ developer.keecker.com is still online (SDK guides, API reference 0.2); a developer USB port exists under the robot.
- Owner tests (Harold, Android 7 robot): casting unreliable, most TV apps fail except Molotov, "go to the charging
  station" and Touch Projection do not work, official app pairing works.
- Details: `docs/07-Hardware/platform.md`, `docs/04-Analysis/FEATURES.md`, `docs/02-Acquisition/Public-Sources.md`.
- ✅ Robot-side protocol read from the robot code (not obfuscated): Jetty on port 8080 serves the file uploader and
  `/remote/keecker.ws`, one message per WebSocket frame, `0xAA` keep-alive, `AuthMessage` in clear then crypto_box,
  pairing rules (known key, setup, 6-press pairing mode, no owner, invitation token), UDP port 43045 (role unknown).
- ✅ Open test client `scripts/remote-client/keecker_remote.py` (no movement commands); offline self-test passes.
- ✅ STM readings decoded: `libhw_robot_jni.so` receives 7-byte messages (16-bit header, reading ID, 32-bit value) from
  five abstract sockets `@socket.stm.{status,propulsion,projector,imu,ir}`; it does not read the UART. The program
  serving them is not in the extracted APKs (🔴 native system daemon, to find on the robot).
- ✅ UDP 43045 = encrypted real-time channel: pointer, D-pad and manual driving (`MOVE`, linear/angular in −1..1).
- 🟡 Earlier ChatGPT sessions recall verified boot "green", which usually means a locked bootloader
  (`docs/02-Acquisition/Prior-Sessions-Review.md`). To confirm with `scripts/robot-readonly-snapshot.ps1`.
- `keecker/remote-api` has no license: field numbers are used for interoperability, files are not copied.
- Harold is contacting Keecker's founder (Pierre Lebeau) on LinkedIn: blessing for the community project, name,
  bootloader unlock, former engineers. The public README was rewritten for this.

## Missions

One mission at a time; each ends with SESSION_STATE.md and CHANGELOG.md updates and Harold's validation.

| # | Mission | Robot needed | Status |
|---|---|---|---|
| 0 | Repository hygiene: `.gitignore`, `CLAUDE.md`, Claude Code deny rules | No | Done 2026-10-28 |
| 1 | `services-api` SDK mapping: `docs/05-Interfaces/Services-API.md`, AIDL → services, services without AIDL, `embedded/stm`, ROS 2 mapping, other public Keecker repositories | No | Started: public repositories reviewed (see `docs/02-Acquisition/Public-Sources.md`) |
| 2 | Reverse environment: REA + Ghidra in WSL2 | No | Done 2026-10-28 (`docs/10-Operations/Reverse-Environment.md`) |
| 3 | DEX recovery from the ODEX, Java analysis of priority services | No (unless bootclasspath is missing) | |
| 4 | Read-only bootloader check + `libhw_robot_jni.so` analysis | Yes, read-only | |
| 5 | `docs/04-Analysis/FEATURES.md` | No | First version 2026-10-28 from public sources |
| 6 | Full partition dump, `persist` backup, EDL (Qualcomm 9008) study | Yes, procedure validated by Harold first | |

## Do not repeat

- Do not repeat network scan.
- Do not repeat APK extraction.
- Do not repeat Binder service listing unless new evidence is required.
- Do not reorganize repository again unless explicitly requested.
- Do not overwrite existing documentation.

## Safety rules

- Read-only operations only.
- No root.
- No flash.
- No reboot.
- No destructive commands.
- No modification of the robot.

## Immediate next step

The robot is away from Harold for several days (from 2026-10-28). When it is back, one home session:

1. `scripts/robot-readonly-snapshot.ps1` (`docs/10-Operations/adb-runbook.md`): bootloader, partitions, kernel, ports, DRM.
2. `scripts/remote-client/keecker_remote.py` (`docs/10-Operations/remote-client.md`): discovery, 6-press pairing,
   projector status, LED and tilt.

Until then, without the robot: preparation of the LineageOS build (needs Harold's Linux x86_64 machine), and the
open robot service design (STM driver from `docs/05-Interfaces/stm32-protocol.md`).