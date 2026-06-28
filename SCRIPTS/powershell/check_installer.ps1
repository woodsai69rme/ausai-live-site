Write-Host "=== TOP 20 LARGEST FILES IN WINDOWS INSTALLER ==="
Get-ChildItem "C:\Windows\Installer" -File -ErrorAction SilentlyContinue |
    Sort-Object Length -Descending |
    Select-Object -First 20 Name, Length |
    ForEach-Object {
        [PSCustomObject]@{
            Name = $_.Name
            SizeMB = [math]::Round($_.Length/1MB, 2)
        }
    } |
    Format-Table -AutoSize

Write-Host "`n=== FILE COUNT ==="
$files = Get-ChildItem "C:\Windows\Installer" -File -ErrorAction SilentlyContinue
Write-Host "Total files: $($files.Count)"

Write-Host "`n=== TOTAL SIZE ==="
$total = ($files | Measure-Object -Property Length -Sum).Sum / 1GB
Write-Host "Total: $([math]::Round($total, 2)) GB"
