# Remote Client — Test Procedure

**Status:** Ready, offline self-test passes; not yet run against a robot
**Last update:** 2026-10-28

## Objective

Check, with a real K1, that the companion-app protocol documented in
[remote-app-protocol.md](../05-Interfaces/remote-app-protocol.md) is complete: discovery, pairing, encryption,
status messages and a harmless projector command. This is the base of the future open companion app.

## Safety

- The client reads status and drives only the projector LED and tilt. It never sends a movement command.
- Pairing adds one admin user on the robot. It does not remove the existing users, unless the robot is in its setup
  state (first start or factory reset): do not run it on a robot in setup.
- The client key pair and the robot keys it has seen are stored in `%USERPROFILE%\.keeckeros\remote-client.json`.
  Keep that file private; it is outside the repository.

## Prerequisites

- PC on the same Wi-Fi network as the robot, robot awake.
- Python 3.10 or newer. Create the environment in a short path: with a long path, Windows fails to load a `zeroconf`
  DLL ("file name too long").

  ```powershell
  py -3 -m venv $env:USERPROFILE\.keeckeros\venv
  & $env:USERPROFILE\.keeckeros\venv\Scripts\python.exe -m pip install -r scripts\remote-client\requirements.txt
  Set-Alias kr "$env:USERPROFILE\.keeckeros\venv\Scripts\python.exe"
  ```

## Procedure

1. Offline check (no robot needed):

   ```powershell
   kr scripts\remote-client\keecker_remote.py selftest
   ```

2. Find the robot. Note its address, port and TXT fields for the documentation:

   ```powershell
   kr scripts\remote-client\keecker_remote.py discover
   ```

3. Pair and read the status. The first attempt is expected to be refused with `UNKNOWN_USER`: press the top button of
   the robot 6 times (it says "pairing"), then run the same command again.

   ```powershell
   kr scripts\remote-client\keecker_remote.py status --host <robot-ip>
   ```

   Expected: `ServiceVersionMessage` (1.14.6), "Authenticated, session encrypted", then a projector status and,
   if the robot pushes it, a battery status.

4. Projector commands:

   ```powershell
   kr scripts\remote-client\keecker_remote.py projector --host <robot-ip> --led off
   kr scripts\remote-client\keecker_remote.py projector --host <robot-ip> --led on
   kr scripts\remote-client\keecker_remote.py projector --host <robot-ip> --tilt 45
   ```

5. Optional: `listen --host <robot-ip> --seconds 30` prints every message the robot pushes, for the documentation.

6. Copy the console output into a file under `firmware/captures/` (git-ignored) and tell Claude.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `discover` finds nothing | PC and robot on different networks, multicast filtered by the router, or robot asleep. Use `--host` with the IP from the router or from the ADB snapshot |
| Connection refused on 8080 | HTTP server not started yet, or a different port: use the port shown by `discover` |
| `UNKNOWN_USER` after the 6 presses | Pairing mode expired, or the presses were not recognised: retry and listen for "pairing" |
| `robot key changed` | The robot was factory reset, or another device answers on that address. Check, then use `--accept-new-key` |
| Decryption error after authentication | Protocol difference to investigate: keep the full output |
