# Scan specific folders for audit

Write-Host "=== SCANNING INSTALLERS FOLDER ==="
if (Test-Path "C:\windows\installers") {
    $installers = Get-ChildItem "C:\windows\installers" -ErrorAction SilentlyContinue
    $installersSize = ($installers | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "Count: $($installers.Count)"
    Write-Host "Size: $([math]::Round($installersSize, 2)) GB"
    Write-Host "`nFirst 30 items:"
    $installers | Sort-Object Length -Descending | Select-Object -First 30 Name, Length, CreationTime | Format-Table -AutoSize
} else {
    Write-Host "C:\windows\installers not found"
}

Write-Host "`n=== SCANNING EXPERIMENTAL FOLDERS ==="
$experimentalPaths = @(
    "C:\experimental",
    "C:\Users\karma\experimental",
    "C:\experimental",
    "C:\repo",
    "C:\repos",
    "C:\Users\karma\repo",
    "C:\Users\karma\repos"
)

foreach ($path in $experimentalPaths) {
    if (Test-Path $path) {
        Write-Host "`n--- $path ---"
        Get-ChildItem $path -Directory -ErrorAction SilentlyContinue |
            Sort-Object CreationTime -Descending |
            Select-Object Name, CreationTime |
            Select-Object -First 20 |
            Format-Table -AutoSize
    }
}

Write-Host "`n=== X: DRIVE COMPARISON ==="
if (Test-Path "X:\01_SOFTWARE") {
    Get-ChildItem "X:\01_SOFTWARE" -Directory -ErrorAction SilentlyContinue |
        Select-Object Name, CreationTime |
        Format-Table -AutoSize
}
