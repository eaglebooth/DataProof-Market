import ast
import copy
import hashlib
import json
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "DataProofMarket.py"
SOURCE = CONTRACT.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)

BUYER = "0x" + "1" * 40
PROVIDER_A = "0x" + "2" * 40
PROVIDER_B = "0x" + "3" * 40
OTHER = "0x" + "4" * 40
PROVIDER_C = "0x" + "5" * 40
PROVIDER_D = "0x" + "6" * 40
RUBRIC_URL = "https://arweave.net/" + "r" * 43


class UserError(Exception):
    pass


class SenderAddress:
    def __init__(self, value):
        self.as_hex = value


class FakeMap(dict):
    pass


class RenderStore:
    def __init__(self):
        self.bodies = {}
        self.unavailable = set()

    def render(self, url, mode="text"):
        if url in self.unavailable:
            raise RuntimeError("network unavailable")
        return self.bodies[url]

    def get(self, url):
        if url in self.unavailable:
            raise RuntimeError("network unavailable")
        return types.SimpleNamespace(body=self.bodies[url].encode())


def digest(body):
    return "sha256:" + hashlib.sha256(body.encode()).hexdigest()


def immutable_url(marker):
    return "https://arweave.net/" + marker * 43


def load_production_harness():
    contract = next(node for node in TREE.body if isinstance(node, ast.ClassDef) and node.name == "DataProofMarket")
    methods = []
    for node in contract.body:
        if isinstance(node, ast.FunctionDef):
            method = copy.deepcopy(node)
            method.decorator_list = []
            methods.append(method)
    harness = ast.ClassDef(name="ProductionHarness", bases=[], keywords=[], body=methods, decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[harness], type_ignores=[]))
    render_store = RenderStore()
    gl = types.SimpleNamespace(
        message=types.SimpleNamespace(sender_address=SenderAddress(BUYER), value=0),
        message_raw={"datetime": "2026-10-08T00:00:00Z"},
        vm=types.SimpleNamespace(UserError=UserError),
        nondet=types.SimpleNamespace(web=render_store, exec_prompt=lambda _prompt: ""),
        eq_principle=types.SimpleNamespace(
            strict_eq=lambda callback: callback(),
            prompt_comparative=lambda callback, _principle: callback(),
        ),
    )
    transfers = []
    namespace = {
        "Address": lambda value: value,
        "_Recipient": lambda address: types.SimpleNamespace(emit_transfer=lambda value: transfers.append((address, value))),
        "gl": gl,
        "hashlib": hashlib,
        "json": json,
        "datetime": __import__("datetime").datetime,
        "u256": int,
        "MAX_CANDIDATES": 5,
        "COMMIT_SECONDS": 300,
        "REVEAL_SECONDS": 300,
    }
    exec(compile(module, str(CONTRACT), "exec"), namespace)
    instance = namespace["ProductionHarness"]()
    instance.tournament_count = 0
    instance.submission_count = 0
    instance.total_received = 0
    instance.active_prizes = 0
    instance.active_bonds = 0
    instance.total_credited = 0
    instance.total_withdrawn = 0
    instance.balance = 10**30
    for field in ("tournament_data", "submission_data", "tournament_slot", "provider_entry", "credits"):
        setattr(instance, field, FakeMap())
    return instance, gl, render_store, transfers


def set_time(gl, second):
    gl.message_raw = {"datetime": f"2026-10-08T00:{second // 60:02d}:{second % 60:02d}Z"}


def open_and_commit(contract, gl, prize=10**24, bond=10**20):
    rubric = "Rubric requires provenance, schema clarity, representative samples, and compatible licensing." * 2
    contract._test_rubric = rubric
    gl.message.sender_address = SenderAddress(BUYER)
    gl.message.value = prize
    tid = contract.open_tournament("Mobility dataset tournament", "Select a traceable dataset suitable for urban accessibility model training and evaluation.", RUBRIC_URL, digest(rubric), bond, 3)
    for provider, marker in ((PROVIDER_A, "a"), (PROVIDER_B, "b")):
        gl.message.sender_address = SenderAddress(provider)
        gl.message.value = bond
        bodies = [
            ("Manifest " + marker + " documents provenance, schema, collection methods, and known limitations. ") * 2,
            ("Sample " + marker + " contains representative records and documented field meanings. ") * 2,
            ("License " + marker + " grants compatible reuse rights and states attribution requirements. ") * 2,
        ]
        contract.commit_submission(tid, *(digest(body) for body in bodies))
        setattr(contract, f"_test_{marker}_bodies", bodies)
    return tid


