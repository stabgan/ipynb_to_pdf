#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment…"
    python3 -m venv venv
fi

source ./venv/bin/activate
pip install -q -r requirements.txt
python3 main.py
