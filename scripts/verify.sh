#!/usr/bin/env bash
set -euo pipefail
python -m py_compile contracts/fitted_contract.py
python -m pytest tests/ -q
node --check frontend/app.js
printf '%s\n' 'Offline checks passed. This is not GenVM or StudioNet proof.'
