# 🚀 ALL-IN-ONE SYSTEM BOOT & ENHANCEMENT SCRIPT
# Run this to validate and document the entire setup

Write-Host "=== Phase 1: Verifying CLI Tools ===" -ForegroundColor Cyan
$tools = @("opencode", "crush", "kilo")
foreach ($t in $tools) {
    if (Get-Command $t -ErrorAction SilentlyContinue) {
        Write-Host "✅ $t available" -ForegroundColor Green
    } else {
        Write-Host "❌ $t MISSING" -ForegroundColor Red
    }
}

Write-Host "`n=== Phase 2: Checking Services ===" -ForegroundColor Cyan
$services = @("chromoting", "com.docker.service")
foreach ($s in $services) {
    $svc = Get-Service -Name $s -ErrorAction SilentlyContinue
    if ($svc) {
        Write-Host ("{0}: {1} / {2}" -f $s, $svc.Status, $svc.StartType) -ForegroundColor Green
    } else {
        Write-Host "${s}: NOT FOUND" -ForegroundColor Yellow
    }
}

Write-Host "`n=== Phase 3: Checking Autostart ===" -ForegroundColor Cyan
$runKeys = Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
"Docker Desktop", "DockerArchonAutostart" | ForEach-Object {
    $v = $runKeys.$_
    if ($v) {
        Write-Host "✅ $_ registered in HKCU Run" -ForegroundColor Green
    }
}

$startupScripts = Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup" -Filter "*.lnk" -ErrorAction SilentlyContinue
$startupScripts | ForEach-Object {
    Write-Host "Startup item: $($_.Name)" -ForegroundColor Green
}

Write-Host "`n=== Phase 4: Checking Remote Desktop Config ===" -ForegroundColor Cyan
$autoLogon = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -ErrorAction SilentlyContinue
if ($autoLogon.AutoAdminLogon -eq 1) {
    Write-Host "✅ Auto sign-in enabled" -ForegroundColor Green
} else {
    Write-Host "❌ Auto sign-in NOT configured (run setup_autologon_admin.ps1 as admin)" -ForegroundColor Red
}

Write-Host "`n=== Phase 5: Revenue Projects Status ===" -ForegroundColor Cyan
$revenueProjects = Get-ChildItem "C:\Users\karma\REVENUE_GENERATORS" -Directory | Where-Object { $_.Name -match "recovery|trader|money|platform|tool" }
$revenueProjects | ForEach-Object {
    $hasReadme = Test-Path "C:\Users\karma\REVENUE_GENERATORS\$($_.Name)\README.md"
    $status = if ($hasReadme) { "✅" } else { "❌" }
    Write-Host "  $status $($_.Name)" -ForegroundColor Green
}

Write-Host "`n=== Phase 6: Generating System Report ===" -ForegroundColor Cyan
$report = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    CLIs = "${(opencode --version 2>$null)}, ${(crush --help 2>$null)}, ${(kilo --version 2>$null)}"
    Docker = "${(docker --version 2>$null)}"
    Services = @{
        CRD = (Get-Service chromoting).Status
        Docker = (Get-Service com.docker.service -ErrorAction SilentlyContinue).Status
    }
    RevenueProjects = $revenueProjects.Count
}

$report | ConvertTo-Json -Depth 3 > "C:\Users\karma\SYSTEM_REPORT.json"
Write-Host "System report saved to SYSTEM_REPORT.json" -ForegroundColor Green

Write-Host "`n✅ ALL SYSTEMS CHECKED" -ForegroundColor Cyan