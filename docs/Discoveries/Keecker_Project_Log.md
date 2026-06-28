## 2026-06-28 — Main ODEX extraction

### File

firmware/odex/com.keecker.services.odex

### Size

70,189,776 bytes (67 MB)

### SHA256

ABA15779A89B2A429D71A541119BD70062FABBFD09233F6274914DD92097FBDC

### Acquisition

```bash
adb pull /system/priv-app/com.keecker.services/oat/arm64/com.keecker.services.odex
```

### Notes

- Successfully extracted over ADB Wi-Fi.
- Initial transfer failures were caused by poor Wi-Fi signal quality, not by the device.
- The file is now preserved as forensic evidence and will be used for Java bytecode recovery.

---

# 2026-06-28 — Main ODEX Analysis

## Evidence

File:

firmware/odex/com.keecker.services.odex

SHA256:

ABA15779A89B2A429D71A541119BD70062FABBFD09233F6274914DD92097FBDC

Size:

70,189,776 bytes

## Binary Header

Magic:

7F 45 4C 46

Interpretation:

- ELF container
- 64-bit
- ARM64 (AArch64)
- Android ART ODEX/OAT executable

## Acquisition

```bash
adb pull /system/priv-app/com.keecker.services/oat/arm64/com.keecker.services.odex
```

Notes:

- Successfully extracted over ADB.
- Previous transfer failures were caused by poor Wi-Fi signal quality.
- This file is preserved as forensic evidence.
---

# 2026-06-28 — Boot OAT extraction

## File

firmware/boot-oat/boot.oat

## Size

10,331,088 bytes

## Acquisition

```bash
adb pull /system/framework/arm64/boot.oat firmware/boot-oat/

# 2026-06-28 — Phase II ADB Exploration

## Android Platform

Confirmed:

* Android 7.0
* SDK 24
* ARM64
* Qualcomm Snapdragon 820 (MSM8996)

## ADB

USB:

Working

Wi-Fi:

Working

```
adb connect 192.168.1.191:5555
```

Stable connection confirmed.

## Binder

133 Binder services identified.

Proprietary services discovered:

* KeeckerRegistryService
* IhmService
* RecoveryService

## APK Acquisition

Extracted:

* com.keecker.services.apk
* com.keecker.services.ota.apk
* com.keecker.apps.data.apk
* com.keecker.apps.diagnostic.apk
* com.keecker.apps.launcher_netflix.apk
* K1_LeanbackCustomizer.apk
* K1_TvSetupCustomizer.apk
* KeeckerLeanbackWidget.apk

SHA256 hashes recorded.

## Native Libraries

Confirmed:

* ROS
* OpenCV
* TensorFlow
* SLAM
* Navigation
* Object Detection
* JNI Robot Control
* Native Camera

## ODEX

Extracted:

firmware/odex/com.keecker.services.odex

Size:

70,189,776 bytes

SHA256:

ABA15779A89B2A429D71A541119BD70062FABBFD09233F6274914DD92097FBDC

Binary format:

* ELF
* ARM64
* Android ART ODEX

## boot.oat

Extracted.

Purpose:

Android boot classpath required for ART/OAT analysis.

## Conclusion

The Android platform has now been successfully acquired.

Future work will focus on reconstructing Java bytecode from the ODEX files and analysing proprietary robot services.
