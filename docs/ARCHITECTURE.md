# Architecture — Fitted 1.0

```text
 Browser wallet ─── signed GenLayer writes + transaction fees ───┐
                                                                  ▼
 Browser dashboard ◄─ finalized contract view reads ── StudioNet Intelligent Contract
                                                                  │
                     ┌────────────────────────────────────────────┘
                     ▼
           GenLayer Optimistic Democracy
           leader: fetch public sources → interpret requirements
           validators: independently fetch and interpret sources
           accept iff material findings and fetch availability agree
                     │
                     ▼
            deterministic classification, score, digest, certificate storage
```

## Authoritative state

`standards: TreeMap[str, str]`: JSON master standard records, with latest version pointer, owner, and active flag.

`standard_versions: TreeMap[str, str]`: immutable per-version snapshots keyed `FIT-1:1`, `FIT-1:2` and so on. Version snapshots contain name, purpose, exact requirements, and publication timestamp.

`applications: TreeMap[str, str]`: immutable applicant identity, name, description, URL list, pinned standard version and status. Only a successful evaluation adds a certificate and marks it `EVALUATED`.

`standard_ids`, `application_ids`: bounded page-accessible ordered indexes; total scan/row count not used to return unbounded arrays.

`evaluation_count`: total successful evaluations.

JSON blobs are used as deterministic, bounded, explicit serialization for cross-version stability and convenient APIs. The maximum size of requirement/source lists is capped. A later storage redesign should assess GenVM execution budgets on a fully populated registry.

## Important invariants

- Caller identity is taken from GenLayer's consensus-bound `sender_address`, never an application parameter.
- Standard IDs are monotonic contract-created identifiers. A stored version is never overwritten.
- Application's `standard_version` is set only once, at submission time.
- Candidate evidence URLs are fixed after submission; no mutable offchain score endpoint can modify them.
- `evaluate_candidate` is permissionless but accepts only a pending application.
- Evaluator failure does not change contract storage or trap a custody balance.
- Independent validators fetch and assess from the raw URLs, not from a requester's summary.
- `validate_judgment` checks schema, duplicate/missing IDs, enum domains, cited source index and verbatim quote grounding.
- Validator agreement requires every material per-rule decision, source-quality level, and source availability to match. Exact natural-language explanations and precise quoted substrings may differ.
- Outcome and weighted score are deterministic and never accepted from AI output.
- The certificate captures the full per-requirement evidence record and digests the pinned standard, URLs and finding set.

## Trust boundary

The browser is UX only: renders formatted contract state, submits an unsigned intent to the connected wallet for signing, estimates fees, waits for finalization, and refreshes reads. Users must verify the contract address and connected chain. There is no backend signer, delegated admin key, permissioned moderator, or settlement role.

Public web content is untrusted. Prompt injection strings are framed as data, truncated and forbidden from acting as instructions in the adjudication prompt. Validators re-evaluate. Nevertheless AI prompt-injection and deception cannot be eliminated by wording alone; critical requirements should prefer independently corroborated source evidence and live red-team testing.

## Source processing

URLs: HTTPS only, no credentials/fragments, restricted port, reject non-global IPs and local/internal DNS suffixes; reject popular shortener/paste hosts and canonical duplicates within one submission. `gl.nondet.web.get` independently retrieves each URL. HTTP errors and empty content become `UNAVAILABLE`. Script/style HTML is removed and whitespace normalized; each source is bounded at 12,000 raw bytes then 10,000 normalized characters. SHA-256 fingerprints are audit metadata, not exact-match equivalence criteria. Literal quote verification is based on the local normalized source excerpt; it does not infer facts beyond the retrieved text.

## Practical scaling

Current design optimizes independent auditable decisions over high-frequency matching. Evaluations can be expensive (up to 4 source fetches and AI inference on each validator). UI must avoid automatic mass evaluation or unbounded polling. Future versions can add a read-only indexer with source-aware TTLs, transaction replay resistance, and daily RPC budgets if necessary without giving it authority over contract writes.
