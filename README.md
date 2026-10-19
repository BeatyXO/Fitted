# Fitted — evidence-backed proof of suitability, on GenLayer

**Fitted is not a dispute court.** It is a versioned suitability protocol for evaluating products, services, agents, and technical solutions against explicit human requirements. Applicants publish documentary evidence. Every GenLayer validator independently fetches the same public evidence, interprets each requirement, and agrees on material decision fields. Contract code—not the LLM—computes the final certificate.

**Status:** deployed to GenLayer StudioNet (chain 61999). GenVM lint, schema validation, typecheck, Direct Mode checks, and finalized proof for all four certificate outcomes and the core standard lifecycle are recorded in [`deployments/studionet.json`](deployments/studionet.json) and [`deployments/lifecycle_transactions.json`](deployments/lifecycle_transactions.json). The frontend is built locally and ready for user-managed Vercel deployment. See [`docs/VERIFICATION.md`](docs/VERIFICATION.md) for categorized evidence and remaining limits.

## Product differentiation

Crossbench (reference: https://github.com/zoefunds/Crossbench) is a two-party, stake-backed dispute resolution protocol. Fitted is a many-to-one requirement-to-solution suitability registry without disputants, financial escrow, winner selection, or backend adjudication. Its core entities are **versioned standards → candidate applications → requirement-level consensus findings → immutable fit certificates**. No Crossbench source, styles, or architectural artifacts were copied.

| Principle | What Fitted implements |
|---|---|
| True GenLayer fit | External public HTTPS fetches + model judgments + independent comparative validator rerun |
| Frozen evaluation target | Every submission pins the current version; owner revisions never rewrite that version |
| Material consensus | Validators independently derive `decision`, `quality`, and source availability; prose differences tolerated |
| Grounding | Non-UNKNOWN findings require 10–160 characters copied literally from the retrieved excerpt |
| Least authority | Any account may evaluate; only standard owner revises/retires; no operator key or hosted adjudicator |
| Deterministic conclusions | Strict mandatory-gate priority and weighted score in deterministic contract code |
| Liveness preservation | An unfinalized or failed evaluation keeps `PENDING`; no user funds are escrowed |
| Visible limitations | Source failures, unknown findings and unverifiable requirements are surfaced rather than turned into success |

## Files

- `contracts/fitted_contract.py` — standalone, self-contained GenLayer Intelligent Contract
- `frontend/index.html`, `frontend/styles.css`, `frontend/app.js` — responsive, wallet-connected dashboard
- `tests/` — 69 passing offline Python tests using a **clearly labeled GenLayer interface stand-in**, NOT real GenVM
- `docs/ARCHITECTURE.md` — trust boundaries and data model
- `docs/CONTRACT_SPEC.md` — precise method interface and policy calculations
- `docs/SECURITY.md` — attack surface, threat model, and limitations
- `docs/DEPLOYMENT.md` — real StudioNet deployment and evidence checklist
- `docs/BENCHMARK.md` — specific Crossbench strengths, gaps, and differential plan
- `docs/VERIFICATION.md` — what was and was not verified

## Quick start

**Offline tests (no node, chain, or wallet required):**

```sh
python -m pip install pytest
python -m pytest tests/ --ignore=tests/test_direct.py -q
python -m py_compile contracts/fitted_contract.py
node --check frontend/app.js
```

**Real GenLayer Direct Mode (mocked web/model boundaries; not StudioNet consensus):**

```sh
python -m pytest tests/test_direct.py -q
```

**Frontend development and production build:**

```sh
npm --prefix frontend ci
npm --prefix frontend test
npm --prefix frontend run build
npm --prefix frontend run dev
```

The Vite production build bundles the exact-locked `genlayer-js@1.1.8` dependency locally. No runtime SDK CDN is used. No test transactions are preloaded or simulated. An unconfigured deployment shows an intentionally empty read-only registry, not demo data.

**Deploy and verify:** follow [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md). The contract constructor has no parameters. After deployment, enter the real address in the dashboard. The URL parameter `?contract=0x...` is supported for sharing a read-only registry view.

## Workflow

1. A wallet publishes a standard with **1–6 requirements**, at least one mandatory, each with a unique ID and weight 1–5.
2. A standard owner may publish new immutable versions or retire the standard. Old versions and certificates remain readable.
3. Anyone submits a candidate (name, description, **1–4 distinct public HTTPS sources**). The contract freezes the standard version in the submission record.
4. Anyone calls `evaluate_candidate`. Validators independently fetch URLs, classify `SATISFIED` / `NOT_SATISFIED` / `UNKNOWN`, classify provenance, and cite literal text.
5. Validators must agree on material classifications and source availability. The contract deterministically returns `FIT`, `CONDITIONAL`, `UNFIT`, or `UNVERIFIED` and stores source fingerprints and a certificate digest.
6. The frontend waits for an actual finalized successful transaction before refreshing final chain state.

### Outcome priority

1. Any **mandatory NOT_SATISFIED** → `UNFIT`.
2. Otherwise any **mandatory UNKNOWN** → `UNVERIFIED`.
3. Otherwise all requirements `SATISFIED` → `FIT`.
4. Otherwise → `CONDITIONAL` (mandatory conditions proven but optional gaps remain).

The weighted score is a separate descriptive value: `floor(100 × satisfied requirement weights / all weights)`. No numeric score can overrule the mandatory gates. A `UNFIT` candidate may therefore have a high numerical score; the mandatory-rule failure is still decisive.

## Design limitations

- A literal quote only proves that text appeared on the fetched source; it is **not cryptographic proof that the source's claims are truthful**. Validator classification includes provenance but cannot guarantee identity authenticity or real-world performance.
- HTTP pages can change after publication. Certificates include a fetched-content SHA-256 fingerprint and issuance time, but **Fitted v1 does not automatically expire, revoke, or refresh previous certificates**. Submit a new candidate against the latest standard for a new assessment.
- IP literals, private and local hosts, non-standard ports, URL fragments, and common redirect/paste hosts are rejected. DNS rebinding and redirect-target IP enforcement still depend on GenLayer's validator networking sandbox.
- Consensus can stall on changing or unreachable pages. A failed transaction does not consume application state, but the system has no guaranteed deadline, refund, or bounded recovery under persistent external failure.
- The deployed source is self-contained and **does not own, transfer, lock, or redistribute GEN**. Users still pay chain transaction fees.
- `get_stats` and registries are contract state, not an offchain analytical cache. Large registries should be accessed with bounded pages, not exhaustive background polling.

## Network

GenLayer **StudioNet**: chain ID `61999`, RPC `https://studio.genlayer.com/api`, explorer `https://explorer-studio.genlayer.com`, currency `GEN` (testnet). The separate studio development preview chain ID is 61997; do not mix the two.

## Inspiration and attribution

The project benchmarked the publicly available Crossbench source and GenLayer's official docs to identify qualities of strong submissions. Code, naming, UI, domain model, state transitions, and business behavior are original to Fitted. See [`docs/BENCHMARK.md`](docs/BENCHMARK.md).

## v1.1 wallet and UI hardening

See docs/FRONTEND_WALLET.md. Local suite: 69 Python offline boundary tests and 7 Direct Mode tests; 10 Node wallet tests. The SDK is pinned and bundled locally. Deployment and read-only registry reads finalized on StudioNet; live lifecycle writes and production hosting remain outstanding.

