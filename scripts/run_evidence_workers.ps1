$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$outputRoot = Join-Path $projectRoot 'outputs'
$null = New-Item -ItemType Directory -Force -Path $outputRoot
$keyFile = Join-Path $outputRoot 'evidence-worker.key'
if (!(Test-Path -LiteralPath $keyFile)) {
    $workerBytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($workerBytes)
    [System.IO.File]::WriteAllText($keyFile, [Convert]::ToBase64String($workerBytes))
}
$services = @(
    @{ Name='privacy'; Env='.venv-privacy'; Module='evidence_tools.privacy_app:app'; Port=8092 },
    @{ Name='vision'; Env='.venv-vision'; Module='evidence_tools.worker_app:app'; Port=8091 }
)
foreach ($service in $services) {
    $workerPython = Join-Path $projectRoot ($service.Env + '\Scripts\python.exe')
    if (!(Test-Path -LiteralPath $workerPython)) { throw ('Install ' + $service.Env + ' first. See scripts/setup_evidence_tools.ps1.') }
    $running = $false
    try { $null = Invoke-RestMethod ('http://127.0.0.1:' + $service.Port + '/health') -TimeoutSec 2; $running = $true } catch { }
    if (!$running) {
        if (Get-NetTCPConnection -LocalPort $service.Port -State Listen -ErrorAction SilentlyContinue) { throw ('Port ' + $service.Port + ' is occupied by another service') }
        Start-Process -FilePath $workerPython -ArgumentList @('-m','uvicorn',$service.Module,'--host','127.0.0.1','--port',$service.Port,'--no-access-log') `
            -WorkingDirectory $projectRoot -WindowStyle Hidden `
            -RedirectStandardOutput (Join-Path $outputRoot ($service.Name + '-worker.stdout.log')) `
            -RedirectStandardError (Join-Path $outputRoot ($service.Name + '-worker.stderr.log')) | Out-Null
    }
}
$ready = $false
for ($attempt = 0; $attempt -lt 60; $attempt++) {
    try {
        $workerStatus = Invoke-RestMethod 'http://127.0.0.1:8091/health' -TimeoutSec 2
        if ($workerStatus.ready) { $ready=$true; break }
        if ($workerStatus.error) { throw ('Vision startup failed: ' + $workerStatus.error) }
    } catch { if ($_.Exception.Message -like '*startup failed*') { throw } }
    Start-Sleep -Milliseconds 1000
}
if (!$ready) { throw 'Evidence workers did not become ready. Check outputs/*-worker.stderr.log.' }
Write-Output 'Local PaddleOCR, imagededup and Presidio workers are ready.'
