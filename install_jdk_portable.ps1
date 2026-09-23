# ============================================
# Portable Java JDK 17 Installer for Karma's Toolset
# Downloads Microsoft OpenJDK 17 ZIP → Tools\jdk\jdk-17\
# No admin / no MSI needed. Idempotent: re-run is safe.
# Designed to be called from install_all.ps1 OR standalone.
# ============================================

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"  # avoid Invoke-WebRequest progress bar

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  PORTABLE JDK 17 INSTALLER" -ForegroundColor Cyan
Write-Host "  Target: ~\$env:USERPROFILE\Tools\jdk\jdk-17\" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# === Constants ==================================================
$JDK_VERSION = "17"
$JDK_VENDOR = "Microsoft OpenJDK"
$JDK_URL = "https://aka.ms/download-jdk/microsoft-jdk-17-windows-x64.zip"
$JDK_INSTALL_ROOT = Join-Path $env:USERPROFILE "Tools\jdk"
$JDK_FINAL_DIR = Join-Path $JDK_INSTALL_ROOT ("jdk-" + $JDK_VERSION)
$MARKER_FILE = Join-Path $JDK_FINAL_DIR ".portable-jdk-installed.json"
$TMP_ZIP = Join-Path $env:TEMP ("ms-jdk-17-" + [guid]::NewGuid().ToString().Substring(0,8) + ".zip")

# === Pre-flight: already installed? =============================
if (Test-Path $MARKER_FILE) {
    $existing = Get-Content $MARKER_FILE -Raw | ConvertFrom-Json
    Write-Host "[INFO] JDK already installed at: $($existing.install_dir)" -ForegroundColor Yellow
    Write-Host "[INFO] Vendor: $($existing.vendor)  Version: $($existing.java_version)" -ForegroundColor Yellow
    Write-Host "[INFO] Installed: $($existing.install_date)" -ForegroundColor Yellow
    Write-Host "[INFO] Use --force to reinstall." -ForegroundColor Gray
    Write-Host ""
    Write-Host "To verify: & \"$JDK_FINAL_DIR\bin\java.exe\" -version" -ForegroundColor Cyan
    if (-not ($args -contains "--force")) {
        exit 0
    }
    Write-Host ""
    Write-Host "[FORCE] Re-installing JDK 17..." -ForegroundColor Magenta
}

# === Force TLS 1.2 (Win10 PowerShell 5.1 defaults to TLS 1.0) ===
Write-Host "[1/5] Enabling TLS 1.2..." -ForegroundColor Yellow
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# === Download ZIP ================================================
Write-Host "[2/5] Downloading JDK 17 from $JDK_URL ..." -ForegroundColor Yellow
Write-Host "       (size ~190 MB; may take 30-120 s)" -ForegroundColor DarkGray
try {
    Invoke-WebRequest -Uri $JDK_URL -OutFile $TMP_ZIP -UseBasicParsing -ErrorAction Stop
} catch {
    Write-Host "[FAIL] Download failed: $_" -ForegroundColor Red
    Remove-Item -Path $TMP_ZIP -ErrorAction SilentlyContinue
    exit 11
}
$sizeMB = [math]::Round((Get-Item $TMP_ZIP).Length / 1MB, 1)
Write-Host "       Downloaded: $sizeMB MB" -ForegroundColor Green

# === Extract ZIP =================================================
Write-Host "[3/5] Extracting to $JDK_INSTALL_ROOT ..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $JDK_INSTALL_ROOT | Out-Null
# Use Expand-Archive (PowerShell-native cmdlet, ships with PS 5.1+).
# AVOIDS BOTH the gitbash tar PATH-leak AND any System32/tar.exe resolution issues.
# Slower than native tar (3-5x) but ~30-60s for a 190MB JDK is acceptable for a
# rare operator-driven installer. Rock-solid under any shell invocation.
try {
    Expand-Archive -Path $TMP_ZIP -DestinationPath $JDK_INSTALL_ROOT -Force
} catch {
    Write-Host "[FAIL] Extraction failed: $_" -ForegroundColor Red
    Remove-Item -Path $TMP_ZIP -ErrorAction SilentlyContinue
    exit 12
}

# Cleanup ZIP
Remove-Item -Path $TMP_ZIP -ErrorAction SilentlyContinue

# === Normalize nested folder name ===============================
Write-Host "[4/5] Normalizing JDK layout..." -ForegroundColor Yellow
# The ZIP contains a top-level folder like "jdk-17.0.X+XX\" which we rename to "jdk-17\"
$extracted = Get-ChildItem -Path $JDK_INSTALL_ROOT -Directory | Sort-Object Name -Descending
if ($extracted.Count -gt 0 -and $extracted[0].FullName -ne $JDK_FINAL_DIR) {
    # If marker-target dir exists, remove first
    if (Test-Path $JDK_FINAL_DIR) { Remove-Item -Path $JDK_FINAL_DIR -Recurse -Force }
    Rename-Item -Path $extracted[0].FullName -NewName ("jdk-" + $JDK_VERSION)
    Write-Host "       Renamed: $($extracted[0].Name) → jdk-$JDK_VERSION" -ForegroundColor Green
}

# === Smoke-test + write marker ==================================
Write-Host "[5/5] Verifying Java works..." -ForegroundColor Yellow
$JAVA_EXE = Join-Path $JDK_FINAL_DIR "bin\java.exe"
if (-not (Test-Path $JAVA_EXE)) {
    Write-Host "[FAIL] java.exe not found at $JAVA_EXE after extraction" -ForegroundColor Red
    exit 13
}
try {
    $verOut = & $JAVA_EXE -version 2>&1 | Out-String
} catch {
    Write-Host "[FAIL] java.exe failed to execute: $_" -ForegroundColor Red
    exit 14
}
$javaVersionLine = ($verOut -split "`n" | Where-Object { $_ -match 'openjdk version' } | Select-Object -First 1)
if (-not $javaVersionLine) {
    Write-Host "[FAIL] java.exe did not print 'openjdk version' line" -ForegroundColor Red
    Write-Host $verOut -ForegroundColor DarkGray
    exit 15
}

# Write success marker
$marker = [pscustomobject]@{
    vendor        = $JDK_VENDOR
    target        = $JDK_VERSION
    install_dir   = $JDK_FINAL_DIR
    install_date  = (Get-Date).ToString("o")
    java_version  = $javaVersionLine.Trim()
    source_url    = $JDK_URL
    installer     = "install_jdk_portable.ps1"
}
$marker | ConvertTo-Json | Set-Content -Path $MARKER_FILE -Encoding UTF8

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  JDK 17 PORTABLE INSTALL COMPLETE" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Path:      $JDK_FINAL_DIR" -ForegroundColor White
Write-Host "  Java exe:  $JAVA_EXE" -ForegroundColor White
Write-Host "  Version:   $javaVersionLine" -ForegroundColor White
Write-Host ""
Write-Host "Usage options:" -ForegroundColor Cyan
Write-Host "  Per-session:    call Tools\set_jdk_env.bat from any cmd window" -ForegroundColor Gray
Write-Host "  War-room HUD:   python war_room.py validate-tools (will auto-detect)" -ForegroundColor Gray
Write-Host "  Permanent:      [Environment]::SetEnvironmentVariable('JAVA_HOME','$JDK_FINAL_DIR','User')" -ForegroundColor Gray
Write-Host ""
