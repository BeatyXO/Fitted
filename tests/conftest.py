"""Offline GenLayer interface stand-in for deterministic unit/integration tests.
Not a GenVM or validator-network test. See VERIFICATION.md for scope.
"""
import importlib.util
import sys
import types
from pathlib import Path
import pytest

CONTRACT = Path(__file__).resolve().parents[1] / "contracts" / "fitted_contract.py"

class UserError(Exception):
    pass

class Return:
    def __init__(self, calldata):
        self.calldata = calldata

class GenLayerShim:
    def __init__(self):
        self.vm = types.SimpleNamespace(UserError=UserError, Return=Return, run_nondet_unsafe=self.consensus)
        self.public = types.SimpleNamespace(write=lambda f: f, view=lambda f: f)
        self.message = types.SimpleNamespace(sender_address="0x" + "a" * 40)
        self.message_raw = {"datetime": "2026-10-19T18:00:00+00:00"}
        self.nondet = types.SimpleNamespace(web=types.SimpleNamespace(get=self.fetch), exec_prompt=self.model)
        self.pages = {}
        self.findings = None
        self.fetches = 0
        self.model_calls = 0
        self.disagree = False

    def fetch(self, url):
        self.fetches += 1
        if url not in self.pages:
            raise OSError("missing page")
        return types.SimpleNamespace(body=self.pages[url].encode("utf-8"))

    def model(self, prompt, response_format=None):
        assert response_format == "json"
        assert "REQUIREMENTS=" in prompt and "SOURCES=" in prompt
        self.model_calls += 1
        if self.findings is None:
            raise ValueError("model not configured")
        out = {"findings": [dict(f) for f in self.findings]}
        if self.disagree and self.model_calls % 2 == 0:
            out["findings"][0]["decision"] = "NOT_SATISFIED"
        return out

    def consensus(self, leader_fn, validator_fn):
        original = leader_fn()
        if not validator_fn(Return(original)):
            raise UserError("NO_CONSENSUS")
        return original

@pytest.fixture()
def harness(monkeypatch):
    gl = GenLayerShim()
    mod = types.ModuleType("genlayer")
    mod.gl = gl
    mod.u32 = int
    mod.TreeMap = dict
    mod.DynArray = list
    mod.Address = str
    gl.Contract = object
    monkeypatch.setitem(sys.modules, "genlayer", mod)
    spec = importlib.util.spec_from_file_location("fitted_contract_offline", CONTRACT)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    contract = source.Fitted()
    contract.standards = {}
    contract.standard_versions = {}
    contract.applications = {}
    contract.standard_ids = []
    contract.application_ids = []
    return source, contract, gl

@pytest.fixture()
def requirements():
    return [
        {"id": "offline", "text": "Exports offline reports without network access", "mandatory": True, "weight": 5},
        {"id": "csv", "text": "Offers CSV export for business analysis", "mandatory": False, "weight": 2},
    ]

@pytest.fixture()
def standard(harness, requirements):
    import json
    source, contract, gl = harness
    sid = contract.create_standard("Analytics Fit", "Assess analytics tools against clear operational requirements", json.dumps(requirements))
    return source, contract, gl, sid

@pytest.fixture()
def candidate(standard):
    import json
    source, contract, gl, sid = standard
    url = "https://docs.supplier.example/features"
    gl.pages[url] = "The supplier product exports offline reports without network access. It offers CSV export for business analysis."
    aid = contract.submit_candidate(sid, "Example Candidate", "Demonstration of an analytics product's evidence", json.dumps([url]))
    return source, contract, gl, sid, aid

@pytest.fixture()
def positive_findings():
    return [
        {"id": "offline", "decision": "SATISFIED", "quality": "DIRECT", "source_index": 0, "quote": "exports offline reports without network access", "reason": "Official docs explicitly establish offline export."},
        {"id": "csv", "decision": "SATISFIED", "quality": "DIRECT", "source_index": 0, "quote": "offers CSV export for business analysis", "reason": "Official docs describe CSV export."},
    ]
