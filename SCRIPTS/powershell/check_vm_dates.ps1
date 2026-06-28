Write-Host "=== KALI VM DATES - ALL 3 ==="

$paths = @(
    "C:\AI\kali-linux-2025.1c-virtualbox-amd64",
    "C:\AI\kaliosboxvm",
    "C:\AI\kali-linux-2025.1c-vmware-amd64.vmwarevm"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        $item = Get-Item $path
        Write-Host "`n========================================"
        Write-Host "VM: $($item.Name)"
        Write-Host "========================================"
        Write-Host "Created: $($item.CreationTime)"
        Write-Host "Modified: $($item.LastWriteTime)"
        Write-Host "Path: $path"
        Write-Host ""
        
        Get-ChildItem $path -File -ErrorAction SilentlyContinue |
            Select-Object Name, Length, LastWriteTime |
            Format-Table -AutoSize
    } else {
        Write-Host "`nNOT FOUND: $path"
    }
}
