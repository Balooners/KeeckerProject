# Keecker Project
## Technical Discoveries Log

Version: 1.0
Last update: 2026-06-28

---

# Project objective

Reverse engineer the Keecker robot in order to:

- understand its software architecture
- discover every available network service
- identify undocumented APIs
- document the complete platform
- build the Keecker Explorer framework

---

# Hardware

## Robot

Manufacturer

    Keecker

Model

    Keecker K1

Main SoC

    Qualcomm Snapdragon 820 (MSM8996)

Architecture

    ARM64 (arm64-v8a)

Android

    Android 7.0 (SDK 24)

Security patch

    2018-01-05

Build fingerprint

    Keecker/keecker_k1_mb02/keecker_k1:7.0/NRD90M/100140002:user/release-keys

---

# Network discovery

Detected open ports

| Port | Status | Description |
|-------|--------|-------------|
|5555|OPEN|ADB over TCP|
|8008|OPEN|Google Cast|
|8009|OPEN|Google Cast TLS|
|8080|OPEN|React Web UI|
|8443|OPEN|Google Cast Eureka API|
|9000|OPEN|Unknown|

---

# HTTP services

## Port 8080

React application.

Discovered assets

- main.95994ac6.js
- main.de605b4c.css

No REST API discovered.

---

## Port 8443

Google Cast / Eureka API.

Confirmed endpoints

GET

    /setup/eureka_info

GET

    /setup/eureka_info?options=detail

Returned information

- Manufacturer
- Model
- Build revision
- Public RSA key
- Uptime
- Device name
- SSDP UUID

Interesting endpoint

/setup/reboot

Returns

    HTTP 405

Meaning:

Endpoint exists but requires another HTTP method.

---

# JavaScript analysis

Downloaded bundle

    static_js_main.95994ac6.js

Detected

- Google Cast
- Dial

No REST endpoint discovered.

No fetch()

No axios()

No websocket()

---

# Android Debug Bridge

USB port discovered under the robot.

First issue

USB cable was charge-only.

Replacing the cable immediately exposed the Android device.

ADB state

Initial

    unauthorized

RSA authorization accepted on robot screen.

Current state

    device

ADB over TCP

Confirmed.

Connection

adb connect 192.168.1.191:5555

Works without USB cable.

---

# Android properties

ADB daemon

Running.

TCP ADB

5555

USB mode

mtp,adb

OTA server

https://0-6-dot-backend-prod.appspot.com/keecker/ota

---

# Keecker packages

Confirmed packages

com.keecker.services

com.keecker.services.ota

com.keecker.apps.data

com.keecker.apps.diagnostic

com.keecker.apps.launcher_netflix

---

# Binder services

Discovered proprietary services

KeeckerRegistryService

IhmService

RecoveryService

These services are likely the main internal IPC interfaces.

---

# Current strategy

Previous strategy

Network crawling.

New strategy

ADB-first reverse engineering.

Future work

- extract APKs
- reverse Java code
- identify Binder interfaces
- document internal APIs
- identify robot control services
- integrate discoveries into Keecker Explorer

---

# Milestones

✓ Network scanner

✓ HTTP crawler

✓ JavaScript downloader

✓ JavaScript analyzer

✓ JSON reports

✓ Google Cast discovery

✓ Eureka API discovery

✓ USB ADB discovery

✓ Wi-Fi ADB discovery

Next milestone

APK extraction and reverse engineering.
