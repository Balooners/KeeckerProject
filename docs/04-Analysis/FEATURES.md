# Keecker K1 Feature Inventory

**Status:** In Progress (first version from public sources)
**Last update:** 2026-10-28

> **2026-10-28:** the OS target is now a recent Android TV, not Linux (see `CLAUDE.md`). The "KeeckerOS replacement" column
> still lists Linux-oriented options (ROS 2, Nav2, Waydroid). It will be revised for the Android target.

## Objective

List everything the Keecker K1 did, where each function ran (robot, Keecker cloud, third party), what survived the end of the company, and the strategy for KeeckerOS.

## Context

Sources are listed in [Public-Sources.md](../02-Acquisition/Public-Sources.md). The hardware is described in [platform.md](../07-Hardware/platform.md). The `Protocol` column names messages from `keecker/remote-api` (`proto/*.proto`), the protocol the companion app used to drive the robot.

Strategy values:

- **Reuse**: keep the original component and run it on the robot.
- **Reimplement**: write our own implementation of the same behaviour.
- **Replace**: use an existing open-source project.
- **Drop**: no viable path, or not worth the effort.

"EOL" refers to the final official release, announced as "March 8th" on the end-of-life support page.

## Evidence and Analysis

### Mobility and navigation

| Feature | Description | Runs on | After EOL | Protocol | Strategy | KeeckerOS replacement |
|---|---|---|---|---|---|---|
| Manual driving | Joystick in the app, live camera view | Robot | ✅ Works | `SpeedMessage`, `RelativeGoToMessage`, `StopMessage` | Reimplement | ROS 2 `cmd_vel` to the motion MCU |
| Mapping | Guided mapping with the joystick, room by room in one session; several maps (floors, houses) | Robot (map copies on the cloud) | ✅ Works locally | `StartMappingMessage`, `MapMessage`, `UploadMapMessage`, `DownloadMapMessage` | Replace | slam_toolbox |
| Rooms and spots | Named rooms, favourite spots (with projection and volume settings), waypoints | Robot | ✅ Works | `AddRoomMessage`, `AddSpotMessage`, `GoToSpotMessage`, `AddWaypointMessage` | Reimplement | Semantic layer on top of Nav2 |
| Autonomous navigation | A* global path on an occupancy grid; local planner samples commands 10 times per second and simulates them; MCU handles last-moment safety | Robot + MCU | ✅ Works | `GoToMessage`, `PathMessage`, `PlannerStatusMessage` | Replace | Nav2 (DWB controller follows the same sampling principle) |
| Localisation | Particle filter fusing odometry, gyroscope, depth-camera point clouds, Wi-Fi signal strength and magnetic field; dock used as a landmark | Robot | ✅ Works | `PoseMessage`, `RobotIsLostMessage` | Replace | AMCL or slam_toolbox localisation; Wi-Fi and magnetic cues optional |
| Docking | Returns to the dock on request or at 5% battery | Robot | ✅ Works | `GoToChargingStationMessage`, `AddChargingStationMessage` | Reimplement | Nav2 docking (opennav_docking) |
| Align to wall | Turns to face a wall for projection | Robot | ✅ Works | `StartAlignToWallMessage` | Reimplement | Depth-camera plane fit |
| Follow Me (beta) | Follows a person using the 360° camera, 0.5 m/s, voice-triggered | Robot | ✅ Works | `StartFollowMeMessage` | Reuse or reimplement | Person detection and tracking on the fisheye image |
| Cliff and obstacle safety | 12 proximity sensors, hole detection | MCU | ✅ Works | `ObstacleMessage` | Reuse | Keep the MCU firmware as is |

### Projection and display

| Feature | Description | Runs on | After EOL | Protocol | Strategy | KeeckerOS replacement |
|---|---|---|---|---|---|---|
| Projector control | On/off, 90° tilt wall to ceiling, autofocus, auto-keystone, brightness, flip, zoom | Robot | ✅ Works | `ProjectionMessages.proto` (`KeystoneMessage`, `FocusMessage`, `FlipMessage`, `BrightnessMessage`, `DisplayModeMessage`) | Reimplement | Driver for the projector path (to be identified) |
| Android TV launcher | Projected Android TV home screen, Google Play apps | Robot + Google | ✅ Works | `LaunchApplicationMessage`, `ListApplicationMessage` | Replace | Kodi or a custom launcher; Android apps through Waydroid |
| Touch Projection (beta) | Hand interaction on the projected wall after calibration | Robot | 🟡 Unknown | - | Reimplement later | Depth camera + calibration |
| Ambiances | Fireplace, aquarium, Milky Way, beach, "play with the cat" | Robot | ✅ Works | - | Reimplement | Media content |

### Media and entertainment

| Feature | Description | Runs on | After EOL | Strategy | KeeckerOS replacement |
|---|---|---|---|---|---|
| Streaming apps | Netflix, YouTube, Spotify, Plex, Kodi, Molotov, myCANAL… via Google Play | Robot + third parties | 🟡 The final release patched Netflix, YouTube and Spotify; Netflix is installed manually | Replace | Jellyfin, Kodi; Android apps through Waydroid |
| Google Cast | Built-in Chromecast | Robot + Google | ✅ Works (kept at EOL) | Drop | No free implementation (Widevine DRM, Google certification) |
| AirPlay | Through third-party apps (AirScreen) | Robot | ✅ Works | Replace | UxPlay |
| Spotify Connect | The robot appears as a Spotify device | Robot + Spotify | 🟡 Patched at EOL | Replace | librespot / Raspotify |
| File transfer | Web page on the robot (port 8080) to send any file over Wi-Fi | Robot | ✅ Works | Reimplement | Local web UI |
| Bluetooth | Gamepads (up to 4), keyboards, speakers | Robot | ✅ Works | Reuse | BlueZ |
| Games | Android games on the projector with gamepads | Robot | ✅ Works | Replace | Waydroid, RetroArch |

