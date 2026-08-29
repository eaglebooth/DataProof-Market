from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GENLAYER = (ROOT / "frontend" / "src" / "lib" / "genlayer.ts").read_text(encoding="utf-8")
CONTRACT_PAGE = (ROOT / "frontend" / "src" / "app" / "contract" / "page.tsx").read_text(encoding="utf-8")
SHELL = (ROOT / "frontend" / "src" / "components" / "AppShell.tsx").read_text(encoding="utf-8")
LAYOUT = (ROOT / "frontend" / "src" / "app" / "layout.tsx").read_text(encoding="utf-8")


class FrontendReleaseStaticTests(unittest.TestCase):
    def test_canonical_contract_is_built_in(self):
        self.assertIn("0x4AD7AaDf9e75563702B849866f55b524dA7420c1", GENLAYER)
        self.assertIn("canonicalContractAddress", GENLAYER)
        self.assertNotIn("NEXT_PUBLIC_CONTRACT_ADDRESS", GENLAYER)
        self.assertNotIn("NEXT_PUBLIC_NETWORK", GENLAYER)
        self.assertIn('const network: NetworkName = "studionet"', GENLAYER)

    def test_browser_cannot_override_contract(self):
        self.assertNotIn("localStorage", GENLAYER)
        self.assertNotIn("setConfiguredAddress", GENLAYER)
        self.assertNotIn("REVIEWER-SELECTABLE DEPLOYMENT", CONTRACT_PAGE)

    def test_contract_page_is_verification_only(self):
        self.assertIn("Read live state", CONTRACT_PAGE)
        self.assertNotIn("<input", CONTRACT_PAGE)

    def test_brand_asset_is_wired_everywhere(self):
        self.assertIn("/dataproof-logo.png", SHELL)
        self.assertIn("/dataproof-logo.png", LAYOUT)


if __name__ == "__main__":
    unittest.main()
