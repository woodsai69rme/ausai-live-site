# Disk Space Audit Report

**Generated:** 2026-02-19  
**User:** karma

---

## Current Disk Usage

| Drive | Used | Free | Total | Usage |
|-------|------|------|-------|-------|
| **C:** | 912.29 GB | 18.47 GB | 930.76 GB | **98%** ⚠️ |
| **X:** | 926.00 GB | 5.51 GB | 931.51 GB | **99.4%** ⚠️ |

---

## C: Drive Analysis

### Large System Folders

| Folder | Size | Notes |
|--------|------|-------|
| Windows | 28.99 GB | System files |
| Program Files | 28.69 GB | 64-bit applications |
| Program Files (x86) | 15.99 GB | 32-bit applications |
| Windows\Installer | 11.92 GB | MSI cache (491 files) |
| Windows\WinSxS | ~15-20 GB | Component store |
| ProgramData\NVIDIA Corporation | 6.89 GB | GPU drivers/cache |
| ProgramData\Package Cache | 1.24 GB | Visual Studio installer cache |

### User Profile (C:\Users\karma)

| Folder | Size | Cleanup Potential |
|--------|------|-------------------|
| EXPERIMENTAL | 11.87 GB | ⭐⭐⭐ Review/delete |
| Downloads | 8.40 GB | ⭐⭐⭐ Clean old files |
| .continue | 5.00 GB | ⭐⭐ AI project cache |
| Documents | 1.72 GB | ⭐ Review |
| auggdash26_consolidated | 1.69 GB | Project files |
| .qwen | 834 MB | AI assistant cache |
| COMPLETED_PROJECTS | 744 MB | ⭐⭐ Archive/delete |
| ACTIVE_PROJECTS | 443 MB | Active work |
| .vscode | 387 MB | ⭐ Clean extensions |
| .cursor | 340 MB | ⭐ AI editor cache |
| .gemini | 333 MB | ⭐ AI cache |
| .lmstudio | 233 MB | ⭐⭐ Local LLM models |
| .bun | 226 MB | Runtime cache |
| .trae | 219 MB | ⭐ Editor cache |
| .kiro | 198 MB | ⭐ Editor cache |

---

## X: Drive Analysis

*Full scan timed out - manual review recommended*

---

## Cleanup Options (No Automatic Actions)

### 🔴 HIGH IMPACT (5+ GB each)

#### 1. Clean EXPERIMENTAL Folder - **~12 GB**
```
Location: C:\Users\karma\EXPERIMENTAL
Action: Review contents, delete unnecessary files
Risk: Low (if files are truly experimental)
```

#### 2. Clean Downloads Folder - **~8.4 GB**
```
Location: C:\Users\karma\Downloads
Action: Delete old installers, move important files
Risk: Low
```

#### 3. Clean AI Editor Caches - **~6 GB combined**
```
Folders:
- C:\Users\karma\.continue (5.0 GB)
- C:\Users\karma\.cursor (340 MB)
- C:\Users\karma\.gemini (333 MB)
- C:\Users\karma\.trae (219 MB)
- C:\Users\karma\.kiro (198 MB)
Action: Clear conversation history, cached completions
Risk: Low (will lose conversation history)
```

#### 4. Clean NVIDIA Cache - **~7 GB**
```
Location: C:\ProgramData\NVIDIA Corporation
Action: Use GeForce Experience or NVIDIA control panel to clear shader cache
Risk: Low (cache will rebuild)
```

#### 5. Run DISM Cleanup - **~5-20 GB**
```
Command (Admin): DISM /Online /Cleanup-Image /StartComponentCleanup
Action: Remove superseded Windows updates
Risk: Safe - Microsoft recommended
Note: Cannot uninstall old updates after running
```

#### 6. Disable Hibernation - **~8-32 GB** (if enabled)
```
Command (Admin): powercfg /h off
Action: Removes hiberfil.sys
Risk: Low (loses hibernate feature, fast startup still works)
```

#### 7. Clean Visual Studio Cache - **~1.2 GB**
```
Location: C:\ProgramData\Package Cache
Action: Use Visual Studio Installer → Modify → Repair
Risk: Low
```

---

### 🟡 MEDIUM IMPACT (1-5 GB each)

#### 8. Clean Local LLM Models - **~233 MB+**
```
Location: C:\Users\karma\.lmstudio
Action: Delete unused models
Risk: Low (can re-download)
```

#### 9. Clean Completed Projects - **~744 MB**
```
Location: C:\Users\karma\COMPLETED_PROJECTS
Action: Archive to external/X: drive or delete
Risk: Medium (backup first)
```

