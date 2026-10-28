# Companion App ↔ Robot Protocol

**Status:** In Progress (static analysis of the official app and of the robot server; not yet observed on the network)
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

Artifact: robot side, `com.keecker.services` 1.14.6, Java classes recovered from `com.keecker.services.odex`
(SHA256 `ABA15779A89B2A429D71A541119BD70062FABBFD09233F6274914DD92097FBDC`, method in
[Reverse-Environment.md](../10-Operations/Reverse-Environment.md)). The robot code is not obfuscated. Classes read:
`com.keecker.services.remote.httpserver.*` (HTTP and WebSocket server), `com.keecker.services.remote.net.*`
(connections, handshake), `com.keecker.services.security.SecurityManager` (pairing rules),
`com.keecker.common.messages.{MessageUtils, ProtobufCommunicationImp}`, `com.keecker.common.utils.{Network, Communication}`,
`com.keecker.common.utils.nsd.{NsdBroadcaster, Constants}`. Constants were read from the DEX static values
(`rea inspect-android-class`).

Artifact: network scan of 2026-06-28 (`explorer/reports/NET-8080.json`, `explorer/raw/8080/`): port 8080 serves a page
titled "Keecker File uploader", Jetty error pages, and static files whose `Last-Modified` date is the server start time.

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
- ✅ Robot side (`NsdBroadcaster`): the service name is the robot name, the port is the HTTP server port, and the TXT
  record holds `uuid` (robot UUID), `v` (services version code) and `vn` (services version name).

### Wi-Fi transport ✅

- **WebSocket** at `ws://<host>:<port>/remote/keecker.ws`, where host and port come from the mDNS record. OkHttp client.
- Connect, read and write timeouts are 10 s. A keep-alive is sent every 5 s, and the connection is considered dead after 10 s without incoming data.
- Payloads are **binary** WebSocket frames (byte arrays handed to the message layer).
- The same host also exposes HTTP at `http://<host>:<port>`, probably the file transfer service. Its port comes from the record and is not necessarily the WebSocket port.

### Robot server ✅ Confirmed (robot side)

- One embedded **Jetty** server (`HttpServerService`) serves the file uploader web page, the upload servlet, static
  directories and every WebSocket endpoint, on a single port (`Network.getHttpPort`).
- **Port 8080** ✅: the port constant is set at runtime and could not be read statically, but the 2026-06-28 scan found
  the "Keecker File uploader" page, Jetty error pages and start-time file dates on 8080, which is this server.
  Clients should still take the port from the mDNS record.
- A WebSocket connection is not handled by Jetty itself. `WebsocketHandler` opens an Android local (Unix) socket to the
  remote service, sends the request path and the phone IP, then relays every binary frame both ways. On that internal
  socket, each message is prefixed by its length in ASCII decimal followed by a `0x00` byte, and `0x03` marks the end of
  the stream. This internal framing never appears on the network.
- **Keep-alive**: a binary frame of exactly one byte `0xAA` is echoed back by Jetty and never reaches the service.
  This is the app's 5-second keep-alive.
- **Framing on the WebSocket** ✅: one binary frame carries exactly one protocol message (a `KeeckerMessage`, encrypted
  after the handshake). There is no length prefix.
### Real-time control over UDP ✅ Confirmed (robot side)

The remote service also listens on **UDP port 43045** (`Network.UDP_PORT`, `UDPSocketManager`), for low-latency
joystick and pointer input:

- A datagram is accepted only from an IP address that already has an authenticated WebSocket session; it is
  decrypted with that phone's public key (same crypto manager as the WebSocket).
- Plain content (`UDPMessage`): 1 command byte, then `x` and `y` as two 64-bit IEEE doubles, big-endian
  (Java `ByteBuffer` default), 17 bytes. 🟡 The robot decrypts its whole receive buffer (`ENCRYPTED_SIZE`), so a client
  should send exactly nonce (24) + MAC (16) + 17 = 57 bytes.
- Commands (IDs from the official app, where the enum initialiser is intact):

| ID | Command | Robot action |
|---|---|---|
| 0 | `MOUSE_MOVE` | Move the on-screen pointer by (`x`, `y`) |
| 1 | `MOUSE_DOWN` | Pointer down |
| 2 | `MOUSE_CLICK` | Click |
| 3 | `MOUSE_END_DRAG` | Pointer up |
| 4 | `MOUSE_SCROLL` | Wheel: `x` = 1 up, 0 down; `y` = amount |
| 32-39 | `DPAD_UP`, `DPAD_DOWN`, `DPAD_LEFT`, `DPAD_RIGHT`, `DPAD_CENTER`, `DPAD_BACK`, `DPAD_HOME`, `DPAD_PLAY_PAUSE` | Remote-control keys |
| 48 | `MOVE` | Manual driving: `x` = linear, `y` = angular, each between −1 and 1 (clamped by the movement planner; the official SDK maps 1 to 0.5 m/s and 3 rad/s). `x` = `y` = 0 releases manual control. Any `MOVE` also stops "follow me" |

