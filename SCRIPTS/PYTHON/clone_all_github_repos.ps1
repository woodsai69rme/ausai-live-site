# Clone ALL GitHub repos for woodsai69rme and leahmfoots
# Uses gh CLI to list and clone repos

param(
    [string]$Account = "woodsai69rme",
    [string]$Destination = "X:\githubrepo"
)

Write-Host "=== Cloning all repos for $Account ===" -ForegroundColor Cyan

# Check if gh is authenticated
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not authenticated! Run: gh auth login" -ForegroundColor Red
    exit 1
}

# Get all repos
Write-Host "Fetching repo list..." -ForegroundColor Yellow
$reposJson = gh repo list $Account --limit 1000 --json name,url,visibility 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error fetching repos: $reposJson" -ForegroundColor Red
    exit 1
}

$repos = $reposJson | ConvertFrom-Json
Write-Host "Found $($repos.Count) repos" -ForegroundColor Green

# Clone each repo
$cloned = 0
$skipped = 0
$failed = 0

foreach ($repo in $repos) {
    $repoName = $repo.name
    $repoPath = Join-Path $Destination $repoName
    $repoUrl = $repo.url
    
    if (Test-Path $repoPath) {
        Write-Host "[SKIP] $repoName (already exists)" -ForegroundColor Gray
        $skipped++
    } else {
        Write-Host "[CLONE] $repoName..." -ForegroundColor Yellow
        Set-Location $Destination
        $result = gh repo clone "$Account/$repoName" $repoPath 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Cloned successfully!" -ForegroundColor Green
            $cloned++
        } else {
            Write-Host "  Error: $result" -ForegroundColor Red
            $failed++
        }
    }
}

Write-Host "`n=== Complete ===" -ForegroundColor Cyan
Write-Host "Cloned: $cloned" -ForegroundColor Green
Write-Host "Skipped: $skipped" -ForegroundColor Yellow
Write-Host "Failed: $failed" -ForegroundColor Red
