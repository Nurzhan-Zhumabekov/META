param([switch]$Rebuild, [switch]$RequireMeta)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$frontendRoot = Join-Path $projectRoot 'web'
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (!(Test-Path -LiteralPath $pythonPath)) { throw 'Create the Python virtual environment and install requirements.txt first.' }
function Test-DemoReadiness {
    if ($RequireMeta) {
        & $pythonPath (Join-Path $PSScriptRoot 'check_demo.py') --require-meta
        if ($LASTEXITCODE -ne 0) { throw 'Demo preflight failed. Resolve the failed checks before recording or presenting.' }
    }
}
& $pythonPath (Join-Path $PSScriptRoot 'install_demo_models.py')
if ($LASTEXITCODE -ne 0) { throw 'Bundled ML model installation failed.' }
if ((Test-Path -LiteralPath (Join-Path $projectRoot '.venv-vision\Scripts\python.exe')) -and
    (Test-Path -LiteralPath (Join-Path $projectRoot '.venv-privacy\Scripts\python.exe'))) {
    & (Join-Path $PSScriptRoot 'run_evidence_workers.ps1')
}
if ($Rebuild -or !(Test-Path -LiteralPath (Join-Path $frontendRoot 'dist\index.html'))) {
    Push-Location $frontendRoot
    try {
        if (!(Test-Path -LiteralPath 'node_modules')) { & npm ci; if ($LASTEXITCODE -ne 0) { throw 'npm ci failed.' } }
        & npm run build
        if ($LASTEXITCODE -ne 0) { throw 'Web build failed.' }
    } finally { Pop-Location }
}
$existingServer = $false
try {
    $null = Invoke-RestMethod 'http://127.0.0.1:8090/api/analysis/status' -TimeoutSec 2
    $existingServer = $true
} catch { }
if ($existingServer) {
    Test-DemoReadiness
    Write-Output 'Web application is already available at http://localhost:8090/'
    return
}
if (Get-NetTCPConnection -LocalPort 8090 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 8090 is already in use by another service. Stop that service before launching the web app.'
}
$null = New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot 'outputs')
Start-Process -FilePath $pythonPath `
    -ArgumentList @('-m', 'uvicorn', 'src.web:app', '--host', '127.0.0.1', '--port', '8090') `
    -WorkingDirectory $projectRoot -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $projectRoot 'outputs\web-api.stdout.log') `
    -RedirectStandardError (Join-Path $projectRoot 'outputs\web-api.stderr.log') | Out-Null
$ready = $false
for ($attempt = 0; $attempt -lt 25; $attempt++) {
    try { $null = Invoke-RestMethod 'http://127.0.0.1:8090/api/analysis/status' -TimeoutSec 1; $ready = $true; break } catch { Start-Sleep -Milliseconds 400 }
}
if (!$ready) { throw 'Web server did not become ready. Check outputs/web-api.stderr.log.' }
Test-DemoReadiness
Write-Output 'Web application is available at http://localhost:8090/'
