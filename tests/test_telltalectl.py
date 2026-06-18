import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "telltalectl.py"


class TelltaleCtlTests(unittest.TestCase):
    def run_ctl(self, *args, cwd=None):
        return subprocess.run(
            ["python3", str(SCRIPT), *args],
            cwd=cwd or ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def test_validate_schemas(self):
        result = self.run_ctl("validate-schemas")
        self.assertIn("ok: 7 schemas", result.stdout)

    def test_validate_rejects_scorecard_without_basis(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad-scorecard.json"
            path.write_text(json.dumps({
                "value_to_destination": {"score": 4, "basis": []},
                "cost_to_try": {"score": 1, "basis": ["x"]},
                "verification_distance": {"score": 1, "basis": ["x"]},
                "dependency_readiness": {"score": 5, "basis": ["x"]},
                "information_gain_if_fail": {"score": 3, "basis": ["x"]},
                "unknown_surface": {"score": 1, "basis": ["x"]},
                "coordination_cost": {"score": 1, "basis": ["x"]},
                "reversibility": {"score": 5, "basis": ["x"]},
            }))
            result = subprocess.run(
                ["python3", str(SCRIPT), "validate", "--kind", "island-scorecard", "--file", str(path)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("basis", result.stderr + result.stdout)

    def test_select_island_uses_priority_then_lower_cost(self):
        def scorecard(value, cost, info, readiness=5, verification=1, unknown=1, coordination=1, reversibility=5):
            def s(score, name):
                return {"score": score, "basis": [name]}
            return {
                "value_to_destination": s(value, "value"),
                "cost_to_try": s(cost, "cost"),
                "verification_distance": s(verification, "verification"),
                "dependency_readiness": s(readiness, "ready"),
                "information_gain_if_fail": s(info, "info"),
                "unknown_surface": s(unknown, "unknown"),
                "coordination_cost": s(coordination, "coordination"),
                "reversibility": s(reversibility, "reverse"),
            }
        islands = [
            {"id": "expensive", "title": "Expensive", "status": "ready", "scope": ["a"], "dependencies": [], "close_criteria": ["done"], "scorecard": scorecard(5, 4, 4)},
            {"id": "cheap", "title": "Cheap", "status": "ready", "scope": ["b"], "dependencies": [], "close_criteria": ["done"], "scorecard": scorecard(4, 1, 3)},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "islands.json"
            path.write_text(json.dumps({"islands": islands}))
            result = self.run_ctl("select-island", "--file", str(path))
            selected = json.loads(result.stdout)
            self.assertEqual(selected["id"], "cheap")


    def test_init_run_uses_packaged_schemas_from_external_project_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "consumer-project"
            project.mkdir()
            subprocess.run(["git", "init", "-b", "consumer-branch"], cwd=project, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            result = self.run_ctl("init-run", "--input-source", "user_prompt", cwd=project)

            self.assertRegex(result.stdout.strip(), r"^tt-\d{8}-\d{6}$")
            trace = project / ".claude" / "telltale" / "branches" / "consumer-branch" / "event-trace.jsonl"
            state = project / ".claude" / "telltale" / "branches" / "consumer-branch" / "state.json"
            self.assertTrue(trace.exists())
            self.assertTrue(state.exists())

    def test_branch_key_uses_external_project_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "consumer-project"
            project.mkdir()
            subprocess.run(["git", "init", "-b", "consumer-branch"], cwd=project, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            result = self.run_ctl("branch-key", cwd=project)

            self.assertEqual(result.stdout.strip(), "consumer-branch")

    def test_all_helper_entrypoints_use_bundled_schemas_without_project_schemas(self):
        scripts = [
            ROOT / "scripts" / "telltalectl.py",
            ROOT / "skills" / "sail" / "scripts" / "telltalectl.py",
            ROOT / "hermes" / "skills" / "sail" / "scripts" / "telltalectl.py",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "consumer-project"
            project.mkdir()
            subprocess.run(["git", "init", "-b", "consumer-branch"], cwd=project, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            for script in scripts:
                with self.subTest(script=script):
                    shutil.rmtree(project / ".claude", ignore_errors=True)
                    result = subprocess.run(
                        ["python3", str(script), "init-run", "--input-source", "user_prompt"],
                        cwd=project,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                    self.assertFalse((project / "schemas").exists(), "helper must not create schemas/ in the user project")
                    trace = project / ".claude" / "telltale" / "branches" / "consumer-branch" / "event-trace.jsonl"
                    self.assertTrue(trace.exists())

    def test_smoke_creates_closed_trace_and_report(self):
        result = self.run_ctl("smoke")
        self.assertIn("ok: smoke branch", result.stdout)
        branch = [line for line in result.stdout.splitlines() if line.startswith("ok: smoke branch")][0].split()[-1]
        trace = ROOT / ".claude" / "telltale" / "branches" / branch / "event-trace.jsonl"
        report = ROOT / ".claude" / "telltale" / "branches" / branch / "reports" / "convergence-report.md"
        state = ROOT / ".claude" / "telltale" / "branches" / branch / "state.json"
        self.assertTrue(trace.exists())
        self.assertTrue(report.exists())
        state_json = json.loads(state.read_text())
        self.assertEqual(state_json["status"], "SUCCESS")
        report_text = report.read_text(encoding="utf-8")
        self.assertIn("## 🗺️ 항해 진행", report_text)
        self.assertIn("- 🏝️ 도착한 섬 수: 1", report_text)
        self.assertIn("- ✅ 마지막 도착 섬: island-smoke", report_text)
        self.assertIn("- ⛵ 항해 상태: 완료", report_text)
        self.assertIn("- 🎮 진행 HUD: 🏝️ 1개 섬 도착 · ⛵ 완료 · ✅ island-smoke", report_text)
        for english_label in [
            "Route Progress",
            "Islands reached",
            "Last island reached",
            "Sailing status",
            "Progress HUD",
            "completed",
            "none",
        ]:
            self.assertNotIn(english_label, report_text)
        closed = self.run_ctl("validate-trace", "--file", str(trace), "--require-close")
        self.assertIn("ok:", closed.stdout)


if __name__ == "__main__":
    unittest.main()
