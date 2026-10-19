# Verification log — 2026-10-19

## Confirmed

- GenVM linter `0.11.0`, explicitly pinned to `GENVM_VERSION=v0.2.16`: lint passed 3 checks; contract validation recognized `Fitted` with 11 methods (6 views, 5 writes); typecheck reported no errors or warnings; schema generation succeeded.
- Actual `genlayer-test 0.29.2` Direct Mode: **7 passed**. Coverage includes authorization, immutable version pins, all four outcomes, unavailable sources, quote grounding, semantic validator rechecks, source mutation, replay rejection, duplicate URLs, non-public URLs, and pagination bounds. Direct Mode is in-process and does not prove StudioNet consensus.
- Offline contract-boundary suite using the explicitly labeled GenLayer stand-in: **69 passed**. Separate from the Direct Mode count.
- Python syntax compile passed.
- Frontend package pins `genlayer-js 1.1.8` and Vite `6.4.4`; production build bundles the SDK locally. Node wallet suite: **10 passed**. `npm audit` reported 0 known vulnerabilities after the Vite update.
- Chromium inspection of the built frontend at 375px and 1440px found no horizontal overflow; the app displayed its actual empty on-chain registry. The dedicated Playwright smoke script could not run because Python Playwright is unavailable.
- StudioNet deployment finalized at `0x299B9577A4b03efab9F760715ce6Db5437943cBe`, tx `0xea2d3bf0b016742fe10e34e41fba1052855086f74fdd80b449bcd4467443e861`. Five validators committed/revealed; three agreed and two were idle. Execution succeeded, no value was credited, and deployed source hash matched the local contract hash. See [`../deployments/studionet.json`](../deployments/studionet.json).
- Finalized reads returned the expected 11-method schema, `get_stats` with zero records, and an empty standards page.

## Still outstanding

- StudioNet lifecycle proof: publish a standard, submit a candidate, finalize FIT/CONDITIONAL/UNFIT/UNVERIFIED evaluations on independent public evidence, revise and verify pinned versions, reject a duplicate evaluation, and retire a standard. The initial CLI submission attempt rolled back with `requirements must be JSON`; no standard was created and the contract remains unchanged.
- Production Vercel deployment and live URL. The user intends to deploy this themselves.
- Playwright E2E suite and wallet-signed browser transactions.

The verified source package is published at https://github.com/BeatyXO/Fitted. Production hosting remains for the user to deploy.

No numerical audit score is assigned. Test categories are not combined into a claim of StudioNet lifecycle success. The live evidence available is deployment finality plus read-only state, not successful product lifecycle transactions.
