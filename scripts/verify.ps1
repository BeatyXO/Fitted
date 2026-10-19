$ErrorActionPreference = 'Stop'
Write-Host 'Fitted offline verification (not GenVM or StudioNet proof)'
python -m py_compile contracts/fitted_contract.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pytest tests/ -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
node --check frontend/app.js
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'Offline checks passed. Live chain verification is still required.'
