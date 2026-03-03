$ErrorActionPreference = "Stop"

if (-not (Get-Command py -ErrorAction SilentlyContinue) -and -not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python nao encontrado. Instale Python 3 e tente novamente."
}

if (-not (Test-Path ".venv")) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        py -m venv .venv
    } else {
        python -m venv .venv
    }
}

$pythonExe = ".venv\\Scripts\\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Error "Falha ao localizar o Python do ambiente virtual em .venv\\Scripts\\python.exe"
}

$depsStamp = ".venv\\.deps_installed"
if (-not (Test-Path $depsStamp) -or ((Get-Item "requirements.txt").LastWriteTime -gt (Get-Item $depsStamp).LastWriteTime)) {
    & $pythonExe -m pip install --upgrade pip
    & $pythonExe -m pip install -r requirements.txt
    New-Item -Path $depsStamp -ItemType File -Force | Out-Null
}

& $pythonExe -m streamlit run app.py
