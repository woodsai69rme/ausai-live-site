# Remote Desktop + AutoSignIn Setup

## Purpose
Keep this Windows machine accessible via Chrome Remote Desktop and automatically restart Docker/Archon services after reboots without manual intervention.

## Files

| File | Purpose |
|------|---------|
| `docker_autostart.ps1` | Waits for Docker Desktop, health-checks Archon containers, starts/restarts as needed |
| `setup_autologon_admin.ps1` | Run **once in elevated PowerShell** - sets auto sign-in + Docker service auto-start |
| `docker_autostart.wsf` | Silent wrapper for startup |
| `autologon.reg` | Registry template (legacy) |

## One-Time Setup (Elevated)

1. Run **PowerShell as Administrator**
2. Execute:
```powershell
Set-Service -Name com.docker.service -StartupType Automatic -Status Running
$reg='HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon'
Set-ItemProperty -Path $reg -Name AutoAdminLogon -Value 1
Set-ItemProperty -Path $reg -Name DefaultUserName -Value karma
Set-ItemProperty -Path $reg -Name DefaultDomainName -Value karma
Set-ItemProperty -Path $reg -Name DefaultPassword -Value 'YOUR_PASSWORD'
```

Or use the self-service file `setup_autologon_admin.ps1` after placing your password in:
`%LOCALAPPDATA%\Docker\autologon_pass.txt`

## Already Configured

- Chrome Remote Desktop service (`chromoting`): **Automatic** ✅
- Docker autostart in HKCU Run + Startup folder ✅
- Docker/Archon startup script registered ✅

## Verification

```powershell
# Check auto sign-in
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' AutoAdminLogon, DefaultUserName

# Check Docker service
Get-Service com.docker.service | Select-Object Name, Status, StartType

# Check startup registration
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' DockerArchonAutostart

# Check Chrome Remote Desktop
Get-Service chromoting | Select-Object Name, Status, StartType
```