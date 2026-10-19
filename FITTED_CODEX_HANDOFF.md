# Codex continuation brief — get Fitted above the Crossbench benchmark

You are operating on the **original, independently designed Fitted source** in this repository. Preserve its product thesis: independently validated solution/requirement suitability, not a dispute tribunal or Crossbench clone. First inspect `README.md`, `docs/BENCHMARK.md`, `docs/SECURITY.md`, and `docs/VERIFICATION.md`. **Do not change Crossbench source or reuse Crossbench code.**

## Mission

Take Fitted from a locally tested project to a **provably deployed, reliable GenLayer StudioNet product**. Score it critically on four dimensions: (a) GenLayer fit, (b) contract quality, (c) engineering reliability, (d) frontend quality. Do not assign a high score based on code volume or test counts. Compare against the published Crossbench strengths, not an invented judge score.

## Non-negotiable engineering standards

1. Run the actual GenVM linter and Direct Mode on the standalone contract. Fix **every real error**, including GenVM-specific restrictions, storage allocations, `TreeMap` semantics, `gl.vm.run_nondet_unsafe`, UI schema method signatures, source fetch and HTTP status handling. Do not substitute a CPython mock for GenVM proof.
2. Create real Direct Mode tests for authorization, version immutability, all four outcomes, validator semantic agreement/conflict, source unavailability, source mutation, normalization/quote grounding, duplicate URLs, large inputs, non-public URLs, non-owner actions, replay, invalid IDs, repeated reads, full pagination, and no financial-value pathways.
3. Deploy a fresh Fitted contract to **StudioNet 61999** only after successful lint and direct tests. Record the address, source hash, deployment tx hash, actual validator results, latest finalized reads, failure logs, and SDK/runner version in a new `deployments/studionet.json` file. Never invent addresses, hashes, receipts, metrics, or votes. Never move user funds beyond intentional network fees.
4. Execute complete real lifecycle scripts on StudioNet: publish standard, submit candidate, evaluate each of FIT/CONDITIONAL/UNFIT/UNVERIFIED on independently fetchable public evidence, revise standard and verify pinned prior version, test duplicate evaluation rejection, retire standard. Each result must include real finalized transaction proof plus post-finalization contract read.
5. **Audit equivalence**: validators must independently re-fetch and judge each decisive claim, not merely schema-check the leader. Verify the mandatory outcome cannot flip under permitted tolerance. Record any liveness issues and recoverability limits honestly; do not introduce financial escrow.
6. Verify literal evidence quotes are present in the independently fetched normalized text; consider misleading quotes, content provenance, self-hosted fake sources, redirect/DNS attack surfaces, website mutations, and prompt injection. Treat source availability separately from source truth.
7. Replace runtime `esm.sh` SDK dependency with an **exact-pinned, reproducible local production build** (Vite or equivalent) and tested wallet integration. Verify `genlayer-js` version API signatures against the current stable StudioNet release. Run dependency audit, typecheck, lint, production build and client tests. Keep UI direct signed writes; no fake data and no backend signing.
8. Make the frontend a fully usable product: standards publishing/revision/retirement, candidate source submission, finalized transaction receipts, robust pending/error screens, account/wallet/network switching, certificate quotes and provenance, same-version multi-candidate comparison, accessible responsive design. Confirm 375px and 1440px without overflow and a real deployed production URL.
9. Add useful operational protections: bounded paginated reads, structured transaction error handling, RPC budget awareness, pending-transaction recovery without fabricated success, and documented backup/rollback address procedures.
10. Push the verified repository to the authorized user GitHub repository **only when account write access is explicitly available**; if the intended account is inaccessible, leave the package intact and report that blocker rather than pushing it under an unrelated account.

## Acceptance deliverables

- GitHub repository URL, exact commit SHA and clean tree.
- Deployed contract address and live frontend URL, both actually reachable.
- Reproducible builds and test counts categorized as offline mock, Direct Mode, StudioNet, browser/E2E (never blend categories).
- Real explorer links and at least one successful finalized transaction for each outcome and critical lifecycle action.
- Security review with any remaining severity-ranked issues and reproducible steps.
- Final comparison matrix showing objective evidence of parity or superiority over Crossbench across all four scoring categories; explicitly mark unknown scores.

The original 69 offline tests pass as of 2026-10-19. That is a starting baseline, **not** completion proof. Continue until an external reviewer could independently reproduce the demonstration.

## Current verified local changes (2026-10-19)

Wallet dropdown copy/disconnect, consent-based refresh reconnection, wrong-network switch/add, card glow, JS wallet unit tests, and 375/390/1440 Chromium smoke are complete and verified. Remaining work: real GenVM lint/gltest, pinned SDK build, StudioNet deployment and wallet/consensus E2E, public hosting and audit.

