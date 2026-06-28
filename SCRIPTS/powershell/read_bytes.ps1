$path = "X:\AETHER_CORE_SYSTEM\backups\SYSTEM_CORE_GAL\Empire_Clone_20260305_1358.gal"
$fs = [System.IO.File]::OpenRead($path)
$buffer = New-Object byte[] 100
$fs.Read($buffer, 0, 100) | Out-Null
$fs.Close()
[System.BitConverter]::ToString($buffer)