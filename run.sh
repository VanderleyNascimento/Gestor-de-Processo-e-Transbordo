#!/usr/bin/env bash
set -euo pipefail

# Bootstrap local venv and dependencies, then run Streamlit.
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 nao encontrado. Instale Python 3 antes de continuar."
  exit 1
fi

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

if [ ! -f ".venv/.deps_installed" ] || [ requirements.txt -nt ".venv/.deps_installed" ]; then
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
  touch .venv/.deps_installed
fi

python -m streamlit run app.py
