# Security model and known limitations

| Concern | Control | Residual issue |
|---|---|---|
| Forged standard ownership | `gl.message.sender_address` controls revise/retire | Wallet compromise remains possible |
| Future standards rewriting earlier submissions | Immutable version snapshots and pinned application version | No migration/revocation of old certificates |
| Score fabrication | Deterministic code calculates outcome and score | AI remains responsible for qualitative per-rule classification |
| Hallucinated quotes | Quote must be a literal 10–160-character substring of retrieved normalized text | A real quote can still be misleading or context-free |
| Fake evidence source | HTTPS/public-source restrictions, citation/provenance grades | A public web page can be fraudulent, claim ownership falsely, or change |
| Link alias / duplicated self-evidence | Canonical URLs deduplicated within submission | Two unrelated URLs could repeat identical content; no cross-URL semantic dedupe in v1 |
| SSRF | No private IP literals, localhost/local suffixes, credentials, nonstandard ports, fragments or major shorteners | DNS rebinding and redirects require network sandbox policy |
| Prompt injection | Bounded quoted evidence supplied as data, independent validator re-evaluation | Cannot prove all malicious instructions are neutralized |
| Leader manipulates fit | Validator independently judges and compares complete material tuple, including evidence source fingerprints; accepted judgments are fully revalidated after the nondeterministic boundary | Validator models could share biases/errors and still agree |
| Divergent model decisions | Exact decision/quality agreement, no score tolerance that could flip mandatory gate | Higher consensus failure rate on ambiguous requirements |
| Unavailable sources | Explicit UNAVAILABLE and unknown, no success inference from 404/errors | Models can still be wrong about source reliability or relevance |
| Consensus rollback | No escrow, pending submission remains retryable | No guaranteed consensus or timed completion under chain failure |
| Offchain authority escalation | All writes signed directly by user's wallet; backend-free UI | Compromised CDN/website may induce misleading wallet prompts |
| Silent front-end success | Waits for SDK `TransactionStatus.FINALIZED`, requires `ExecutionResult.FINISHED_WITH_RETURN`, then refreshes | Production signed-write flow and wallet-provider interoperability remain unverified; local UI smoke uses a test-only provider double |
| Lost pending receipt | Stores only the public tx hash, contract, account, method and local submission time; recovery polls the original hash and never resubmits | Browser local storage can be cleared; users can recover the tx independently from the public explorer |
| Denial of service | Max 6 requirements, 4 sources, 24-row read pages; no unbounded contract list read | Onchain registry storage and repeated failed evaluations still cost user/network resources |

## Threat assumptions

GenLayer validators and their sandbox enforce applicable RPC, DNS and networking boundaries. This contract does not control redirected target IPs or TLS certificate inspection performed by the runtime. A certificate reports that independent validators agreed on material classifications against evidence observed at the time; it does not assert that any underlying commercial product works as promised.

## Remaining work before a high-stakes launch

- Run `genvm-lint`, Direct Mode and StudioNet execution with real model providers and more than one validator.
- Stress prompt injection, contradictory source content, HTML entities, source mutability, redirect chains, long static pages, and low-trust source provenance.
- Test fee estimates, validator rotation, pending or reverted transaction accounting, and wallet reconnect paths on the exact target SDK.
- Consider content pinning/archive and a time-bound certificate lifecycle with explicit revocation or recheck mechanics.
- Verify the live Vercel URL after each frontend release. One wallet-signed `create_standard` production write and registry readback were verified on 2026-10-20. The old deployed bundle misreported its successful receipt; the local parser fix must be deployed and verified. Candidate/evaluation writes, disconnect/reconnect, account changes, and production pending recovery remain unverified.
