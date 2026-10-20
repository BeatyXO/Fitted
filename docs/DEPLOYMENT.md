# Fitted StudioNet deployment and acceptance runbook

**Hardened StudioNet deployment and core lifecycle completed** at `0xCFd6184ad5589a329E8F89984d2FfEc98607cD72`; see [`../deployments/studionet_hardened.json`](../deployments/studionet_hardened.json) for the source hash, finalized deployment and lifecycle receipts, validator votes, and state readbacks. The earlier deployment is retained as history. The hardened source compares evidence fingerprints across validators and revalidates accepted judgments after the nondeterministic boundary. Local frontend checks and live read-only chain interaction passed. The user will publish the frontend to Vercel; additional adversarial security and stress review remain useful follow-up.

## Preparation

1. Install the current stable GenLayer CLI and Python `gltest`/GenVM linter for **StudioNet**, not an unrelated release candidate. See https://docs.genlayer.com/developers/intelligent-contracts/tooling-setup and https://docs.genlayer.com/developers/intelligent-contracts/testing .
2. Validate `genlayer network list`, then select `studionet` and inspect `genlayer network info` for `https://studio.genlayer.com/api` and chain ID **61999**.
3. Provision a funded testnet deployer wallet in the local CLI. **Never commit or send its private key** with this project or into a frontend env variable.
4. Verify the Python contract source's exact content hash and pin the SDK/runner versions used for the test.

## Static and GenVM checks

```bash
python -m pytest tests/ --ignore=tests/test_direct.py -q
python -m pytest tests/test_direct.py -q
python -m py_compile contracts/fitted_contract.py
node --check frontend/app.js
# Pin the exact deployed runner for the GenVM linter (PowerShell):
$env:GENVM_VERSION = 'v0.2.16'
genvm-lint check contracts/fitted_contract.py --json
# Generate/check schema with your CLI version (flags vary across releases):
genlayer schema --contract contracts/fitted_contract.py
```

Use the exact syntax printed by `genlayer deploy --help` for your installed CLI. On supported stable GenLayer CLI releases:

```bash
genlayer network set studionet
genlayer deploy --contract contracts/fitted_contract.py
```

The Python class `Fitted` has no constructor parameters. Save the returned real contract address, deployment tx hash, runner identifier, finalized transaction receipt and every validator's vote. Never infer an address from a transaction submission message.

## Acceptance matrix: real chain writes, not mocks

Perform **at least** the following actions using funded testnet wallets. Preserve raw tx and read results in `deployments/studionet.json` (create after successful deployment), with a source hash. Use one honest public documentation source and separately test controlled public documents containing negative and inconclusive cases.

| Case | Expected invariant |
|---|---|
| A | New standard v1 owned by the caller; 1–6 bounded requirements |
| B | Unauthorized revision/retirement reverts; owner revision creates v2 |
| C | Applications created before v2 still reference v1 |
| D | Fetched text and validator model outputs produce a FIT certificate with literal citations |
| E | A mandatory contradiction gives UNFIT regardless of numeric score |
| F | A missing mandatory fact returns UNVERIFIED, not UNFIT or FIT |
| G | Optional gap with mandatory satisfied gives CONDITIONAL |
| H | On missing/failed source, validator findings cannot fraudulently use an absent quote |
| I | Genuine validator disagreement causes failure/retry without changing PENDING state |
| J | Double evaluation cannot replace an existing certificate |
| K | A retired standard no longer accepts submissions; old certificates remain readable |
| L | Wallet-signed frontend write reaches FINALIZED + successful execution and then updates read state |
| M | Browser at 375px and 1440px, no clipping; tab/keyboard flows work |
| N | Two candidates evaluated under the same version compare correctly; different versions never share a ranking |

## Frontend

`frontend/` pins `genlayer-js@1.1.8` and Vite in its lockfile and bundles the SDK locally. The production build and frontend tests have passed. The user plans to publish the built frontend to Vercel after handoff. Never switch successful transaction status to a submitted or merely accepted stage.

After a verified deployment, publish the frontend to a static host with HTTPS. On Vercel, optionally set `VITE_CONTRACT_ADDRESS` to the deployed contract address for the Production, Preview, and Development environments you use, then redeploy. The frontend also accepts a `?contract=0x...` URL parameter, which overrides the environment value, or the address can be entered in the dashboard. Do not supply an invented default address.

## Provenance checklist to include in the final submission

- GitHub repo + immutable commit SHA; SHA-256 of contract source;
- Live frontend URL + full deployed bundle/config hash;
- StudioNet contract and deployment tx explorer URLs, chain ID and runtime dependency version;
- 5/5 or documented validator decision breakdown for each test;
- Raw finalization receipts with `txExecutionResultName`, not only submitted hashes;
- Exact command outputs from lint, test, frontend build and mobile checks;
- A dated list of failures, known limitations and remaining follow-ups.

## Rollback

Fitted v1 contracts are not upgradeable in place. If a critical issue is found, cease creating new standards on that deployment, publish a new versioned contract address, and clearly mark prior certificates as legacy in the frontend. Existing old-chain records remain public; a new deployment does not silently migrate or revoke them. There is no user escrow to recover, but gas and previously published records cannot be rolled back.



