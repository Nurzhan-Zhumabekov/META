param([switch]$Rebuild)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$sdkRoot = Join-Path $env:LOCALAPPDATA 'Android\Sdk'
if (!(Test-Path -LiteralPath (Join-Path $sdkRoot 'platform-tools\adb.exe'))) {
    $codexSdkRoot = Join-Path $env:LOCALAPPDATA 'Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\Android\Sdk'
    if (Test-Path -LiteralPath (Join-Path $codexSdkRoot 'platform-tools\adb.exe')) { $sdkRoot = $codexSdkRoot }
}
$adbPath = Join-Path $sdkRoot 'platform-tools\adb.exe'
$emulatorPath = Join-Path $sdkRoot 'emulator\emulator.exe'
$serial = 'emulator-5554'
$apkPath = Join-Path $projectRoot 'mobile\build\app\outputs\flutter-apk\app-debug.apk'

if (!(Test-Path -LiteralPath $adbPath) -or !(Test-Path -LiteralPath $emulatorPath)) {
    throw 'Install the Android SDK and Meta_Demo_API_35 virtual device first. See ANDROID_RUN.md.'
}

try {
    $null = Invoke-RestMethod 'http://127.0.0.1:8000/analysis/status' -TimeoutSec 3
} catch {
    Start-Process -FilePath (Join-Path $projectRoot '.venv\Scripts\python.exe') `
        -ArgumentList @('-m', 'uvicorn', 'src.api:app', '--host', '127.0.0.1', '--port', '8000') `
        -WorkingDirectory $projectRoot -WindowStyle Hidden | Out-Null
}

$devices = & $adbPath devices
if (!($devices -match "^$serial\s")) {
    Start-Process -FilePath $emulatorPath -ArgumentList @(
        '-avd', 'Meta_Demo_API_35', '-port', '5554', '-memory', '2048',
        '-cores', '2', '-no-boot-anim', '-no-snapshot-load'
    ) -WindowStyle Normal | Out-Null
}

$deadline = (Get-Date).AddMinutes(4)
$booted = $false
while ((Get-Date) -lt $deadline) {
    $readyDevices = & $adbPath devices
    if ($readyDevices -match "^$serial\s+device") {
        $bootValue = & $adbPath -s $serial shell getprop sys.boot_completed
        if (($bootValue -join '').Trim() -eq '1') { $booted = $true; break }
    }
    Start-Sleep -Seconds 2
}
if (!$booted) { throw 'Android emulator did not finish booting within four minutes.' }

if ($Rebuild -or !(Test-Path -LiteralPath $apkPath)) {
    & flutter config --android-sdk $sdkRoot
    $jdkHint = Join-Path $projectRoot 'outputs\android-setup\jdk-home.txt'
    if (Test-Path -LiteralPath $jdkHint) {
        $jdkDirectory = (Get-Content -LiteralPath $jdkHint -Raw).Trim()
        if (Test-Path -LiteralPath (Join-Path $jdkDirectory 'bin\jlink.exe')) {
            & flutter config --jdk-dir $jdkDirectory
        }
    }
    Push-Location (Join-Path $projectRoot 'mobile')
    try {
        & flutter build apk --debug --target-platform android-x64 `
            --dart-define-from-file=..\outputs\reviewer-defines.json
        if ($LASTEXITCODE -ne 0) { throw 'Android APK build failed.' }
    } finally { Pop-Location }
}

& $adbPath -s $serial reverse tcp:8000 tcp:8000
if ($LASTEXITCODE -ne 0) { throw 'Could not forward the local backend to Android.' }
& $adbPath -s $serial install -r $apkPath
if ($LASTEXITCODE -ne 0) { throw 'APK installation failed.' }
& $adbPath -s $serial shell am start -n com.example.social_demo/.MainActivity
if ($LASTEXITCODE -ne 0) { throw 'Android app did not start.' }
