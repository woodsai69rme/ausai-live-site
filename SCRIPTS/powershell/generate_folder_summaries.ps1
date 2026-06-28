# Generate summary report with file type breakdowns
$outputFile = "C:\Users\karma\EXPERIMENTAL_FOLDER_SUMMARIES.txt"
$folder = "C:\Users\karma\EXPERIMENTAL"

Write-Host "Generating folder summaries with file type breakdowns..."

# Header
"EXPERIMENTAL FOLDER - DETAILED SUMMARIES" | Out-File $outputFile
"Generated: $(Get-Date)" | Out-File $outputFile -Append
"=" * 120 | Out-File $outputFile -Append
"" | Out-File $outputFile -Append

# Get all subfolders
$subfolders = Get-ChildItem $folder -Directory -ErrorAction SilentlyContinue
$totalFolders = $subfolders.Count
$processed = 0

foreach ($subfolder in $subfolders | Sort-Object Name) {
    $processed++
    Write-Host "Processing $processed of $totalFolders : $($subfolder.Name)..."
    
    $path = $subfolder.FullName
    
    # Get files
    $files = Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue
    $fileCount = $files.Count
    
    if ($fileCount -eq 0) {
        "" | Out-File $outputFile -Append
        "FOLDER: $($subfolder.Name)" | Out-File $outputFile -Append
        "  Status: EMPTY" | Out-File $outputFile -Append
        continue
    }
    
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum
    $oldest = ($files | Measure-Object -Property LastWriteTime -Minimum).Minimum
    $newest = ($files | Measure-Object -Property LastWriteTime -Maximum).Maximum
    
    # File type breakdown
    $fileTypes = $files | Group-Object Extension | Sort-Object Count -Descending | Select-Object -First 10
    
    "" | Out-File $outputFile -Append
    "FOLDER: $($subfolder.Name)" | Out-File $outputFile -Append
    "-" * 80 | Out-File $outputFile -Append
    "  Files:      $fileCount" | Out-File $outputFile -Append
    "  Size:       $([math]::Round($totalSize/1MB, 2)) MB ($([math]::Round($totalSize/1GB, 3)) GB)" | Out-File $outputFile -Append
    "  Date Range: $($oldest.ToString("yyyy-MM-dd")) to $($newest.ToString("yyyy-MM-dd"))" | Out-File $outputFile -Append
    "" | Out-File $outputFile -Append
    "  Top File Types:" | Out-File $outputFile -Append
    
    foreach ($ft in $fileTypes) {
        $ftSize = ($files | Where-Object Extension -eq $ft.Name | Measure-Object -Property Length -Sum).Sum
        "    $($ft.Name.PadRight(15)) : $($ft.Count.ToString().PadLeft(6)) files, $([math]::Round($ftSize/1MB, 2)) MB" | Out-File $outputFile -Append
    }
    
    # Sample of largest files
    $largest = $files | Sort-Object Length -Descending | Select-Object -First 5
    if ($largest) {
        "" | Out-File $outputFile -Append
        "  Largest Files:" | Out-File $outputFile -Append
        foreach ($f in $largest) {
            "    $([math]::Round($f.Length/1MB, 2)) MB : $($f.Name)" | Out-File $outputFile -Append
        }
    }
}

"" | Out-File $outputFile -Append
"=" * 120 | Out-File $outputFile -Append
"END OF SUMMARIES" | Out-File $outputFile -Append

Write-Host ""
Write-Host "COMPLETE!" -ForegroundColor Green
Write-Host "Output file: $outputFile"
Write-Host "File size: $([math]::Round((Get-Item $outputFile).Length/1MB, 2)) MB"
