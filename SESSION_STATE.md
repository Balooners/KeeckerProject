# SESSION_STATE.md

Last update: 2026-06-28

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
- Need tools such as oat2dex / baksmali / vdexExtractor / JADX fallback workflow.

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

Set up the ODEX reconstruction toolchain and recover DEX/classes from the Android 7 ARM64 ODEX.