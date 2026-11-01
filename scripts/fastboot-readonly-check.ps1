<#
.SYNOPSIS
  Read-only bootloader check of a Keecker K1: lock state and partition list, then back to Android.

.DESCRIPTION
  Downloads Google's official Android SDK Platform-Tools if needed (checks Google's Authenticode signature),
  reboots the robot into the bootloader with adb, runs only reading commands (fastboot getvar all,
  fastboot oem device-info), then fastboot reboot. Nothing is flashed, erased or unlocked.
  Output: firmware/captures/<timestamp>_fastboot/ (git-ignored). Procedure: docs/10-Operations/adb-runbook.md.

.EXAMPLE
  .\scripts\fastboot-readonly-check.ps1
  .\scripts\fastboot-readonly-check.ps1 -Redact     # mask the serial number before sharing
#>
# SPDX-License-Identifier: Apache-2.0
param(
    [switch]$Redact
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$out = Join-Path $root ("firmware/captures/" + (Get-Date -Format 'yyyy-MM-dd_HHmmss') + "_fastboot")
New-Item -ItemType Directory -Force $out | Out-Null

# 1. Official Platform-Tools, kept outside the repository
$toolsDir = Join-Path $env:LOCALAPPDATA 'keeckeros'
$pt = Join-Path $toolsDir 'platform-tools'
$fastboot = Join-Path $pt 'fastboot.exe'
$adb = Join-Path $pt 'adb.exe'
if (-not (Test-Path $fastboot)) {
    Write-Host 'Downloading Android SDK Platform-Tools from dl.google.com...'
    New-Item -ItemType Directory -Force $toolsDir | Out-Null
    $zip = Join-Path $toolsDir 'platform-tools-latest-windows.zip'
    Invoke-WebRequest -UseBasicParsing -Uri 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip' -OutFile $zip
    Expand-Archive $zip -DestinationPath $toolsDir -Force
    Remove-Item $zip
}
foreach ($exe in $fastboot, $adb) {
    $sig = Get-AuthenticodeSignature $exe
    if ($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch 'Google') {
        throw "Signature check failed for ${exe}: $($sig.Status) $($sig.SignerCertificate.Subject)"
    }
}
& $fastboot --version | Out-File -Encoding utf8 (Join-Path $out 'fastboot-version.txt')
Write-Host "Platform-Tools OK (signed by Google): $pt"

function Run([string]$name, [string]$exe, [string[]]$cmd) {
    $file = Join-Path $out "$name.txt"
    "# $(Split-Path -Leaf $exe) $($cmd -join ' ')" | Out-File -Encoding utf8 $file
    & $exe @cmd 2>&1 | ForEach-Object { "$_" } | Tee-Object -Variable lines | Out-File -Encoding utf8 -Append $file
    return $lines
}

# 2. Reboot into the bootloader (the robot projects nothing while in fastboot)
$devices = & $adb devices | Select-String '\tdevice$'
if (-not $devices) { throw 'No authorised adb device. Plug the robot in over USB and accept the debugging prompt.' }
Write-Host 'Rebooting the robot into the bootloader...'
& $adb reboot bootloader

$found = $false
for ($i = 0; $i -lt 45 -and -not $found; $i++) {
    Start-Sleep -Seconds 2
    $found = [bool](& $fastboot devices 2>$null | Select-String 'fastboot')
}
if (-not $found) {
    Write-Warning 'The robot is not visible in fastboot after 90 s. Windows probably lacks the fastboot USB driver.'
    Write-Warning 'To return to Android: unplug USB, then hold the top button until the robot restarts.'
    exit 1
}
Write-Host 'Robot in fastboot. Reading only...'

# 3. Read-only commands
Run 'fastboot-devices' $fastboot @('devices', '-l') | Out-Null
$info = Run 'oem-device-info' $fastboot @('oem', 'device-info')
$vars = Run 'getvar-all' $fastboot @('getvar', 'all')

# 4. Back to Android
Write-Host 'Rebooting to Android...'
Run 'fastboot-reboot' $fastboot @('reboot') | Out-Null
$back = $false
for ($i = 0; $i -lt 60 -and -not $back; $i++) {
    Start-Sleep -Seconds 3
    $back = [bool](& $adb devices | Select-String '\tdevice$')
}

if ($Redact) {
    $serials = $vars | Select-String 'serialno:\s*(\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value } | Sort-Object -Unique
    foreach ($file in Get-ChildItem $out -File) {
        $text = Get-Content $file.FullName -Raw
        if ($null -eq $text) { continue }
        foreach ($s in $serials) { $text = $text.Replace($s, '<serial>') }
        Set-Content -Encoding utf8 -NoNewline $file.FullName $text
    }
}
Get-ChildItem $out -File | Where-Object Name -ne 'SHA256SUMS.txt' | Get-FileHash -Algorithm SHA256 |
    ForEach-Object { "$($_.Hash.ToLower())  $(Split-Path -Leaf $_.Path)" } |
    Out-File -Encoding utf8 (Join-Path $out 'SHA256SUMS.txt')

Write-Host ''
Write-Host 'Bootloader state:'
$info | Select-String -Pattern 'unlocked|tamper|secure|charger|version' | ForEach-Object { "  $($_.Line)" }
$vars | Select-String -Pattern 'unlocked|secure|version-bootloader|product:|variant' | ForEach-Object { "  $($_.Line)" }
Write-Host ("Partitions listed: " + @($vars | Select-String 'partition-size').Count)
Write-Host ("Robot back in Android: " + $back)
Write-Host "Done. Folder to share with Claude: $out"