⚠️ `MOVE` drives the robot. The open test client does not implement it.

### Bluetooth transport ✅

- Classic Bluetooth RFCOMM, service UUID **`7fdc2820-6bc9-11e3-981f-0800200c9a66`**.

### Message layer (from `keecker/remote-api`)

- Every message is wrapped in `KeeckerMessage { type_name, message bytes }`, where `type_name` is the fully qualified class name of the inner protobuf message.
- The first exchange is `AuthMessage { key, userId, deviceId, token, errorCode, platform, versionCode }`: the app sends its public key (and optionally an invitation token), the robot answers with its own public key, then all traffic is encrypted.
- Since the final release, a new phone is authorised by pressing the robot's top button 6 times (offline pairing). Pairing still works with the official app on a recent phone (tested by Harold).
- ✅ `type_name` is the Java class name of the inner message **without** the `com.keecker.common.messages.` prefix,
  for example `AuthMessage` or `projection.ProjectorStatusMessage` (`MessageUtils`). `RegisterMessage` and
  `UnregisterMessage`, on the other hand, carry the **full** class name of the message to subscribe to.

### Handshake ✅ Confirmed (robot side)

From `RemoteCommunicationImp` and `SecurityManager`:

1. The phone sends `AuthMessage` **in clear** (a plain `KeeckerMessage`) with `key` (its raw 32-byte public key) and
   `deviceId`, both required, plus `userId` (account identifier), optional `token`, `platform` and `versionCode`.
2. If `versionCode` is not 0, the robot first answers `ServiceVersionMessage` (services version, model `K1`,
   `forceUpgrade` always false in 1.14.6). Otherwise it assumes protocol v1.
3. The robot checks the device (rules below). If accepted, it sends `AuthMessage` with its own public key, in clear,
   and switches the connection to encrypted mode. All later frames, in both directions, are encrypted.
4. If refused, it sends `AuthMessage` with `errorCode`, waits one second, and closes. The robot also says
   "unauthorized" aloud.

Pairing rules (`SecurityManager.validateUser`), in order:

| Case | Result |
|---|---|
| Public key known, and registered for this `deviceId` | Accepted |
| Robot in setup state, and `userId` given | ⚠️ All users and keys are deleted, this device becomes the only admin |
| Pairing mode on (6 presses on the top button; the robot says "pairing"), and `userId` given | Device added as admin, pairing mode off |
| Robot has no key at all, and `userId` given | Device added as admin |
| Invitation `token` and `userId` given | Token consumed, device added with the token's level and dates |
| Otherwise | Refused (`UNKNOWN_USER`, `INCORRECT_PUBLIC_KEY_AND_DEVICE_ID`, …) |

Remote (cloud) connections were limited to admin users. Invitations could have start and end dates.

### Security observations 🟡

- The first exchange is not authenticated: during pairing, a device on the same network could intercept the key
  exchange. Outside pairing mode, an unknown key is refused. An open client should remember the robot key after the
  first pairing and alert if it changes (trust on first use).
- The setup state accepts any device and wipes existing users: our own service should keep pairing tied to a physical
  action on the robot.

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

A test client implementing all four pieces is in `scripts/remote-client/` ([remote-client.md](../10-Operations/remote-client.md)).
It passes an offline test against a simulated robot; it has not yet run against a real robot.

## Open Questions

- [x] Port number and TXT record fields of `_keecker._tcp`: port 8080, TXT `uuid`, `v`, `vn` (see Robot server). To observe live: `scripts/remote-client` `discover`.
- [x] libsodium construction, key storage and nonce handling (see Encryption).
- [x] `AuthMessage` travels in clear inside a `KeeckerMessage`; the robot stores users and keys in its security database (see Handshake).
- [x] Framing inside the binary WebSocket frames: one message per frame, no length prefix; `0xAA` keep-alive.
- [x] Server side: Jetty `HttpServerService`, `WebsocketHandler` bridge, `WebSocketServer` and `RemoteCommunicationImp` in the remote service.
- [ ] First live run of the test client (pairing, projector status, LED).
- [x] Role of UDP port 43045: encrypted real-time pointer, D-pad and manual driving commands (see Real-time control over UDP).
- [ ] Role of BLE (advertisement content) and of the Bluetooth RFCOMM link during setup.
