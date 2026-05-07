param(
    [Parameter(Mandatory=$true)]
    [string]$NewCookie
)

$scripts = Get-ChildItem -Path "scripts" -Filter "*_downloader.ps1"

foreach ($script in $scripts) {
    Write-Host "🔄 Patching $($script.Name) with new session cookie..."
    $content = Get-Content $script.FullName -Raw
    
    # 1. Update Cookie String
    $content = $content -replace '\$cookies = ".*?"', "`$cookies = `"$NewCookie`""
    
    # 2. Inject HTML Safety Check if missing
    if ($content -notmatch "HTML Login Ghost") {
        $oldCode = 'Invoke-WebRequest -Uri $fullUrl -Headers @{"Cookie"=$cookies} -OutFile $targetPath -ErrorAction Stop'
        $newCode = 'Invoke-WebRequest -Uri $fullUrl -Headers @{"Cookie"=$cookies} -OutFile $targetPath -ErrorAction Stop
        
        # Safety Check: Inspect for HTML Login Ghost
        $test = Get-Content $targetPath -TotalCount 10
        if ($test -match "<!DOCTYPE html>" -or $test -match "<html") {
            Write-Host "❌ FATAL: Session cookie expired. Server served HTML Login Page."
            Remove-Item $targetPath -Force
            Stop-Job $job
            exit -1
        }'
        $content = $content.Replace($oldCode, $newCode)
    }
    
    Set-Content $script.FullName $content
}

Write-Host "✅ Mission Session Cookies Synchronized across all 8 instruments."