#### 10. Clean VS Code Extensions - **~387 MB**
```
Location: C:\Users\karma\.vscode\extensions
Action: Remove unused extensions
Risk: Low
```

#### 11. Clean Windows Installer Cache - **~11.9 GB**
```
Location: C:\Windows\Installer
Action: Use PatchCleaner tool (third-party)
Risk: Medium - DO NOT manually delete
Tool: https://www.codesector.com/patchcleaner
```

#### 12. Clear Recycle Bin
```
Command: empty-recyclebin (PowerShell) or right-click → Empty
Action: Permanently delete recycled files
Risk: Low (files already "deleted")
```

#### 13. Clean Chrome/Edge Browser Cache - **~1-5 GB**
```
Action: Ctrl+Shift+Delete → Cached images/files
Risk: Low (sites may load slower initially)
```

---

### 🟢 LOW IMPACT (<1 GB each)

#### 14. Clear Temp Folders
```
Commands:
- del /q /s %TEMP%\*
- del /q /s C:\Windows\Temp\*
Risk: None
```

#### 15. Clear Windows Update Download Cache
```
Commands (Admin):
net stop wuauserv && net stop bits
del /q /s C:\Windows\SoftwareDistribution\Download\*
net start wuauserv && net start bits
Risk: Low
```

#### 16. Clean AI Assistant Cache (.qwen)
```
Location: C:\Users\karma\.qwen
Action: Clear conversation history
Risk: Low
```

#### 17. Clean Bun Runtime Cache
```
Location: C:\Users\karma\.bun
Action: Clear package cache
Risk: Low
```

---

### 📦 X: DRIVE OPTIONS

#### 18. Move Large Folders from C: to X:
```
Candidates:
- C:\Users\karma\EXPERIMENTAL → X:\EXPERIMENTAL
- C:\Users\karma\Downloads → X:\Downloads
- C:\Users\karma\COMPLETED_PROJECTS → X:\ARCHIVE
Risk: Low (update shortcuts/links)
```

#### 19. Clean X: Drive
```
Action: Manual review needed - scan timed out
Command to scan: powershell -Command "Get-ChildItem 'X:\' -Recurse | Measure-Object -Property Length -Sum"
```

---

## Recommended Priority Order

| Priority | Action | Est. Space |
|----------|--------|------------|
| 1 | Clean EXPERIMENTAL folder | ~12 GB |
| 2 | Clean Downloads | ~8 GB |
| 3 | Run DISM cleanup | ~5-20 GB |
| 4 | Clean AI editor caches | ~6 GB |
| 5 | Clean NVIDIA cache | ~7 GB |
| 6 | Disable hibernation | ~8-32 GB |
| 7 | Move folders to X: drive | ~20 GB |
| 8 | Use PatchCleaner on Installer | ~5-10 GB |
| 9 | Clear browser caches | ~1-5 GB |
| 10 | Empty Recycle Bin | Variable |

---

## Commands Reference (For Manual Execution)

### Safe Cleanup Commands
```batch
REM Clear temp folders
del /q /s %TEMP%\*
del /q /s C:\Windows\Temp\*

REM Check disk space after cleanup
powershell -Command "Get-PSDrive C,D | Select-Object Name,@{N='FreeGB';E={[math]::Round($_.Free/1GB,2)}}"
```

### Admin Commands (Run as Administrator)
```batch
REM DISM cleanup
DISM /Online /Cleanup-Image /StartComponentCleanup

REM Disable hibernation
powercfg /h off

REM Clear Windows Update cache
net stop wuauserv && net stop bits
del /q /s C:\Windows\SoftwareDistribution\Download\*
net start wuauserv && net start bits

REM Empty Recycle Bin (PowerShell)
powershell -Command "Clear-RecycleBin -Force"
```

---

## Warnings

⚠️ **DO NOT manually delete:**
- C:\Windows\Installer (use PatchCleaner)
- C:\Windows\WinSxS (use DISM)
- C:\ProgramData\Package Cache (use VS Installer)
- C:\Windows\System32 files
- C:\Program Files unless uninstalling properly

⚠️ **Backup before deleting:**
- EXPERIMENTAL folder contents
- COMPLETED_PROJECTS
- Any documents you're unsure about

---

## Next Steps

1. **Immediate:** Run the disk_cleanup.bat (already created) as Administrator
2. **Manual:** Review and clean EXPERIMENTAL and Downloads folders
3. **Optional:** Move large folders to X: drive
4. **Maintenance:** Set up Storage Sense for automatic cleanup
