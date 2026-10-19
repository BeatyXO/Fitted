import json
import pytest
from conftest import UserError

def test_standard_is_wallet_owned_and_versioned(standard, requirements):
    mod, c, gl, sid = standard
    old = c.get_standard_version(sid, 1)
    gl.message.sender_address = "0x" + "b" * 40
    with pytest.raises(UserError, match="only standard owner"):
        c.revise_standard(sid, "Unapproved owner mutation is forbidden", json.dumps(requirements))
    gl.message.sender_address = "0x" + "a" * 40
    new_rules = [{"id": "privacy", "text": "Uses encrypted storage for sensitive information", "mandatory": True, "weight": 5}]
    assert c.revise_standard(sid, "Updated privacy-first requirements for evaluation", json.dumps(new_rules)) == "FIT-1:2"
    assert c.get_standard_version(sid, 1) == old
    assert c.get_standard_version(sid, 2)["requirements"] == new_rules

def test_submission_pins_frozen_requirement_version(candidate, requirements):
    mod, c, gl, sid, aid = candidate
    c.revise_standard(sid, "Modern requirements for a revised evaluation standard", json.dumps(requirements))
    assert c.get_standard(sid)["current_version"] == 2
    assert c.get_application(aid)["standard_version"] == 1
    assert c.get_application(aid)["status"] == "PENDING"

def test_real_evaluation_path_invokes_independent_model_and_fetch(candidate, positive_findings):
    mod, c, gl, sid, aid = candidate
    gl.findings = positive_findings
    assert c.evaluate_candidate(aid) == "FIT"
    assert gl.fetches == 2 and gl.model_calls == 2  # leader + validator
    cert = c.get_application(aid)["certificate"]
    assert cert["score"] == 100 and cert["version"] == 1
    assert len(cert["digest"]) == 64 and len(cert["source_hashes"][0]) == 64
    assert c.get_stats()["evaluations"] == 1
    with pytest.raises(UserError, match="already evaluated"):
        c.evaluate_candidate(aid)

def test_unknown_mandatory_is_unverified(candidate, positive_findings):
    mod, c, gl, sid, aid = candidate
    gl.findings = positive_findings
    gl.findings[0] = {"id": "offline", "decision": "UNKNOWN", "quality": "UNVERIFIED", "source_index": -1, "quote": "", "reason": "No reliable evidence exists."}
    assert c.evaluate_candidate(aid) == "UNVERIFIED"

def test_hard_violation_is_unfit_even_when_score_high(harness):
    mod, c, gl = harness
    requirements = [{"id": "hard", "text": "Critical condition must be satisfied by evidence", "mandatory": True, "weight": 1},
                    {"id": "optional", "text": "Optional condition is helpful for workflow efficiency", "mandatory": False, "weight": 5}]
    result = mod.calculate_fit(requirements, [{"decision": "NOT_SATISFIED"}, {"decision": "SATISFIED"}])
    assert result["outcome"] == "UNFIT" and result["score"] == 83

def test_conditional_outcome(candidate, positive_findings):
    mod, c, gl, sid, aid = candidate
    gl.findings = positive_findings
    gl.findings[1] = {"id": "csv", "decision": "UNKNOWN", "quality": "UNVERIFIED", "source_index": -1, "quote": "", "reason": "CSV is not established."}
    assert c.evaluate_candidate(aid) == "CONDITIONAL"

def test_model_hallucinated_quotes_are_rejected(candidate, positive_findings):
    mod, c, gl, sid, aid = candidate
    gl.findings = positive_findings
    gl.findings[0]["quote"] = "This quotation is not present in retrieved evidence"
    with pytest.raises(UserError, match="quoted material not found"):
        c.evaluate_candidate(aid)
    assert c.get_application(aid)["status"] == "PENDING"

def test_validator_disagreement_keeps_pending(candidate, positive_findings):
    mod, c, gl, sid, aid = candidate
    gl.findings = positive_findings
    gl.disagree = True
    with pytest.raises(UserError, match="NO_CONSENSUS"):
        c.evaluate_candidate(aid)
    assert c.get_application(aid)["status"] == "PENDING"

def test_unavailable_page_cannot_prove_fit(candidate, positive_findings):
    mod, c, gl, sid, aid = candidate
    gl.pages.clear()
    gl.findings = positive_findings
    with pytest.raises(UserError, match="quoted material not found"):
        c.evaluate_candidate(aid)

def test_rejects_ssrf_and_weak_url_forms(harness):
    mod, c, gl = harness
    for url in ["http://docs.example.com/abc", "https://127.0.0.1/page", "https://localhost/page", "https://x.local/page", "https://bit.ly/abc", "https://user:pass@example.com/page", "https://example.com:8080/page", "https://example.com/page#mutable"]:
        with pytest.raises(UserError):
            mod.safe_url(url)

def test_reject_duplicate_sources(harness):
    mod, c, gl = harness
    with pytest.raises(UserError, match="duplicate"):
        mod.parse_sources(json.dumps(["https://example.com/path", "https://EXAMPLE.com/path/"]))

def test_fully_bounded_requirement_schema(harness):
    mod, c, gl = harness
    invalid = [[{"id":"ok", "text":"long descriptive requirement", "mandatory": True, "weight": 0}],
               [{"id":"duplicate", "text":"long descriptive requirement", "mandatory": True, "weight": 1},
                {"id":"duplicate", "text":"another long requirement text", "mandatory": True, "weight": 2}],
               [{"id":"only", "text":"long descriptive requirement", "mandatory": False, "weight": 1}]]
    for item in invalid:
        with pytest.raises(UserError):
            mod.parse_requirements(json.dumps(item))

def test_retired_standard_disallows_new_candidates(standard):
    mod, c, gl, sid = standard
    c.retire_standard(sid)
    with pytest.raises(UserError, match="retired"):
        c.submit_candidate(sid, "Name", "A meaningful description of proposed capabilities", json.dumps(["https://example.com/a"]))

def test_pagination_bounded(candidate):
    mod, c, gl, sid, aid = candidate
    assert c.list_standards(0, 24)["total"] == 1
    assert c.list_applications(0, 24)["items"][0]["id"] == aid
    with pytest.raises(UserError):
        c.list_applications(0, 25)

def test_cannot_conflate_unknown_and_negative(harness):
    mod, _, _ = harness
    criteria = [{"id":"req", "text":"long descriptive requirement", "mandatory":True, "weight":5}]
    assert mod.calculate_fit(criteria, [{"decision":"UNKNOWN"}])["outcome"] == "UNVERIFIED"
    assert mod.calculate_fit(criteria, [{"decision":"NOT_SATISFIED"}])["outcome"] == "UNFIT"

def test_validator_compares_conclusions_not_prose(harness):
    mod, _, _ = harness
    leader = [{"id": "one", "decision": "SATISFIED", "quality": "DIRECT", "reason": "Leader"}]
    other = [{"id": "one", "decision": "SATISFIED", "quality": "DIRECT", "reason": "Validator"}]
    assert mod.judgments_agree(leader, other)
    other[0]["quality"] = "SECONDARY"
    assert not mod.judgments_agree(leader, other)
