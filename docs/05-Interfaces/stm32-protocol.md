# STM UART Protocol (SoC → motion microcontroller)

**Status:** In Progress (commands and readings decoded statically; device tests pending)
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
| `0x01` | STM safeties configuration (sent once at start-up) | `0x00003F00` at start-up, logged as "all STM safeties enabled except invalid cliff ranges" | ✅ ID and start-up value; 🟡 meaning of each bit |
| `0x02` | Velocity command (`setVelocityCommand`) | Bytes 2-3: angular speed, bytes 4-5: linear speed. Each is a signed 16-bit value, least significant byte first, equal to the input × 1000 (🟡 so mm/s and mrad/s, if the inputs are m/s and rad/s as in the SDK). Value `0xFFFFFFFF` when the command is marked invalid | ✅ ID and packing; 🟡 units |
| `0x03` | Projector focus position (`cmdProjectorFocus`) | Position in byte 2 | ✅ |
| `0x04` | Projector tilt position (`cmdProjectorTilt`) | Position in byte 2 | ✅ |
| `0x07` | Projector focus calibration request (`cmdProjectorCalibration`, also at start-up) | Flag bit plus a 16-bit value | ✅ ID and role (start-up log "Requesting Focus calibration"), 🟡 value |
| `0x08` | Projector tilt calibration request (`cmdProjectorCalibration`, also at start-up) | Flag bit plus a 16-bit value | ✅ ID and role (start-up log "Requesting Tilt calibration"), 🟡 value |
| `0x09` | Fan duty cycles (`setFansDutycycles`) | Two 8-bit values | ✅ |
| `0x17` | Propulsion PWM, open loop (`setPropulsionDutycycles`, also used by the velocity path in PWM mode) | Two signed 8-bit duty cycles, clamped to -100..100 | ✅ |
| `0x18`-`0x23`, `0x2e`, `0x2f` | PID gains (`setPids`) | One gain per command | ✅ IDs, 🟡 order of gains |
| `0x31` | Wheel dimensions (`setWheelsDimensions`) | Two 8-bit values | ✅ |
| `0x32`-`0x34` | Sent from internal threads (periodic requests) | Unknown | 🔴 Hypothesis: reading requests |

The remaining JNI functions (IR calibration, safeties toggles, battery deep sleep, gyroscope sensitivity, tests, debug) call other code paths that are not yet mapped.

### Velocity path in PWM mode ✅ Confirmed

When a "PWM movement control" flag is set, `setVelocityCommand` does not send `0x02`. It converts the linear and angular speeds into left and right wheel duty cycles, clamps them to ±100, and sends `0x17`.

### Start-up sequence ✅ Confirmed

From the library main loop (`Loop()`), in order:

1. Read the STM identifier from `/data/misc/keecker/stm_uuid` (up to 26 bytes) and log it.
2. Start the reading threads (next section).
3. Power the board off, then on, then connect (reset GPIO and UART, see above).
4. Wait for a fresh firmware revision reading (ID `0x00`) made of one letter and three digits, for example `A123`.
   Until then, log the bytes received and retry, every 100 ms when nothing arrives.
5. Notify the Java service that the controller is connected.
6. Send `0x01` = `0x00003F00` (safeties), then `0x08` (tilt calibration) and `0x07` (focus calibration).

### Readings direction (STM → SoC) ✅ Confirmed (format), 🟡 units

The library does **not** read the UART itself. It connects, as a client, to five Linux abstract-namespace Unix
sockets and receives fixed **7-byte** messages:

| Socket | Readings carried (🟡 grouping inferred from the names) |
|---|---|
| `@socket.stm.status` | revision, status, temperature, fans, light, debug |
| `@socket.stm.propulsion` | velocity, wheel speed, PWM, current |
| `@socket.stm.projector` | focus, tilt, calibration |
| `@socket.stm.imu` | accelerometer, gyroscope, magnetometer |
| `@socket.stm.ir` | IR ranges, errors, calibration (opened only when a configuration level is 2 or more) |

The program that owns the UART receive side and serves these sockets is **not** in `com.keecker.services.apk` nor in
the other extracted APKs (no `bind`/`listen` there). 🔴 Hypothesis: a native system daemon. To identify on the robot,
read-only: `/proc/net/unix`, process list, init `.rc` files (added to `scripts/robot-readonly-snapshot.ps1`).

Reading message layout:

