# KeeckerOS

> **Open Reverse Engineering & Preservation Project for the Keecker K1**

KeeckerOS is an open-source project dedicated to documenting, understanding and preserving the Keecker K1 robotic platform.

The objective is to build the most complete technical documentation ever produced for the Keecker robot and eventually create an open software platform allowing existing robots to continue operating for many years.

---

# Objectives

* Reverse engineer the Android platform
* Document the complete software architecture
* Reverse proprietary APKs and ODEX files
* Identify Binder services
* Understand JNI interfaces
* Document robot hardware
* Understand navigation, SLAM and perception
* Document OTA updates
* Build an open SDK
* Develop KeeckerOS

---

# Current Status

## Hardware

* Keecker K1
* Qualcomm Snapdragon 820 (MSM8996)
* ARM64

## Android

* Android 7.0
* SDK 24
* Security Patch 2018-01-05

## Reverse Engineering

✅ USB ADB

✅ Wi-Fi ADB

✅ APK extraction

✅ ODEX extraction

✅ Binder services discovered

✅ AndroidManifest analysed

## Native Platform

Confirmed native technologies:

* ROS
* OpenCV
* TensorFlow
* SLAM
* Object Detection
* Native Camera
* JNI Robot Control

---

# Repository Structure

```text
docs/
firmware/
network/
reverse/
scripts/
sdk/
tools/
```

---

# Documentation

Technical documentation is organised by domain.

* Architecture
* Android
* Hardware
* Binder
* Native Libraries
* OTA
* Reverse Engineering
* Discoveries

Every technical statement is backed by direct evidence (ADB, APK, ODEX, binaries or logs).

---

# Long-Term Vision

KeeckerOS aims to become the reference documentation and development platform for the Keecker K1 while respecting the engineering work of the original Keecker team.