### Home monitoring

| Feature | Description | Runs on | After EOL | Protocol | Strategy | KeeckerOS replacement |
|---|---|---|---|---|---|---|
| Remote camera | Live view of both cameras from the app, at home and away. LEDs turn red while a camera is on | Robot + Keecker relay servers | ❌ Remote access removed ("we are not able to maintain camera servers") | `StartCameraStreamingMessage`, `SwitchCameraStreamingMessage`, `TakePictureMessage` | Reimplement | WebRTC on the local network; remote access through WireGuard or Tailscale; keep the red-LED rule |
| Patrol | Scheduled tour of chosen rooms, live view, email summary of temperature and humidity | Robot + cloud (programs, email) | ❌ "Keecker Program" removed | `AddPatrolMessage`, `GoToPatrolMessage` | Reimplement | Local scheduler + Nav2 waypoints; Frigate for detection |
| Home Analytics | Temperature and humidity per room, history | Robot + cloud | ❌ Removed | - | Reimplement | Home Assistant integration (MQTT) |
| Alarm / Sleep Aid | Go to a spot at a set time, play content, projector on or off | Robot + cloud (programs) | ❌ Programs removed | `AlarmMessage`, `SleepAidMessage`, `CreateUpdateProgramMessage` | Reimplement | Local scheduler |
| Video call | Robot ↔ smartphone call | Robot + Keecker servers | ❌ Removed | `ConferenceMessages.proto` | Replace | Jitsi or WebRTC |

### Voice

| Feature | Description | Runs on | After EOL | Strategy | KeeckerOS replacement |
|---|---|---|---|---|---|
| "Hey Keecker" | Wake word and about 30 commands: projection, volume, go to a room, dock, follow me, launch apps, timer, temperature, ambiances | Robot (recognition engine to identify) | 🟡 Probably works for local commands | Replace | openWakeWord + Vosk or Whisper, intents mapped to ROS 2 actions |
| Voice notifications | Spoken messages for battery and failed actions (since release 1.10.0-701) | Robot (TTS) | ✅ Probably works | Replace | Piper TTS |
| Alexa / Google Home | Voice control through smart speakers | Third-party cloud + Keecker cloud | ❌ Removed | Replace | Home Assistant Assist |
| Apple Watch, Siri Shortcuts | Projector, volume, align to wall | Keecker app | 🟡 Unknown | Drop or later | Home Assistant |

### Access, pairing and administration

| Feature | Description | Runs on | After EOL | Protocol | Strategy | KeeckerOS replacement |
|---|---|---|---|---|---|---|
| Companion app | iOS / Android app; earlier web app at `my.keecker.com` | Phone + robot | 🟡 The app must still be installable; the web app is gone | `remote-api` | Reimplement | PWA served by the robot |
| Authentication | Public-key pairing (libsodium); the robot checked on Keecker servers whether a user had access; invitations through the cloud | Robot + cloud | 🟡 Replaced at EOL by offline pairing: press the top button 6 times | `AccessControlMessages.proto`, `AuthMessage` | Reimplement | Local pairing, keys stored on the robot only |
| Offline mode | The robot creates its own Wi-Fi network when none is available | Robot | ✅ Works | `WifiConnectMessage`, `SelectSSIDMessage` | Reimplement | NetworkManager hotspot |
| Remote access | Control from outside the home through Keecker servers | Cloud | ❌ Ended | `DistantConnectionMessage`, `StartVpnMessage` | Replace | WireGuard / Tailscale, disabled by default |
| OTA updates | System update from settings, 25% battery minimum | Keecker servers | ❌ Ended | - | Reimplement | Signed updates (A/B or OSTree) |
| Diagnostics | Self-diagnostic from the app | Robot + cloud | ❌ Removed at EOL | `DiagnosticMessages.proto` | Reimplement | Local health page |
| Factory reset | Settings menu, or switching on 10 times up to the Android logo | Robot | ✅ Works | - | Reimplement | Recovery mode |

### Professional offer

Keecker also sold the robot to businesses (meeting rooms, hotel lounges, coworking spaces, events), with training, replacement within 48 h, anti-theft tracking and yearly maintenance. ✅ Confirmed (archived `eu-fr/pro` page). No impact on KeeckerOS.

## Conclusions

1. **Robot-side features still work without the company**: driving, mapping, navigation, docking, projector, local media, Bluetooth, local voice commands. The OS to replace runs mostly on the robot.
2. **Everything that went through Keecker servers has disappeared**: remote access, remote camera, programs (patrol, alarm, sleep aid), home analytics, video call, diagnostics, Alexa and Google Home, OTA. Self-hosted replacements bring the most value back to owners.
3. `keecker/remote-api` describes the full control surface. A new open companion app can drive **today's** robot through this protocol, and KeeckerOS can expose the same capabilities later.
4. Only DRM-locked services (Netflix, Google Cast) have no free path. They can survive for a while in Waydroid or the original Android install.

## Open Questions

- [ ] Is the original companion app still installable on recent iOS and Android? Is the offline pairing fully functional?
- [ ] Which speech engine "Hey Keecker" used, and whether it works offline.
- [ ] Which services in `com.keecker.services` implement each `remote-api` message (to map with the Binder services list).
- [ ] Wire format and transport of `remote-api` (TCP port, framing around `KeeckerMessage`), to capture from a live session.
