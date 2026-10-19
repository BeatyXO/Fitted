"""Real GenLayer Direct Mode checks using genlayer-test's direct_vm runtime.

Direct Mode exercises GenLayer storage, call context, serialization and web/LLM
cheatcodes in-process. It does not model StudioNet multi-validator finality.
"""
import json
import os
import tempfile
from pathlib import Path

import pytest
from gltest.direct import loader as direct_loader


CONTRACT = str(Path(__file__).resolve().parents[1] / "contracts" / "fitted_contract.py")
SOURCE = "https://docs.example.org/product"
PAGE = "The product exports reports without network access."


def rules(optional=False):
    result = [{"id": "offline", "text": "Exports reports without network access",
               "mandatory": True, "weight": 5}]
    if optional:
        result.append({"id": "csv", "text": "Offers a CSV export", "mandatory": False, "weight": 2})
    return result


def finding(decision="SATISFIED", rid="offline", quality="DIRECT", index=0,
            quote="exports reports without network access"):
    return {"id": rid, "decision": decision, "quality": quality,
            "source_index": index, "quote": quote,
            "reason": "The retrieved source directly establishes this finding."}


def install_evidence(direct_vm, response, findings=None):
    direct_vm.mock_web(r"docs\.example\.org/product", response)
    direct_vm.mock_llm(r"You are checking FIT", json.dumps({"findings": findings or [finding()]}))


@pytest.fixture
def windows_direct_stdin(direct_vm, monkeypatch):
    """Work around genlayer-test 0.29.2 unlinking its still-open stdin tempfile on Windows."""
    original_load = direct_loader._load_module

    def inject(vm):
        from genlayer.py import calldata
        from genlayer.py.types import Address

        sender = Address(vm.sender) if isinstance(vm.sender, bytes) else vm.sender
        contract_address = Address(vm._contract_address) if isinstance(vm._contract_address, bytes) else vm._contract_address
        origin = vm.origin
        origin_address = Address(origin) if isinstance(origin, bytes) else origin
        payload = calldata.encode({
            "contract_address": contract_address, "sender_address": sender,
            "origin_address": origin_address, "stack": [], "value": vm._value,
            "datetime": vm._datetime, "is_init": False, "chain_id": vm._chain_id,
            "entry_kind": 0, "entry_data": b"", "entry_stage_data": None,
        })
        fd, path = tempfile.mkstemp()
        os.write(fd, payload)
        os.lseek(fd, 0, os.SEEK_SET)
        vm._original_stdin_fd = os.dup(0)
        os.dup2(fd, 0)
        os.close(fd)
        vm._direct_message_path = path

    def load_module(path):
        try:
            return original_load(path)
        finally:
            os.dup2(direct_vm._original_stdin_fd, 0)
            os.close(direct_vm._original_stdin_fd)
            os.unlink(direct_vm._direct_message_path)

    monkeypatch.setattr(direct_loader, "_inject_message_to_fd0", inject)
    monkeypatch.setattr(direct_loader, "_load_module", load_module)


def publish(direct_vm, contract, criteria=None):
    return contract.create_standard("Direct Mode standard",
                                    "Assess a product against documented requirements",
                                    json.dumps(criteria or rules()))


@pytest.mark.direct
def test_direct_storage_authorization_revision_and_version_pin(direct_vm, direct_deploy, direct_alice, direct_bob, windows_direct_stdin):
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.16")
    direct_vm.sender = direct_alice
    sid = publish(direct_vm, contract)
    aid = contract.submit_candidate(sid, "Candidate", "A documented product candidate",
                                    json.dumps([SOURCE]))
    assert contract.get_application(aid)["standard_version"] == 1

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("only standard owner"):
        contract.revise_standard(sid, "Unauthorized revision of the standard requirements", json.dumps(rules()))
    direct_vm.sender = direct_alice
    assert contract.revise_standard(sid, "Revised standard requirements for the next version", json.dumps(rules())) == sid + ":2"
    assert contract.get_standard_version(sid, 1)["requirements"] == rules()
    assert contract.get_standard_version(sid, 2)["requirements"] == rules()
    assert contract.get_application(aid)["standard_version"] == 1


@pytest.mark.direct
@pytest.mark.parametrize(("decision", "expected"), [
    ("SATISFIED", "FIT"), ("NOT_SATISFIED", "UNFIT"), ("UNKNOWN", "UNVERIFIED")])
