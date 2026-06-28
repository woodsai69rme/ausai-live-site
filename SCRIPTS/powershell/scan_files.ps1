$date = (Get-Date).AddMonths(-3)
Get-ChildItem -Path C:\ -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.CreationTime -gt $date } | Select-Object FullName, CreationTime, Length, Mode | Sort-Object CreationTime -Descending | ConvertTo-Json -Depth 1
