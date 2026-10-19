$ErrorActionPreference = 'Stop'
Write-Host 'Fitted verification: offline tests, real GenLayer Direct Mode, and production frontend build'
$env:GENVM_VERSION = 'v0.2.16'
genvm-lint check contracts/fitted_contract.py --json
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
genvm-lint typecheck contracts/fitted_contract.py --json
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
genvm-lint schema contracts/fitted_contract.py --json
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m py_compile contracts/fitted_contract.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pytest tests/ --ignore=tests/test_direct.py -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pytest tests/test_direct.py -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm.cmd ci --prefix frontend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm.cmd test --prefix frontend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm.cmd run lint --prefix frontend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm.cmd run build --prefix frontend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'Local static, test and build verification passed. StudioNet lifecycle proof and public hosting remain separate release gates.'
