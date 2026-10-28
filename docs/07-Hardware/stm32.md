# Motion Microcontroller (STM32) Link

**Status:** In Progress (static analysis, no device access)
**Last update:** 2026-10-28

## Objective

Identify how the main processor talks to the motion microcontroller, and which robot functions that microcontroller owns.

## Context

The Keecker navigation blog post states that a dedicated microcontroller executes motion commands and reads the proximity sensors in real time ([platform.md](platform.md)). This document records the first static look at the library that drives it.

## Evidence

Artifact: `lib/arm64-v8a/libhw_robot_jni.so` from `firmware/apk/com.keecker.services.apk` (not redistributed).

- SHA256: `819120ce5f9c4aaaabb939947e1b6f85080e92c1425e6b9b6cbf177533d12051`
- GNU Build ID: `84e3f35053121e7980c29955bd6ece474a9779c4`
- ELF 64-bit, AArch64, size 702,648 bytes. Dynamic dependencies: `liblog`, `libm`, `libstdc++`, `libdl`, `libc` only (no Android framework dependency besides JNI).

Commands (WSL, binutils-aarch64-linux-gnu):

```bash
unzip -o com.keecker.services.apk 'lib/*'
strings -n 4 libhw_robot_jni.so | grep -iE "/dev/|tty"
aarch64-linux-gnu-nm -D --defined-only libhw_robot_jni.so | grep " Java_"
aarch64-linux-gnu-nm -D --undefined-only libhw_robot_jni.so
aarch64-linux-gnu-nm -DC --defined-only libhw_robot_jni.so | grep "keecker::"
```

Observations:

1. Device paths in strings: `/dev/ttyHSL1` and `/dev/resetboard`.
2. Imported libc functions: `open`, `read`, `write`, `poll`, `select`, `ioctl`, `tcgetattr`, `tcsetattr`, `cfsetispeed`, `cfsetospeed`, `tcflush`. These are standard POSIX serial-port (termios) calls.
3. C++ classes (exported symbols):
   - `keecker::uart_driver::Uart` with `Open`, `Read`, `Write`, `Flush`, `FlushInput`, `WaitForData`, `AvailableData`, `Close`;
   - `keecker::motor_controller::MotorController` with `Connect`, `Disconnect`, `PowerOn`, `PowerOff`, `UartWrite(unsigned char, unsigned int)`;
   - `keecker::motor_controller::ReadingsDispatcher` with one dispatcher per reading type;
   - `keecker::motor_controller::StmData` with `SetPropulsionPwm`, `SetFansPwm`, `SetProjectorPosition`, `SetProjectorCalibration`.
4. 24 JNI entry points belong to the Java class `com.keecker.embedded.stm.motorcontrol.HwRobotService`, for example `setVelocityCommand`, `setPids`, `setWheelsDimensions`, `setPropulsionDutycycles`, `setPwmMovementControl`, `cmdProjectorTilt`, `cmdProjectorFocus`, `cmdProjectorCalibration`, `setFansDutycycles`, `putBatteryInDeepSleep`, `toggleSTMSafeties`, `ignoreSTMSafeties`, `startIROffsetCalibration`, `startIRCrosstalkCalibration`, `writeIRCalibrationsToFlash`, `setGyroSensitivity`, `startMainTest`.

Readings dispatched from the microcontroller (`ReadingsDispatcher::Dispatch*`): wheel speed, velocity, propulsion current, propulsion PWM, IR ranges, IR errors, IR calibration status, accelerometer, gyroscope, magnetic field, ambient light (ALS), fan speed, projector focus, projector tilt, projector focus and tilt calibration, STM temperature, firmware revision, status, debug register.

## Analysis

- ✅ Confirmed: the main processor talks to the microcontroller over a **UART**, `/dev/ttyHSL1` (Qualcomm "HSL" high-speed-lite serial port), using termios. Evidence: device string, termios imports, `uart_driver::Uart` class, `MotorController::UartWrite`.
- ✅ Confirmed: the microcontroller is an STM part. The Java package `com.keecker.embedded.stm` and the methods `toggleSTMSafeties` and `DispatchSTMTemperature` name it.
- ✅ Confirmed: the microcontroller owns much more than the wheels. It also handles the 12 IR proximity sensors (with calibration stored in its flash), the IMU (accelerometer, gyroscope, magnetometer), the ambient light sensor, the fans, the **projector focus and tilt motors**, battery deep sleep, and the motion safeties.
- 🟡 Probable: commands are short frames of a command byte plus a value (`UartWrite(unsigned char, unsigned int)`).
- 🔴 Hypothesis: `/dev/resetboard` resets or powers the microcontroller (GPIO exposed by the Keecker kernel).

## Conclusions

The robot hardware behind the STM is reachable through one serial port, with no proprietary kernel driver involved on the motion side. On Linux, a UART is a standard device. Once the frame format is decoded, a small open driver (ROS 2 node) can replace `libhw_robot_jni.so` and give access to propulsion, safeties, IMU, IR sensors, fans and projector motors.

## Open Questions

- [x] Baud rate, termios settings, command frame format and command IDs: see [stm32-protocol.md](../05-Interfaces/stm32-protocol.md).
- [ ] Reading frames sent back by the STM.
- [x] `/dev/resetboard` is the STM reset GPIO (`1` written, 100 ms wait). Kernel driver still unknown.
- [ ] Which UART of the Open-Q 820 `ttyHSL1` maps to, for the future Linux device tree.
- [ ] STM firmware version (`DispatchRevision`) and whether firmware updates went through `com.keecker.services.ota`.
- [ ] Whether `toggleKeeckerUnbridled` disables speed limits (safety relevant).
