# Crossbench benchmark and what Fitted must prove

Reference inspected on 2026-10-19: https://github.com/zoefunds/Crossbench (main branch). The fact that Crossbench *scored highly* was supplied by the requester; **no independently verifiable judge-issued numerical score or scoring rubric was available in the repository**.

## Concrete strengths found in Crossbench

1. **GenLayer is core protocol logic.** Independent validators retrieve public evidence and decide disputed claims, while the contract deterministically derives payouts. This is not a centralized oracle feeding a blockchain receipt.
2. **Explicit trust boundaries.** Wallets sign value-moving transactions; read-only backend has no escrow authority. Contract enforces parties, deadlines, evidence immutability, credits and withdrawals.
3. **Material Equivalence Principle.** Validator agreement tolerates harmless differences in explanations and source rendering but rejects opposing support or substantial provenance conflicts.
4. **Source-quality controls.** Canonical URL deduplication, independently fetched content fingerprints, source issuer provenance, structured ledger references, and mutation warnings.
5. **Complete user journey.** Browser wallet writes, transaction lifecycle monitoring, evidence forms, response/challenge flow, and deadline-aware UX.
6. **Engineering proof.** Repository includes deployment/rollback runbooks, security limitations, frontend + backend source, historical and current lifecycle evidence. README reports 34 contract, 10 backend, 9 frontend tests and a 5/5 validator deployment on StudioNet.
7. **Specific disclosure of failure.** Crossbench documents that certain outer-consensus failures roll back an attempted failure counter, preventing a planned escape threshold from being reliable in production. Its successful later retry does not erase that issue.

Source paths: `README.md`, `ARCHITECTURE.md`, `contracts/crossbench_contract.py`, `docs/VERIFICATION_EVIDENCE.md`, `docs/ESCROW_RECOVERY.md`, `frontend/lib/genlayer.ts`. These were inspected directly from the original public repository. Reported production URL: https://crossbench-app.vercel.app/; published contract: `0x2352A0cBF175F1e69eBc8364A35301570378FF22` (as reported by its own README, not independently replayed in this audit).

## Design decisions that avoid cloning

| Dimension | Crossbench | Fitted |
|---|---|---|
| Primary action | Resolve a claimant/respondent dispute | Certify a proposed solution's suitability for a requirements version |
| Parties | Two named opponent wallets | Standard publisher, open applicants, permissionless evaluators |
| Monetary logic | Matching GEN stakes, escrow, settlement credits and withdrawals | No user escrow or application funds; only transaction fees |
| Workflow | Create → accept → submit evidence → preliminary verdict → challenge → finalize → withdraw | Publish criteria → pin version → submit sources → evaluate → compare certificates |
| AI responsibility | Attribute and weigh adversarial evidence to produce dispute verdict | Determine whether each independently sourced quote proves a specific requirement |
| Deterministic policy | Aggregate weighted evidence into settlement | Enforce mandatory gates and compute transparent weighted fit |
| Long-term data | Case resolution and audit | Requirements version graph and reusable suitability ledger |
| Frontend emphasis | Dispute management dashboard | Editorial standards registry, submission desk, certificate viewer and same-version comparison lab |

## Criteria to exceed Crossbench (not current achievement claims)

**GenLayer fit:** demonstrate through real 5-validator StudioNet tests that qualitative interpretations change an on-chain outcome; show `FIT`, `CONDITIONAL`, `UNFIT`, and `UNVERIFIED`, source errors, validator disagreement/rotation, and pinned-version behavior. No offchain authority may select outcomes.

**Contract quality:** pass a real GenVM lint run; measure consensus cost with four sources/six requirements; test pagination, version ownership, spoofed quotes, semantic contradiction, source status and mutable pages; review any runtime-dependent code in the actual GenVM (not just CPython).

**Engineering:** ship reproducible builds and continuous tests; log deploy SHA, contract source SHA, transaction IDs, receipts, selected validator counts and reconciliation; handle RPC-rate failures and no network clearly; confirm production frontend bundle uses the deployed contract and chain ID, with no simulation fallback.

**Frontend:** prove keyboard/tab/mobile usability, every form's user validation, live chain interactions, wallet reconnection, mixed finality, error states, and proof-level source navigation; remove runtime CDN dependency before production and retest bundled SDK.

**Evidence:** attach raw JSON outputs and public explorer URLs for each verified outcome; screenshots alone do not establish chain success.

## Honest current comparison

Fitted now has a verified StudioNet deployment, matching local/deployed source hash, successful GenVM checks, a bundled SDK build, separate offline and Direct Mode suites, all four finalized outcome certificates, standard revision/pinning, duplicate rejection, and retirement proof. It still cannot be said to exceed Crossbench's demonstrated end-to-end product engineering: Fitted's production frontend URL, wallet-signed browser flows, and broad adversarial acceptance remain unverified. Public frontend deployment is intentionally left to the user. Numerical comparative scores remain unknown because no judge rubric or independently verifiable score was available.
