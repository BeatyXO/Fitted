# Contract interface and exact semantics

**Contract:** `contracts/fitted_contract.py`, class `Fitted`, no constructor args, version `1.0.0`.

| Method | Mode | Caller | Purpose |
|---|---|---|---|
| `create_standard(name, purpose, requirements_json)` | write | any wallet | Create first frozen requirement snapshot; return standard ID |
| `revise_standard(standard_id, purpose, requirements_json)` | write | owner only | Publish next frozen version |
| `retire_standard(standard_id)` | write | owner only | Stop new submissions; keep history |
| `submit_candidate(standard_id, name, description, sources_json)` | write | any wallet | Bind evidence and latest standard version |
| `evaluate_candidate(application_id)` | write, nondeterministic | permissionless | Independent source retrieval + GenLayer AI consensus + deterministic certificate |
| `get_standard(standard_id)` | view | any | Read latest pointer and owner |
| `get_standard_version(standard_id, version)` | view | any | Inspect immutable requirement snapshot |
| `get_application(application_id)` | view | any | Read applicant, sources, status and certificate |
| `list_standards(offset, count)` | view | any | Paginated master standards, `count` 1–24 |
| `list_applications(offset, count)` | view | any | Paginated submission list, `count` 1–24 |
| `get_stats()` | view | any | Public authoritative totals |

**Requirements JSON input:** array of 1–6 objects `{ "id": "offline_export", "text": "Exports reports without an internet connection", "mandatory": true, "weight": 3 }`. IDs are distinct lowercase ASCII identifiers (1–20 chars). Text 12–350 characters. At least one mandatory criterion, weight integer 1–5, boolean mandatory exact.

**Source JSON input:** array of 1–4 distinct HTTPS URLs, each ≤500 characters with a public DNS name, standard port, no credentials, no fragment or private IP literal. URL canonization removes hostname case differences and trailing slash variants.

**Findings JSON output:** an object `{"findings":[{"id":"offline_export","decision":"SATISFIED","quality":"DIRECT","source_index":0,"quote":"Exact substring from retrieved content","reason":"Concise explanation"}]}`. Decision `SATISFIED / NOT_SATISFIED / UNKNOWN`. Provenance `DIRECT / SECONDARY / UNVERIFIED`. Decisive findings require a verified text excerpt containing the quote; unknown findings must cite `-1`, empty quote and `UNVERIFIED` quality. The validator independently computes its own findings; it does not merely check whether the leader emitted the right schema.

**Consensus equality:** comparison of the entire ordered list of `(id, decision, quality)` and the fetched/unavailable source-status list. Source hashes, narratives and quote snippets are *not* exact-consensus fields because rendered web content may vary harmlessly. This prioritizes safety of material conclusions over maximum liveness.

**Outcome:** mandatory NOT_SATISFIED → UNFIT, otherwise mandatory UNKNOWN → UNVERIFIED, otherwise all SATISFIED → FIT, else CONDITIONAL. Score is the integer percentage of weights satisfied, and does not override mandatory failures.

**Certificate:** application ID, standard ID and version, outcome, score, counts of satisfied/failed/unknown, requirement findings, source SHA-256 text fingerprints, fetch status, immutable issuance time, and digest `sha256(canonical_json(snapshot, source_urls, findings))`. The digest is a reproducible identifier for the recorded inputs/outcomes, not a substitute for transaction inclusion proof.
