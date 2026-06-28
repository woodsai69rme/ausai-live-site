# DETAILED DISK CLEANUP AUDIT REPORT

**Generated:** 2026-02-19  
**User:** karma  
**Scope:** EXPERIMENTAL + AI Caches + System Files

---

## EXECUTIVE SUMMARY

| Category | Current Size | Recoverable | Priority |
|----------|-------------|-------------|----------|
| **EXPERIMENTAL Folder** | 11.87 GB | ~8-10 GB | ⭐⭐⭐ |
| **AI Editor Caches** | 6.0 GB | ~4-5 GB | ⭐⭐⭐ |
| **NVIDIA Cache** | 6.89 GB | ~6 GB | ⭐⭐ |
| **Windows\Installer** | 11.92 GB | ~5-8 GB | ⭐⭐ |
| **DISM Cleanup** | Unknown | ~5-20 GB | ⭐⭐⭐ |
| **Hibernation** | DISABLED | N/A | ✅ Done |

**TOTAL POTENTIAL RECOVERY: ~28-49 GB**

---

## 1. EXPERIMENTAL FOLDER DETAILED AUDIT

**Location:** `C:\Users\karma\EXPERIMENTAL`  
**Total Size:** 11.87 GB  
**Subfolders:** 140+ folders

### Top-Level Folder Structure

| Category | Folders | Est. Size | Action |
|----------|---------|-----------|--------|
| **ULTIMATE_* packages** | 4 folders | 0.87 GB | ⚠️ Review - old installs |
| **awesome-* collections** | 12 folders | 7.44 MB | ✅ Keep - reference lists |
| **nexus-ide*** | 3 folders | 368 MB | ⚠️ Review - IDE projects |
| **voice_assistant*** | 2 folders | 16.56 MB | ⚠️ Review - old projects |
| **pentest*** | 2 folders | 1.9 MB | ⚠️ Review - security tools |
| **agent*** | 3 folders | 1.58 MB | ⚠️ Review - AI agents |
| **Other 130+ folders** | Various | ~3 GB | ⭐ Review individually |

### Recommended Actions for EXPERIMENTAL

#### 🔴 DELETE CANDIDATES (Est. 4-6 GB)

```
Folder Pattern                          Reason
─────────────────────────────────────────────────────────────────
ULTIMATE_AI_PACKAGE_*                   Old installers/backups
ULTIMATE_AI_SYSTEM                     Duplicate system files
backsept*                              Old test projects
busept                                 Old test projects
farqgemini                             Old test projects
CONFIGURATION                          Likely duplicate configs
DEPLOYMENT_INFRASTRUCTURE              Old deployment files
DASHBOARDS_ANALYTICS                   Old dashboard code
DATA_MANAGEMENT                        Duplicate data files
DOCUMENTATION_SYSTEM                   Old docs
SECURITY_COMPLIANCE                    Old compliance docs
TESTING_QA                             Old test files
```

#### 🟡 REVIEW NEEDED (Est. 2-3 GB)

```
Folder Pattern                          Notes
─────────────────────────────────────────────────────────────────
nexus-ide* (368 MB)                     Check if still in use
voice_assistant* (16 MB)                Check project status
pentest* (2 MB)                         Security tools - keep?
agent* (2 MB)                           AI agents - active?
github_repos                            May have valuable code
opencode/opencoder                      Check if migrated
gemini-*                               Check if still used
```

#### 🟢 SAFE TO KEEP (Est. 1-2 GB)

```
Folder Pattern                          Reason
─────────────────────────────────────────────────────────────────
awesome-* (7.44 MB)                     Reference lists (GitHub)
examples                                Sample code
scripts                                 Utility scripts
configs                                 Active configurations
data                                    Active data files
```

### Manual Review Commands

