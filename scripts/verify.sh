#!/usr/bin/env bash
set -euo pipefail
export GENVM_VERSION=v0.2.16
genvm-lint check contracts/fitted_contract.py --json
genvm-lint typecheck contracts/fitted_contract.py --json
genvm-lint schema contracts/fitted_contract.py --json
python -m py_compile contracts/fitted_contract.py
python -m pytest tests/ --ignore=tests/test_direct.py -q
python -m pytest tests/test_direct.py -q
npm --prefix frontend ci
npm --prefix frontend test
npm --prefix frontend run lint
npm --prefix frontend run build
printf '%s\n' 'Local static, test and build verification passed. StudioNet lifecycle proof and public hosting remain separate release gates.'
