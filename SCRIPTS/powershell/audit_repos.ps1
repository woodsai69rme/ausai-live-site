# Comprehensive Repo Audit Script - Fixed
$repos = Get-ChildItem -Path X:\githubrepo -Directory | Where-Object { Test-Path "$($_.FullName)\.git" }
$results = @()

foreach ($repo in $repos) {
    $repoPath = $repo.FullName
    $repoName = $repo.Name

    Write-Host "Scanning: $repoName" -ForegroundColor Cyan

    $info = [PSCustomObject]@{
        Name = $repoName
        Path = $repoPath
        HasReadme = $false
        ReadmeFirstLines = ""
        HasPackageJson = $false
        HasPythonProject = $false
        GitStatus = "unknown"
        LastCommit = ""
        RemoteUrl = ""
        Description = ""
        MainLanguage = "unknown"
    }

    # Check for README
    $readmeFiles = @("README.md", "README.txt", "README", "readme.md")
    foreach ($rf in $readmeFiles) {
        $rfPath = Join-Path $repoPath $rf
        if (Test-Path $rfPath) {
            $info.HasReadme = $true
            $info.ReadmeFirstLines = (Get-Content $rfPath -TotalCount 10 -ErrorAction SilentlyContinue) -join " "
            break
        }
    }

    # Check for package.json (Node.js)
    if (Test-Path "$repoPath\package.json") {
        $info.HasPackageJson = $true
        try {
            $pkg = Get-Content "$repoPath\package.json" -Raw -ErrorAction SilentlyContinue | ConvertFrom-Json
            if ($pkg.description) { $info.Description = $pkg.description }
            if ($pkg.name) { $info.Name = $pkg.name }
        } catch {}
    }

    # Check for Python project
    if ((Test-Path "$repoPath\pyproject.toml") -or (Test-Path "$repoPath\setup.py") -or (Test-Path "$repoPath\requirements.txt")) {
        $info.PythonProject = $true
    }

    # Detect main language
    if (Test-Path "$repoPath\package.json") { $info.MainLanguage = "JavaScript/TypeScript" }
    elseif (Test-Path "$repoPath\pyproject.toml") { $info.MainLanguage = "Python" }
    elseif (Test-Path "$repoPath\Cargo.toml") { $info.MainLanguage = "Rust" }
    elseif (Test-Path "$repoPath\go.mod") { $info.MainLanguage = "Go" }
    elseif (Test-Path "$repoPath\pom.xml") { $info.MainLanguage = "Java" }

    # Get git info
    if (Test-Path "$repoPath\.git") {
        Set-Location $repoPath
        try {
            $status = git status --short 2>$null
            if ($status) { $info.GitStatus = "has changes" } else { $info.GitStatus = "clean" }
            $info.LastCommit = (git log -1 --format="%ci - %s" 2>$null)
            $info.RemoteUrl = (git remote get-url origin 2>$null)
        } catch {}
        Set-Location X:\githubrepo
    }

    $results += $info
}

# Output results
$results | Export-Csv -Path C:\Users\karma\repo_audit.csv -NoTypeInformation
$results | ConvertTo-Json -Depth 3 | Out-File -Path C:\Users\karma\repo_audit.json

Write-Host "`nAudit complete! Results saved." -ForegroundColor Green
Write-Host "Total repos scanned: $($results.Count)" -ForegroundColor Yellow