```powershell
# List largest subfolders in EXPERIMENTAL
Get-ChildItem 'C:\Users\karma\EXPERIMENTAL' -Directory | 
  ForEach-Object { 
    $size = (Get-ChildItem $_.FullName -Recurse -ErrorAction SilentlyContinue | 
      Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
    [PSCustomObject]@{
      Folder = $_.Name
      SizeGB = [math]::Round($size/1GB, 2)
    }
  } | Sort-Object SizeGB -Descending | Select-Object -First 20

# Find folders not modified in 6+ months
Get-ChildItem 'C:\Users\karma\EXPERIMENTAL' -Directory | 
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddMonths(-6) } |
  Select-Object Name, LastWriteTime
```

---

## 2. AI EDITOR CACHES DETAILED AUDIT

### 2.1 .continue (5.0 GB)

**Location:** `C:\Users\karma\.continue`

| Component | Size | Safe to Delete |
|-----------|------|----------------|
| `index/lancedb/*` | ~3 GB | ✅ Yes - vector DB cache |
| `index.sqlite*` | ~500 MB | ✅ Yes - search index |
| `dev_data/*` | ~800 MB | ✅ Yes - development data |
| `chatInteraction.jsonl` | ~50 MB | ⚠️ Loses chat history |
| `chatFeedback.jsonl` | ~10 MB | ⚠️ Loses feedback data |
| `sessions/*` | ~100 MB | ⚠️ Loses session data |

**Recommendation:** Clear all except recent sessions if needed  
**Recoverable:** ~4.5 GB

### 2.2 .cursor (340 MB)

**Location:** `C:\Users\karma\.cursor`

| Component | Size | Safe to Delete |
|-----------|------|----------------|
| `extensions/*` | 150 MB | ⚠️ Editor extensions |
| `extensions\ms-vscode.powershell-*` | 300 MB | ⚠️ PowerShell extension |
| `extensions\google.geminicodeassist-*` | 267 MB | ⚠️ Gemini extension |
| `extensions\kilocode.kilo-code-*` | 154 MB | ⚠️ Kilo Code extension |
| `extensions\rooveterinaryinc.roo-cline-*` | 154 MB | ⚠️ Roo Cline extension |

**Note:** These are VS Code extensions installed by Cursor. Deleting will require re-download.

**Recommendation:** Keep if actively using Cursor  
**Recoverable:** 0-340 MB (if not using Cursor)

### 2.3 .gemini (333 MB)

**Location:** `C:\Users\karma\.gemini`

| Component | Size | Safe to Delete |
|-----------|------|----------------|
| `tmp/*` | 875 MB | ✅ Yes - temporary files |
| `tmp\*\chats` | ~400 MB | ⚠️ Loses chat history |
| `antigravity-browser-profile/*` | 578 MB | ✅ Browser cache |
| `antigravity-browser-profile\Default\Code Cache` | 237 MB | ✅ Code cache |
| `antigravity-browser-profile\Default\Cache` | 58 MB | ✅ Browser cache |
| `antigravity-browser-profile\Crashpad\reports` | 49 MB | ✅ Crash reports |

**Recommendation:** Clear tmp and browser cache, keep chats if needed  
**Recoverable:** ~250 MB

### 2.4 .trae (219 MB)

**Location:** `C:\Users\karma\.trae`

| Component | Size | Safe to Delete |
|-----------|------|----------------|
| `extensions/*` | 4.2 GB | ⚠️ Editor extensions |
| `extensions\yzane.markdown-pdf-*` | 324 MB | ⚠️ Markdown extension |
| `extensions\anthropic.claude-code-*` | 500 MB+ | ⚠️ Claude extension |
| `extensions\loki-laufeyson.intelligent-assistant-*` | 235 MB | ⚠️ Assistant extension |

**Recommendation:** Keep if actively using Trae  
**Recoverable:** 0-219 MB (if not using Trae)

### 2.5 .kiro (198 MB)

**Location:** `C:\Users\karma\.kiro`

