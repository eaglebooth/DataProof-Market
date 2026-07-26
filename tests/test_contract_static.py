import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "DataProofMarket.py"
SOURCE = CONTRACT.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


class ContractStaticTests(unittest.TestCase):
    def test_required_runner_header_is_exact(self):
        self.assertEqual(
            SOURCE.splitlines()[:3],
            [
                "# v0.2.16",
                '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }',
                "from genlayer import *",
            ],
        )

    def test_contract_uses_semantic_consensus_and_real_transfers(self):
        self.assertIn("gl.eq_principle.prompt_comparative", SOURCE)
        self.assertNotIn("gl.eq_principle.strict_eq", SOURCE)
        self.assertIn("@gl.public.write.payable", SOURCE)
        self.assertIn("_Recipient(Address(provider)).emit_transfer", SOURCE)
        self.assertIn("_Recipient(Address(buyer)).emit_transfer", SOURCE)

    def test_public_methods_have_no_more_than_six_parameters(self):
        for node in ast.walk(TREE):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            is_public = any(
                isinstance(decorator, ast.Attribute)
                and isinstance(decorator.value, ast.Attribute)
                and isinstance(decorator.value.value, ast.Name)
                and decorator.value.value.id == "gl"
                and decorator.value.attr == "public"
                for decorator in node.decorator_list
            )
            is_payable_public = any(
                isinstance(decorator, ast.Attribute) and decorator.attr == "payable"
                for decorator in node.decorator_list
            )
            if is_public or is_payable_public:
                parameter_count = len(node.args.args) - 1
                self.assertLessEqual(
                    parameter_count,
                    6,
                    f"{node.name} has {parameter_count} parameters",
                )

    def test_sender_bound_roles_and_state_guards_are_present(self):
        for marker in [
            "gl.message.sender_address.as_hex.lower()",
            'raise gl.vm.UserError("BUYER_ONLY")',
            'raise gl.vm.UserError("PROVIDER_ONLY")',
            'raise gl.vm.UserError("PARTY_ONLY")',
            'raise gl.vm.UserError("RULING_NOT_READY")',
            'raise gl.vm.UserError("SUBMISSION_WINDOW_CLOSED")',
            'raise gl.vm.UserError("LICENSE_WINDOW_CLOSED")',
        ]:
            self.assertIn(marker, SOURCE)

    def test_immutable_sources_and_digests_are_required(self):
        for marker in [
            "https://ipfs.io/ipfs/",
            "https://arweave.net/",
            'value.startswith("sha256:")',
            "rubric_digest",
            "manifest_digest",
            "sample_digest",
            "license_digest",
        ]:
            self.assertIn(marker, SOURCE)

    def test_no_unbounded_history_scan_or_fake_runtime(self):
        for marker in [
            "while True",
            "range(self.bounty_count",
            "mockContract",
            "demoBounties",
            "testnetAsimov",
        ]:
            self.assertNotIn(marker, SOURCE)


if __name__ == "__main__":
    unittest.main()
