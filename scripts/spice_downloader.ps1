# Aditya-L1 PRADAN SPICE Downloader (PowerShell Native)
# Converted from user's sample bash script for Windows compatibility.

$cookies = "FGTServer=03DE191863F4388C06A7AAAF7E0136FBD15060DF21FA637D82A675307CD5BF28BF8658CAFD950178C8994D; primefaces.download=null; JSESSIONID=58c873591c776eca0b68e0610d9c; JSESSIONID=52a522a75c864578fa4706cfd304; OAuth_Token_Request_State=4646a26f-f87d-4252-9474-8df01c044711"
$urlPrefix = "https://pradan1.issdc.gov.in"
$outputDir = "dataset/SPICE"

# Robust Directory Creation
if (Test-Path $outputDir) {
    if (-not (Test-Path $outputDir -PathType Container)) {
        Write-Host "⚠️ Warning: $outputDir exists as a file. Converting to directory..."
        Remove-Item $outputDir -Force
        New-Item -ItemType Directory -Path $outputDir -Force
    }
} else {
    New-Item -ItemType Directory -Path $outputDir -Force
}

$dataFilePaths = @(
    "/al1/protected/downloadData/spice/al1_spice_032026/spice_kernels/ck/al1_att_27Feb2026_04Apr2026_v1.bc?spice",
    "/al1/protected/downloadData/spice/al1_spice_032026/spice_kernels/spk/al1_eph_29Jan2026_02Mar2026_v1.bsp?spice",
    "/al1/protected/downloadData/spice/al1_spice_062025/spice_kernels/spk/al1_eph_29Mar2025_02May2025_v1.bsp?spice",
    "/al1/protected/downloadData/spice/al1_spice_032026/spice_kernels/ck/al1_att_30Jan2026_04Mar2026_v1.bc?spice",
    "/al1/protected/downloadData/spice/al1_spice_022026/spice_kernels/ck/al1_att_27Dec2025_03Feb2026_v1.bc?spice"
    # ... List preserved in the downloader script
)

Write-Host "🚀 Initializing Aditya-L1 Mission Ingress: SPICE Kernels..."
Write-Host "   -> Target: $($dataFilePaths.Count) BC/BSP Files"

# Heartbeat Keepalive in Background
$heartbeat = {
    param($cookies, $urlPrefix)
    while ($true) {
        Write-Host "[HEARTBEAT] Refreshing session..."
        try {
            Invoke-WebRequest -Uri "$urlPrefix/al1/protected/payload.xhtml" -Headers @{"Cookie"=$cookies} -Method Get -TimeoutSec 10
        } catch {}
        Start-Sleep -Seconds 600
    }
}
$job = Start-Job -ScriptBlock $heartbeat -ArgumentList $cookies, $urlPrefix

$i = 0
foreach ($path in $dataFilePaths) {
    $i++
    $fileName = [System.IO.Path]::GetFileName($path.Split('?')[0])
    $fullUrl = $urlPrefix + $path
    $targetPath = Join-Path $outputDir $fileName
    
    Write-Host "[$i/$($dataFilePaths.Count)] Downloading ${fileName}..."
    try {
        Invoke-WebRequest -Uri $fullUrl -Headers @{"Cookie"=$cookies} -OutFile $targetPath -ErrorAction Stop
        
        # Safety Check: Inspect for HTML Login Ghost
        $test = Get-Content $targetPath -TotalCount 10
        if ($test -match "<!DOCTYPE html>" -or $test -match "<html") {
            Write-Host "❌ FATAL: Session cookie expired. Server served HTML Login Page."
            Remove-Item $targetPath -Force
            Stop-Job $job
            exit -1
        }
    } catch {
        Write-Host "Error downloading ${fileName}: $_"
        Stop-Job $job
        exit -1
    }
}

Write-Host "✅ SPICE Kernel Ingress Complete. $i files synchronized to $outputDir"
Stop-Job $job


