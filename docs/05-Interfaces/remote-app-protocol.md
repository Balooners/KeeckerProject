# Companion App ↔ Robot Protocol

**Status:** In Progress (static analysis of the official app; not yet observed on the network)
**Last update:** 2026-10-28

## Objective

Describe how the official Keecker companion app finds the robot, connects to it and exchanges messages, so that an open replacement app can talk to existing robots.

## Context

- Message definitions are public in `keecker/remote-api` (protobuf, see [Public-Sources.md](../02-Acquisition/Public-Sources.md)).
- Transport and discovery are not documented by Keecker. They come from the official app, analysed with REA/JADX ([Reverse-Environment.md](../10-Operations/Reverse-Environment.md)).
- The app is obfuscated: its class names are single letters. Names below describe roles, not original identifiers.

## Evidence

Artifact: official Android companion app (not redistributed).

| Field | Value |
|---|---|
| File | `Keecker_2.0.3_APKPure.apk` (downloaded by Harold from APKPure; runs on a Samsung S25 Ultra) |
| SHA256 | `131245524fa5763ec795dfffc3fa9e7dce1e806007ad4992f922c11f44b27c5c` |
| Package | `com.keecker.remote`, version 2.0.3 (code 20003), minSdk 21, targetSdk 26 |
| Signer | `CN=KEECKER, O=Android, L=PARIS, C=FR, emailAddress=contact@keecker.com`, certificate SHA256 `dd84943940b6ab0998e62142c64907a5464e18c1b0825172b4a7d321f78b3451`, valid 2017-01-18 to 2044-06-05; v1 and v2 signatures verified, digest matches |
| Same signer as the robot | ✅ `com.keecker.services.apk` from the robot carries the same certificate. The APKPure copy is therefore the genuine Keecker build |
| Native libraries | `libsodiumjni.so` (libsodium), `libjingle_peerconnection_so.so` (WebRTC), `libsharedmemory.so` |

Commands: `rea inspect-apk-signature`, `rea inspect-android-package`, `rea search-android-classes`, `rea inspect-android-class`, `rea inspect-android-method`, plus a string search on `classes.dex`.

## Analysis

### Connection types

The app defines four connection types (`com.keecker.common.messages.ConnectionType`). Each discovered robot can be reachable through several of them at once, merged by robot UUID.

| Type | Used for | Evidence | Confidence |
|---|---|---|---|
| `WIFI` | Normal local control | NSD discovery class, WebSocket connection class | ✅ Confirmed |
| `BLUETOOTH` | Classic Bluetooth RFCOMM link (setup, no Wi-Fi) | Bluetooth scanner, `BluetoothSocket` connection class, service UUID below | ✅ Confirmed |
| `BLE` | Discovery of nearby robots | Scan logic treats BLE results separately | 🟡 Probable (role) |
| Remote / Pusher | Access from outside the home through Keecker's cloud (Pusher real-time service) | `com.keecker.common.messages.pusher.PusherConnection`, `DistantConnectionMessage` | 🟡 Probable; the service no longer exists |

### Discovery on the local network ✅

- The robot advertises a DNS-SD (mDNS) service of type **`_keecker._tcp.`**, found with Android `NsdManager`.
- The resolved service gives the robot UUID, its name, the host address and the port.
- An earlier search for "Bluetooth" found no class because the Bluetooth code is obfuscated. It is located through the `android.bluetooth` intents it registers.

### Wi-Fi transport ✅

- **WebSocket** at `ws://<host>:<port>/remote/keecker.ws`, where host and port come from the mDNS record. OkHttp client.
- Connect, read and write timeouts are 10 s. A keep-alive is sent every 5 s, and the connection is considered dead after 10 s without incoming data.
- Payloads are **binary** WebSocket frames (byte arrays handed to the message layer).
- The same host also exposes HTTP at `http://<host>:<port>`, probably the file transfer service. Its port comes from the record and is not necessarily the WebSocket port.

### Bluetooth transport ✅

- Classic Bluetooth RFCOMM, service UUID **`7fdc2820-6bc9-11e3-981f-0800200c9a66`**.

### Message layer (from `keecker/remote-api`)

- Every message is wrapped in `KeeckerMessage { type_name, message bytes }`, where `type_name` is the fully qualified class name of the inner protobuf message.
- The first exchange is `AuthMessage { key, userId, deviceId, token, errorCode, platform, versionCode }`: the app sends its public key (and optionally an invitation token), the robot answers with its own public key, then all traffic is encrypted.
- Since the final release, a new phone is authorised by pressing the robot's top button 6 times (offline pairing). Pairing still works with the official app on a recent phone (tested by Harold).

### Encryption ✅ Confirmed (app side)

From the app classes in `com.keecker.common.messages.crypto` and the bundled libsodium-jni wrapper:

- **Keys**: each side has a 32-byte public key and a 32-byte secret key (libsodium `crypto_box` key pair). The app stores its own pair in the `KEYSTORE` shared preferences, under `PUB_KEY` and `PRIV_KEY`. Keys are serialised as Base64, URL-safe alphabet, without padding or line wraps.
- **Encrypted frame**: `nonce (24 random bytes) || box`, where `box` is the libsodium public-key authenticated encryption of the plaintext with the peer's public key and the sender's secret key. The box keeps the 16-byte authenticator and drops the 16 zero bytes of the classic NaCl output: the same layout as `crypto_box_easy`.
- 🟡 Primitive: Curve25519-XSalsa20-Poly1305 (`crypto_box`), inferred from the wrapper's 32/24/32/16 byte constants. The exact native function name is still to be confirmed.
- **Layering**: an "encrypted connection" wraps the transport (WebSocket or Bluetooth). It encrypts every outgoing byte array and decrypts every incoming one, dropping frames that fail authentication.

## Conclusions

An open client needs four pieces, all now identified:

1. mDNS browse for `_keecker._tcp`;
2. a WebSocket to `/remote/keecker.ws`;
3. the libsodium key exchange of `AuthMessage`;
4. protobuf messages from `remote-api`.

This makes a new companion app possible for current robots, and keeps the same protocol available to the future Android TV build.

## Open Questions

- [ ] Port number and TXT record fields of `_keecker._tcp` (to observe at home: `avahi-browse -rt _keecker._tcp` or `dns-sd -B _keecker._tcp`).
- [x] libsodium construction, key storage and nonce handling (see Encryption).
- [ ] Whether `AuthMessage` travels in clear inside a `KeeckerMessage`, and how the robot stores authorised keys.
- [ ] Framing inside the binary WebSocket frames (raw protobuf, or a length prefix).
- [ ] Server side: which class in `com.keecker.services` hosts `/remote/keecker.ws`.
- [ ] Role of BLE (advertisement content) and of the Bluetooth RFCOMM link during setup.
