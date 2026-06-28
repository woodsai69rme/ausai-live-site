Get-Process | Where-Object {$_.WorkingSet64 -gt 100MB} | 
    Sort-Object WorkingSet64 -Descending | 
    Select Name, Id, @{N='RAM(MB)';E={[math]::Round($_.WorkingSet64/1MB,0)}} | 
    Format-Table -AutoSize
