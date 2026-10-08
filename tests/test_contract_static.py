import ast
import unittest
from pathlib import Path

SOURCE = (Path(__file__).parents[1] / "contracts" / "DataProofMarket.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)

class ContractStaticTests(unittest.TestCase):
    def test_runner_is_pinned(self):
        self.assertEqual(SOURCE.splitlines()[0], "# v0.2.16")
        self.assertIn("py-genlayer:", SOURCE.splitlines()[1])

    def test_two_consensus_modes_have_separate_jobs(self):
        self.assertIn("gl.eq_principle.strict_eq(verify)", SOURCE)
        self.assertIn("gl.eq_principle.prompt_comparative(evaluate, principle)", SOURCE)
        self.assertIn("hashlib.sha256", SOURCE)

    def test_real_custody_uses_pull_payments_and_cei(self):
        self.assertIn("@gl.public.write.payable", SOURCE)
        self.assertIn("self.credits[sender] = u256(0)", SOURCE)
        self.assertIn("_Recipient(Address(sender)).emit_transfer", SOURCE)
        self.assertLess(SOURCE.index("self.credits[sender] = u256(0)"), SOURCE.index("emit_transfer(value=amount)"))

    def test_protocol_is_bounded_and_replay_guarded(self):
        for marker in ["MAX_CANDIDATES = 5", "DUPLICATE_PROVIDER", "SUBMISSION_ALREADY_REVEALED", "RULING_NOT_READY", "NOTHING_TO_WITHDRAW"]:
            self.assertIn(marker, SOURCE)
        self.assertNotIn("while True", SOURCE)
        self.assertNotIn("range(self.tournament_count", SOURCE)

    def test_commit_reveal_and_authoritative_time_exist(self):
        for marker in ['gl.message_raw["datetime"]', "OPEN_COMMIT", "OPEN_REVEAL", "READY_FOR_JURY", "COMMIT_WINDOW_CLOSED", "REVEAL_WINDOW_CLOSED"]:
            self.assertIn(marker, SOURCE)

    def test_ai_never_returns_or_sets_an_amount(self):
        prompt = SOURCE[SOURCE.index('return gl.nondet.exec_prompt("Rank datasets'):SOURCE.index('principle = "Equivalent')]
        self.assertNotIn("amount", prompt.lower())
        self.assertNotIn("prize", prompt.lower())

    def test_public_abi_stays_bounded(self):
        for node in ast.walk(TREE):
            if not isinstance(node, ast.FunctionDef): continue
            if any(isinstance(d, ast.Attribute) and d.attr in ("write", "view", "payable") for d in node.decorator_list):
                self.assertLessEqual(len(node.args.args) - 1, 6, node.name)

    def test_immutable_sources_and_digests_are_required(self):
        for marker in ["https://ipfs.io/ipfs/", "https://arweave.net/", 'value.startswith("sha256:")', "manifest_digest", "sample_digest", "license_digest"]:
            self.assertIn(marker, SOURCE)

if __name__ == "__main__": unittest.main()
