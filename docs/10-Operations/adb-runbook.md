# ADB Runbook — Read-only Device Session

**Status:** Ready, not yet run
**Last update:** 2026-10-28

## Objective

Answer the open device questions in one session at the robot, without changing anything on it:

1. Bootloader lock state and OEM unlock support (the decisive gate for a new Android TV build).
2. Partition table (names and sizes), needed before any backup plan.
3. Kernel, device tree, SoC identity.
4. Presence of `/dev/ttyHSL1` and `/dev/resetboard` (STM link).
5. Listening ports, including the companion-app WebSocket.
6. DRM (Widevine) libraries and Cast-related properties.
7. The program that serves the `@socket.stm.*` readings sockets ([stm32-protocol.md](../05-Interfaces/stm32-protocol.md)).

What was already observed or only remembered from earlier sessions is listed in
[Prior-Sessions-Review.md](../02-Acquisition/Prior-Sessions-Review.md).

## Safety

Every command is a read: `getprop`, `cat`, `ls`, `settings get`, `dumpsys`, `pm list`. The script never runs
`root`, `remount`, `install`, `push`, `reboot` or `fastboot`, and never writes a setting.

Out of scope for this session, and each needing Harold's explicit approval first: rebooting into fastboot or recovery,
EDL (Qualcomm 9008), partition dumps, toggling "OEM unlocking".

## Prerequisites

- Windows PC with `adb` (already installed with scrcpy).
- Robot on, developer options enabled, USB debugging allowed. USB cable to the developer port under the robot
  ([platform.md](../07-Hardware/platform.md)), or ADB over Wi-Fi on port 5555.
- On first connection, accept the RSA key prompt on the projected screen. If `adb devices` shows `unauthorized`,
  the prompt was not accepted (this happened in earlier sessions).

## Procedure

1. Connect and check:

   ```powershell
   adb devices -l            # USB
   adb connect <robot-ip>:5555   # or Wi-Fi
   ```

2. Run the snapshot from the repository root:

   ```powershell
   .\scripts\robot-readonly-snapshot.ps1
   # several devices: .\scripts\robot-readonly-snapshot.ps1 -Serial <robot-ip>:5555
   ```

   Output: `firmware/captures/<timestamp>/` (git-ignored), one `.txt` file per command and a `SHA256SUMS.txt`.
   The bootloader summary is printed at the end.

   Owners who share their capture with the community add `-Redact`: serial numbers, the STM identifier and MAC
   addresses are masked before the hashes are computed.

3. Look, without touching: Settings → Developer options → is there an **"OEM unlocking"** switch, and is it greyed
   out? Take a photo of the screen. Do not toggle it.

4. Tell Claude the capture folder name. Claude reads it, updates the documentation, and decides with Harold what
   comes next.

## Reading the bootloader result

| Result | Meaning | Next step |
|---|---|---|
| `ro.boot.flash.locked=0` or `verifiedbootstate=orange` | Bootloader already unlocked | Plan backup, then temporary boot of a test image (approval needed) |
| `flash.locked=1`, `ro.oem_unlock_supported=1`, switch present | Locked but unlockable through fastboot | Plan the backup first: unlocking wipes user data |
| `flash.locked=1`, no unlock support, no switch | Locked, no official path | Study the Qualcomm EDL route (signed programmer for MSM8996) |
| Empty values | Property not set by this firmware | Use `cmdline` (`androidboot.*` fields) and the other files |

## Open Questions

- [ ] First run of this procedure on the robot.
- [ ] Fastboot reachability (`adb reboot bootloader`), in a later approved session.
