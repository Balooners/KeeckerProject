# Official Companion App — Screens and Functions

**Status:** First version
**Last update:** 2026-11-02

## Objective

Describe what the official Keecker app (`com.keecker.remote` 2.0.3) offers on each screen, link each function to the
protocol ([remote-app-protocol.md](../05-Interfaces/remote-app-protocol.md)), and list what the open companion app must
cover. Described in our own words; the screenshots are not redistributed.

## Evidence

- 26 screenshots taken by Harold on 2026-06-28 between 08:36 and 10:20, Samsung S25 Ultra, app 2.0.3 connected over
  Wi-Fi to his K1 (services 1.14.6). Local copy: `firmware/captures/photos-2026-06/` (git-ignored; the screenshots show
  the phone's public key and device identifier).
- Protocol message names come from `keecker/remote-api` and from the robot code. A link between a screen control and a
  message is ✅ when verified on the robot, 🟡 when inferred from names and code.

## Analysis

The app has five bottom tabs. A header shows the robot name and its battery level.

### 1. Apps

Three lists of the Android TV apps installed on the robot: recent apps (removable), Keecker apps (Google Assistant,
file transfer) and installed apps (Google Play, YouTube, Plex, TV, AlfredCamera, TV File Commander, Smarters Pro,
TrueConf, Send Files To TV, Sideload Launcher, M6+, Molotov, myCANAL…). Each tile can be pinned. A search icon filters.
Tapping a tile launches the app on the projector.

- 🟡 Protocol: application list and launch messages (`ApplicationManager` on the robot, `LaunchIntentMessage`).

### 2. Movement (three sub-tabs)

| Sub-tab | Content | Protocol |
|---|---|---|
| Send to | List of rooms and spots to send the robot to (empty list in the screenshots) | 🟡 `GoToSpotMessage` |
| Map | "No map available" with a "Create a map" button | 🟡 mapping messages (`MappingManager`) |
| Movement & camera | Round joystick, "Auto-align" button (face the wall) | Joystick: 🟡 UDP `MOVE` (port 43045); auto-align: 🟡 `StartAlignToWallMessage` |

### 3. Command (remote control, three sub-tabs)

| Sub-tab | Content | Protocol |
|---|---|---|
| D-pad | Arrows, OK, then back, home, play/pause and microphone buttons | ✅ UDP `DPAD_*` commands (tested 2026-11-02) |
| Touchpad | Large touch area plus a vertical scroll strip, same bottom buttons | 🟡 UDP `MOUSE_*` commands |
| Keyboard | Text field with the phone keyboard, typed text goes to the robot | 🟡 keyboard messages (`KeyboardManager`) |

### 4. Projection (five sub-tabs)

Each sub-tab shows a side view of the projector and a slider, plus a "Projector on" switch at the bottom.

| Sub-tab | Content | Protocol |
|---|---|---|
| Orientation | Tilt slider (wall to ceiling) | ✅ `OrientationMessage` (tested 2026-11-01) |
| Focus | Slider and "Auto" switch | ✅ `FocusMessage` (`value`, `auto`), tested 2026-11-02 |
| Brightness | Slider | ✅ `BrightnessMessage`, tested 2026-11-02 |
| Shape | Keystone slider and "Auto" switch | ✅ `KeystoneMessage` (`value`, `auto`), tested 2026-11-02 |
| Advanced | Horizontal and vertical flip switches, zoom slider (×1.0), projection mode Normal / Film / Eco; note: "Keecker can only be in Eco mode while charging" | 🟡 `FlipMessage`; ✅ `ZoomMessage`; `DisplayModeMessage`: ✅ "Eco" = `PICTURE` (the only mode accepted while plugged in), 🟡 "Normal" and "Film" probably `USER` and `MOVIE` |
| "Projector on" switch | Turns the projected image on or off | 🟡 `LedsMessage`, which ✅ switches the light source (tested 2026-11-01) |

### 5. Settings

- Keecker card: battery level, name; volume slider; switches for voice command, Keecker voice, touch projection,
  safety sensors; "touch projection calibration" entry.
- My Keecker: connection type (Wi-Fi), rename, storage used.
- App theme: dark theme.
- Account: the phone's public key and device identifier (shown in clear), "connect to another Keecker".
- Support, FAQ, app version (2.0.3), services version (1.14.6), privacy policy, terms, open-source licences.

Protocol: 🟡 `SetVolumeMessage`, `VoiceRecognitionStatusMessage`, `TextToSpeechStatusMessage`, `TouchWallMessage`
(`isOn`, `startCalibration`), `SetNameMessage`, `StorageStatusMessage`. The safety sensors switch maps to the STM
safeties (command `0x01` on the STM side, [stm32-protocol.md](../05-Interfaces/stm32-protocol.md)); its app message is
not identified yet.

The open-source licence list shows the usual Android stack of the time: AndroidX / support libraries, Room, data
binding, Dagger 2.16, Butter Knife, Timber, LeakCanary, Kotlin, Bouncy Castle, SQLite JDBC.

## Conclusions

The open companion app needs, at minimum, the same five areas: launching apps, sending the robot somewhere and mapping,
a remote control (D-pad, touchpad, keyboard), projector settings, and robot settings. All of them map to messages
already documented. The screens not shown here (camera, surveillance, programs, invitations) were removed or depended
on Keecker servers.

## Open Questions

- [x] Focus, brightness, keystone, zoom, D-pad verified on the robot (2026-11-02).
- [ ] Remaining 🟡 mappings: flip, Normal/Film modes (robot unplugged), touchpad, keyboard, settings switches.
- [ ] Message behind the "safety sensors" switch. Never disable the safeties during tests.
- [ ] Rooms, spots and map messages once a map exists on the robot.
