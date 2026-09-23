# Clone all GitHub repos for authenticated account(s) into X:\githubrepo
# Handles private repos via gh CLI keyring token.
# Golden Rule: never deletes existing clones - skip if directory exists.

param(
    [string[]]$Accounts = @("woodsai69rme"),
    [string]$Destination = "X:\githubrepo",
    [switch]$PullExisting,
    [int]$Limit = 1000
)

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = "C:\Users\karma\_DOCS_ARCHIVE\clone_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir "clone_$timestamp.log"
$reportFile = Join-Path $logDir "clone_$timestamp.json"

function Write-Log($msg, $color = "White") {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] $msg"
    Add-Content -Path $logFile -Value $line
    Write-Host $line -ForegroundColor $color
}

# Invalid GITHUB_TOKEN env overrides gh keyring and breaks private repo access
if ($env:GITHUB_TOKEN) {
    Write-Log "Clearing GITHUB_TOKEN env (was overriding gh keyring)" "Yellow"
    Remove-Item Env:GITHUB_TOKEN -ErrorAction SilentlyContinue
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Log "gh CLI not found. Install GitHub CLI first." "Red"
    exit 1
}

if (-not (Test-Path $Destination)) {
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Write-Log "Created destination $Destination" "Green"
}

$summary = @{
    started_at = (Get-Date).ToString("o")
    destination = $Destination
    accounts = @()
    totals = @{ cloned = 0; skipped = 0; pulled = 0; failed = 0 }
    failures = @()
}

foreach ($account in $Accounts) {
    Write-Log "=== Account: $account ===" "Cyan"
    gh auth switch -u $account 2>&1 | Out-Null
    $login = gh api user --jq ".login" 2>&1
    if ($LASTEXITCODE -ne 0 -or "$login" -ne $account) {
        Write-Log "Not authenticated for $account - run: gh auth login" "Red"
        Write-Log "  gh api user returned: $login" "Red"
        $summary.accounts += @{ account = $account; status = "auth_failed"; repos = 0 }
        continue
    }
    Write-Log "Authenticated as $login" "Green"

    Write-Log "Fetching repo list (limit $Limit)..." "Yellow"
    $reposJson = gh repo list $account --limit $Limit --json name,url,visibility,isPrivate,isFork,updatedAt 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Error listing repos for ${account}: $reposJson" "Red"
        $summary.accounts += @{ account = $account; status = "list_failed"; repos = 0 }
        continue
    }

    $repos = $reposJson | ConvertFrom-Json
    Write-Log "Found $($repos.Count) repos for $account" "Green"
    $acctStats = @{ account = $account; status = "ok"; repos = $repos.Count; cloned = 0; skipped = 0; pulled = 0; failed = 0 }

    foreach ($repo in $repos) {
        $repoName = $repo.name
        $repoPath = Join-Path $Destination $repoName
        $fullName = "$account/$repoName"

        if (Test-Path $repoPath) {
            if ($PullExisting -and (Test-Path (Join-Path $repoPath ".git"))) {
                Write-Log "[PULL] $repoName" "DarkCyan"
                Push-Location $repoPath
                git pull --ff-only 2>&1 | ForEach-Object { Write-Log "  $_" "DarkGray" }
                if ($LASTEXITCODE -eq 0) {
                    $acctStats.pulled++
                    $summary.totals.pulled++
                } else {
                    Write-Log "  pull failed for $repoName" "Yellow"
                }
                Pop-Location
            } else {
                Write-Log "[SKIP] $repoName (exists)" "DarkGray"
                $acctStats.skipped++
                $summary.totals.skipped++
            }
            continue
        }

        Write-Log "[CLONE] $fullName ..." "Yellow"
        Push-Location $Destination
        $result = gh repo clone $fullName $repoPath 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "  OK $repoName" "Green"
            $acctStats.cloned++
            $summary.totals.cloned++
        } else {
            Write-Log "  FAIL $repoName : $result" "Red"
            $acctStats.failed++
            $summary.totals.failed++
            $summary.failures += @{ repo = $fullName; error = ($result -join " ") }
        }
        Pop-Location
    }

    $summary.accounts += $acctStats
}

$summary.finished_at = (Get-Date).ToString("o")
$summary | ConvertTo-Json -Depth 6 | Set-Content -Path $reportFile -Encoding UTF8

Write-Log "" 
Write-Log "=== COMPLETE ===" "Cyan"
Write-Log "Cloned: $($summary.totals.cloned)" "Green"
Write-Log "Skipped: $($summary.totals.skipped)" "DarkGray"
Write-Log "Pulled: $($summary.totals.pulled)" "DarkCyan"
Write-Log "Failed: $($summary.totals.failed)" "Red"
Write-Log "Log: $logFile" "White"
Write-Log "Report: $reportFile" "White"

if ($summary.totals.failed -gt 0) { exit 2 }
exit 0