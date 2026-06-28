# Changelog

## 2026-06-28 — Phase II: ADB Exploration

### Added

* Confirmed ADB over USB
* Confirmed ADB over Wi-Fi
* Identified Android platform (Android 7.0 / API 24)
* Confirmed Qualcomm Snapdragon 820 (MSM8996)
* Enumerated 133 Binder services
* Identified proprietary Keecker Binder services
* Extracted proprietary APKs
* Extracted main ODEX (`com.keecker.services.odex`)
* Extracted Android boot image (`boot.oat`)
* Identified native robotics libraries
* Confirmed ROS components
* Confirmed OpenCV integration
* Confirmed TensorFlow integration
* Started technical documentation structure

### Changed

* Reverse engineering strategy changed from network-first to ADB-first.

### Notes

No modification has been made to the robot.

All operations performed were read-only.
