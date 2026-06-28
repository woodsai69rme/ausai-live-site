# Fast Repo Audit - No git commands
$repos = Get-ChildItem -Path X:\githubrepo -Directory | Where-Object { Test-Path "$($_.FullName)\.git" }

$results = @()
$count = 0

foreach ($repo in $repos) {
    $count++
    $repoPath = $repo.FullName
    $repoName = $repo.Name
    
    Write-Progress -Activity "Auditing Repos" -Status $repoName -PercentComplete (($count / $repos.Count) * 100)
    
    $readme = ""
    $type = "Unknown"
    $desc = ""
    $files = 0
    
    # Check for README
    $readmeFiles = @("README.md", "README.txt", "README", "readme.md")
    foreach ($rf in $readmeFiles) {
        $rfPath = Join-Path $repoPath $rf
        if (Test-Path $rfPath) {
            $readme = (Get-Content $rfPath -First 10 -ErrorAction SilentlyContinue) -join " "
            break
        }
    }
    
    # Detect project type
    if (Test-Path "$repoPath\package.json") {
        $type = "Node.js"
        try {
            $pkg = Get-Content "$repoPath\package.json" -ErrorAction SilentlyContinue | ConvertFrom-Json
            $desc = $pkg.description
        } catch {}
    }
    elseif ((Test-Path "$repoPath\pyproject.toml") -or (Test-Path "$repoPath\setup.py") -or (Test-Path "$repoPath\requirements.txt")) {
        $type = "Python"
    }
    elseif (Test-Path "$repoPath\Cargo.toml") {
        $type = "Rust"
    }
    elseif (Test-Path "$repoPath\go.mod") {
        $type = "Go"
    }
    elseif (Test-Path "$repoPath\pom.xml") {
        $type = "Java"
    }
    
    # Count files
    $files = (Get-ChildItem $repoPath -File -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
    
    $results += [PSCustomObject]@{
        Name = $repoName
        Type = $type
        Description = if ($desc) { $desc } else { $readme.Substring(0, [Math]::Min(100, $readme.Length)) }
        FileCount = $files
    }
}

# Output
$results | Export-Csv -Path C:\Users\karma\repo_audit_fast.csv -NoTypeInformation
Write-Host "`nAudit complete! $($results.Count) repos scanned." -ForegroundColor Green
Write-Host "Results saved to repo_audit_fast.csv" -ForegroundColor Yellow

# Summary by type
$results | Group-Object Type | Sort-Object Count -Descending | Format-Table