| Component | Size | Safe to Delete |
|-----------|------|----------------|
| `extensions/*` | 1.3 GB | ⚠️ Editor extensions |
| `extensions\blackboxapp.blackboxagent-*` | 351 MB | ⚠️ Blackbox extension |
| `extensions\continue.continue-*` | 226 MB | ⚠️ Continue extension |
| `extensions\kilocode.kilo-code-*` | 171 MB | ⚠️ Kilo Code extension |

**Recommendation:** Keep if actively using Kiro  
**Recoverable:** 0-198 MB (if not using Kiro)

### 2.6 .lmstudio (233 MB)

**Location:** `C:\Users\karma\.lmstudio`

| Component | Size | Safe to Delete |
|-----------|------|----------------|
| `extensions/backends/*` | 3.8 GB | ⚠️ LLM backends (multiple versions) |
| `extensions/backends/llama.cpp-*` | 2.5 GB | ⚠️ Multiple llama.cpp versions |
| `.internal/*` | 88 MB | ✅ Internal cache |

**Note:** Contains multiple versions of llama.cpp backends (1.28.0 through 1.46.0)

**Recommendation:** Keep only latest backend version  
**Recoverable:** ~2 GB (by removing old backend versions)

### 2.7 .qwen (834 MB)

**Location:** `C:\Users\karma\.qwen`

| Component | Size | Safe to Delete |
|-----------|------|----------------|
| `tmp/*` | 836 MB | ✅ Yes - temporary files |
| `tmp\*\chats` | ~200 MB | ⚠️ Loses chat history |
| `projects\*\chats` | ~1.1 GB | ⚠️ Loses project chats |
| `debug/*` | <1 MB | ✅ Debug logs |
| `todos/*` | <1 MB | ✅ Todo files |

**Recommendation:** Clear tmp folder  
**Recoverable:** ~600 MB

### 2.8 .bun (226 MB)

**Location:** `C:\Users\karma\.bun`

| Component | Size | Safe to Delete |
|-----------|------|----------------|
| `bin/*` | 220 MB | ⚠️ Bun binaries (re-downloadable) |
| `install/cache/*` | 71 MB | ✅ Package cache |
| `install\cache\pyright@*` | 18 MB | ✅ Old pyright version |
| `install\cache\prettier@*` | 8 MB | ✅ Old prettier version |

**Recommendation:** Clear install/cache folder  
**Recoverable:** ~70 MB

---

## 3. NVIDIA CORPORATION CACHE

**Location:** `C:\ProgramData\NVIDIA Corporation`  
**Total Size:** 6.89 GB

| Component | Size | Safe to Delete |
|-----------|------|----------------|
| `NVIDIA App/UpdateFramework/ota-artifacts` | 8.8 GB | ✅ Update cache |
| `nvtopps/rise` | 3.4 GB | ⚠️ NVIDIA app data |
| `NVIDIA App/G-Assist` | 3.0 GB | ⚠️ AI assistant data |
| `Downloader/*` | 1.4 GB | ✅ Driver download cache |

**Cleaning Method:**
1. Open **GeForce Experience** or **NVIDIA App**
2. Go to Settings
3. Clear shader cache / download cache
4. Or manually delete `Downloader` and `UpdateFramework/ota-artifacts`

**Recoverable:** ~6 GB

---

## 4. WINDOWS\INSTALLER AUDIT

**Location:** `C:\Windows\Installer`  
**Total Size:** 11.92 GB (491 files)

### Largest Files

