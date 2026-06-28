$ErrorActionPreference = "SilentlyContinue"
$Error.Clear()

$logPath = "C:\Users\karma\docker_startup.log"
$dockerDir = "C:\Users\karma"

function Write-Log {
    param([string]$Msg)
    $entry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Msg"
    Add-Content -Path $logPath -Value $entry
}

Write-Log "=== Startup script triggered ==="

$maxWait = 600
$waited = 0
$dockerReady = $false

while (-not $dockerReady) {
    if ($waited -ge $maxWait) {
        Write-Log "ERROR: Docker not responding after $($maxWait) seconds - aborting"
        exit 1
    }
    $output = docker version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerReady = $true
        Write-Log "Docker is ready after $($waited) seconds"
        break
    }
    Start-Sleep -Seconds 5
    $waited += 5
    Write-Log "Waiting for Docker Desktop... ($waited s)"
}

docker info 2>&1 | Out-Null

$script:ComposeArgs = @("-f", "$dockerDir\docker-compose.yml")

$containers = docker compose @script:ComposeArgs "ps" 2>&1
$statusStr = $containers -join "`n"

$allHealthy = $true

if ($statusStr -match "archon-|postgres|pgbouncer|healthy") {
    $healthyCount = ([regex]::Matches($statusStr, "healthy")).Count
    $totalRelevant = (($statusStr -split "`n") | Where-Object { $_ -match "archon-|postgres|pgbouncer" }).Count
    if ($healthyCount -ge $totalRelevant -and $totalRelevant -gt 0) {
        $allHealthy = $true
        Write-Log "All $totalRelevant containers healthy"
    } else {
        $allHealthy = $false
        Write-Log "Partial health: $healthyCount/$totalRelevant containers healthy - restarting"
    }
} else {
    $allHealthy = $false
    Write-Log "No containers running or unhealthy"
}

if (-not $allHealthy) {
    Write-Log "Starting/restarting Archon services..."
    docker compose @script:ComposeArgs "up" "-d" 2>&1 | Out-Null
    Start-Sleep -Seconds 15

    $mcpWait = 0
    $mcpHealthy = $false
    while ($mcpWait -lt 90 -and -not $mcpHealthy) {
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:8051/health" -UseBasicParsing -TimeoutSec 3
            if ($r.StatusCode -eq 200) {
                $mcpHealthy = $true
                Write-Log "MCP health check: OK ($($r.StatusCode))"
            }
        } catch {
        }
        if (-not $mcpHealthy) {
            Start-Sleep -Seconds 10
            $mcpWait += 10
            Write-Log "Waiting for MCP health... ($mcpWait s)"
        }
    }
    if (-not $mcpHealthy) {
        Write-Log "WARNING: MCP did not pass health check within $($mcpWait) seconds"
    }
} else {
    Write-Log "Archon services appear to be running. Checking health..."
    $endpoints = @(
        @{ Url = "http://localhost:8181/health"; Name = "Server" },
        @{ Url = "http://localhost:8051/health"; Name = "MCP" },
        @{ Url = "http://localhost:8052/health"; Name = "Agents" }
    )
    foreach ($ep in $endpoints) {
        try {
            $r = Invoke-WebRequest -Uri $ep.Url -UseBasicParsing -TimeoutSec 3
            if ($r.StatusCode -eq 200) {
                Write-Log "$($ep.Name) health check: OK ($($r.StatusCode))"
            } else {
                Write-Log "$($ep.Name) health check: HTTP $($r.StatusCode)"
            }
        } catch {
            Write-Log "$($ep.Name) not responding - restarting containers"
            docker compose @script:ComposeArgs "restart" 2>&1 | Out-Null
        }
    }
}

Write-Log "=== Startup script completed ==="
exit 0
