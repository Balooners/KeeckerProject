# Keecker K1 Hardware Platform

**Status:** In Progress
**Last update:** 2026-10-28

## Objective

Describe the physical robot as a whole (compute module, sensors, actuators, power) and what each part means for a Linux-based replacement OS.

## Context

This first version is built from **public sources** (see [Public-Sources.md](../02-Acquisition/Public-Sources.md)) and the official SDK. It has not been checked against the device yet. Items to verify on the robot are listed under Open Questions.

Abbreviations used below: "Support guide" is the official 85-page Support Q&A (2019-02), "Specs" is the archived keecker.com specifications page, "Nav blog" is the Keecker blog post #9 on navigation algorithms (2018), "SDK" is `keecker/services-api`.

## Evidence and Analysis

### Overview

| Item | Value | Source | Confidence |
|---|---|---|---|
| Model name | Keecker K1 | Support guide, certification section | ✅ Confirmed |
| Dimensions | 38.8 cm high, 37.8 cm wide, 39.7 cm long | Specs | ✅ Confirmed |
| Weight | 9.4 kg with battery | Specs | ✅ Confirmed |
| Design / assembly | Designed in Paris, assembled in China | Support guide | ✅ Confirmed |
| External ports | None (no USB, no HDMI). Wi-Fi and Bluetooth only | Support guide | ✅ Confirmed |

### Compute module

| Item | Value | Source | Confidence |
|---|---|---|---|
| Module | Intrinsyc **Open-Q 820** system-on-module ("Radio Module: ITCNFA324 Integrated on Open Q-820") | Support guide, certification section | ✅ Confirmed (official document) |
| SoC | Qualcomm Snapdragon 820, quad-core 2.2 GHz | Specs; ADB snapshot D001 | ✅ Confirmed |
| RAM | 3 GB | Specs | ✅ Confirmed |
| Storage | 32 GB or 160 GB flash | Specs | ✅ Confirmed |
| Wi-Fi / BT | 802.11 a/b/g/n/ac, access-point mode; Bluetooth 4.1 BLE | Specs | ✅ Confirmed |
| OS shipped | "Keecker OS1", Android TV 7 (Nougat) | Specs; ADB (SDK 24) | ✅ Confirmed |

The Open-Q 820 is a commercial module, not a Keecker design. Intrinsyc (now Lantronix) sold it with 3 GB LPDDR4 and 32 GB UFS, which matches the K1 32 GB version. Its vendor lists **Debian Linux** among its supported operating systems. The SoC variant on Open-Q modules is the APQ8096, the version of the Snapdragon 820 without a cellular modem. The same SoC is used by the DragonBoard 820c, which has mainline Linux support (`arch/arm64/boot/dts/qcom/apq8096-db820c.dts`).

- 🟡 Probable: the K1 SoC is an APQ8096 rather than an MSM8996. The repository so far says "MSM8996", which comes from Android properties. To verify: `/proc/device-tree/model`, `/proc/device-tree/compatible`, `ro.board.platform`.
- 🟡 Probable: Lantronix datasheets and user guides for the Open-Q 820 (module pinout, power, boot) apply to the K1 compute module. This would make a Linux port much more realistic than on a fully custom board.

### Motion

| Item | Value | Source | Confidence |
|---|---|---|---|
| Drive | Two motorized drive wheels (differential drive), castor wheels in front | Nav blog; press | ✅ Confirmed |
| Odometry | Magnetic encoders on both drive wheels | Nav blog | ✅ Confirmed |
| Speed | About 0.5 m/s (Follow Me) | Support guide | ✅ Confirmed |
| Obstacles crossed | Up to about 2 cm (door steps, cables, carpets) | Support guide | ✅ Confirmed |
| Cliff detection | Stops in front of holes and stairs | Support guide | ✅ Confirmed |
| Motion microcontroller | A dedicated microcontroller executes the motion commands and reads the proximity sensors in real time, independently of the main processor | Nav blog | ✅ Confirmed |
| MCU family | STM (Java package `com.keecker.embedded.stm`, method names `toggleSTMSafeties`, `DispatchSTMTemperature`); exact part number unknown | SDK; `libhw_robot_jni.so` | ✅ Confirmed (STM), part number open |
| Link between SoC and MCU | UART `/dev/ttyHSL1` (termios), see [stm32.md](stm32.md) | `libhw_robot_jni.so` static analysis | ✅ Confirmed |

### Perception sensors