| File | Size | Date | Type |
|------|------|------|------|
| 5ad52e7.msp | 753 MB | Jun 2026 | Office update |
| 5ad54a1.msp | 753 MB | Jun 2026 | Office update |
| 117d967a.msp | 599 MB | Apr 2025 | Office update |
| ae676a6.msp | 440 MB | Dec 2025 | Office update |
| ae675f8.msp | 440 MB | Dec 2025 | Office update |
| 24ffd51.msp | 401 MB | Sep 2025 | Office update |
| 24ffe10.msp | 401 MB | Sep 2025 | Office update |
| 2ffa3.msp | 398 MB | Oct 2025 | Office update |
| 3004a.msp | 398 MB | Oct 2025 | Office update |
| 2f0ad11.msi | 383 MB | Apr 2025 | Application install |

**⚠️ WARNING:** Do NOT manually delete files from this folder!

### Safe Cleaning Options

#### Option A: PatchCleaner (Recommended)
```
Download: https://www.codesector.com/patchcleaner
- Scans for orphaned installer files
- Identifies files no longer needed
- Can move files instead of deleting (safer)
- Estimated recovery: 5-8 GB
```

#### Option B: DISM with ResetBase (Aggressive)
```cmd
DISM /Online /Cleanup-Image /StartComponentCleanup /ResetBase
```
⚠️ This prevents uninstalling ALL current Windows updates

**Recoverable:** ~5-8 GB (with PatchCleaner)

---

## 5. DISM CLEANUP ANALYSIS

**Command:** `DISM /Online /Cleanup-Image /StartComponentCleanup`

### What Gets Cleaned
- Superseded Windows Update files
- Old component versions
- Temporary installation files
- Service pack backups (if applicable)

### Expected Results
- **Typical:** 5-10 GB
- **After major update:** 10-20 GB
- **Time:** 10-60 minutes

### Safety
- ✅ Safe to run
- ✅ Microsoft recommended
- ⚠️ Cannot uninstall old updates after running

---

## 6. HIBERNATION STATUS

**Status:** ✅ **DISABLED**

```
powercfg /a output:
  Hibernate: Hibernation has not been enabled.
  Fast Startup: Hibernation is not available.
```

**Space already saved:** ~8-32 GB (hibernation was never enabled)

---

## 7. CONSOLIDATED CLEANUP PLAN

### Phase 1: Safe Automated Cleanup (Recover: ~8-12 GB)

```batch
REM 1. DISM Cleanup (5-20 GB)
DISM /Online /Cleanup-Image /StartComponentCleanup

REM 2. Clear temp folders (1-2 GB)
del /q /s %TEMP%\*
del /q /s C:\Windows\Temp\*

REM 3. Clear AI cache tmp folders (1-2 GB)
del /q /s "%USERPROFILE%\.gemini\tmp\*"
del /q /s "%USERPROFILE%\.qwen\tmp\*"
del /q /s "%USERPROFILE%\.bun\install\cache\*"
```

### Phase 2: Manual AI Cache Cleanup (Recover: ~4-6 GB)

```
Application          Action                              Space
─────────────────────────────────────────────────────────────────
.continue            Clear index/lancedb, index.sqlite   ~4.5 GB
.gemini              Clear tmp, browser cache            ~250 MB
.qwen                Clear tmp folder                    ~600 MB
.bun                 Clear install/cache                 ~70 MB
.lmstudio            Remove old llama.cpp versions       ~2 GB
```

### Phase 3: EXPERIMENTAL Folder (Recover: ~8-10 GB)

```
Action               Folders                            Space
─────────────────────────────────────────────────────────────────
Delete old backups   ULTIMATE_AI_PACKAGE*, backsept*    ~1 GB
Delete old configs   CONFIGURATION, DEPLOYMENT_*        ~500 MB
Delete old docs      DOCUMENTATION_*, SECURITY_*        ~200 MB
Review large folders nexus-ide*, voice_assistant*       ~400 MB
Archive old projects Move to X: drive                   ~5 GB
```

### Phase 4: NVIDIA Cache (Recover: ~6 GB)

```
Method: Use NVIDIA App or GeForce Experience
- Settings → Clear shader cache
- Settings → Clear download cache
Or manually delete:
- C:\ProgramData\NVIDIA Corporation\Downloader\*
- C:\ProgramData\NVIDIA Corporation\NVIDIA App\UpdateFramework\ota-artifacts\*
```

