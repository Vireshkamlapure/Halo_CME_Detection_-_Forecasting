# Aditya-L1 PRADAN PAPA Downloader (PowerShell Native)
# Converted from user's sample bash script for Windows compatibility.

$cookies = "FGTServer=03DE191863F4388C06A7AAAF7E0136FBD15060DF21FA637D82A675307CD5BF28BF8658CAFD950178C8994D; primefaces.download=null; JSESSIONID=58c873591c776eca0b68e0610d9c; JSESSIONID=52a522a75c864578fa4706cfd304; OAuth_Token_Request_State=4646a26f-f87d-4252-9474-8df01c044711"
$urlPrefix = "https://pradan1.issdc.gov.in"
$outputDir = "dataset/PAPA"

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
    "/al1/protected/downloadData/papa/level2/2024/12/UNP_9999_999999/PPA_SWR_ion_E32_25001070030965_UNP_9999_999999_L0_V1_1_20241231115955_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2023/12/UNP_9999_999999/PPA_SWR_ele_E16_23357014442693_UNP_9999_999999_L0_V1_1_20231222205522_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2023/12/UNP_9999_999999/PPA_SWP_ele_E16_23357014442693_UNP_9999_999999_L0_V1_1_20231222205417_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2023/12/UNP_9999_999999/PPA_SWR_ele_E16_23357013259960_UNP_9999_999999_L0_V1_1_20231222120011_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2023/12/UNP_9999_999999/PPA_SWP_ele_E16_23357013259960_UNP_9999_999999_L0_V1_1_20231222115938_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2024/12/UNP_9999_999999/PPA_SWR_ion_E32_25001055529288_UNP_9999_999999_L0_V1_1_20241231000031_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2023/12/UNP_9999_999999/PPA_SWR_ele_E16_23357011712927_UNP_9999_999999_L0_V1_1_20231222000108_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2023/12/UNP_9999_999999/PPA_SWP_ele_E16_23357011712927_UNP_9999_999999_L0_V1_1_20231222000003_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2024/12/UNP_9999_999999/PPA_SWR_ion_E32_24366065516453_UNP_9999_999999_L0_V1_1_20241230115928_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2023/12/UNP_9999_999999/PPA_SWR_ele_E16_23356013917890_UNP_9999_999999_L0_V1_1_20231221205359_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2023/12/UNP_9999_999999/PPA_SWP_ele_E16_23356013917890_UNP_9999_999999_L0_V1_1_20231221205325_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2024/12/UNP_9999_999999/PPA_SWR_ion_E32_24366054956696_UNP_9999_999999_L0_V1_1_20241230000003_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2023/12/UNP_9999_999999/PPA_SWR_ele_E16_23356011148684_UNP_9999_999999_L0_V1_1_20231220235944_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2023/12/UNP_9999_999999/PPA_SWP_ele_E16_23356011148684_UNP_9999_999999_L0_V1_1_20231220235944_L2_V1_0.cdf?papa",
    "/al1/protected/downloadData/papa/level2/2024/12/UNP_9999_999999/PPA_SWR_ion_E32_24365064930605_UNP_9999_999999_L0_V1_1_20241229115900_L2_V1_0.cdf?papa"
    # ... List preserved in the downloader script
)

Write-Host "🚀 Initializing Aditya-L1 Mission Ingress: PAPA Real-Time Data..."
Write-Host "   -> Target: $($dataFilePaths.Count) CDF Files"

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

Write-Host "✅ PAPA Real-Data Ingress Complete. $i files synchronized to $outputDir"
Stop-Job $job


