@echo off
setlocal enabledelayedexpansion

where py >nul 2>nul
if %errorlevel%==0 (
  set PY_CMD=py
) else (
  where python >nul 2>nul
  if not %errorlevel%==0 (
    echo Python nao encontrado. Instale Python 3 e tente novamente.
    exit /b 1
  )
  set PY_CMD=python
)

if not exist ".venv" (
  %PY_CMD% -m venv .venv
)

set PYTHON_EXE=.venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
  echo Falha ao localizar "%PYTHON_EXE%".
  exit /b 1
)

if not exist ".venv\.deps_installed" (
  "%PYTHON_EXE%" -m pip install --upgrade pip
  "%PYTHON_EXE%" -m pip install -r requirements.txt
  type nul > ".venv\.deps_installed"
)

"%PYTHON_EXE%" -m streamlit run app.py
