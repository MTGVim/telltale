import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "telltalectl.py"


class TelltaleDoctorTests(unittest.TestCase):
    def run_doctor(self, cwd=ROOT):
        return subprocess.run(
            ["python3", str(SCRIPT), "doctor"],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_doctor_reports_healthy_repository(self):
        result = self.run_doctor()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Telltale doctor", result.stdout)
        self.assertIn("OK   plugin manifest found", result.stdout)
        self.assertIn("OK   marketplace manifest found", result.stdout)
        self.assertIn("OK   public command found: /telltale:sail", result.stdout)
        self.assertIn("OK   local alias found: /sail", result.stdout)
        self.assertIn("OK   Hermes skill found: hermes/skills/sail", result.stdout)
        self.assertIn("OK   generated state is gitignored", result.stdout)
        self.assertRegex(result.stdout, r"OK   versions match: \d+\.\d+\.\d+")
        self.assertIn("Result: healthy", result.stdout)

    def test_doctor_fails_on_version_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            ignore = shutil.ignore_patterns(".git", ".claude/telltale")
            shutil.copytree(ROOT, repo, ignore=ignore)
            package_json = repo / "package.json"
            data = json.loads(package_json.read_text())
            data["version"] = "9.9.9"
            package_json.write_text(json.dumps(data, indent=2) + "\n")

            result = self.run_doctor(cwd=repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("FAIL version mismatch", result.stdout)
            self.assertIn("package.json: 9.9.9", result.stdout)
            self.assertIn("Result: unhealthy", result.stdout)

    def test_doctor_fails_when_required_surface_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            ignore = shutil.ignore_patterns(".git", ".claude/telltale")
            shutil.copytree(ROOT, repo, ignore=ignore)
            (repo / "commands" / "telltale-sail.md").unlink()

            result = self.run_doctor(cwd=repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("FAIL public command missing: commands/telltale-sail.md", result.stdout)
            self.assertIn("Result: unhealthy", result.stdout)


if __name__ == "__main__":
    unittest.main()
