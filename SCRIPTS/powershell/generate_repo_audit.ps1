$ReportPath = "C:\Users\karma\FULL_REPO_AUDIT.md"
$SearchPaths = @("C:\Users\karma", "X:\githubrepo")
$MaxDepth = 5

$ExcludeDirs = @("AppData", "node_modules", "\.venv", "env", "vendor", "\.nuget", "\.rustup", "\.cargo", "Pictures", "Music", "Videos", "Downloads", "Documents")

function Get-RepoInfo {
    param($Path)
    
    $RepoName = Split-Path $Path -Leaf
    $Status = "Active/Unknown"
    $Summary = "No description found."
    
    # Check for package.json for description first
    $PkgJsonPath = Join-Path $Path "package.json"
    if (Test-Path $PkgJsonPath) {
        try {
            $Pkg = Get-Content $PkgJsonPath -Raw | ConvertFrom-Json
            if ($Pkg.description) {
                $Summary = $Pkg.description
            }
        } catch {}
    }

    # If no description from package.json, try README.md
    if ($Summary -eq "No description found.") {
        $ReadmePath = Join-Path $Path "README.md"
        if (Test-Path $ReadmePath) {
            try {
                $ReadmeContent = Get-Content $ReadmePath -TotalCount 15 -ErrorAction SilentlyContinue
                if ($ReadmeContent) {
                    # Try to find the first non-empty line that isn't just a heading or badge
                    foreach ($line in $ReadmeContent) {
                        if (![string]::IsNullOrWhiteSpace($line) -and $line -notmatch "^(#|\[|!)") {
                            $Summary = $line.Trim()
                            if ($Summary.Length -gt 150) { 
                                $Summary = $Summary.Substring(0, 147) + "..." 
                            }
                            # Escape pipes for markdown table
                            $Summary = $Summary -replace '\|', '\|'
                            break
                        }
                    }
                }
            } catch {}
        }
    }
    
    # Check git status
    if (Test-Path (Join-Path $Path ".git")) {
        try {
            Push-Location $Path
            $gitStatus = git status -s 2>&1
            if ($LASTEXITCODE -ne 0) {
                 $Status = "Git Error/Not Repo"
            } elseif ([string]::IsNullOrWhiteSpace($gitStatus)) {
                $Status = "Clean"
            } else {
                $Status = "Uncommitted Changes"
            }
            Pop-Location
        } catch {
            $Status = "Git Error"
            if ((Get-Location).Path -eq $Path) { Pop-Location }
        }
    } else {
        $Status = "Not a Git Repo"
    }

    return [PSCustomObject]@{
        Name = $RepoName
        Path = $Path
        Status = $Status
        Summary = $Summary
    }
}

"# Full Project & Repository Audit Report`n> Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" | Out-File -FilePath $ReportPath -Encoding UTF8

foreach ($SearchPath in $SearchPaths) {
    if (Test-Path $SearchPath) {
        "## Scanning $SearchPath`n" | Out-File -FilePath $ReportPath -Append -Encoding UTF8
        "| Project | Path | Status | Summary |" | Out-File -FilePath $ReportPath -Append -Encoding UTF8
        "|---|---|---|---|" | Out-File -FilePath $ReportPath -Append -Encoding UTF8
        
        Write-Host "Scanning $SearchPath for Git repositories (Depth $MaxDepth)..."
        
        # Find all .git directories to identify repos
        $GitDirs = Get-ChildItem -Path $SearchPath -Filter ".git" -Directory -Recurse -Depth $MaxDepth -ErrorAction SilentlyContinue | Where-Object {
            $pathStr = $_.FullName
            $ExcludeMatch = $false
            foreach ($ex in $ExcludeDirs) {
                if ($pathStr -match "\\$ex\\") {
                    $ExcludeMatch = $true
                    break
                }
            }
            -not $ExcludeMatch
        }
        
        $Count = 0
        foreach ($GitDir in $GitDirs) {
            $RepoPath = $GitDir.Parent.FullName
            $Info = Get-RepoInfo -Path $RepoPath
            "| **$($Info.Name)** | `$($Info.Path)` | $($Info.Status) | $($Info.Summary) |" | Out-File -FilePath $ReportPath -Append -Encoding UTF8
            Write-Host "Found: $($Info.Name) - $($Info.Status)"
            $Count++
        }
        
        if ($Count -eq 0) {
            "| *(None found)* | - | - | - |" | Out-File -FilePath $ReportPath -Append -Encoding UTF8
        }
        "`n" | Out-File -FilePath $ReportPath -Append -Encoding UTF8
        Write-Host "Found $Count repositories in $SearchPath.`n"
    } else {
        "## Scanning $SearchPath`n**Path not found or inaccessible.**`n" | Out-File -FilePath $ReportPath -Append -Encoding UTF8
        Write-Host "Path not found: $SearchPath"
    }
}

Write-Host "Audit complete. Report saved to $ReportPath"
