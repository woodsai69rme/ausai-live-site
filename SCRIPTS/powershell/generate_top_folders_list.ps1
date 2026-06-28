# Generate file listing for top folders only
$outputFile = "C:\Users\karma\EXPERIMENTAL_TOP_FOLDERS_FILE_LIST.txt"
$folder = "C:\Users\karma\EXPERIMENTAL"

Write-Host "Generating file list for TOP folders only..."

# Header
"EXPERIMENTAL FOLDER - TOP FOLDERS FILE LISTING" | Out-File $outputFile
"Generated: $(Get-Date)" | Out-File $outputFile -Append
"Focus: Largest folders (cleanup priorities)" | Out-File $outputFile -Append
"=" * 120 | Out-File $outputFile -Append
"" | Out-File $outputFile -Append

# Top folders to scan (by size from our earlier scan)
$topFolders = @(
    "_UNSORTED",
    "dwhelper",
    "gpt4all",
    "config",
    "augguebak",
    "DATA_MANAGEMENT",
    "NEXUS-IDE-MASTER",
    "GITHUBREPO",
    "farqgemini",
    "enterprise",
    "busept",
    "opencode",
    "Projects",
    "python",
    "device"
)

$totalFiles = 0
$totalSize = 0

foreach ($subfolder in $topFolders) {
    $path = Join-Path $folder $subfolder
    if (Test-Path $path) {
        Write-Host "Scanning: $subfolder..."
        
        "" | Out-File $outputFile -Append
        "FOLDER: $subfolder" | Out-File $outputFile -Append
        "-" * 80 | Out-File $outputFile -Append
        
        $files = Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue
        $folderSize = ($files | Measure-Object -Property Length -Sum).Sum
        $folderCount = $files.Count
        
        "Files: $folderCount | Size: $([math]::Round($folderSize/1MB, 2)) MB" | Out-File $outputFile -Append
        "" | Out-File $outputFile -Append
        
        foreach ($file in $files) {
            $sizeMB = if ($file.Length -gt 0) { [math]::Round($file.Length/1MB, 4) } else { 0 }
            $line = "{0,-12} {1,-50} {2}" -f "$($sizeMB) MB", $file.LastWriteTime.ToString("yyyy-MM-dd"), $file.FullName.Replace($folder, "")
            $line | Out-File $outputFile -Append
            $totalFiles += 1
            $totalSize += $file.Length
        }
    }
}

"" | Out-File $outputFile -Append
"=" * 120 | Out-File $outputFile -Append
"SUMMARY" | Out-File $outputFile -Append
"Total files listed: $totalFiles" | Out-File $outputFile -Append
"Total size: $([math]::Round($totalSize/1GB, 2)) GB" | Out-File $outputFile -Append
"=" * 120 | Out-File $outputFile -Append

Write-Host ""
Write-Host "COMPLETE!" -ForegroundColor Green
Write-Host "Total files listed: $totalFiles"
Write-Host "Output file: $outputFile"
Write-Host "File size: $([math]::Round((Get-Item $outputFile).Length/1MB, 2)) MB"
