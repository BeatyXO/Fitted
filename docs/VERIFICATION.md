# Verification log — 2026-10-19

## Confirmed

- GenVM linter `0.11.0`, explicitly pinned to `GENVM_VERSION=v0.2.16`: lint passed 3 checks; contract validation recognized `Fitted` with 11 methods (6 views, 5 writes); typecheck reported no errors or warnings; schema generation succeeded.
- Actual `genlayer-test 0.29.2` Direct Mode: **7 passed**. Coverage includes authorization, immutable version pins, all four outcomes, unavailable sources, quote grounding, semantic validator rechecks, source mutation, replay rejection, duplicate URLs, non-public URLs, and pagination bounds. Direct Mode is in-process and does not prove StudioNet consensus.
- Offline contract-boundary suite using the explicitly labeled GenLayer stand-in: **69 passed**. Separate from the Direct Mode count.
- Python syntax compile passed.
- Frontend package pins `genlayer-js 1.1.8` and Vite `6.4.4`; production build bundles the SDK locally. Node wallet suite: **10 passed**. `npm audit` reported 0 known vulnerabilities after the Vite update.
- Chromium inspection of the built frontend at 375px and 1440px found no horizontal overflow; the app displayed its actual empty on-chain registry. The dedicated Playwright smoke script could not run because Python Playwright is unavailable.
- StudioNet deployment finalized at `0x299B9577A4b03efab9F760715ce6Db5437943cBe`, tx `0xea2d3bf0b016742fe10e34e41fba1052855086f74fdd80b449bcd4467443e861`. Five validators committed/revealed; three agreed and two were idle. Execution succeeded, no value was credited, and deployed source hash matched the local contract hash. See [`../deployments/studionet.json`](../deployments/studionet.json).
- Initial post-deployment reads returned the expected 11-method schema and an empty registry; subsequent lifecycle reads are recorded below.
- Full StudioNet lifecycle completed on the deployed contract. Four outcome certificates finalized: APP-1 `FIT`, APP-2 `CONDITIONAL`, APP-4 `UNFIT`, APP-5 `UNVERIFIED`; APP-3 also finalized as `UNVERIFIED` on an earlier isolation claim. Each certificate was read back after finality with a fetched-source fingerprint and grounded quote for decisive findings. Final chain stats: **4 standards, 5 candidates, 5 evaluations**.
- FIT-1 revision finalized at v2; APP-1 remains pinned to v1 and APP-2 is pinned to v2. FIT-1 retirement finalized with `active: false`; APP-1 and APP-2 certificates remain readable. A second evaluation of APP-1 finalized as a contract rollback with `candidate already evaluated`, leaving the original FIT certificate unchanged.
- Sanitized transaction statuses, consensus votes, and lifecycle hashes are recorded in [`../deployments/lifecycle_transactions.json`](../deployments/lifecycle_transactions.json). The raw CLI receipt logs were not included because they contain verbose validator runtime configuration; the saved proof contains only transaction status, result, execution summaries, and votes.

## Still outstanding

- Full independent reproduction on a second wallet/provider and a broader adversarial evidence corpus.
- Production Vercel deployment and live URL. The user intends to deploy this themselves.
- GitHub publication. This folder has no `.git` repository or configured remote. `gh auth status` reports both saved GitHub accounts have invalid tokens. No destination repository URL is specified, so no authorized push can currently be completed.
- Playwright E2E suite and wallet-signed browser transactions.

No numerical audit score is assigned. Test categories are not combined into a claim of StudioNet lifecycle success. The live evidence available is deployment finality plus read-only state, not successful product lifecycle transactions.
