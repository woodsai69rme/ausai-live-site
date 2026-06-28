$ErrorActionPreference = "SilentlyContinue"
$cutoffDate = (Get-Date).AddMonths(-3)
$outputFile = "C:\Users\karma\audit_x_drive.txt"

Write-Host "Scanning X: drive for files created after $cutoffDate..."

$results = Get-ChildItem -Path "X:\" -Recurse -Force -ErrorAction SilentlyContinue | 
    Where-Object { $_.CreationTime -gt $cutoffDate } | 
    Select-Object FullName, CreationTime, Length, @{N='Type';E={if($_.PSIsContainer){'DIR'}else{'FILE'}}} | 
    Sort-Object CreationTime -Descending

$results | Format-Table -AutoSize | Out-String -Width 4096 | Out-File $outputFile -Encoding UTF8

Write-Host "Found $($results.Count) items. Results saved to $outputFile"
