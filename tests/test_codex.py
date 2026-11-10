import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "install_codex.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class CodexCompatibility(unittest.TestCase):
    def test_install_and_run_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = installer.install(Path(tmp) / "codex home")
            self.assertEqual(len(list(target.glob("ig-*/SKILL.md"))), 13)
            cases = [
                ("ig-reel/hookscore.py", "I lost $18,000 because of one missing contract."),
                ("ig-reel/beats.py", "I lost $18,000.\nHere is the clause I changed."),
                ("ig-caption/caption.py", "My first 30 reels taught me this. 한글"),
                ("ig-human/humanize.py", "We leverage seamless tools. 한글"),
                ("ig-human/detect.py", "We leverage seamless tools. 한글"),
                ("ig-viral/swipe.py", "account\tmedian\tviews\thook\n@demo\t100\t1000\tI lost $18,000 because of one missing contract.\n"),
            ]
            for script, text in cases:
                with self.subTest(script=script):
                    result = subprocess.run(
                        [sys.executable, "-X", "utf8", str(target / script), "-", "--json"],
                        input=text, text=True, encoding="utf-8", capture_output=True,
                        cwd=tmp)
                    payload = json.loads(result.stdout)
                    self.assertTrue(payload)
                    expected = int(payload["verdict"] != "READY") if "caption.py" in script else 0
                    self.assertEqual(result.returncode, expected, result.stderr)
                    if "swipe" in script:
                        self.assertNotIn("not found", result.stderr)
                        self.assertNotIn("skipped", result.stderr)
            first = target / "ig-reel/SKILL.md"
            first.write_text("user edits", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                installer.install(Path(tmp) / "codex home")
            self.assertEqual(first.read_text(encoding="utf-8"), "user edits")

    def test_skill_paths_and_names(self):
        for skill in (ROOT / "skills").glob("ig-*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            self.assertIn("name: " + skill.parent.name, text)
            self.assertIn("description:", text)
            self.assertNotIn("~/.claude/", text)
            self.assertNotIn("/ig-", text)


if __name__ == "__main__":
    unittest.main()