def test_direct_all_mandatory_outcomes(direct_vm, direct_deploy, decision, expected, windows_direct_stdin):
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.16")
    sid = publish(direct_vm, contract)
    aid = contract.submit_candidate(sid, "Candidate", "A documented product candidate", json.dumps([SOURCE]))
    if decision == "UNKNOWN":
        install_evidence(direct_vm, {"status": 503, "body": ""}, [
            finding("UNKNOWN", quality="UNVERIFIED", index=-1, quote="")])
    else:
        page = PAGE if decision == "SATISFIED" else "The product does not export reports without network access."
        quote = "exports reports without network access" if decision == "SATISFIED" else "does not export reports without network access"
        install_evidence(direct_vm, {"status": 200, "body": page}, [finding(decision, quote=quote)])
    assert contract.evaluate_candidate(aid) == expected
    certificate = contract.get_application(aid)["certificate"]
    assert certificate["outcome"] == expected
    assert certificate["source_status"] == (["UNAVAILABLE"] if decision == "UNKNOWN" else ["FETCHED"])


@pytest.mark.direct
def test_direct_conditional_quote_grounding_and_replay(direct_vm, direct_deploy, windows_direct_stdin):
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.16")
    sid = publish(direct_vm, contract, rules(optional=True))
    aid = contract.submit_candidate(sid, "Candidate", "A documented product candidate", json.dumps([SOURCE]))
    direct_vm.mock_web(r"docs\.example\.org/product", {"status": 200, "body": PAGE})
    direct_vm.mock_llm(r"You are checking FIT", json.dumps({"findings": [
        finding(), finding("UNKNOWN", "csv", "UNVERIFIED", -1, "")]}))
    assert contract.evaluate_candidate(aid) == "CONDITIONAL"
    with direct_vm.expect_revert("candidate already evaluated"):
        contract.evaluate_candidate(aid)

    bad_id = contract.submit_candidate(sid, "Spoof candidate", "A candidate with a false quote", json.dumps([SOURCE]))
    direct_vm.clear_mocks()
    direct_vm.mock_web(r"docs\.example\.org/product", {"status": 200, "body": PAGE})
    direct_vm.mock_llm(r"You are checking FIT", json.dumps({"findings": [
        finding(quote="A quote that is not present in the fetched document")]}))
    with direct_vm.expect_revert():
        contract.evaluate_candidate(bad_id)
    assert contract.get_application(bad_id)["status"] == "PENDING"


@pytest.mark.direct
def test_direct_validator_rechecks_material_decision_and_source_mutation(direct_vm, direct_deploy, windows_direct_stdin):
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.16")
    sid = publish(direct_vm, contract)
    aid = contract.submit_candidate(sid, "Candidate", "A documented product candidate", json.dumps([SOURCE]))
    install_evidence(direct_vm, {"status": 200, "body": PAGE})
    contract.evaluate_candidate(aid)
    assert direct_vm.run_validator()

    direct_vm.clear_mocks()
    direct_vm.mock_web(r"docs\.example\.org/product", {"status": 200, "body": "A different page with no matching claim."})
    direct_vm.mock_llm(r"You are checking FIT", json.dumps({"findings": [
        finding("UNKNOWN", quality="UNVERIFIED", index=-1, quote="")]}))
    assert not direct_vm.run_validator()


@pytest.mark.direct
def test_direct_input_guards_reads_pagination_and_retirement(direct_vm, direct_deploy, direct_bob, windows_direct_stdin):
    contract = direct_deploy(CONTRACT, sdk_version="v0.2.16")
    sid = publish(direct_vm, contract)
    with direct_vm.expect_revert("duplicate evidence URLs"):
        contract.submit_candidate(sid, "Duplicate", "A candidate with duplicate links", json.dumps([SOURCE, SOURCE + "/"]))
    with direct_vm.expect_revert():
        contract.submit_candidate(sid, "Private URL", "A candidate with a private link", json.dumps(["https://127.0.0.1/private"]))
    with direct_vm.expect_revert("page size"):
        contract.list_standards(0, 0)
    assert contract.list_standards(0, 24)["items"][0]["id"] == sid
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("only standard owner"):
        contract.retire_standard(sid)\n