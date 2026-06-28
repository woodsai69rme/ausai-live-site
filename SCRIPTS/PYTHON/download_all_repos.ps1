# Download ALL GitHub repos for woodsai69rme and leahmfoots
# This script will list all repos from both accounts and clone any missing ones

$accounts = @("woodsai69rme", "leahmfoots")
$basePath = "X:\githubrepo"
$token = "" # Will be fetched from gh CLI

# Try to get token
try {
    $token = (gh auth token 2>$null)
    if (-not $token) {
        Write-Host "No GitHub token found. Please run: gh auth login" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error getting token: $_" -ForegroundColor Red
    exit 1
}

$headers = @{Authorization = "token $token"}

foreach ($account in $accounts) {
    Write-Host "`nFetching repos for $account..." -ForegroundColor Cyan
    
    $allRepos = @()
    $page = 1
    
    # Fetch all repos (paginated)
    do {
        $url = "https://api.github.com/user/repos?per_page=100&page=$page&type=owner&affiliation=owner"
        try {
            $repos = Invoke-RestMethod -Uri $url -Headers $headers -ErrorAction Stop
            $allRepos += $repos
            $page++
        } catch {
            Write-Host "Error fetching repos: $_" -ForegroundColor Red
            break
        }
    } while ($repos.Count -eq 100)
    
    Write-Host "Found $($allRepos.Count) repos for $account" -ForegroundColor Green
    
    # Check which repos are missing locally
    foreach ($repo in $allRepos) {
        $repoName = $repo.name
        $repoPath = Join-Path $basePath $repoName
        $cloneUrl = $repo.clone_url
        
        if (Test-Path $repoPath) {
            Write-Host "  [EXISTS] $repoName" -ForegroundColor Gray
        } else {
            Write-Host "  [MISSING] Cloning $repoName..." -ForegroundColor Yellow
            Set-Location $basePath
            try {
                git clone $cloneUrl 2>&1 | Out-Null
                Write-Host "    Cloned successfully!" -ForegroundColor Green
            } catch {
                Write-Host "    Error cloning: $_" -ForegroundColor Red
            }
        }
    }
}

Write-Host "`n=== Download Complete ===" -ForegroundColor Cyan
Write-Host "All repos from woodsai69rme and leahmfoots have been processed." -ForegroundColor Green
