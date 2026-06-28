# EXPERIMENTAL Folder Analysis Report
# Generates a detailed report of all subdirectories

$outputFile = "C:\Users\karma\SCRIPTS\experimental_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  EXPERIMENTAL FOLDER ANALYSIS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$basePath = "C:\Users\karma\EXPERIMENTAL"

if (-not (Test-Path $basePath)) {
    Write-Host "EXPERIMENTAL folder not found!" -ForegroundColor Red
    exit
}

$report = @()
$totalSize = 0
$totalFiles = 0

Write-Host "Scanning subdirectories..." -ForegroundColor Yellow

$subdirs = Get-ChildItem $basePath -Directory -ErrorAction SilentlyContinue

foreach ($dir in $subdirs) {
    Write-Host "  Processing: $($dir.Name)" -ForegroundColor Gray
    
    $files = Get-ChildItem $dir.FullName -Recurse -File -ErrorAction SilentlyContinue
    $size = ($files | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
    $fileCount = ($files | Measure-Object).Count
    
    $totalSize += $size
    $totalFiles += $fileCount
    
    $report += [PSCustomObject]@{
        Name = $dir.Name
        Size_GB = [math]::Round($size / 1GB, 2)
        File_Count = $fileCount
        Last_Modified = $dir.LastWriteTime
        Days_Old = (New-TimeSpan -Start $dir.LastWriteTime -End (Get-Date)).Days
    }
}

# Sort by size (largest first)
$sortedReport = $report | Sort-Object Size_GB -Descending

# Export to CSV
$sortedReport | Export-Csv -Path $outputFile -NoTypeInformation

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SUMMARY" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Total Subdirectories: $($subdirs.Count)" -ForegroundColor White
Write-Host "Total Files: $totalFiles" -ForegroundColor White
Write-Host "Total Size: $([math]::Round($totalSize / 1GB, 2)) GB" -ForegroundColor White
Write-Host "`nReport saved to: $outputFile" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  TOP 20 LARGEST FOLDERS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$sortedReport | Select-Object -First 20 Name, Size_GB, Last_Modified, Days_Old | Format-Table -AutoSize

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  OLDEST FOLDERS (Not modified in 180+ days)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$oldFolders = $sortedReport | Where-Object { $_.Days_Old -gt 180 }
if ($oldFolders) {
    $oldFolders | Select-Object Name, Size_GB, Last_Modified, Days_Old | Format-Table -AutoSize
    Write-Host "`nPotential recovery from old folders: $([math]::Round(($oldFolders | Measure-Object Size_GB -Sum).Sum, 2)) GB" -ForegroundColor Yellow
} else {
    Write-Host "No folders older than 180 days found." -ForegroundColor Green
}

Write-Host "`n========================================`n" -ForegroundColor Cyan
