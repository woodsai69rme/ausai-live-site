# Cleanup Downloads Folder Script
# Moves files older than 30 days to an archive folder

$sourcePath = "C:\Users\karma\Downloads"
$archivePath = "C:\Users\karma\Downloads\ARCHIVE_OLD"
$cutoffDate = (Get-Date).AddDays(-30)

# Create archive directory
New-Item -Path $archivePath -ItemType Directory -Force | Out-Null

# Get old files
$oldFiles = Get-ChildItem -Path $sourcePath -File | Where-Object { $_.LastWriteTime -lt $cutoffDate }

# Move files
foreach ($file in $oldFiles) {
    try {
        Move-Item -Path $file.FullName -Destination $archivePath -Force
        Write-Host "Moved: $($file.Name)"
    } catch {
        Write-Warning "Failed to move: $($file.Name) - $($_.Exception.Message)"
    }
}

# Summary
$movedCount = (Get-ChildItem -Path $archivePath -File).Count
$movedSize = (Get-ChildItem -Path $archivePath -File | Measure-Object -Property Length -Sum).Sum
Write-Host "`n=========================================="
Write-Host "CLEANUP SUMMARY"
Write-Host "=========================================="
Write-Host "Files moved to archive: $movedCount"
Write-Host "Total size archived: $([math]::Round($movedSize/1GB, 2)) GB"
Write-Host "Archive location: $archivePath"
Write-Host "=========================================="
