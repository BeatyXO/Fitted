#!/usr/bin/env bash
set -euo pipefail
python -m py_compile contracts/fitted_contract.py
python -m pytest tests/ --ignore=tests/test_direct.py -q
python -m pytest tests/test_direct.py -q
npm --prefix frontend ci
npm --prefix frontend test
npm --prefix frontend run lint
npm --prefix frontend run build
printf '%s\n' 'Local verification passed. GenVM lint SDK validation and StudioNet lifecycle proof remain separate release gates.'
