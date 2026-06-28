# === PHASE 1: Delete Junk Folders ===
$junkFolders = @(
    'C:\Users\karma\{',
    'C:\Users\karma\}',
    'C:\Users\karma\if',
    'C:\Users\karma\else',
    'C:\Users\karma\echo',
    'C:\Users\karma\-p',
    'C:\Users\karma\Directory created or already exists',
    'C:\Users\karma\Directory created or exists',
    'C:\Users\karma\Directory may already exist'
)
foreach ($f in $junkFolders) {
    if (Test-Path $f) {
        Remove-Item -Recurse -Force $f
        Write-Host "[DELETED] $f" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] $f (not found)" -ForegroundColor Yellow
    }
}

# === PHASE 2: Delete Large Temp Artifacts ===
$tempFiles = @(
    'C:\Users\karma\EXPERIMENTAL_FULL_FILE_LIST.csv',
    'C:\Users\karma\EXPERIMENTAL_ALL_FILES.txt',
    'C:\Users\karma\EXPERIMENTAL_FOLDER_SUMMARIES.txt',
    'C:\Users\karma\EXPERIMENTAL_TOP_FOLDERS_FILE_LIST.txt',
    'C:\Users\karma\EXPERIMENTAL_AUDIT_REPORT_TEMPLATE.md',
    'C:\Users\karma\EXPERIMENTAL_COMPLETE_AUDIT.md',
    'C:\Users\karma\EXPERIMENTAL_FILE_COUNTS_SUMMARY.md'
)
foreach ($f in $tempFiles) {
    if (Test-Path $f) {
        Remove-Item -Force $f
        Write-Host "[DELETED] $f" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] $f (not found)" -ForegroundColor Yellow
    }
}

# === PHASE 3: Clean Logs from Home Root ===
$logFiles = @(
    'C:\Users\karma\verbose.log',
    'C:\Users\karma\backend.log',
    'C:\Users\karma\backend_server.log',
    'C:\Users\karma\frontend.log',
    'C:\Users\karma\playwright-mcp-server.log',
    'C:\Users\karma\jew_unified_system.log'
)
foreach ($f in $logFiles) {
    if (Test-Path $f) {
        Remove-Item -Force $f
        Write-Host "[DELETED] $f" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] $f (not found)" -ForegroundColor Yellow
    }
}

# === PHASE 4: Archive Old Audit Docs ===
$archiveDir = 'C:\Users\karma\_DOCS_ARCHIVE'
if (-not (Test-Path $archiveDir)) { New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null }

$auditDocs = @(
    'COMPREHENSIVE_SYSTEM_AUDIT_MASTER_REPORT.md',
    'COMPREHENSIVE_SYSTEM_AUDIT_REPORT.md',
    'FULL_SYSTEM_AUDIT_REPORT.md',
    'AUDIT_REPORT.md',
    'DETAILED_CLEANUP_AUDIT_REPORT.md',
    'FULL_AUDIT_AND_GOLDEN_RULES_REVIEW.md',
    'ULTIMATE_SYSTEM_AUDIT_REPORT_2026.md'
)
foreach ($doc in $auditDocs) {
    $src = "C:\Users\karma\$doc"
    if (Test-Path $src) {
        Move-Item -Force $src $archiveDir
        Write-Host "[ARCHIVED] $doc -> _DOCS_ARCHIVE\" -ForegroundColor Cyan
    } else {
        Write-Host "[SKIP] $doc (not found)" -ForegroundColor Yellow
    }
}

Write-Host "`n=== ALL 4 PHASES COMPLETE ===" -ForegroundColor Magenta
