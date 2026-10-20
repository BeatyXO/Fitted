"""Contract-boundary regression cases run through the GenLayer interface stand-in."""
import json
import pytest
from conftest import UserError

@pytest.mark.parametrize("url", [
    "http://example.com/x", "https://localhost/path", "https://127.0.0.1/path",
    "https://10.0.0.1/path", "https://192.168.1.2/path", "https://169.254.169.254/path",
    "https://bit.ly/abc", "https://foo.tinyurl.com/abc", "https://pastebin.com/abc",
    "https://user:secret@example.com/file", "https://docs.example.com:8443/docs",
    "https://docs.example.com/report#fragment", "https://app.local/report", "https://a.internal/report",
])
def test_invalid_source_forms(url, harness):
    mod, _, _ = harness
    with pytest.raises(UserError):
        mod.safe_url(url)

@pytest.mark.parametrize("bad", [
    [], [{}], ["not a dict"],
    [{"id": "Upper", "text": "A substantial verifiable source-backed requirement", "mandatory": True, "weight": 2}],
    [{"id": "r1", "text": "too short", "mandatory": True, "weight": 2}],
    [{"id": "r1", "text": "A substantial verifiable source-backed requirement", "mandatory": "true", "weight": 2}],
    [{"id": "r1", "text": "A substantial verifiable source-backed requirement", "mandatory": True, "weight": True}],
    [{"id": "r1", "text": "A substantial verifiable source-backed requirement", "mandatory": True, "weight": 6}],
    [{"id": "r1", "text": "A substantial verifiable source-backed requirement", "mandatory": False, "weight": 1}],
    [{"id": "r1", "text": "A substantial verifiable source-backed requirement", "mandatory": True, "weight": 1}] * 2,
    [{"id": "r" + str(i), "text": "A substantial verifiable source-backed requirement", "mandatory": True, "weight": 1} for i in range(7)],
])
def test_invalid_requirements(bad,harness):
    mod, _, _ = harness
    with pytest.raises(UserError):
        mod.parse_requirements(json.dumps(bad))

@pytest.mark.parametrize("raw", [
    "not json", "[]", json.dumps(["https://example.com/x"]*2),
    json.dumps(["https://example.com/"+str(i) for i in range(5)]),
    json.dumps([42]), json.dumps(["https://example.com:5000/x"]),
])
def test_invalid_source_lists(raw,harness):
    mod, _, _ = harness
    with pytest.raises(UserError):
        mod.parse_sources(raw)

@pytest.mark.parametrize("decisions,expected", [
    (["SATISFIED","SATISFIED"], "FIT"),
    (["SATISFIED","UNKNOWN"], "CONDITIONAL"),
    (["SATISFIED","NOT_SATISFIED"], "CONDITIONAL"),
    (["UNKNOWN","SATISFIED"], "UNVERIFIED"),
    (["UNKNOWN","UNKNOWN"], "UNVERIFIED"),
    (["NOT_SATISFIED","SATISFIED"], "UNFIT"),
    (["NOT_SATISFIED","UNKNOWN"], "UNFIT"),
])
def test_deterministic_decision_priority(decisions,expected, harness,requirements):
    mod,_,_=harness
    assert mod.calculate_fit(requirements,[{"decision":x} for x in decisions])["outcome"]==expected

@pytest.mark.parametrize("tamper", [
    lambda rows: rows[:1],
    lambda rows: rows+[dict(rows[0])],
    lambda rows: [dict(rows[0],id="invalid"),rows[1]],
    lambda rows: [dict(rows[0],decision="SURE"),rows[1]],
    lambda rows: [dict(rows[0],quality="SPOOFED"),rows[1]],
    lambda rows: [dict(rows[0],source_index=99),rows[1]],
    lambda rows: [dict(rows[0],quote="fabricated offchain claim"),rows[1]],
    lambda rows: [dict(rows[0],reason=""),rows[1]],
])
def test_bad_model_findings_rejected(candidate,positive_findings,tamper):
    mod,c,gl,sid,aid=candidate
    gl.findings=tamper(positive_findings)
    with pytest.raises(UserError):
        c.evaluate_candidate(aid)
    assert c.get_application(aid)["certificate"] is None

def test_retires_only_by_owner(standard):
    mod,c,gl,sid=standard
    gl.message.sender_address='0x'+'b'*40
    with pytest.raises(UserError,match="only standard owner"):
        c.retire_standard(sid)
    assert c.get_standard(sid)["active"] is True