### Phase 5: Windows\Installer (Recover: ~5-8 GB)

```
Tool: PatchCleaner
- Download from codesector.com
- Run scan
- Review orphaned files
- Move (don't delete) identified files
```

---

## 8. PRIORITY ACTION LIST

| # | Action | Effort | Recover | Risk |
|---|--------|--------|---------|------|
| 1 | Run DISM cleanup | Low | 5-20 GB | None |
| 2 | Clear .continue cache | Low | 4.5 GB | Low |
| 3 | Clear .gemini tmp | Low | 250 MB | None |
| 4 | Clear .qwen tmp | Low | 600 MB | None |
| 5 | Clear .bun cache | Low | 70 MB | None |
| 6 | Clean NVIDIA cache | Medium | 6 GB | Low |
| 7 | Review EXPERIMENTAL | High | 8-10 GB | Medium |
| 8 | Run PatchCleaner | Medium | 5-8 GB | Low |
| 9 | Clean .lmstudio backends | Medium | 2 GB | Low |

**TOTAL:** ~32-57 GB recoverable

---

## 9. COMMANDS REFERENCE

### Safe Cleanup Commands (No Admin)
```powershell
# Clear .continue vector DB cache
Remove-Item "$env:USERPROFILE\.continue\index\lancedb" -Recurse -Force
Remove-Item "$env:USERPROFILE\.continue\index.sqlite*" -Force

# Clear .gemini tmp
Remove-Item "$env:USERPROFILE\.gemini\tmp" -Recurse -Force

# Clear .qwen tmp
Remove-Item "$env:USERPROFILE\.qwen\tmp" -Recurse -Force

# Clear .bun cache
Remove-Item "$env:USERPROFILE\.bun\install\cache" -Recurse -Force

# Check disk space
Get-PSDrive C | Select-Object Name,@{N='FreeGB';E={[math]::Round($_.Free/1GB,2)}}
```

### Admin Commands
```cmd
REM DISM cleanup
DISM /Online /Cleanup-Image /StartComponentCleanup

REM Clear Windows Update cache
net stop wuauserv && net stop bits
del /q /s C:\Windows\SoftwareDistribution\Download\*
net start wuauserv && net start bits

REM Empty Recycle Bin
powershell -Command "Clear-RecycleBin -Force"
```

---

## 10. FILES TO PRESERVE

### DO NOT DELETE
```
✅ C:\Users\karma\Documents\*     (User documents)
✅ C:\Users\karma\Pictures\*      (User photos)
✅ C:\Users\karma\Videos\*        (User videos)
✅ C:\Users\karma\Downloads\*     (Downloaded files)
✅ C:\Users\karma\ACTIVE_PROJECTS\*  (Active work)
✅ C:\Windows\System32\*          (System files)
✅ C:\Windows\Installer\*          (Use PatchCleaner only)
```

### BACKUP BEFORE DELETING
```
⚠️ C:\Users\karma\EXPERIMENTAL\github_repos\*     (May have code)
⚠️ C:\Users\karma\EXPERIMENTAL\opencode\*         (Check if migrated)
⚠️ C:\Users\karma\EXPERIMENTAL\nexus-ide\*        (IDE projects)
⚠️ C:\Users\karma\COMPLETED_PROJECTS\*            (Archive first)
```

---

## 11. MAINTENANCE RECOMMENDATIONS

### Weekly
- Clear browser cache (Ctrl+Shift+Delete)
- Empty Recycle Bin
- Clear %TEMP% folder

### Monthly
- Run DISM cleanup
- Review Downloads folder
- Clear AI editor caches

### Quarterly
- Review EXPERIMENTAL folder
- Run PatchCleaner
- Archive old projects to X: drive

---

**Report End**
