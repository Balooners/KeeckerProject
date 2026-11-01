# Artifact Register

Canonical register of known Keecker K1 artifacts.

Redistribution status defaults to `Unknown` until legal review is complete. Proprietary binaries, APKs, ODEX/OAT files, and firmware extracts must not be redistributed publicly while their status is unresolved.

| ID | Filename | Type | Source path on device | Local path | Size | SHA256 | Acquisition command | Redistributable | Notes |
|---|---|---|---|---|---:|---|---|---|---|
| ART-0001 | com.keecker.services.apk | APK | Unknown; resolve with `adb shell pm path com.keecker.services` | Not present in repository | Unknown | Unknown | `adb shell pm path com.keecker.services` then `adb pull <device-path> <local-path>` | Unknown | Listed as extracted in discovery notes; metadata not yet normalized in this register. |
| ART-0002 | com.keecker.services.ota.apk | APK | Unknown; resolve with `adb shell pm path com.keecker.services.ota` | Not present in repository | Unknown | Unknown | `adb shell pm path com.keecker.services.ota` then `adb pull <device-path> <local-path>` | Unknown | Listed as extracted in discovery notes; metadata not yet normalized in this register. |
| ART-0003 | com.keecker.apps.data.apk | APK | Unknown; resolve with `adb shell pm path com.keecker.apps.data` | Not present in repository | Unknown | Unknown | `adb shell pm path com.keecker.apps.data` then `adb pull <device-path> <local-path>` | Unknown | Listed as extracted in discovery notes; metadata not yet normalized in this register. |
| ART-0004 | com.keecker.apps.diagnostic.apk | APK | Unknown; resolve with `adb shell pm path com.keecker.apps.diagnostic` | Not present in repository | Unknown | Unknown | `adb shell pm path com.keecker.apps.diagnostic` then `adb pull <device-path> <local-path>` | Unknown | Listed as extracted in discovery notes; metadata not yet normalized in this register. |
| ART-0005 | com.keecker.apps.launcher_netflix.apk | APK | Unknown; resolve with `adb shell pm path com.keecker.apps.launcher_netflix` | Not present in repository | Unknown | Unknown | `adb shell pm path com.keecker.apps.launcher_netflix` then `adb pull <device-path> <local-path>` | Unknown | Listed as extracted in discovery notes; metadata not yet normalized in this register. |
| ART-0006 | K1_LeanbackCustomizer.apk | APK | Unknown | Not present in repository | Unknown | Unknown | `adb pull <device-path> <local-path>` | Unknown | Listed as extracted in discovery notes; package/source path needs confirmation. |
| ART-0007 | K1_TvSetupCustomizer.apk | APK | Unknown | Not present in repository | Unknown | Unknown | `adb pull <device-path> <local-path>` | Unknown | Listed as extracted in discovery notes; package/source path needs confirmation. |
| ART-0008 | KeeckerLeanbackWidget.apk | APK | Unknown | Not present in repository | Unknown | Unknown | `adb pull <device-path> <local-path>` | Unknown | Listed as extracted in discovery notes; package/source path needs confirmation. |
| ART-0009 | com.keecker.services.odex | ODEX | `/system/priv-app/com.keecker.services/oat/arm64/com.keecker.services.odex` | `firmware/odex/com.keecker.services.odex` | 70189776 | ABA15779A89B2A429D71A541119BD70062FABBFD09233F6274914DD92097FBDC | `adb pull /system/priv-app/com.keecker.services/oat/arm64/com.keecker.services.odex firmware/odex/` | Unknown | Local file present. ART/OAT Android runtime artifact in ELF container. |
| ART-0010 | boot.oat | OAT | `/system/framework/arm64/boot.oat` | `firmware/boot-oat` | 10331088 | CD1FC9D22E149CA8C69CB59E82245F4062CF321BF7791541C2206EFB42672B4E | `adb pull /system/framework/arm64/boot.oat firmware/boot-oat/` | Unknown | Local file present as `firmware/boot-oat`; filename/path should be normalized later without losing provenance. |
| ART-0011 | spidemux | Native executable (ELF AArch64, Android 24, stripped) | `/system/bin/spidemux` | `firmware/bin/spidemux` (git-ignored) | 22624 | 2793BB5722183AA0961AAC631C412A906486A8B68919A4114EC0152CB6F9B713 | `adb pull /system/bin/spidemux firmware/bin/spidemux` (2026-11-01, robot `keecker_k1_mb02`, build 100140002) | No | STM readings daemon: SPI reader and `@socket.stm.*` server ([stm32-protocol.md](../05-Interfaces/stm32-protocol.md)). |
| ART-0012 | Read-only snapshot | Text captures | Many (`getprop`, `/proc`, `ps`, …) | `firmware/captures/2026-11-01_234644/` (git-ignored, `SHA256SUMS.txt` inside) | — | see `SHA256SUMS.txt` | `scripts/robot-readonly-snapshot.ps1` | No (contains serial numbers) | First run of the runbook ([adb-runbook.md](../10-Operations/adb-runbook.md)). |
| ART-0013 | Fastboot read-only check | Text captures | Bootloader (`fastboot getvar all`, `fastboot oem device-info`) | `firmware/captures/2026-11-02_003414_fastboot/` (git-ignored, `SHA256SUMS.txt` inside) | — | see `SHA256SUMS.txt` | `scripts/fastboot-readonly-check.ps1` | No (contains the serial number) | Bootloader locked, `secure: yes`, LK 0.5 ([adb-runbook.md](../10-Operations/adb-runbook.md)). |

## Open Metadata Tasks

- Confirm APK source paths.
- Add APK sizes and SHA256 hashes.
- Decide public redistribution status.
- Decide whether large binary artifacts stay in Git, move to Git LFS, or remain local-only.
