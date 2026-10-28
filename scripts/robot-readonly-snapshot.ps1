<#
.SYNOPSIS
  Read-only snapshot of a Keecker K1 over ADB, for the bootloader, partition, network and DRM questions.

.DESCRIPTION
  Every command below only reads. Nothing is written to the robot: no root, remount, install,
  push, reboot or fastboot. Output goes to firmware/captures/<timestamp>/ (git-ignored), with a
  SHA256 manifest. Procedure: docs/10-Operations/adb-runbook.md.

.EXAMPLE
  .\scripts\robot-readonly-snapshot.ps1                   # USB, single device
  .\scripts\robot-readonly-snapshot.ps1 -Serial 192.168.1.50:5555
#>
# SPDX-License-Identifier: Apache-2.0
param(
    [string]$Serial = ''
)

$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$out = Join-Path $root ("firmware/captures/" + (Get-Date -Format 'yyyy-MM-dd_HHmmss'))
New-Item -ItemType Directory -Force $out | Out-Null

$adbArgs = @()
if ($Serial) { $adbArgs = @('-s', $Serial) }

function Save([string]$name, [string[]]$cmd) {
    $file = Join-Path $out "$name.txt"
    "# adb $($adbArgs -join ' ') $($cmd -join ' ')" | Out-File -Encoding utf8 $file
    & adb @adbArgs @cmd 2>&1 | Out-File -Encoding utf8 -Append $file
    Write-Host "  $name"
}

function Shell([string]$name, [string]$command) { Save $name @('shell', $command) }

Write-Host "Output: $out"
Save 'adb-devices' @('devices', '-l')

Write-Host 'Identity and build'
Shell 'getprop-all' 'getprop'
Shell 'build-props' 'for p in ro.build.fingerprint ro.build.display.id ro.build.version.release ro.build.version.sdk ro.build.version.security_patch ro.product.model ro.product.name ro.hardware; do echo "$p=$(getprop $p)"; done'
Shell 'uname' 'uname -a; cat /proc/version'
Shell 'cpuinfo' 'cat /proc/cpuinfo'
Shell 'meminfo' 'head -5 /proc/meminfo'
Shell 'device-tree-model' 'cat /proc/device-tree/model; echo; cat /proc/device-tree/compatible | tr "\0" "\n"'
Shell 'soc-id' 'cat /sys/devices/soc0/soc_id /sys/devices/soc0/machine /sys/devices/soc0/hw_platform /sys/devices/soc0/revision 2>&1'

Write-Host 'Bootloader and verified boot (decisive gate for a new ROM)'
Shell 'bootloader-props' 'for p in ro.boot.flash.locked ro.boot.verifiedbootstate ro.boot.veritymode ro.boot.vbmeta.device_state ro.oem_unlock_supported sys.oem_unlock_allowed ro.secure ro.debuggable ro.adb.secure ro.build.type ro.build.tags ro.bootloader ro.boot.bootloader ro.boot.hardware ro.boot.serialno ro.boot.secureboot ro.product.device ro.product.board ro.board.platform ro.frp.pst; do echo "$p=$(getprop $p)"; done'
Shell 'oem-unlock-setting' 'settings get global oem_unlock_allowed; settings get global development_settings_enabled'
Shell 'cmdline' 'cat /proc/cmdline'

Write-Host 'Partitions (names and sizes only, no content)'
Shell 'by-name' 'ls -l /dev/block/bootdevice/by-name/ 2>&1; ls -l /dev/block/platform/*/by-name/ 2>&1'
Shell 'proc-partitions' 'cat /proc/partitions'
Shell 'mounts' 'cat /proc/mounts'

Write-Host 'Robot hardware nodes'
Shell 'dev-nodes' 'ls -l /dev/ttyHSL* /dev/ttyHS* /dev/resetboard /dev/video* /dev/input/ 2>&1; cat /proc/tty/drivers'
Shell 'dev-all' 'ls -l /dev'
Shell 'su-check' 'which su; ls -l /system/xbin/su /system/bin/su 2>&1; id'

Write-Host 'Network (listening ports of the companion-app server)'
Shell 'net-tcp' 'cat /proc/net/tcp; cat /proc/net/tcp6'
Shell 'net-udp' 'cat /proc/net/udp; cat /proc/net/udp6'
Shell 'netstat' 'netstat -ltnu 2>&1'
Shell 'ip-addr' 'ip addr'

Write-Host 'DRM and Cast'
Shell 'drm-libs' 'ls -l /system/vendor/lib/mediadrm /system/vendor/lib64/mediadrm /vendor/lib/mediadrm 2>&1'
Shell 'drm-props' 'getprop | grep -iE "drm|widevine|wvm|cast|gms"'
Shell 'drm-dumpsys' 'dumpsys media.drm 2>&1 | head -80'

Write-Host 'Packages'
Shell 'packages' 'pm list packages -f -U'
Shell 'keecker-services-pkg' 'dumpsys package com.keecker.services | head -60'

Write-Host 'SHA256 manifest'
Get-ChildItem $out -File | Where-Object Name -ne 'SHA256SUMS.txt' | Get-FileHash -Algorithm SHA256 |
    ForEach-Object { "$($_.Hash.ToLower())  $(Split-Path -Leaf $_.Path)" } |
    Out-File -Encoding utf8 (Join-Path $out 'SHA256SUMS.txt')

Write-Host ''
Write-Host 'Bootloader summary:'
Get-Content (Join-Path $out 'bootloader-props.txt') | Select-Object -Skip 1
Write-Host ''
Write-Host "Done. Folder to share with Claude: $out"