| Sensor | Details | Source | Confidence |
|---|---|---|---|
| 3D depth camera | Forward-facing time-of-flight camera. Field of view about 45° wide by 70° high, maps up to about 2 m. Weak on transparent, reflective or sunlit surfaces | Nav blog; Support guide; Specs | ✅ Confirmed |
| Proximity sensors | 12 sensors around the base. Ranges reported in mm, with per-sensor error and trigger masks | SDK `MovementSafetiesStatus.NB_OF_PROXIMITY_SENSORS = 12` | ✅ Confirmed |
| IMU | Accelerometer, gyroscope, magnetometer (compass) | Nav blog; Specs | ✅ Confirmed |
| Top camera | 13 MP Sony sensor with a 360° fisheye lens. Used for Follow Me and remote viewing. The SDK has dewarp parameters | Specs; Support guide; SDK `embedded/camera` | ✅ Confirmed |
| Front camera | 5 MP, used for remote driving and video calls | Specs | ✅ Confirmed |
| Environment | Temperature, humidity, ambient light | Specs | ✅ Confirmed |
| Other | Infrared, GPS listed in specifications | Specs | ✅ Confirmed (listed), role unknown |
| Microphones | 2 microphones, "Hey Keecker" wake word | Specs | ✅ Confirmed |

### Projector

| Item | Value | Source |
|---|---|---|
| Type | LED, 1000 lumens, 20,000 h lifetime, < 25 dB | Specs |
| Resolution | 720p native (WXGA, 16:10), contrast 6000:1, accepts 1080i | Specs |
| Optics | Fixed focal length, throw ratio 0.90:1, throw distance 0.4-2.7 m, image 52-359 cm; 78" at 1.5 m | Specs |
| Motorized | Tilts 90° from wall to ceiling | Specs |
| Automation | Autofocus, auto-keystone, digital zoom | Specs |
| Touch Projection (beta) | Hand-on-wall interaction after a calibration in front of a flat wall | Support guide |

All values ✅ Confirmed from official pages. The projector control path (which bus drives focus, tilt and the LED engine) is unknown.

### Audio

4.1 system: 4 × 10 W full-range speakers and 1 × 50 W subwoofer, up to 117 dB (Specs, ✅ Confirmed).

### Power

| Item | Value | Source |
|---|---|---|
| Battery | Li-ion, 12 Ah, 300 Wh | Specs |
| Runtime | 6 h full use, 3 days music only, about 7 days patrol only; about 30 h without projection after the April 2018 update | Specs; blog #2 |
| Charging | 4 h full charge, 75% after 2 h. Works indefinitely while docked | Support guide |
| Docking station | 10.2 × 19.3 × 11.5 cm, 750 g, 100-240 V AC. Two metal contacts under the robot. A recessed micro-button resets a battery that has entered protection mode | Support guide; Specs |
| Auto-docking | Returns to the dock at 5% battery. The dock is a SLAM landmark | Support guide; Nav blog |

All values ✅ Confirmed from official documents.

### Human interface

- Physical button on top, next to the 360° camera: 1 tap toggles sound, 2 taps toggle the projector, a long press turns everything on or off. Pressing it 6 times quickly enters the offline pairing mode added by the final release. ✅ Confirmed (Support guide; end-of-life FAQ).
- On/off switch under the robot, between the drive wheels. ✅ Confirmed.
- LED ring around the top camera. It turns red whenever a camera is on (privacy), blue when the projector wakes, and blinks green when charging. ✅ Confirmed.

## Conclusions

1. The K1 is a commercial Qualcomm module (Open-Q 820) plus a motion microcontroller, sensors and actuators. A Linux port can start from existing work on the same SoC (DragonBoard 820c in mainline, Debian support from the module vendor).
2. Real-time motion and safety are handled by the microcontroller, not by Android. If the protocol between the SoC and that MCU is understood, motion is reusable as is under Linux, without rewriting motor control.
3. The navigation sensor set (ToF depth camera, 12 proximity sensors, wheel encoders, IMU) is exactly what Nav2 and slam_toolbox expect.

## Open Questions

- [ ] Exact SoC variant (APQ8096 or MSM8996) and device tree `model` / `compatible` on the robot.
- [x] Physical link to the motion MCU: UART `/dev/ttyHSL1` ([stm32.md](stm32.md)). Frame format still to decode.
- [ ] Depth camera model and interface (USB or MIPI CSI). `libzcam*` / `ZcamService` are candidates.
- [ ] Projector control path: focus and tilt motors are driven by the STM ([stm32.md](stm32.md)); keystone and LED driver still unknown.
- [ ] FCC ID on the regulatory label, and whether an FCC filing with internal photos exists.
- [ ] Hardware revisions across units (the docking station was redesigned: the Support guide mentions a "new charging station").
