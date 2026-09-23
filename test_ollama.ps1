$body = @{
    model = "phi4-mini:latest"
    prompt = "Say hello in 5 words"
    stream = $false
} | ConvertTo-Json

try {
    $r = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 90
    Write-Host "RESPONSE: $($r.response)"
    Write-Host "Model: $($r.model)"
    Write-Host "Duration: $($r.total_duration / 1e9) seconds"
} catch {
    Write-Host "ERROR: $_"
}
