# STM UART Protocol (SoC → motion microcontroller)

**Status:** In Progress (command direction decoded statically; readings direction and device tests pending)
**Last update:** 2026-10-28

## Objective

Document the serial protocol between the Snapdragon and the STM microcontroller, so that an open service can drive the robot without the proprietary `libhw_robot_jni.so`.

## Context

The link itself is described in [stm32.md](../07-Hardware/stm32.md). This document covers the wire format, from AArch64 disassembly of `libhw_robot_jni.so` (SHA256 `819120ce5f9c4aaaabb939947e1b6f85080e92c1425e6b9b6cbf177533d12051`), using `aarch64-linux-gnu-objdump` and `nm`. Behaviour is described in our own words; no disassembly is reproduced beyond constants.

## Evidence and Analysis

### Port setup ✅ Confirmed

| Item | Value | Evidence |
|---|---|---|
| Device | `/dev/ttyHSL1` | string in the library |
| Open flags | read/write, no controlling terminal, non-blocking (`0x902`) | `Uart::Open` |
| Speed | **115200 baud** (`B115200` = `0x1002`, set for input and output) | `cfsetispeed` / `cfsetospeed` arguments |
| Frame | 8 data bits, no parity, 1 stop bit, receiver enabled, modem lines ignored (`CS8 | CREAD | CLOCAL`), raw mode (no canonical input, no echo, no signals, no output processing) | termios flags written before `tcsetattr` |
| Read timing | `VMIN = 1`, `VTIME = 1` | `c_cc` bytes written before `tcsetattr` |

### Reset before connecting ✅ Confirmed

`MotorController::Connect` writes the string `1` to **`/dev/resetboard`**, closes it, waits **100 ms**, then opens the UART. If the reset device cannot be opened, it logs `Can't open reset gpio %s`. `/dev/resetboard` is therefore a GPIO exposed by the Keecker kernel to reset the STM.

### Command frame (SoC → STM) ✅ Confirmed

Every command is a fixed **7-byte** frame:

| Byte | Content |
|---|---|
| 0 | Start byte `0xBE` |
| 1 | Command ID |
| 2-5 | 32-bit argument, most significant byte first |
| 6 | Checksum: XOR of bytes 0 to 5 |

Source: `MotorController::UartWrite(uint8 command, uint32 value)` builds exactly this frame and writes 7 bytes.

### Command IDs

Mapped from the JNI entry points of `com.keecker.embedded.stm.motorcontrol.HwRobotService`. Each ID is the constant passed to `UartWrite` in that function.

| ID | Function | Argument | Confidence |
|---|---|---|---|
| `0x02` | Velocity command (`setVelocityCommand`) | Bytes 2-3: angular speed, bytes 4-5: linear speed. Each is a signed 16-bit value, least significant byte first, equal to the input × 1000 (🟡 so mm/s and mrad/s, if the inputs are m/s and rad/s as in the SDK). Value `0xFFFFFFFF` when the command is marked invalid | ✅ ID and packing; 🟡 units |
| `0x03` | Projector focus position (`cmdProjectorFocus`) | Position in byte 2 | ✅ |
| `0x04` | Projector tilt position (`cmdProjectorTilt`) | Position in byte 2 | ✅ |
| `0x07`, `0x08` | Projector calibration (`cmdProjectorCalibration`) | Flag bit plus a 16-bit value | ✅ IDs, 🟡 meaning |
| `0x09` | Fan duty cycles (`setFansDutycycles`) | Two 8-bit values | ✅ |
| `0x17` | Propulsion PWM, open loop (`setPropulsionDutycycles`, also used by the velocity path in PWM mode) | Two signed 8-bit duty cycles, clamped to -100..100 | ✅ |
| `0x18`-`0x23`, `0x2e`, `0x2f` | PID gains (`setPids`) | One gain per command | ✅ IDs, 🟡 order of gains |
| `0x31` | Wheel dimensions (`setWheelsDimensions`) | Two 8-bit values | ✅ |
| `0x01`, `0x32`-`0x34` | Sent from internal threads (main loop, periodic requests) | Unknown | 🔴 Hypothesis: status and reading requests |

The remaining JNI functions (IR calibration, safeties toggles, battery deep sleep, gyroscope sensitivity, tests, debug) call other code paths that are not yet mapped.

### Velocity path in PWM mode ✅ Confirmed

When a "PWM movement control" flag is set, `setVelocityCommand` does not send `0x02`. It converts the linear and angular speeds into left and right wheel duty cycles, clamps them to ±100, and sends `0x17`.

## Conclusions

The command direction of the protocol is simple: 115200 baud 8N1, 7-byte frames with a `0xBE` start byte and an XOR checksum. An open Android or Linux service can drive the wheels and the projector motors with a few dozen lines, provided the STM is reset and powered as the original library does.

⚠️ Safety: the STM also enforces obstacle and cliff safeties. A replacement driver must never disable them (`toggleSTMSafeties`, `ignoreSTMSafeties`, `toggleKeeckerUnbridled` exist), and must stop the robot when the link is lost.

## Open Questions

- [ ] Readings direction (STM → SoC): frame format, start byte, and the IDs behind each `ReadingsDispatcher::Dispatch*` (wheel speed, IR ranges, IMU, battery…).
- [ ] Meaning of commands `0x01` and `0x32`-`0x34`, and the polling rate.
- [ ] Watchdog behaviour: does the STM stop the motors if no velocity command arrives for a while?
- [ ] Confirm the units on the robot, by sending a small velocity while the robot is on its back or on a stand, with Harold's approval.
- [ ] Mapping of `/dev/ttyHSL1` to an Open-Q 820 UART (BLSP) for a future device tree.
