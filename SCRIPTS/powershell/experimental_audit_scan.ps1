# Comprehensive EXPERIMENTAL Folder Audit Scanner
# This script gathers detailed information about all files and folders

$targetPath = "C:\Users\karma\EXPERIMENTAL"
$outputFile = "C:\Users\karma\experimental_scan_output.txt"

Write-Host "Starting comprehensive scan of $targetPath..." -ForegroundColor Cyan
Write-Host ""

# Get all items recursively with detailed info
$allItems = Get-ChildItem -Path $targetPath -Recurse -Force -ErrorAction SilentlyContinue | 
    Select-Object 
        FullName,
        Name,
        @{Name="Type";Expression={if($_.PSIsContainer){"Directory"}else{"File"}}},
        @{Name="SizeBytes";Expression={if($_.PSIsContainer){0}else{($_ | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum}},
        @{Name="SizeMB";Expression={if($_.PSIsContainer){0}else{[math]::Round(($_.Length / 1MB), 2)}},
        @{Name="LastModified";Expression={$_.LastWriteTime}},
        @{Name="Created";Expression={$_.CreationTime}},
        @{Name="Extension";Expression={$_.Extension}},
        @{Name="IsHidden";Expression={$_.Attributes -match "Hidden"}},
        @{Name="IsSystem";Expression={$_.Attributes -match "System"}},
        @{Name="IsReadOnly";Expression={$_.Attributes -match "ReadOnly"}},
        @{Name="DirectoryPath";Expression={$_.DirectoryName}}

# Calculate folder sizes separately
Write-Host "Calculating folder sizes..." -ForegroundColor Cyan
$folderSizes = @{}
$directories = Get-ChildItem -Path $targetPath -Recurse -Directory -Force -ErrorAction SilentlyContinue
foreach ($dir in $directories) {
    $size = (Get-ChildItem -Path $dir.FullName -Recurse -File -Force -ErrorAction SilentlyContinue | 
             Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
    $folderSizes[$dir.FullName] = $size
}

# Generate report
$report = @()
$report += "=" * 120
$report += "COMPREHENSIVE EXPERIMENTAL FOLDER AUDIT REPORT"
$report += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$report += "Target Path: $targetPath"
$report += "=" * 120
$report += ""

# Summary statistics
$totalFiles = ($allItems | Where-Object {$_.Type -eq "File"}).Count
$totalDirs = ($allItems | Where-Object {$_.Type -eq "Directory"}).Count
$totalSize = ($allItems | Where-Object {$_.Type -eq "File"} | Measure-Object -Property SizeBytes -Sum).Sum

$report += "SUMMARY STATISTICS"
$report += "-" * 60
$report += "Total Files:     $totalFiles"
$report += "Total Folders:   $totalDirs"
$report += "Total Size:      $([math]::Round($totalSize / 1MB, 2)) MB ($totalSize bytes)"
$report += ""

# Group by extension for analysis
$report += "FILE TYPES BREAKDOWN"
$report += "-" * 60
$extensionGroups = $allItems | Where-Object {$_.Type -eq "File"} | Group-Object -Property Extension | Sort-Object Count -Descending
foreach ($group in $extensionGroups) {
    $groupSize = ($group.Group | Measure-Object -Property SizeBytes -Sum).Sum
    $report += "$($group.Name.PadRight(15)) : $($group.Count.ToString().PadLeft(5)) files, $([math]::Round($groupSize / 1KB, 2)) KB"
}
$report += ""

# Detailed file listing
$report += "=" * 120
$report += "DETAILED FILE AND FOLDER LISTING"
$report += "=" * 120
$report += ""

foreach ($item in $allItems) {
    $indent = if ($item.Type -eq "Directory") { "[DIR] " } else { "[FILE]" }
    $sizeInfo = if ($item.Type -eq "Directory") { 
        $folderSizes[$item.FullName] 
    } else { 
        $item.SizeBytes 
    }
    $sizeDisplay = if ($sizeInfo -gt 1MB) { 
        "$([math]::Round($sizeInfo / 1MB, 2)) MB" 
    } elseif ($sizeInfo -gt 1KB) { 
        "$([math]::Round($sizeInfo / 1KB, 2)) KB" 
    } else { 
        "$sizeInfo bytes" 
    }
    
    $report += "$indent $($item.FullName)"
    $report += "       Size: $sizeDisplay | Modified: $($item.LastModified) | Created: $($item.Created)"
    if ($item.Extension) {
        $report += "       Extension: $($item.Extension) | Hidden: $($item.IsHidden) | ReadOnly: $($item.IsReadOnly)"
    }
    $report += ""
}

# Save to file
$report | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host ""
Write-Host "Scan complete! Results saved to: $outputFile" -ForegroundColor Green
Write-Host ""
Write-Host "Please share the contents of $outputFile for detailed analysis." -ForegroundColor Yellow
