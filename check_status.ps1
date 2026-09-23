# Start all services
Write-Host "=== Checking what's running ==="

# Get listening ports
Get-NetTCPConnection -State Listen | Select-Object LocalPort,OwningProcess | Sort-Object LocalPort | Format-Table -AutoSize

# Check Docker
Write-Host "`n=== Docker Status ==="
$dockerProc = Get-Process | Where-Object {$_.ProcessName -like "*docker*"}
if ($dockerProc) { Write-Host "Docker running" } else { Write-Host "Docker NOT running" }

# Check Ollama models via API
Write-Host "`n=== Ollama Models ==="
$models = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get
$models.models | Select-Object name, @{N="SizeGB";E={[math]::Round($_.size/1GB,1)}}, parameter_size | Format-Table -AutoSize

# Check key folders
Write-Host "`n=== Key Project Folders ==="
$folders = @(
    "C:\Users\karma\jarvis-dashboard",
    "C:\Users\karma\REVENUE_GENERATORS",
    "C:\Users\karma\ComfyUI",
    "C:\Users\karma\ACTIVE_PROJECTS"
)
foreach ($f in $folders) {
    if (Test-Path $f) { Write-Host "EXISTS: $f" } else { Write-Host "MISSING: $f" }
}
