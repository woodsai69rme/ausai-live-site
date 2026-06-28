# Project Status Review
# Reviews all projects and generates status report

$ErrorActionPreference = "Stop"
$outputFile = "C:\Users\karma\PROJECT_STATUS_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PROJECT STATUS REVIEW" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$paths = @(
    @{Name="ACTIVE_PROJECTS"; Path="C:\Users\karma\ACTIVE_PROJECTS"},
    @{Name="EXPERIMENTAL"; Path="C:\Users\karma\EXPERIMENTAL"},
    @{Name="REVENUE_GENERATORS"; Path="C:\Users\karma\REVENUE_GENERATORS"},
    @{Name="projects\ACTIVE"; Path="C:\Users\karma\projects\ACTIVE"}
)

$projects = @()

foreach ($pathInfo in $paths) {
    if (Test-Path $pathInfo.Path) {
        Write-Host "Reviewing: $($pathInfo.Name)" -ForegroundColor Yellow
        
        $projectDirs = Get-ChildItem -Path $pathInfo.Path -Directory -ErrorAction SilentlyContinue
        
        foreach ($project in $projectDirs) {
            # Check for key files
            $hasReadme = Test-Path "$($project.FullName)\README.md"
            $hasPackageJson = Test-Path "$($project.FullName)\package.json"
            $hasRequirements = Test-Path "$($project.FullName)\requirements.txt"
            $hasConfig = (Test-Path "$($project.FullName)\config.json") -or 
                        (Test-Path "$($project.FullName)\config.yaml") -or
                        (Test-Path "$($project.FullName)\.env.example")
            
            # Get file count and size
            $files = Get-ChildItem -Path $project.FullName -Recurse -File -ErrorAction SilentlyContinue
            $fileCount = $files.Count
            $totalSize = ($files | Measure-Object -Property Length -Sum).Sum
            
            # Check last activity
            $lastModified = $project.LastWriteTime
            $daysSinceUpdate = (New-TimeSpan -Start $lastModified -End (Get-Date)).Days
            
            # Determine status
            $completeness = 0
            if ($hasReadme) { $completeness += 25 }
            if ($hasPackageJson -or $hasRequirements) { $completeness += 25 }
            if ($hasConfig) { $completeness += 25 }
            if ($fileCount -gt 0) { $completeness += 25 }
            
            $status = if ($completeness -ge 75) { "COMPLETE" }
                      elseif ($completeness -ge 50) { "NEEDS_WORK" }
                      else { "INCOMPLETE" }
            
            $projects += [PSCustomObject]@{
                Category = $pathInfo.Name
                ProjectName = $project.Name
                Status = $status
                Completeness = $completeness
                Files = $fileCount
                Size_MB = [math]::Round($totalSize / 1MB, 2)
                HasREADME = $hasReadme
                HasPackageJson = $hasPackageJson
                HasRequirements = $hasRequirements
                HasConfig = $hasConfig
                LastModified = $lastModified.ToString("yyyy-MM-dd")
                DaysSinceUpdate = $daysSinceUpdate
                FullPath = $project.FullName
            }
        }
        
        Write-Host "  Reviewed $($projectDirs.Count) projects" -ForegroundColor Green
    }
}

# Export to CSV
$projects | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8

# Generate summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PROJECT STATUS SUMMARY" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$totalProjects = $projects.Count
$complete = ($projects | Where-Object { $_.Status -eq "COMPLETE" }).Count
$needsWork = ($projects | Where-Object { $_.Status -eq "NEEDS_WORK" }).Count
$incomplete = ($projects | Where-Object { $_.Status -eq "INCOMPLETE" }).Count

Write-Host "Total Projects: $totalProjects" -ForegroundColor White
Write-Host "  ✅ Complete: $complete ($([math]::Round($complete/$totalProjects*100, 1))%)" -ForegroundColor Green
Write-Host "  ⚠️  Needs Work: $needsWork ($([math]::Round($needsWork/$totalProjects*100, 1))%)" -ForegroundColor Yellow
Write-Host "  ❌ Incomplete: $incomplete ($([math]::Round($incomplete/$totalProjects*100, 1))%)" -ForegroundColor Red

Write-Host "`nBy Category:" -ForegroundColor Cyan
$projects | Group-Object Category | ForEach-Object {
    $catComplete = ($_.Group | Where-Object { $_.Status -eq "COMPLETE" }).Count
    Write-Host "  $($_.Name): $($_.Count) projects ($catComplete complete)" -ForegroundColor White
}

Write-Host "`nReport saved to: $outputFile" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  INCOMPLETE PROJECTS (Action Required)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$incompleteProjects = $projects | Where-Object { $_.Status -eq "INCOMPLETE" } | 
    Sort-Object Size_MB -Descending | Select-Object -First 20

if ($incompleteProjects.Count -gt 0) {
    $incompleteProjects | Format-Table ProjectName, Category, Size_MB, HasREADME, LastModified -AutoSize
} else {
    Write-Host "No incomplete projects!" -ForegroundColor Green
}

Write-Host "`n========================================`n" -ForegroundColor Cyan
