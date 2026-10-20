# Verification log — 2026-10-20

## Contract and deployment evidence

- The preserved hardened GenLayer StudioNet deployment is [`0xCFd6184ad5589a329E8F89984d2FfEc98607cD72`](https://explorer-studio.genlayer.com/address/0xCFd6184ad5589a329E8F89984d2FfEc98607cD72), chain ID `61999`, RPC `https://studio.genlayer.com/api`.
- Its source SHA-256 is `9abff3f3aeb83b6d2f69fb2c6032d7bbacc03bd627fd703bec9bcca4145e00b7`. Deployment receipt, validator votes, lifecycle transaction hashes and finalized readbacks remain preserved in [`../deployments/studionet_hardened.json`](../deployments/studionet_hardened.json). No contract code, address, chain, or deployment was changed during this remediation.
- The established finalized lifecycle covers all four outcomes: FIT, CONDITIONAL, UNFIT, and UNVERIFIED, plus immutable version pinning, duplicate-evaluation protection, and retirement. Existing transaction evidence is unchanged.

## Engineering checks run locally

- Offline contract-boundary tests: **70 passed** (`python -m pytest tests/ --ignore=tests/test_direct.py -q`). These use the labeled GenLayer interface stand-in, not real GenVM consensus.
- GenLayer Direct Mode tests: **7 passed** (`python -m pytest tests/test_direct.py -q`). Direct Mode is in-process and not StudioNet consensus.
- Node receipt and wallet tests: **13 passed** (`npm test`; 3 receipt tests and 10 wallet tests). JavaScript syntax checks passed (`npm run check`).
- `npm audit --omit=optional`: **0 known vulnerabilities**.
- Vite production build passed after clean `npm ci`.
- Chromium smoke test passed against the built Vite app served by `vite preview` at **1440px, 390px, and 375px**. It loaded the Vite module bundle and checked keyboard focus, accessible status, navigation, wallet UI state paths using a test-only injected EIP-1193 provider, form validation controls, responsive overflow, and visible RPC failure handling. The provider double did not submit a transaction and is not production wallet evidence.
- The RPC-failure check verifies the app shows a read error and does not label unavailable chain data as an empty registry. A small frontend fix was made to render “Registry unavailable” while reads have failed.

## Production frontend verification

- Production URL: [https://fitted-lake.vercel.app/](https://fitted-lake.vercel.app/).
- Using the connected Chrome browser on 2026-10-20, the deployed page loaded the configured contract address and actual finalized registry data. Before the test write it showed **3 standards, 4 candidates, 4 evaluations**; after the write and refresh it showed **4 standards**, including the new `FIT-4` verification standard.
- The live standards, candidates, certificates, and comparison pages were opened. The four certificates displayed FIT, CONDITIONAL, UNFIT, and UNVERIFIED. APP-1 displayed its finalized certificate digest, a literal source quote, and the linked evidence URL `https://docs.python.org/3/library/venv.html` with a source hash.
- The registry has fewer than the 24 rows per page, so a “load next page” action was not available to verify against a larger live dataset.
- The connected Chrome profile exposed Rabby and account `0xd6423ae82a975d55c6ceac222827a727325e0459`. The wallet was switched to StudioNet (chain ID `61999`) through the app.
- One real wallet-approved `create_standard` transaction finalized successfully: [`0x6e64cfd6efedce4315881a7f9acc5cd3ade1bd5b5bbe70584be73191b7958d30`](https://explorer-studio.genlayer.com/tx/0x6e64cfd6efedce4315881a7f9acc5cd3ade1bd5b5bbe70584be73191b7958d30). The explorer reports FINALIZED, consensus accepted, GenVM execution SUCCESS, result code Return, and returned standard ID `FIT-4`. The standard became visible in the production frontend after refresh. Its name is `Wallet flow verification record`; its purpose explicitly identifies it as an operational verification record.
- The deployed frontend initially displayed an erroneous failure (`unknown / unknown`) for that finalized successful receipt. The local fix now recognizes the SDK's `txExecutionResultName` and conservatively validates raw StudioNet receipts when that normalized field is absent. Receipt tests cover successful, failed, incomplete, non-majority, and unfinalized cases. The corrected bundle still needs to be deployed before verifying that the production UI displays this receipt as successful.
- The production transaction verified connect, network switching, one wallet-signed standard creation, finalization, and registry readback. Disconnect, reconnect, account switching, rejection, unsuccessful execution, pending recovery, real RPC failure, candidate submission, and candidate evaluation were **not** verified in production. UI-only paths and RPC failures were covered only by local Chromium smoke tests. No candidate/evaluation transaction was submitted.
- The currently deployed JS bundle predates the receipt fix. Vercel CLI is authenticated as `ifem1` and cannot inspect the `fitted-lake` project under that account. The project owner must deploy the latest `main` build in the existing Vercel project. Vercel will deploy pushes automatically only when its project Git integration is linked to this repository and `main` is configured as the production branch; that configuration was not verifiable from the available CLI account.

## CI status and links

- GitHub repository: [BeatyXO/Fitted](https://github.com/BeatyXO/Fitted), `main`.
- The previously inspected failed run was [39409434960](https://github.com/BeatyXO/Fitted/actions/runs/39409434960). Its browser job evaluated raw ES module source with `page.evaluate`, causing `Cannot use 'import.meta' outside a module`. The replacement smoke test runs the built Vite app through `vite preview` and Chromium.
- Receipt fix commit `0ac820e459a5f26cabfc3bf19e0d36d9e3db45bc` passed [GitHub Actions run 39416474604](https://github.com/BeatyXO/Fitted/actions/runs/39416474604); all four jobs (`contract-offline`, `contract-direct`, `wallet-ui`, and `browser-responsive`) were green. CI uses clean `npm ci`, runs the frontend production build and audit, and executes Chromium against the Vite-served build.
- Vercel production: [fitted-lake.vercel.app](https://fitted-lake.vercel.app/).
- Contract explorer: [StudioNet contract page](https://explorer-studio.genlayer.com/address/0xCFd6184ad5589a329E8F89984d2FfEc98607cD72).

## Remaining work and limitations

The complete production standard → candidate → evaluation lifecycle has not been run; only one user-approved standard creation transaction was performed. The receipt fix passed CI and was pushed, but its deployment and receipt display still need verification on Vercel. Disconnect/reconnect and adversarial/pending-recovery production checks remain outstanding. Submission readiness is not declared.