| Byte | Content |
|---|---|
| 0-1 | 16-bit value, least significant byte first. 🟡 STM timestamp or sequence counter; stored per reading ID |
| 2 | Reading ID (`0x00`-`0x26`); other values are logged and dropped |
| 3-6 | 32-bit value, most significant byte first (same order as commands) |

The library keeps the last value of each ID with a "fresh" flag and logs "No fresh data for address" when an expected
reading is missing. In the table, `v0`..`v3` are bytes 3 to 6, `A` = `v0 + 256 × v1` and `B` = `v2 + 256 × v3`
(two 16-bit values, least significant byte first, the same packing as the velocity command).

| ID | Reading | Decoding |
|---|---|---|
| `0x00` | Firmware revision | 4 ASCII characters `v0 v1 v2 v3`, expected letter + 3 digits |
| `0x01` | Status | `A` unsigned, bit meaning unknown |
| `0x02` | Measured velocity | `A` and `B` signed, divided by 1000. 🟡 `A` angular (rad/s), `B` linear (m/s), mirroring command `0x02` |
| `0x03` | Projector focus | `v0` position, `B` unsigned second value (🟡 target or state) |
| `0x04` | Projector tilt | `v0` position, `B` unsigned second value (🟡 target or state) |
| `0x06` | Projector calibration state | `v2` focus calibration, `v3` tilt calibration |
| `0x0A` | Wheel speeds | `A` and `B` signed, divided by 1000 (🟡 m/s, wheel order unknown) |
| `0x0B` | Propulsion PWM | two duty cycles: magnitude `v0` with direction `v1`, magnitude `v2` with direction `v3` (direction byte `0` = negative) |
| `0x0C` | Propulsion current | `A` and `B` unsigned, raw units, one per motor |
| `0x11` | Accelerometer X, Y | `A` = X, `B` = Y, signed, raw sensor units |
| `0x12` | Accelerometer Z, gyroscope X | `A` = accel Z, `B` = gyro X, signed |
| `0x13` | Gyroscope Y, Z | `A` = Y, `B` = Z, signed |
| `0x14` | Magnetometer X, Y | `A` = X, `B` = Y, signed |
| `0x15` | Magnetometer Z, STM temperature | `A` = mag Z signed; `v2` = temperature, signed byte (🟡 °C) |
| `0x16`-`0x21` | IR proximity sensors 0 to 11 | one ID per sensor (index = ID − `0x16`); `A` and `B` unsigned (🟡 range and signal) |
| `0x22` | Ambient light | `A` unsigned |
| `0x23` | IR errors | `A` unsigned (🟡 one bit per sensor) |
| `0x24` | IR calibration status | `A` and `B` unsigned |
| `0x25` | Fan speeds | `A` and `B` unsigned |
| `0x26` | Debug register | 4 bytes `v0`..`v3` |
| `0x05`, `0x07`-`0x09`, `0x0D`-`0x10` | Not handled by this library version | — |

Source: the dispatch table of `ReadingsDispatcher::Dispatch` (39 entries) and the `GetAndDispatch*` decoders; the
velocity divisor is the constant 1000.0 stored in the library.

## Conclusions

The command direction of the protocol is simple: 115200 baud 8N1, 7-byte frames with a `0xBE` start byte and an XOR checksum. An open Android or Linux service can drive the wheels and the projector motors with a few dozen lines, provided the STM is reset and powered as the original library does.

⚠️ Safety: the STM also enforces obstacle and cliff safeties. A replacement driver must never disable them (`toggleSTMSafeties`, `ignoreSTMSafeties`, `toggleKeeckerUnbridled` exist), and must stop the robot when the link is lost.

## Open Questions

- [x] Readings direction (STM → SoC): 7-byte messages over five abstract sockets, IDs and decoding (see Readings direction).
- [ ] Which program owns the UART receive side and serves `@socket.stm.*`, and the raw UART frame it reads from the STM.
- [ ] Units of the raw IMU, current and IR values; meaning of the two IR values and of the status bits.
- [ ] Bits of the safeties value `0x3F00` (command `0x01`); meaning of commands `0x32`-`0x34`, and the polling rate.
- [ ] Watchdog behaviour: does the STM stop the motors if no velocity command arrives for a while?
- [ ] Confirm the units on the robot, by sending a small velocity while the robot is on its back or on a stand, with Harold's approval.
- [ ] Mapping of `/dev/ttyHSL1` to an Open-Q 820 UART (BLSP) for a future device tree.
