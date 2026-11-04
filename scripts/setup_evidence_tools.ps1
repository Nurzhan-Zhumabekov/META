$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    & uv python install 3.12
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 installation failed' }
    foreach ($environment in @('.venv-vision','.venv-privacy')) {
        if (!(Test-Path -LiteralPath ($environment + '\Scripts\python.exe'))) {
            & uv venv --python 3.12 $environment
            if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed' }
        }
    }
    & uv pip install --python .venv-vision\Scripts\python.exe 'torch==2.15.0+cpu' 'torchvision==0.29.2+cpu' --index-url https://download.pytorch.org/whl/cpu
    if ($LASTEXITCODE -ne 0) { throw 'CPU PyTorch installation failed' }
    & uv pip install --python .venv-vision\Scripts\python.exe -r requirements-vision.txt
    if ($LASTEXITCODE -ne 0) { throw 'OCR/image dependency installation failed' }
    & uv pip install --python .venv-privacy\Scripts\python.exe -r requirements-privacy.txt
    if ($LASTEXITCODE -ne 0) { throw 'Privacy dependency installation failed' }
    & uv pip install --python .venv-privacy\Scripts\python.exe https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
    if ($LASTEXITCODE -ne 0) { throw 'spaCy model installation failed' }
    & .\scripts\run_evidence_workers.ps1
} finally { Pop-Location }
