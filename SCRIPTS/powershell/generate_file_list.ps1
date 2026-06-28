# Generate complete file listing for EXPERIMENTAL folder
$outputFile = "C:\Users\karma\EXPERIMENTAL_ALL_FILES.txt"
$folder = "C:\Users\karma\EXPERIMENTAL"

Write-Host "Scanning $folder..."
Write-Host "This may take several minutes..."

# Header
"EXPERIMENTAL FOLDER - COMPLETE FILE LISTING" | Out-File $outputFile
"Generated: $(Get-Date)" | Out-File $outputFile -Append
"=" * 120 | Out-File $outputFile -Append
"" | Out-File $outputFile -Append

# Get all files
$files = Get-ChildItem $folder -Recurse -File -ErrorAction SilentlyContinue
$totalFiles = $files.Count
$totalSize = ($files | Measure-Object -Property Length -Sum).Sum

"TOTAL FILES: $totalFiles" | Out-File $outputFile -Append
"TOTAL SIZE: $([math]::Round($totalSize/1GB, 2)) GB" | Out-File $outputFile -Append
"" | Out-File $outputFile -Append
"=" * 120 | Out-File $outputFile -Append
"" | Out-File $outputFile -Append

# List each file
$counter = 0
foreach ($file in $files) {
    $counter++
    $sizeMB = if ($file.Length -gt 0) { [math]::Round($file.Length/1MB, 4) } else { 0 }
    $line = "{0,-8} {1,-12} {2,-50} {3}" -f "[$counter]", "$($sizeMB) MB", $file.LastWriteTime.ToString("yyyy-MM-dd"), $file.FullName
    $line | Out-File $outputFile -Append
    
    if ($counter % 1000 -eq 0) {
        Write-Host "Processed $counter of $totalFiles files..."
    }
}

"" | Out-File $outputFile -Append
"=" * 120 | Out-File $outputFile -Append
"END OF FILE LIST" | Out-File $outputFile -Append

Write-Host ""
Write-Host "COMPLETE!" -ForegroundColor Green
Write-Host "Total files listed: $totalFiles"
Write-Host "Output file: $outputFile"
Write-Host "File size: $([math]::Round((Get-Item $outputFile).Length/1MB, 2)) MB"