def test_versions_are_monotonic_and_applications_capture_versions(standard):
    mod,c,gl,sid=standard
    previous=[]
    for version in range(1,5):
        aid=c.submit_candidate(sid,f"Candidate {version}","A genuinely descriptive candidate context",json.dumps([f"https://example.com/{version}"]))
        previous.append(c.get_application(aid)["standard_version"])
        if version<4:
            c.revise_standard(sid,"Substantive updated standard criteria for applicants",json.dumps([{"id": "capability", "text": "The candidate provides a publicly documented requested capability", "mandatory": True, "weight": 3}]))
    assert previous==[1,2,3,4]
    assert c.list_applications(0,24)["total"]==4
    assert c.get_standard_version(sid,1)["requirements"][0]["id"]=="offline"

def test_certificate_is_bound_to_source_snapshot(candidate,positive_findings):
    mod,c,gl,sid,aid=candidate
    gl.findings=positive_findings
    c.evaluate_candidate(aid)
    cert=c.get_application(aid)["certificate"]
    assert cert["id"]==aid and cert["standard_id"]==sid
    assert cert["source_status"]==["FETCHED"]
    assert cert["satisfied"]==2 and cert["unknown"]==0 and cert["failed"]==0
    # No writable entry point to revise the evaluated certificate.
    assert not hasattr(c,"alter_certificate")

def test_revisions_do_not_rewrite_evaluated_certificates(candidate,positive_findings):
    mod,c,gl,sid,aid=candidate
    gl.findings=positive_findings
    c.evaluate_candidate(aid)
    original=c.get_application(aid)["certificate"].copy()
    c.revise_standard(sid,"Latest revised standard supersedes prior criteria",json.dumps([{"id":"new_rule","text":"A new independently provable business requirement", "mandatory":True,"weight":5}]))
    assert c.get_application(aid)["certificate"]==original

def test_no_content_produces_unverified_not_false_fit(candidate):
    mod,c,gl,sid,aid=candidate
    gl.pages.clear()
    gl.findings=[{"id": "offline", "decision": "UNKNOWN", "quality": "UNVERIFIED", "source_index": -1, "quote": "", "reason": "Source document not retrievable."},
                 {"id": "csv", "decision": "UNKNOWN", "quality": "UNVERIFIED", "source_index": -1, "quote": "", "reason": "No evidence could be inspected."}]
    assert c.evaluate_candidate(aid)=="UNVERIFIED"
    cert=c.get_application(aid)["certificate"]
    assert cert["source_status"]==["UNAVAILABLE"]
    assert cert["source_hashes"]==[""]


def test_http_404_page_not_usable_for_proof(candidate):
    from types import SimpleNamespace
    mod,c,gl,sid,aid=candidate
    gl.nondet.web.get=lambda _: SimpleNamespace(status_code=404,body=b"exports offline reports without network access")
    gl.findings=[{"id":"offline", "decision":"UNKNOWN", "quality":"UNVERIFIED", "source_index":-1,"quote":"","reason":"The source returned HTTP 404."},
                 {"id":"csv", "decision":"UNKNOWN", "quality":"UNVERIFIED", "source_index":-1,"quote":"","reason":"The source returned HTTP 404."}]
    assert c.evaluate_candidate(aid)=="UNVERIFIED"
    assert c.get_application(aid)["certificate"]["source_status"]==["UNAVAILABLE"]


def test_non_utf8_bytes_dont_crash_text_normalization(harness):
    mod,c,gl=harness
    output=mod._normalized_excerpt(b"<style>secret</style>Hello \xff world")
    assert 'secret' not in output and 'Hello' in output

def test_consensus_result_revalidates_grounding_and_source_fingerprints(candidate,positive_findings):
    import hashlib
    mod,c,gl,sid,aid=candidate
    url=c.get_application(aid)["sources"][0]
    text=mod._normalized_excerpt(gl.pages[url].encode("utf-8"))
    fp=hashlib.sha256(text.encode("utf-8")).hexdigest()
    requirements=c.get_standard_version(sid,1)["requirements"]
    result={"findings":positive_findings,"fingerprints":[fp],
            "source_status":["FETCHED"],"evidence":[text]}
    assert mod.validate_assessment_result(result,requirements,1)["fingerprints"]==[fp]

    for changed in (
        dict(result,fingerprints=["bad"]),
        dict(result,evidence=[text+" changed"]),
        dict(result,source_status=["UNAVAILABLE"]),
        dict(result,findings=[dict(positive_findings[0],quote="fabricated evidence quote"),positive_findings[1]]),
        dict(result,findings=[dict(positive_findings[0],source_index=7),positive_findings[1]]),
        dict(result,findings=[dict(positive_findings[0],quality="UNVERIFIED"),positive_findings[1]]),
    ):
        with pytest.raises(UserError):
            mod.validate_assessment_result(changed,requirements,1)
