# Verification log — 2026-10-20

## Confirmed

- GenVM linter `0.11.0`, pinned to `GENVM_VERSION=v0.2.16`: lint passed 3 checks; validation recognized `Fitted` with 11 methods (6 views, 5 writes); typecheck reported no errors; schema generation succeeded.
- Actual `genlayer-test 0.29.2` Direct Mode: **7 passed**. Coverage includes authorization, immutable version pins, all four outcomes, unavailable sources, quote grounding, semantic validator rechecks, source mutation, replay rejection, duplicate URLs, non-public URLs, and pagination bounds. Direct Mode is in-process and does not prove StudioNet consensus.
- Offline contract-boundary suite using the labeled GenLayer stand-in: **70 passed**. Python compile checks passed.
- Frontend package pins `genlayer-js 1.1.8` and Vite `6.4.4`; production build passed. Node wallet suite: **10 passed**. `npm audit --omit=optional` reported 0 known vulnerabilities.
- Chromium inspection of localhost at 375px and 1440px found no horizontal overflow. The local app was checked against finalized StudioNet state, including the live FIT certificate, its grounded quote and source fingerprint. No browser console errors were observed. Dedicated Playwright smoke automation remains unavailable in this environment.
- Hardened StudioNet deployment finalized at `0xCFd6184ad5589a329E8F89984d2FfEc98607cD72`; tx `0x86dcf13826e0b0bf0dd055dddfa7d27fa41cbdf205da5e9bbc6dbcde416f71f2`. Five validators committed/revealed; execution succeeded. Deployed source SHA-256 exactly matches local source: `9abff3f3aeb83b6d2f69fb2c6032d7bbacc03bd627fd703bec9bcca4145e00b7`. See [`../deployments/studionet_hardened.json`](../deployments/studionet_hardened.json).
- Hardened contract lifecycle finalized: FIT, CONDITIONAL, UNFIT, and UNVERIFIED certificates; standard revision with prior-version pinning; duplicate-evaluation rollback preserving the original certificate; standard retirement with historical certificates retained. Final reads: **3 standards, 4 candidates, 4 evaluations**. Every lifecycle receipt and vote breakdown is saved in the hardened deployment proof. The earlier deployment record is preserved separately.
- The security patch compares validator-observed source fingerprints and fully revalidates the accepted judgments after the nondeterministic boundary.
- The completed source and deployment evidence are published in the authorized repository: [github.com/BeatyXO/Fitted](https://github.com/BeatyXO/Fitted).
- The Vercel deployment is live at [fitted-lake.vercel.app](https://fitted-lake.vercel.app/). Browser inspection confirmed the app loads the hardened contract and displays its live registry counts: 3 standards, 4 candidates, 4 evaluations.

## Remaining follow-up

- A second-wallet/provider reproduction and broader adversarial evidence corpus remain useful follow-up work. Wallet-signed browser writes were not used for lifecycle testing; direct SDK writes were finalized and independently read back on StudioNet.

No numerical audit score is assigned. Test categories are reported separately; only the finalized chain lifecycle is described as StudioNet success.
