# EnvironmentSanitizer.ps1 - ENH-H4 Environment Sanitizer (Catalog Pass)
#
# ✅ COMPLIANCE: ADDITIVE ONLY.
# - Walks the host for every `.env*` file and reports locations.
# - NEVER deletes, moves, renames, or rewrites any `.env*` file.
# - Originals remain (Rule #5 - All Backups Critical).
# - Personal folders (Documents, Downloads, Pictures, Videos, Music,
#   Desktop, OneDrive, Downloads\ARCHIVE_OLD) are listed (presence only)
#   but NEVER opened (Rule #8).

[CmdletBinding()]
param(
    [string]$Roots           = "$HOME",
    [int]$MaxDepth           = 5,
    [string]$ReportPath      = "$HOME\ENV_SANITIZER_REPORT.md",
    [string]$ManifestPath    = "$HOME\ENV_SANITIZER_MANIFEST.csv",
    [string[]]$ExcludeGlobs  = @(
        "node_modules", ".venv", "__pycache__", ".cache",
        "node_modules", ".git", ".next", ".venv", "dist", "build"
    )
)

# Personal folders: NEVER OPEN (Rule #8)
$PERSONAL_FOLDERS = @(
    "$HOME\Documents",
    "$HOME\Downloads",
    "$HOME\Pictures",
    "$HOME\Videos",
    "$HOME\Music",
    "$HOME\Desktop",
    "$HOME\OneDrive",
    "$HOME\Downloads\ARCHIVE_OLD"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Test-InPersonal {
    param([string]$Path)
    foreach ($p in $PERSONAL_FOLDERS) {
        if ($Path -like "$p*") {
            return $true
        }
    }
    return $false
}

function Get-EnvFiles {
    param([string]$Root, [int]$Depth, [string[]]$GlobExcludes)

    # Collect dir paths up to Depth first, then filter exclusions.
    $dirList = New-Object System.Collections.Generic.List[string]
    $dirList.Add($Root)

    for ($i = 0; $i -lt $Depth; $i++) {
        $next = New-Object System.Collections.Generic.List[string]
        foreach ($d in $dirList) {
            try {
                $children = Get-ChildItem -LiteralPath $d -Directory -ErrorAction SilentlyContinue
                foreach ($child in $children) {
                    foreach ($g in $GlobExcludes) {
                        if ($child.Name -ieq $g) { continue }
                    }
                    $next.Add($child.FullName)
                }
            } catch { continue }
        }
        foreach ($n in $next) { $dirList.Add($n) }
    }

    foreach ($d in $dirList) {
        if (Test-InPersonal -Path $d) { continue }
        try {
            Get-ChildItem -LiteralPath $d -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -like '.env*' -or $_.Name -cmatch '^env\.' } |
                ForEach-Object {
                    [pscustomobject]@{
                        Path      = $_.FullName
                        SizeBytes = $_.Length
                        LastWrite = $_.LastWriteTime.ToString('o')
                        Sha256    = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256 -ErrorAction SilentlyContinue).Hash
                        InPersonal = 'false'
                    }
                }
        } catch { continue }
    }
}

function Get-PersonalEnvPresence {
    # Catalog only. NEITHER opens NOR sizes files inside personal folders.
    foreach ($p in $PERSONAL_FOLDERS) {
        if (-not (Test-Path -LiteralPath $p)) { continue }
        $count = 0
        try {
            $count = @(Get-ChildItem -LiteralPath $p -File -Recurse -ErrorAction SilentlyContinue -Filter '.env*' | Where-Object { $_.Name -like '.env*' }).Count
        } catch { $count = -1 }
        [pscustomobject]@{
            Path      = $p
            Count     = $count
            InPersonal = 'true'
            Note      = "Listed but NEVER opened. Rule #8."
        }
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
$envFiles   = @(Get-EnvFiles -Root $Roots -Depth $MaxDepth -GlobExcludes $ExcludeGlobs)
$personalPs = @(Get-PersonalEnvPresence)

# Combine: env files (read-hashed) + personal presence (count only).
$combined = $envFiles + $personalPs
$combined | Export-Csv -LiteralPath $ManifestPath -NoTypeInformation -Append

# Append-only Markdown report
$ts      = (Get-Date).ToString('o')
$report  = @"
## ENH-H4 sanitization pass \u2014 $ts

- Scope: $HOME (depth=$MaxDepth)
- Files inspected (catalog-only): $(@($envFiles).Count)
- Personal-folder presence only: $(@($personalPs).Count) (Rule #8: NEVER opened)
- Manifest appended to: $ManifestPath
- Personal folders excluded from contents: Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD

### Top 25 non-personal .env* files by size

| Path | Size | SHA-256 (head) | LastWrite |
|---|---|---|---|
"@

$top = $envFiles | Sort-Object SizeBytes -Descending | Select-Object -First 25
foreach ($e in $top) {
    $sha = if ($e.Sha256) { $e.Sha256.Substring(0,12) } else { '-' }
    $report += "`n| $($e.Path) | $($e.SizeBytes) | $sha | $($e.LastWrite) |"
}

$report += "`n### Personal-folder presence (do NOT auto-merge, do NOT open)`n"
$report += "| Folder | Count | Note |`n|---|---|---|"
foreach ($p in $personalPs) {
    $report += "`n| $($p.Path) | $($p.Count) | $($p.Note) |"
}

$report += "`n### NEVER-DO LIST (this script enforces)`n"
$report += "- ❌ Delete any .env* file"
$report += "- ❌ Rewrite any .env* file in-place"
$report += "- ❌ Open any .env* file inside a Rule #8 personal folder"
$report += "- ❌ Move .env* files out of their existing location"
$report += "- ✅ Read-and-document (this script does)"
$report += "- ✅ Append-only manifest"
$report += "- ✅ Append-only report"

$report | Out-File -LiteralPath $ReportPath -Append -Encoding utf8
$log = "$(Get-Date -Format 'o') ENH-H4 ENV_SANITIZER files=$(@($envFiles).Count) personal=$(@($personalPs).Count)"
$log | Out-File -Append -LiteralPath "$HOME\08_SCRIPTS\ENV_SANITIZER_AUDIT.log" -Encoding utf8

Write-Host "ENH-H4: cataloged $($envFiles.Count) non-personal .env* files; $($personalPs.Count) personal-folder presence entries. Appended to $ReportPath and $ManifestPath."