def reveal_all(contract, gl, store, tid):
    set_time(gl, 300)
    contract.start_reveal(tid)
    urls_by_provider = {}
    for provider, marker in ((PROVIDER_A, "a"), (PROVIDER_B, "b")):
        urls = [immutable_url(marker + suffix) for suffix in ("m", "s", "l")]
        bodies = getattr(contract, f"_test_{marker}_bodies")
        store.bodies.update(dict(zip(urls, bodies)))
        gl.message.sender_address = SenderAddress(provider)
        contract.reveal_dataset(tid, *urls, "Packet documents provenance, sampling limits, schema quality, and reuse rights.")
        urls_by_provider[provider] = urls
    store.bodies[RUBRIC_URL] = contract._test_rubric
    set_time(gl, 600)
    contract.close_reveal(tid)
    return urls_by_provider


class ProductionContractPathTests(unittest.TestCase):
    def test_open_rejects_zero_prize_and_invalid_bond(self):
        contract, gl, _, _ = load_production_harness()
        gl.message.value = 0
        with self.assertRaisesRegex(UserError, "PRIZE_REQUIRED"):
            contract.open_tournament("Valid title", "A sufficiently detailed intended dataset use case for testing.", RUBRIC_URL, "sha256:" + "1" * 64, 1, 2)
        gl.message.value = 100
        with self.assertRaisesRegex(UserError, "INVALID_PROVIDER_BOND"):
            contract.open_tournament("Valid title", "A sufficiently detailed intended dataset use case for testing.", RUBRIC_URL, "sha256:" + "1" * 64, 100, 2)

    def test_wrong_bond_and_buyer_competition_are_rejected(self):
        contract, gl, _, _ = load_production_harness()
        gl.message.value = 1_000
        tid = contract.open_tournament("Valid title", "A sufficiently detailed intended dataset use case for testing.", RUBRIC_URL, "sha256:" + "1" * 64, 100, 2)
        gl.message.value = 100
        with self.assertRaisesRegex(UserError, "BUYER_CANNOT_COMPETE"):
            contract.commit_submission(tid, "sha256:" + "2" * 64, "sha256:" + "3" * 64, "sha256:" + "4" * 64)
        gl.message.sender_address = SenderAddress(PROVIDER_A)
        gl.message.value = 99
        with self.assertRaisesRegex(UserError, "EXACT_BOND_REQUIRED"):
            contract.commit_submission(tid, "sha256:" + "2" * 64, "sha256:" + "3" * 64, "sha256:" + "4" * 64)

    def test_candidate_cap_is_enforced(self):
        contract, gl, _, _ = load_production_harness()
        gl.message.value = 1_000
        tid = contract.open_tournament("Valid title", "A sufficiently detailed intended dataset use case for testing.", RUBRIC_URL, "sha256:" + "1" * 64, 100, 2)
        for provider in (PROVIDER_A, PROVIDER_B):
            gl.message.sender_address = SenderAddress(provider); gl.message.value = 100
            contract.commit_submission(tid, "sha256:" + "2" * 64, "sha256:" + "3" * 64, "sha256:" + "4" * 64)
        gl.message.sender_address = SenderAddress(PROVIDER_C)
        with self.assertRaisesRegex(UserError, "CANDIDATE_CAP_REACHED"):
            contract.commit_submission(tid, "sha256:" + "2" * 64, "sha256:" + "3" * 64, "sha256:" + "4" * 64)

    def test_large_wei_values_survive_json_and_settlement_exactly(self):
        contract, gl, store, _ = load_production_harness()
        prize, bond = 10**24 + 123, 10**20 + 7
        tid = open_and_commit(contract, gl, prize, bond)
        reveal_all(contract, gl, store, tid)
        gl.nondet.exec_prompt = lambda _prompt: json.dumps({"outcome": "RANKED", "winner_id": 0, "runner_up_id": 1, "reason": "Candidate zero best satisfies the locked rubric."})
        self.assertEqual(contract.judge_tournament(tid), "RULING_READY")
        self.assertEqual(contract.settle_tournament(tid), "SETTLED")
        self.assertEqual(contract.credits[PROVIDER_A], prize + bond)
        self.assertEqual(contract.credits[PROVIDER_B], bond)
        self.assertEqual(contract.total_received, prize + 2 * bond)
        self.assertEqual(contract.total_received, contract.total_credited)

    def test_duplicate_commit_and_deadline_guards(self):
        contract, gl, _, _ = load_production_harness()
        tid = open_and_commit(contract, gl)
        gl.message.sender_address = SenderAddress(PROVIDER_A)
        gl.message.value = 10**20
        with self.assertRaisesRegex(UserError, "DUPLICATE_PROVIDER"):
            contract.commit_submission(tid, "sha256:" + "a" * 64, "sha256:" + "b" * 64, "sha256:" + "c" * 64)

    def test_reveal_window_and_duplicate_reveal_guards(self):
        contract, gl, store, _ = load_production_harness()
        tid = open_and_commit(contract, gl)
        gl.message.sender_address = SenderAddress(PROVIDER_A)
        urls = [immutable_url("a" + suffix) for suffix in ("m", "s", "l")]
        with self.assertRaisesRegex(UserError, "REVEAL_WINDOW_CLOSED"):
            contract.reveal_dataset(tid, *urls, "A sufficiently detailed provider disclosure for the packet.")
        set_time(gl, 300); contract.start_reveal(tid)
        store.bodies.update(dict(zip(urls, contract._test_a_bodies)))
        contract.reveal_dataset(tid, *urls, "A sufficiently detailed provider disclosure for the packet.")
        with self.assertRaisesRegex(UserError, "SUBMISSION_ALREADY_REVEALED"):
            contract.reveal_dataset(tid, *urls, "A sufficiently detailed provider disclosure for the packet.")
        set_time(gl, 600)
        gl.message.sender_address = SenderAddress(PROVIDER_B)
        with self.assertRaisesRegex(UserError, "REVEAL_WINDOW_CLOSED"):
            contract.reveal_dataset(tid, *urls, "A sufficiently detailed provider disclosure for the packet.")

    def test_no_reveal_bonds_are_forfeited_and_double_settlement_rejected(self):
        contract, gl, _, _ = load_production_harness()
        tid = open_and_commit(contract, gl, 1_000, 100)
        set_time(gl, 300); contract.start_reveal(tid)
        set_time(gl, 600); contract.close_reveal(tid)
        self.assertEqual(contract.judge_tournament(tid), "RULING_READY")
        self.assertEqual(contract.settle_tournament(tid), "SETTLED")
        self.assertEqual(contract.credits[BUYER], 1_200)
        with self.assertRaisesRegex(UserError, "RULING_NOT_READY"):
            contract.settle_tournament(tid)

    def test_provider_lookup_is_sender_scoped(self):
        contract, gl, _, _ = load_production_harness()
        tid = open_and_commit(contract, gl)
        self.assertEqual(json.loads(contract.get_provider_submission(tid, PROVIDER_A))["provider"], PROVIDER_A)
        self.assertEqual(contract.get_provider_submission(tid, OTHER), "{}")
        set_time(gl, 300)
        with self.assertRaisesRegex(UserError, "COMMIT_WINDOW_CLOSED"):
            contract.commit_submission(tid, "sha256:" + "a" * 64, "sha256:" + "b" * 64, "sha256:" + "c" * 64)

    def test_fetch_outage_cannot_veto_or_confiscate_reveal_bond(self):
        contract, gl, store, _ = load_production_harness()
        prize, bond = 1_000, 100
        tid = open_and_commit(contract, gl, prize, bond)
        urls = reveal_all(contract, gl, store, tid)
        store.unavailable.add(urls[PROVIDER_A][0])
        self.assertEqual(contract.judge_tournament(tid), "RULING_READY")
        self.assertEqual(json.loads(contract.submission_data[0])["status"], "UNAVAILABLE")
        self.assertEqual(contract.settle_tournament(tid), "SETTLED")
        self.assertEqual(contract.credits[BUYER], prize)
        self.assertEqual(contract.credits[PROVIDER_A], bond)
        self.assertEqual(contract.credits[PROVIDER_B], bond)

    def test_recovery_timeout_rejects_outsider_and_allows_party(self):
        contract, gl, store, _ = load_production_harness()
        tid = open_and_commit(contract, gl, 1_000, 100)
        reveal_all(contract, gl, store, tid)
        gl.nondet.exec_prompt = lambda _prompt: json.dumps({"outcome": "RANKED", "winner_id": 99, "runner_up_id": 0, "reason": "Invented identifier."})
        contract.judge_tournament(tid)
        gl.message.sender_address = SenderAddress(OTHER)
        with self.assertRaisesRegex(UserError, "PARTY_ONLY"):
            contract.recover_unavailable(tid)
        set_time(gl, 900)
        gl.message.sender_address = SenderAddress(PROVIDER_B)
        self.assertEqual(contract.recover_unavailable(tid), "SETTLED")

    def test_digest_mismatch_disqualifies_without_veto_or_bond_forfeiture(self):
        contract, gl, store, _ = load_production_harness()
        tid = open_and_commit(contract, gl, 1_000, 100)
        reveal_all(contract, gl, store, tid)
        store.bodies[json.loads(contract.submission_data[1])["sample_url"]] += " tampered"
        self.assertEqual(contract.judge_tournament(tid), "RULING_READY")
        self.assertEqual(json.loads(contract.submission_data[1])["status"], "INVALID")
        contract.settle_tournament(tid)
        self.assertEqual(contract.credits[BUYER], 1_000)
        self.assertEqual(contract.credits[PROVIDER_A], 100)
        self.assertEqual(contract.credits[PROVIDER_B], 100)

    def test_hallucinated_winner_fails_closed(self):
        contract, gl, store, _ = load_production_harness()
        tid = open_and_commit(contract, gl, 1_000, 100)
        reveal_all(contract, gl, store, tid)
        gl.nondet.exec_prompt = lambda _prompt: json.dumps({"outcome": "RANKED", "winner_id": 99, "runner_up_id": 0, "reason": "Invented identifier."})
        self.assertEqual(contract.judge_tournament(tid), "EVIDENCE_UNAVAILABLE")

    def test_missing_or_duplicate_runner_fails_closed(self):
        for runner in (-1, 0, 99):
            contract, gl, store, _ = load_production_harness()
            tid = open_and_commit(contract, gl, 1_000, 100)
            reveal_all(contract, gl, store, tid)
            gl.nondet.exec_prompt = lambda _prompt, runner=runner: json.dumps({"outcome": "RANKED", "winner_id": 0, "runner_up_id": runner, "reason": "Malformed ranking."})
            self.assertEqual(contract.judge_tournament(tid), "EVIDENCE_UNAVAILABLE")

    def test_non_ranked_outcome_cannot_retain_candidate_ids(self):
        contract, gl, store, _ = load_production_harness()
        tid = open_and_commit(contract, gl, 1_000, 100)
        reveal_all(contract, gl, store, tid)
        gl.nondet.exec_prompt = lambda _prompt: json.dumps({"outcome": "NO_QUALIFIED_DATASET", "winner_id": 0, "runner_up_id": 1, "reason": "Contradictory result."})
        self.assertEqual(contract.judge_tournament(tid), "EVIDENCE_UNAVAILABLE")

    def test_withdraw_is_checks_effects_interactions_and_not_replayable(self):
        contract, gl, _, transfers = load_production_harness()
        contract.credits[PROVIDER_A] = 777
        contract.total_credited = 777
        gl.message.sender_address = SenderAddress(PROVIDER_A)
        self.assertEqual(contract.withdraw(), 777)
        self.assertEqual(transfers, [(PROVIDER_A, 777)])
        self.assertEqual(contract.credits[PROVIDER_A], 0)
        with self.assertRaisesRegex(UserError, "NOTHING_TO_WITHDRAW"):
            contract.withdraw()


if __name__ == "__main__":
    unittest.main()
