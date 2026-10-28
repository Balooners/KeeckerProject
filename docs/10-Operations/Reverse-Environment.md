# Reverse Engineering Environment

**Status:** Ready
**Last update:** 2026-10-28

## Objective

Make the reverse engineering toolchain reproducible: REA (MCP for agents), Ghidra for native `.so` files, JADX for APK/DEX.

## Host

- Windows 11 on ARM64 (Snapdragon X Elite). Tools run in **WSL2 Ubuntu 26.04 LTS, aarch64**.
- Native Windows ARM64 is not an option: REA's Android/JADX bridge does not support Windows ARM64, and REA's Windows Ghidra mode only accepts Windows (PE) binaries, while the K1 libraries are ARM64 ELF.

## Installed components

All downloads come from official sources and are checked against a published SHA256.

| Component | Version | Source | SHA256 / check |
|---|---|---|---|
| OpenJDK | 21.0.12.1 | Ubuntu `openjdk-21-jdk` | apt |
| Node.js | 24.22.1 linux-arm64 | https://nodejs.org/dist/v24.22.1/ | `dbabf7a1cbf947e6059ffad2c27b80041db97dea1e553b62afdee7f13fca336e` |
| Ghidra | 12.1.4 | https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build | `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db` |
| jadx-headless-mcp | 0.7.1 | https://github.com/1013503897/jadx-headless-mcp/releases/tag/v0.7.1 | `6e5eacf500b64292bfb73c49797c1958f6ee44646e43e868039ae7feb573ff75` (value published by REA) |
| REA | `rea-agents` 6.8.0 | npm, published from https://github.com/morluto/rea | npm registry |
| Build tools | build-essential, bison, flex, poppler-utils, binutils-aarch64-linux-gnu, adb | Ubuntu apt | apt |

Ghidra 12.1.4 with JDK 21 is the combination REA verifies. Ghidra 12.2 requires JDK 25 and was not used.

## Layout and environment

Everything lives in `~/tools` inside WSL. `~/.bashrc` exports:

```bash
export PATH=$HOME/tools/node/bin:$PATH
export GHIDRA_INSTALL_DIR=$HOME/tools/ghidra
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-arm64
export REA_JADX_MCP_JAR=$HOME/tools/jadx-headless-mcp-0.7.1-all.jar
```

## Ghidra native decompiler for ARM64

The official Ghidra archive only ships `linux_x86_64` and `win_x86_64` decompilers. Build the ARM64 one once:

```bash
cd $GHIDRA_INSTALL_DIR/support/gradle && ./gradlew buildNatives
```

The result is placed in `Ghidra/Features/Decompiler/build/os/linux_arm_64/`.

## Health check

```bash
rea doctor --provider ghidra --json
```

Result on 2026-10-28: `"healthy": true`. Node, Ghidra 12.1.4, native ARM64 decompiler, JDK 21 and the JADX bridge are all reported healthy. Hopper, IDA and Kuna are absent, which is expected.

## Robot Java code from the ODEX

`firmware/odex/com.keecker.services.odex` (Android 7 OAT container) embeds 3 DEX files (DEX version 037), at offsets
`0x1cd8`, `0x87cc38` and `0x11a46e0`, for a total of 18,136 class definitions. They are carved from the DEX magic and header
size with a small script, then their SHA-1 signature and Adler-32 checksum are recomputed: dex2oat modified them in place,
so the original checksums no longer match. The 3 DEX files and the original `AndroidManifest.xml` are zipped into a local
APK under `~/keecker-work/odex/` (never in the repository). REA/JADX then loads it: 8,834 top-level classes, including
`com.keecker.embedded.stm.motorcontrol.HwRobotService`.

Building baksmali/smali from source was refused by the Claude Code permission system (it runs a third-party build script),
so the carving approach was used instead. Some methods may still contain optimised ("quickened") instructions.

## Safety note

REA can drive Android devices over adb, including file transfers. Claude Code's `.claude/settings.json` deny rules cover shell commands only, not MCP tools. Keep the robot disconnected from WSL unless a task requires it, and use read-only operations.
