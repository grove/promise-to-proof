import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
ONBOARDING_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "getting-started.md",
)
CORE_SKILLS = (
    "setup-promise-to-proof",
    "plan-acceptance",
    "deliver-issue",
    "implement-contract",
    "review-implementation",
    "prove",
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class OnboardingDocsTests(unittest.TestCase):
    def test_onboarding_docs_exist(self):
        for path in ONBOARDING_DOCS:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file(), path)

    def test_relative_links_resolve(self):
        for source in ONBOARDING_DOCS:
            text = source.read_text(encoding="utf-8")
            for raw_target in LINK_RE.findall(text):
                target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
                if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                    continue
                path_text = unquote(target.split("#", 1)[0])
                if not path_text:
                    continue
                resolved = (source.parent / path_text).resolve()
                with self.subTest(source=source.relative_to(ROOT), target=target):
                    self.assertTrue(
                        resolved.exists(),
                        f"{source.relative_to(ROOT)} links to missing {target}",
                    )

    def test_first_run_commands_have_real_skills(self):
        combined = "\n".join(path.read_text(encoding="utf-8") for path in ONBOARDING_DOCS)
        for skill in CORE_SKILLS:
            skill_path = ROOT / "skills" / "productivity" / skill / "SKILL.md"
            with self.subTest(skill=skill):
                self.assertTrue(skill_path.is_file(), skill_path)
                self.assertIn(f"/{skill}", combined)

    def test_contract_storage_path_is_consistent(self):
        for source in ONBOARDING_DOCS:
            text = source.read_text(encoding="utf-8")
            with self.subTest(source=source.relative_to(ROOT)):
                self.assertIn(".p2p/work/<slug>/contract.md", text)
                self.assertIn(".p2p/", text)

    def test_supported_controller_profile_is_visible(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        guide = (ROOT / "docs" / "getting-started.md").read_text(encoding="utf-8")
        for text, source in ((readme, "README.md"), (guide, "docs/getting-started.md")):
            with self.subTest(source=source):
                self.assertIn("macOS", text)
                self.assertIn("Codex CLI", text)
                self.assertIn("Python 3.11+", text)
                self.assertIn("Git", text)
                self.assertIn("GitHub", text)
                self.assertIn("optional", text.lower())

    def test_success_terms_stay_distinct(self):
        combined = "\n".join(path.read_text(encoding="utf-8") for path in ONBOARDING_DOCS)
        for verdict in ("IMPLEMENTED", "REVIEWED", "PROVEN"):
            with self.subTest(verdict=verdict):
                self.assertIn(verdict, combined)
        self.assertIn("exact candidate", combined.lower())


if __name__ == "__main__":
    unittest.main()
