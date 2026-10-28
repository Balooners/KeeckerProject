# CLAUDE.md — KeeckerOS

@AGENTS.md
@SESSION_STATE.md

AGENTS.md is the canonical collaboration guide (evidence rules, confidence markers ✅/🟡/🔴, artifact rules, docs taxonomy). This file only adds the long-term product vision and how Claude Code should operate. If the two ever conflict, AGENTS.md wins and the conflict must be reported to Harold.

## Language

- Talk to Harold (project owner) in French.
- Repository documentation, code and commit messages stay in English, consistent with the existing repo and the international Keecker community.

## Product vision

Keecker (the company) shut down; more than 1,000 K1 robots remain in homes without cloud services.

Final goal: an open-source OS that **any Keecker owner can install by themselves**, with no dependency on Keecker servers, using self-hosted services and modern apps. The reverse engineering and documentation work in this repo is the foundation for that.

Harold is the decision maker. Anything touching flashing, the installer, security or public releases requires his review.

## OS target — decided 2026-10-28: recent Android TV

Harold's decision: **a recent Android TV**, not Linux. The owner's needs are Android TV apps (myCANAL, Molotov, Free TV, Jellyfin, IPTV players, Netflix, Disney+) and casting from a phone. The original Android TV 7 (API 24) is already below the minimum of several of these apps.

- Base: LineageOS Android TV build on the msm8996-common tree. The newest official LineageOS for an msm8996 device is 18.1 (Android 11, Xiaomi Mi 5). First target: Android 11, later 12-13 if feasible. Android 14+ is not realistic on this SoC.
- Robot functions: our own open Android service that talks to the STM over UART `/dev/ttyHSL1` (see `docs/07-Hardware/stm32.md`), instead of the Keecker platform-signed `com.keecker.services`.
- Linux (mainline + ROS 2) is no longer the target. It stays documented as a long-term option only.

Blocking questions:

- Is the bootloader unlockable? Read-only check: `ro.boot.flash.locked`, `ro.boot.verifiedbootstate`. If not, study the Qualcomm EDL path.
- Full backup before any write: every partition, especially `persist` (calibration) and the DRM/TrustZone-related partitions.
- DRM and Cast on a non-certified build: Widevine level kept or not, Google Cast receiver availability.

## Planned replacements

| Original | Replacement |
|---|---|
| Keecker cloud | Local API on the robot + self-hosted remote access (WireGuard / Tailscale) + companion app (Play Store, under a new name); integration with Harold's home app |
| Media | Android TV apps from the Play Store (Jellyfin, IPTV players, TV channel apps) |
| Remote video / surveillance | Our own Android service: camera streaming (WebRTC), patrols, alerts |
| Netflix / Disney+ / Google Cast | Depends on DRM level and Cast receiver on our build: to test, not guaranteed |

## Roadmap beyond ROADMAP.md

ROADMAP.md covers repository and reverse engineering phases. Product phases that follow:

1. Reverse tooling: REA MCP + Ghidra, installed from official sources only
2. DEX recovery from `com.keecker.services.odex`, Java analysis of the robot services
3. Bootloader check + `libhw_robot_jni.so` analysis
4. `docs/04-Analysis/FEATURES.md`: full feature inventory (feature | source APK/service/.so/model | strategy reuse/reimplement/replace/drop | replacement)
5. Full partition dump, calibration backup (`persist`), EDL (Qualcomm 9008) recovery path
6. OS target decision (Harold): done, recent Android TV
7. LineageOS Android TV device port (`keecker_k1` on msm8996-common, stock kernel first): boot, projector display, Wi-Fi, audio
8. Robot service on the new Android: STM UART driver, then navigation, docking, cameras, projector focus/tilt
9. Companion app, surveillance, voice
10. End-user installer, documentation, public release

## Additional rules for Claude Code

- **Never commit proprietary material**: APK, ODEX/OAT, DEX, smali, decompiled sources, .so, ML models, partition images. Work outputs go in ignored folders (`firmware/`, `work/`). Run `git status --short` before every commit.
- Document protocols and behaviour in our own words; do not paste decompiled code into docs.
- The robot is connected only when a task needs it. Read-only on the device until Harold says otherwise: no root, flash, reboot, remount, install, push, sideload, fastboot.
- Tools only from official sources (e.g. REA from `morluto/rea` only, never forks or look-alike packages).
- Future OS security baseline: signed updates, no default passwords, remote access off by default, no unauthenticated service. The robot has a camera and lives in living rooms.
- The name "Keecker OS" is provisional until the trademark question is settled.

## Working method

- One mission at a time. At the end of each mission: update SESSION_STATE.md and CHANGELOG.md, then **stop and wait for Harold's validation**.
- Separate confirmed facts (with evidence: file, offset, command, hash) from assumptions, using the AGENTS.md confidence markers.
- Respect the "Do not repeat" section of SESSION_STATE.md.
- Never overwrite existing documentation; extend it.
