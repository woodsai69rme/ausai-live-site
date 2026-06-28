# Clone all missing GitHub repos for woodsai69rme and leahmfoots
# This script extracts repo URLs from existing repos and clones any missing ones

$basePath = "X:\githubrepo"
$accounts = @("woodsai69rme", "leahmfoots")
$allRepoUrls = @{}

# Collect all unique repo URLs from existing repos
$repos = Get-ChildItem -Path $basePath -Directory | Where-Object { Test-Path "$($_.FullName)\.git" }

Write-Host "Scanning existing repos for remote URLs..." -ForegroundColor Cyan

foreach ($repo in $repos) {
    Set-Location $repo.FullName
    $remotes = git remote -v 2>$null
    foreach ($remote in $remotes) {
        if ($remote -match "(https?://[^/]+/([^/]+)/([^/]+)\.git)") {
            $url = $Matches[1]
            $owner = $Matches[2]
            $repoName = $Matches[3]
            
            if ($owner -in $accounts) {
                $allRepoUrls[$repoName] = @{
                    Url = $url
                    Owner = $owner
                    LocalPath = Join-Path $basePath $repoName
                }
            }
        }
    }
    Set-Location $basePath
}

Write-Host "Found $($allRepoUrls.Count) unique repos for your accounts" -ForegroundColor Green

# Check which ones are missing locally
$missingCount = 0
foreach ($repoName in $allRepoUrls.Keys) {
    $info = $allRepoUrls[$repoName]
    if (-not (Test-Path $info.LocalPath)) {
        $missingCount++
        Write-Host "[MISSING] $repoName - Cloning..." -ForegroundColor Yellow
        Set-Location $basePath
        try {
            git clone $info.Url 2>&1 | Out-Null
            Write-Host "  Cloned successfully!" -ForegroundColor Green
        } catch {
            Write-Host "  Error cloning: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "[OK] $repoName" -ForegroundColor Gray
    }
}

Write-Host "`n=== Complete ===" -ForegroundColor Cyan
Write-Host "Total repos tracked: $($allRepoUrls.Count)" -ForegroundColor Yellow
Write-Host "Missing repos cloned: $missingCount" -ForegroundColor Green
