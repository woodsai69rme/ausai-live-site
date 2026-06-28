# Duplicate File Finder
# Finds duplicate files across your system (doesn't delete, just reports)

$ErrorActionPreference = "Stop"
$outputFile = "C:\Users\karma\DUPLICATES_REPORT_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DUPLICATE FILE FINDER" -ForegroundColor Cyan
Write-Host "  Finding duplicates (NOT deleting)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$paths = @(
    "C:\Users\karma\ACTIVE_PROJECTS",
    "C:\Users\karma\EXPERIMENTAL",
    "C:\Users\karma\REVENUE_GENERATORS",
    "C:\Users\karma\projects"
)

$allFiles = @()

foreach ($path in $paths) {
    if (Test-Path $path) {
        Write-Host "Scanning: $path" -ForegroundColor Yellow
        $files = Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue | 
            Select-Object Name, Length, FullName, DirectoryName, LastWriteTime
        $allFiles += $files
        Write-Host "  Found $($files.Count) files" -ForegroundColor Green
    }
}

Write-Host "`nAnalyzing for duplicates..." -ForegroundColor Yellow

# Group by size first (quick filter)
$bySize = $allFiles | Group-Object Length | Where-Object { $_.Count -gt 1 }

Write-Host "  Found $($bySize.Count) size groups with potential duplicates" -ForegroundColor Yellow

# Then group by name within same size
$duplicates = @()
foreach ($sizeGroup in $bySize) {
    $nameGroups = $sizeGroup.Group | Group-Object Name | Where-Object { $_.Count -gt 1 }
    foreach ($nameGroup in $nameGroups) {
        # Verify by hash (slow but accurate)
        $hashes = @{}
        foreach ($file in $nameGroup.Group) {
            try {
                $hash = Get-FileHash -Path $file.FullName -Algorithm MD5 -ErrorAction SilentlyContinue
                if ($hashes.ContainsKey($hash.Hash)) {
                    # Duplicate found!
                    $duplicates += [PSCustomObject]@{
                        FileName = $file.Name
                        Size_MB = [math]::Round($file.Length / 1MB, 2)
                        Path1 = $hashes[$hash.Hash]
                        Path2 = $file.FullName
                        DuplicateGroup = "$($file.Name)_$($file.Length)"
                    }
                } else {
                    $hashes[$hash.Hash] = $file.FullName
                }
            } catch {
                # Skip files we can't hash
            }
        }
    }
}

# Export results
if ($duplicates.Count -gt 0) {
    $duplicates | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8
    
    $totalWasted = ($duplicates | Measure-Object -Property Size_MB -Sum).Sum
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  DUPLICATES FOUND" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Write-Host "Duplicate Groups: $($duplicates.Count)" -ForegroundColor White
    Write-Host "Total Wasted Space: $([math]::Round($totalWasted, 2)) MB" -ForegroundColor Yellow
    Write-Host "`nReport saved to: $outputFile" -ForegroundColor Green
    
    Write-Host "`nTop 10 largest duplicates:" -ForegroundColor Cyan
    $duplicates | Sort-Object Size_MB -Descending | Select-Object -First 10 | Format-Table -AutoSize
    
} else {
    Write-Host "`nNo duplicates found!" -ForegroundColor Green
}

Write-Host "`n========================================`n" -ForegroundColor Cyan
