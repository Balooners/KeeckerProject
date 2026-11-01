# ADB Runbook — Read-only Device Session

**Status:** First run 2026-11-01 (results below)
**Last update:** 2026-11-01

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

## Results of the first run (2026-11-01)

Harold's robot over USB, `adb devices`: `product:keecker_k1_mb02 model:Keecker device:keecker_k1`. Capture
`firmware/captures/2026-11-01_234644/` (ART-0012).

| Question | Result | Confidence |
|---|---|---|
| Bootloader lock | `ro.boot.flash.locked=0`, `ro.boot.verifiedbootstate=green`, `ro.boot.veritymode=enforcing`, `ro.oem_unlock_supported` empty, `sys.oem_unlock_allowed=0`, `settings oem_unlock_allowed` = null | 🟡 The kernel was told "not locked" while verified boot is green: unusual pair, to confirm in fastboot (`fastboot oem device-info`, needs a reboot and Harold's approval). ✅ The "OEM unlocking" switch exists in Developer options, off (owner photo 2026-06-28, [Prior-Sessions-Review.md](../02-Acquisition/Prior-Sessions-Review.md)) |
| Build | `user`, `release-keys`, `ro.secure=1`, `ro.debuggable=0`, `ro.adb.secure=1`; fingerprint `Keecker/keecker_k1_mb02/keecker_k1:7.0/NRD90M/100140002:user/release-keys`, security patch 2018-01-05 | ✅ |
| Root | No `su`; `adb shell` runs as `shell` | ✅ |
| SoC and kernel | APQ8096 (soc_id 291), Linux 3.18.31 built 2019-03-04 | ✅ |
| Partitions | UFS, six LUNs `sda`..`sdf` (`sda` ≈ 26 GB, its largest partition ≈ 22 GB mapped through `dm-0`, 🟡 probably encrypted userdata); partition **names** not readable without root (`by-name` and sysfs `uevent` denied) | ✅ sizes; names to get in fastboot or EDL |
| STM | Six `@socket.stm.*` sockets served by `/system/bin/spidemux` (SPI); STM32F3 | ✅ ([stm32-protocol.md](../05-Interfaces/stm32-protocol.md)) |
| Robot daemons | `spidemux`, `battery_reader`, `ihm_touch` (touch projection), `kcam_service`, `zcam_service`, `iop` | ✅ running |
| Ports | TCP 5555, 6466, 6467 (Android TV remote), 8008, 8009 (Cast), 8080 (Keecker server), 8443, 9000, 10042, 32500; UDP 1900 (UPnP), 5353 (mDNS), 43045 (Keecker real-time) | ✅ |
| DRM | `libwvdrmengine.so` present; `ro.com.google.gmsversion=7.0_r9` (Google-certified build) | ✅ present; Widevine level still unknown |

Not readable as `shell`: `/proc/cmdline`, `/proc/device-tree`, `/data/misc/keecker/`, partition names, some
`/system/bin` entries (`battery_reader`, `ihm_touch`, `iop`). `grep` on `/proc/net/unix` needs `-a`.

## Fastboot read-only check (run by Harold)

Goal: confirm the bootloader lock state and read the partition list. It needs a reboot into the bootloader, so it is
run by Harold himself (the project's Claude Code deny rules block `adb reboot` and `fastboot` for Claude).

One command does everything below (download and signature check of Platform-Tools, reboot into the bootloader,
read-only commands, reboot to Android, captures in `firmware/captures/<timestamp>_fastboot/`):

```powershell
& "<repository>\scripts\fastboot-readonly-check.ps1"            # add -Redact before sharing the output
```

Manual equivalent. Prerequisite: Google's official **Android SDK Platform-Tools** for Windows, from
<https://developer.android.com/tools/releases/platform-tools>, unzipped to `C:\platform-tools`. If `fastboot devices`
shows nothing once the robot is in the bootloader, Windows lacks the driver: Device Manager → the unknown "Android"
device → update driver with the Google USB Driver (official, same site).

Allowed commands, all read-only:

```powershell
adb reboot bootloader                                   # the robot restarts into the bootloader
C:\platform-tools\fastboot.exe devices
C:\platform-tools\fastboot.exe oem device-info 2>&1 | Tee-Object firmware\captures\fastboot-device-info.txt
C:\platform-tools\fastboot.exe getvar all 2>&1 | Tee-Object firmware\captures\fastboot-getvar-all.txt
C:\platform-tools\fastboot.exe reboot                   # back to Android
```

⛔ Never in this check: `flash`, `erase`, `format`, `oem unlock`, `flashing unlock`, `boot`, `set_active`,
`oem` commands other than `device-info`.

What to read: `Device unlocked: true/false`, `Device critical unlocked`, `Charger screen enabled`, and the
`partition-type` / `partition-size` lines (names and sizes of all partitions, needed for the backup plan).

If the robot shows nothing in bootloader mode (no screen in fastboot), it is expected. If `fastboot reboot` cannot be
sent, unplug the USB cable and hold the top button until the robot restarts (🟡 exact duration unknown).

### Results of the fastboot check (2026-11-02)

Run by Harold with `scripts/fastboot-readonly-check.ps1`; capture `firmware/captures/2026-11-02_003414_fastboot/`
(ART-0013). The robot returned to Android by itself.

Windows (ARM64) had no driver for the bootloader interface (`USB\VID_18D1&PID_D00D`, status Error). Fix without any
download: Device Manager → "Android" → Update driver → Browse my computer → Let me pick → Universal Serial Bus devices →
WinUsb Device. The script then continued from fastboot.

| Field | Value | Meaning | Confidence |
|---|---|---|---|
| `oem device-info` | `Device tampered: false`, `Device unlocked: false`, `Device critical unlocked: false`, `Charger screen enabled: false`, `Display panel: hdmi` | **Bootloader locked.** `ro.boot.flash.locked=0` seen in Android was misleading | ✅ |
| `secure` | `yes` | Secure boot active: only signed images while locked | ✅ |
| `kernel`, `version`, `variant`, `product` | `lk`, `0.5`, `Dragon eMMC`, `MSM8996` | Qualcomm's standard Little Kernel bootloader, close to the DragonBoard 820c default (`version-bootloader` empty) | ✅ |
| Partitions | only `system` (3 GB), `userdata` (≈ 20.8 GB), `cache` (256 MB) are listed | This LK only reports partitions with a declared type; the full table must come from elsewhere | ✅ |
| `max-download-size` | `0x20000000` (512 MB) | | ✅ |
| Battery | `battery-voltage: 3808000` (µV), `battery-soc-ok: yes` | 🟡 a single cell value reported by the SoC side | ✅ |

Analysis:

- 🟡 Probable unlock path: standard Qualcomm LK with `Device critical unlocked` support, and the Android "OEM unlocking"
  switch present. That is the stock Android flow (switch on, then `fastboot flashing unlock`). Not tried.
- ⚠️ Unlocking erases `userdata` (and `cache`): installed apps, pairings, maps. Per-robot calibration lives in other
  partitions (🟡 `persist`), normally untouched by an unlock.
- 🔴 Unknown: LK usually asks for an on-screen confirmation with volume and power keys; the K1 has a single top button
  and its display is the projector over HDMI. Whether the prompt is shown and can be confirmed is the open risk.
- Any unlock is a write to the robot and is Harold's decision.

### Unlock attempt (2026-11-02, approved by Harold)

1. "OEM unlocking" switched on in Developer options (navigation by Claude over `adb shell input`, confirmation by
   Harold with the official app's remote; Claude Code's safety classifier blocked Claude from confirming it).
   Result: `sys.oem_unlock_allowed=1`.
2. Reboot to the bootloader, `fastboot flashing get_unlock_ability` → **`0`**.
3. `fastboot flashing unlock` → **`FAILED (remote: 'oem unlock is not allowed')`**. Nothing erased; `fastboot reboot`
   back to Android. The switch is still on.

Analysis:

- ✅ Mechanism, from Qualcomm's LK source (`app/aboot/aboot.c`, quoted by the
  [tjtech analysis](https://tjtech.me/analyze-oem-unlocking-under-android.html)): LK looks for the "allow OEM unlock"
  flag in the last byte of the partition list `{"config", "frp"}`, **`config` first**, `frp` only when `config` does not
  exist. Android writes the flag to the partition named by `ro.frp.pst`, which is **`frp`** on the K1.
- 🟡 Probable cause: the K1 partition table has a `config` partition (as many msm8996 tables do), so LK reads `config`
  where nothing was written, while Android writes `frp`. An integration slip rather than a deliberate lock: Keecker
  never needed unlocking. Not confirmed: partition names are not readable without root (SELinux denies even a lookup
  by name).
- Consequence: the stock unlock path is closed as long as the last byte of `config` is not set. Setting it needs root
  on Android or Qualcomm EDL (9008) access with a programmer signed for this device (`secure: yes`).

## Open Questions

- [x] Fastboot read-only check (2026-11-02): bootloader locked, `secure: yes`, stock LK.
- [x] Stock unlock: refused (`get_unlock_ability: 0` with the switch on).
- [ ] Confirm the `config` partition (EDL partition table, or the Open-Q 820 / DragonBoard 820c reference `partition.xml`).
- [ ] Route to set the flag or back up the robot: EDL programmer (Keecker, Intrinsyc/Lantronix), or root on Android 7.0
      (security patch 2018-01-05, kernel 3.18).
- [ ] Full partition table (EDL, or a temporary boot once unlocked), and a backup of `persist` and the other
      per-robot partitions before any write.
- [ ] Unlock confirmation on a robot with one button (look for owner reports, LK source for the DragonBoard 820c).
- [x] First run of this procedure on the robot (2026-11-01).
- [ ] Widevine security level (L1 or L3), for example with a DRM info app.
- [ ] Fastboot reachability (`adb reboot bootloader`), in a later approved session.
