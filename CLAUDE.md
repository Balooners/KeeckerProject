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

## OS target — open decision

To be decided by Harold once the blocking questions are answered:

1. **Mainline Linux + ROS 2** (preferred): LTS kernel, Debian/Ubuntu, Nav2 + slam_toolbox, Waydroid for Android apps.
2. **Recent Android** (LineageOS, Android 11–13 base, msm8996-common tree).

Blocking questions, highest priority after ODEX reconstruction:

- Is the bootloader unlockable? Read-only check: `ro.boot.flash.locked`, `ro.boot.verifiedbootstate`.
- How does `libhw_robot_jni.so` talk to motors and sensors (microcontroller over serial/USB, or kernel drivers)?

## Planned replacements

| Original | Replacement |
|---|---|
| Keecker cloud | Local API on the robot + self-hosted remote access (WireGuard / Cloudflare tunnel) + PWA control app; optional Home Assistant integration |
| Media | Jellyfin / Kodi, AirPlay (UxPlay), DLNA |
| Remote video / surveillance | Frigate, or Android apps via Waydroid |
| Netflix / Google Cast | No free solution (DRM). Document it, do not spend time on it |

## Roadmap beyond ROADMAP.md

ROADMAP.md covers repository and reverse engineering phases. Product phases that follow:

1. Reverse tooling: REA MCP + Ghidra, installed from official sources only
2. DEX recovery from `com.keecker.services.odex`, Java analysis of the robot services
3. Bootloader check + `libhw_robot_jni.so` analysis
4. `docs/04-Analysis/FEATURES.md`: full feature inventory (feature | source APK/service/.so/model | strategy reuse/reimplement/replace/drop | replacement)
5. Full partition dump, calibration backup (`persist`), EDL (Qualcomm 9008) recovery path
6. OS target decision (Harold)
7. Minimal boot (console, display, Wi-Fi), then motors, camera/SLAM, projector
8. End-user installer, documentation, public release

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
