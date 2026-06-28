# Revenue Generator Activation Checklist
# Reviews and activates revenue generators

$ErrorActionPreference = "Stop"
$outputFile = "C:\Users\karma\REVENUE_STATUS_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REVENUE GENERATOR ACTIVATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$revenuePath = "C:\Users\karma\REVENUE_GENERATORS"

if (-not (Test-Path $revenuePath)) {
    Write-Host "REVENUE_GENERATORS folder not found!" -ForegroundColor Red
    exit
}

$projects = Get-ChildItem -Path $revenuePath -Directory -ErrorAction SilentlyContinue
Write-Host "Found $($projects.Count) revenue generators" -ForegroundColor Yellow

$revenueStatus = @()

foreach ($project in $projects) {
    Write-Host "Checking: $($project.Name)" -ForegroundColor Gray
    
    # Check activation requirements
    $hasReadme = Test-Path "$($project.FullName)\README.md"
    $hasPackageJson = Test-Path "$($project.FullName)\package.json"
    $hasRequirements = Test-Path "$($project.FullName)\requirements.txt"
    $hasEnvExample = Test-Path "$($project.FullName)\.env.example"
    $hasConfig = (Test-Path "$($project.FullName)\config.json") -or (Test-Path "$($project.FullName)\config.yaml")
    
    # Check if node_modules or venv exists (dependencies installed)
    $hasNodeModules = Test-Path "$($project.FullName)\node_modules"
    $hasVenv = (Test-Path "$($project.FullName)\venv") -or (Test-Path "$($project.FullName)\.venv") -or (Test-Path "$($project.FullName)\env")
    
    # Check for main entry points
    $hasMainPy = Test-Path "$($project.FullName)\main.py"
    $hasIndexJs = (Test-Path "$($project.FullName)\index.js") -or (Test-Path "$($project.FullName)\app.js") -or (Test-Path "$($project.FullName)\server.js")
    $hasDockerfile = Test-Path "$($project.FullName)\Dockerfile"
    $hasDockerCompose = Test-Path "$($project.FullName)\docker-compose.yml"
    
    # Calculate readiness score
    $readinessScore = 0
    if ($hasReadme) { $readinessScore += 10 }
    if ($hasPackageJson -or $hasRequirements) { $readinessScore += 10 }
    if ($hasEnvExample) { $readinessScore += 15 }
    if ($hasConfig) { $readinessScore += 10 }
    if ($hasNodeModules -or $hasVenv) { $readinessScore += 20 }
    if ($hasMainPy -or $hasIndexJs) { $readinessScore += 20 }
    if ($hasDockerfile) { $readinessScore += 10 }
    if ($hasDockerCompose) { $readinessScore += 5 }
    
    $status = if ($readinessScore -ge 80) { "READY_TO_ACTIVATE" }
              elseif ($readinessScore -ge 60) { "NEEDS_MINOR_WORK" }
              elseif ($readinessScore -ge 40) { "NEEDS_MAJOR_WORK" }
              else { "NOT_READY" }
    
    $revenueStatus += [PSCustomObject]@{
        ProjectName = $project.Name
        Status = $status
        ReadinessScore = $readinessScore
        HasREADME = $hasReadme
        HasDependencies = ($hasNodeModules -or $hasVenv)
        HasEntryPoint = ($hasMainPy -or $hasIndexJs)
        HasDocker = ($hasDockerfile -or $hasDockerCompose)
        HasEnvExample = $hasEnvExample
        LastModified = $project.LastWriteTime.ToString("yyyy-MM-dd")
        FullPath = $project.FullName
    }
}

# Export to CSV
$revenueStatus | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8

# Generate summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  REVENUE STATUS SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$total = $revenueStatus.Count
$ready = ($revenueStatus | Where-Object { $_.Status -eq "READY_TO_ACTIVATE" }).Count
$minorWork = ($revenueStatus | Where-Object { $_.Status -eq "NEEDS_MINOR_WORK" }).Count
$majorWork = ($revenueStatus | Where-Object { $_.Status -eq "NEEDS_MAJOR_WORK" }).Count
$notReady = ($revenueStatus | Where-Object { $_.Status -eq "NOT_READY" }).Count

Write-Host "Total Revenue Generators: $total" -ForegroundColor White
Write-Host "  Ready: $ready" -ForegroundColor Green
Write-Host "  Needs Minor Work: $minorWork" -ForegroundColor Yellow
Write-Host "  Needs Major Work: $majorWork" -ForegroundColor Yellow
Write-Host "  Not Ready: $notReady" -ForegroundColor Red

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  READY TO ACTIVATE NOW" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$readyProjects = $revenueStatus | Where-Object { $_.Status -eq "READY_TO_ACTIVATE" }
if ($readyProjects) {
    $readyProjects | Sort-Object ReadinessScore -Descending | Format-Table ProjectName, ReadinessScore, HasDependencies, HasEntryPoint -AutoSize
} else {
    Write-Host "No projects ready to activate yet." -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  NEEDS WORK (TOP PRIORITY)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$needsWork = $revenueStatus | Where-Object { $_.Status -in @("NEEDS_MINOR_WORK", "NEEDS_MAJOR_WORK") } |
    Sort-Object ReadinessScore -Descending | Select-Object -First 10

if ($needsWork) {
    $needsWork | Format-Table ProjectName, Status, ReadinessScore, HasREADME, HasDependencies -AutoSize
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Report saved to: $outputFile" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
