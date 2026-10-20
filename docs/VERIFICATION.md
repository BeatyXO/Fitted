# Verification log — 2026-10-20

## Contract and deployment evidence

- The preserved hardened GenLayer StudioNet deployment is [`0xCFd6184ad5589a329E8F89984d2FfEc98607cD72`](https://explorer-studio.genlayer.com/address/0xCFd6184ad5589a329E8F89984d2FfEc98607cD72), chain ID `61999`, RPC `https://studio.genlayer.com/api`.
- Its source SHA-256 is `9abff3f3aeb83b6d2f69fb2c6032d7bbacc03bd627fd703bec9bcca4145e00b7`. Deployment receipt, validator votes, lifecycle transaction hashes and finalized readbacks remain preserved in [`../deployments/studionet_hardened.json`](../deployments/studionet_hardened.json). No contract code, address, chain, or deployment was changed during this remediation.
- The established finalized lifecycle covers all four outcomes: FIT, CONDITIONAL, UNFIT, and UNVERIFIED, plus immutable version pinning, duplicate-evaluation protection, and retirement. Existing transaction evidence is unchanged.

## Engineering checks run locally

- Offline contract-boundary tests: **70 passed** (`python -m pytest tests/ --ignore=tests/test_direct.py -q`). These use the labeled GenLayer interface stand-in, not real GenVM consensus.
- GenLayer Direct Mode tests: **7 passed** (`python -m pytest tests/test_direct.py -q`). Direct Mode is in-process and not StudioNet consensus.
- Node receipt and wallet tests: **15 passed** (`npm test`; 5 receipt tests and 10 wallet tests). JavaScript syntax checks passed (`npm run check`).
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
- Two real wallet-approved `create_standard` transactions finalized successfully. The first, [`0x6e64cfd6efedce4315881a7f9acc5cd3ade1bd5b5bbe70584be73191b7958d30`](https://explorer-studio.genlayer.com/tx/0x6e64cfd6efedce4315881a7f9acc5cd3ade1bd5b5bbe70584be73191b7958d30), returned `FIT-4` (`Wallet flow verification record`). The second, [`0xde14bbdc301ebb445f1ca84e75bd1aa95edd41aa4b9fed9bbf69184b0a717496`](https://explorer-studio.genlayer.com/tx/0xde14bbdc301ebb445f1ca84e75bd1aa95edd41aa4b9fed9bbf69184b0a717496), returned `FIT-5` (`Receipt handling verification 2`). Both are clearly labeled operational verification records and are visible in the production registry. The explorer reports FINALIZED, consensus accepted, and GenVM execution SUCCESS for both.
- The deployed frontend first displayed `unknown / unknown`, then after the first fix displayed `FINALIZED / SUCCESS` as an error. The second production reproduction showed StudioNet includes validator receipts cancelled with `CONSENSUS_VALIDATOR_QUORUM_REACHED` after quorum. The source fix recognizes this successful finalized majority plus leader execution and includes a regression test matching the actual receipt shape. The expanded receipt suite, production build, and Chromium checks pass locally and in CI. The GitHub push triggers the connected Vercel production build automatically; verify the UI message on the next approved production transaction.
- The production transactions verified wallet connect, network switching, two wallet-signed standard creations, finalization, and registry readback. Disconnect, reconnect, account switching, rejection, unsuccessful execution, pending recovery, real RPC failure, candidate submission, and candidate evaluation were **not** verified in production. UI-only paths and RPC failures were covered only by local Chromium smoke tests. No candidate/evaluation transaction was submitted.
- The earlier parser correction reached production through the connected GitHub/Vercel deployment, as confirmed by the changed error message. The quorum-cancellation refinement is on `main` and CI is green. Production registry readback was verified; the final corrected success message has not been observed in Chrome after this latest push.

## CI status and links

- GitHub repository: [BeatyXO/Fitted](https://github.com/BeatyXO/Fitted), `main`.
- The previously inspected failed run was [39409434960](https://github.com/BeatyXO/Fitted/actions/runs/39409434960). Its browser job evaluated raw ES module source with `page.evaluate`, causing `Cannot use 'import.meta' outside a module`. The replacement smoke test runs the built Vite app through `vite preview` and Chromium.
- Receipt parser commit `a006fdfaf983926413d4bf968132920bbbd09c60` passed [GitHub Actions run 39419619789](https://github.com/BeatyXO/Fitted/actions/runs/39419619789); all four jobs (`contract-offline`, `contract-direct`, `wallet-ui`, and `browser-responsive`) were green. CI uses clean `npm ci`, runs the frontend production build and audit, and executes Chromium against the Vite-served build.
- Vercel production: [fitted-lake.vercel.app](https://fitted-lake.vercel.app/).
- Contract explorer: [StudioNet contract page](https://explorer-studio.genlayer.com/address/0xCFd6184ad5589a329E8F89984d2FfEc98607cD72).

## Remaining work and limitations

The complete production standard → candidate → evaluation lifecycle has not been run. The second production reproduction showed a false receipt error; the corrected parser is on `main` and CI is green, while its success message has not been confirmed in Chrome after the latest Vercel update. Disconnect/reconnect and adversarial/pending-recovery production checks remain outstanding. Submission readiness is not declared.
