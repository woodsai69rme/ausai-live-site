$VerbosePreference = "Continue"

Write-Host "=== Starting Antigravity Chat History Cleanup ==="
$brainPath = "C:\Users\karma\.gemini\antigravity\brain"
$currentId = "8fc41dc4-f37c-442c-b64a-3e99187876b9"
$keepDirs = @($currentId, "tempmediaStorage")

$brainSubDirs = Get-ChildItem -Path $brainPath -Directory
foreach ($dir in $brainSubDirs) {
    if ($dir.Name -notin $keepDirs) {
        Write-Host "Removing old chat history: $($dir.Name)"
        Remove-Item -Path $dir.FullName -Recurse -Force
    }
}
Write-Host "Chat history cleanup complete!"
Write-Host ""

Write-Host "=== Starting VS Code Extensions Cleanup ==="
$extPath = "C:\Users\karma\.vscode\extensions"
$extensions = Get-ChildItem -Path $extPath -Directory

$removed = 0
foreach ($ext in $extensions) {
    # Keep Kilo Code and any extension matching "opencode", "cline", or "claude-dev" 
    # (since "opencode" might refer to open source coders like Cline)
    if ($ext.Name -notmatch "kilo-code" -and 
        $ext.Name -notmatch "opencode" -and 
        $ext.Name -notmatch "open-code" -and
        $ext.Name -notmatch "claude-dev" -and
        $ext.Name -notmatch "cline") {
        Write-Host "Removing extension: $($ext.Name)"
        Remove-Item -Path $ext.FullName -Recurse -Force
        $removed++
    } else {
        Write-Host "Keeping extension: $($ext.Name)" -ForegroundColor Green
    }
}
Write-Host "Extension cleanup complete! Removed $removed extensions."
