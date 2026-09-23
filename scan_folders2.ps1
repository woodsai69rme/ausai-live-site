# Find all relevant folders

Write-Host "=== SEARCHING C: ROOT FOR INSTALLERS/REPO ==="
Get-ChildItem "C:\" -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "install|repo|experimental" -or $_.Name -match "^_" } |
    Select-Object Name, FullName |
    Format-Table -AutoSize

Write-Host "`n=== CHECKING COMMON PATHS ==="
$paths = @(
    "C:\installers",
    "C:\repo",
    "C:\repos", 
    "C:\Repositories",
    "C:\Software",
    "C:\Program Files\installers",
    "C:\Users\karma\installers",
    "C:\Users\karma\repo",
    "C:\Users\karma\repos"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
        Write-Host "$path - $([math]::Round($size, 2)) GB"
    }
}

Write-Host "`n=== EXPERIMENTAL FOLDER SIZES ==="
if (Test-Path "C:\Users\karma\experimental") {
    Get-ChildItem "C:\Users\karma\experimental" -Directory -ErrorAction SilentlyContinue |
        ForEach-Object {
            $size = (Get-ChildItem $_.FullName -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
            [PSCustomObject]@{
                Name = $_.Name
                SizeGB = [math]::Round($size, 2)
                Created = $_.CreationTime
            }
        } | Sort-Object SizeGB -Descending |
        Format-Table -AutoSize
}

Write-Host "`n=== X: 01_SOFTWARE DETAILS ==="
if (Test-Path "X:\01_SOFTWARE") {
    Get-ChildItem "X:\01_SOFTWARE" -Directory -Recurse -ErrorAction SilentlyContinue |
        ForEach-Object {
            $size = (Get-ChildItem $_.FullName -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
            [PSCustomObject]@{
                Name = $_.Name
                SizeGB = [math]::Round($size, 2)
            }
        } | Sort-Object SizeGB -Descending |
        Select-Object -First 20 |
        Format-Table -AutoSize
}
