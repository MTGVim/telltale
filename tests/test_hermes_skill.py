import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "hermes" / "skills" / "sail" / "SKILL.md"
CLAUDE_SKILL = ROOT / "skills" / "sail" / "SKILL.md"
PUBLIC_COMMAND = ROOT / "commands" / "telltale-sail.md"
LOCAL_ALIAS = ROOT / ".claude" / "commands" / "sail.md"


def parse_frontmatter(text: str):
    assert text.startswith("---\n")
    end = text.find("\n---\n", 4)
    assert end != -1
    raw = text[4:end]
    data = {}
    for line in raw.splitlines():
        if not line.strip() or line.startswith(" "):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def hermes_skill_command_slug(name: str) -> str:
    slug = name.lower().replace(" ", "-").replace("_", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return f"/{slug}"


class HermesSkillTests(unittest.TestCase):
    def test_skill_frontmatter_exposes_sail_command(self):
        text = SKILL.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        self.assertEqual(frontmatter["name"], "sail")
        self.assertEqual(hermes_skill_command_slug(frontmatter["name"]), "/sail")
        self.assertIn("출항", frontmatter["description"])
        self.assertLessEqual(len(frontmatter["description"]), 60)
        self.assertTrue(frontmatter["description"].endswith("."))

    def test_skill_ships_helper_and_references(self):
        skill_dir = SKILL.parent
        required = [
            skill_dir / "scripts" / "telltalectl.py",
            skill_dir / "references" / "RFC_TELLTALE_M1.md",
            skill_dir / "references" / "HERMES_IMPLEMENTATION_BRIEF.md",
            skill_dir / "references" / "phase-docs.md",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing {path}")

    def test_skill_documents_role_mapping_and_boundaries(self):
        text = SKILL.read_text(encoding="utf-8")
        for phrase in [
            "Orchestrator | Main Hermes agent",
            "Cartographer | `delegate_task`",
            "Sailor | `delegate_task`",
            "Inspector | Separate `delegate_task`",
            "Claude Code marketplace command remains `/telltale:sail`",
            "`출항`",
            "`출항이다`",
        ]:
            self.assertIn(phrase, text)

    def test_claude_code_local_sail_alias_exists(self):
        alias = LOCAL_ALIAS
        text = alias.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        self.assertIn("출항", frontmatter["description"])
        self.assertIn("# /sail", text)
        self.assertIn("/telltale:sail", text)
        self.assertIn("$ARGUMENTS", text)

    def test_claude_code_installed_sail_skill_exists(self):
        text = CLAUDE_SKILL.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        self.assertEqual(frontmatter["name"], "sail")
        self.assertIn("출항", frontmatter["description"])
        self.assertLessEqual(len(frontmatter["description"]), 60)
        self.assertIn("/sail <task", text)
        self.assertIn("/telltale:sail", text)
        self.assertIn("@telltale-cartographer", text)
        self.assertIn("`출항`", text)

    def test_sail_skills_document_korean_emoji_route_progress(self):
        for path in [CLAUDE_SKILL, SKILL]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("## 🧭 한글 항해 진행 HUD", text)
            progress_section = text.split("## 🧭 한글 항해 진행 HUD", 1)[1].split("## Pitfalls", 1)[0]
            self.assertIn("🧭 항해", progress_section)
            self.assertIn("도착", progress_section)
            self.assertIn("현재 작업 섬", progress_section)
            self.assertIn("마지막 도착", progress_section)
            self.assertIn("🏝️", progress_section)
            self.assertIn("⛵", progress_section)
            self.assertIn("✅", progress_section)
            for english_label in [
                "🧭 Route",
                "reached",
                "sailing:",
                "last island",
                "Emoji Route Progress",
            ]:
                self.assertNotIn(english_label, progress_section)

    def test_natural_language_chulhang_triggers_are_on_all_entry_surfaces(self):
        surfaces = [CLAUDE_SKILL, SKILL, PUBLIC_COMMAND, LOCAL_ALIAS]
        for path in surfaces:
            text = path.read_text(encoding="utf-8")
            frontmatter = parse_frontmatter(text)
            self.assertIn("출항", frontmatter["description"], path)
            self.assertIn("## 자연어 트리거", text, path)
            for trigger in ["`출항`", "`출항이다`", "`이 작업 출항하자`"]:
                self.assertIn(trigger, text, path)

    def test_m1_documents_sequential_safety_and_briefing_milestones(self):
        for path in [CLAUDE_SKILL, SKILL, PUBLIC_COMMAND]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("한 번에 하나의 현재 작업 섬", text, path)
            self.assertIn("병렬 후보", text, path)
            for milestone in ["🗺️ 항해 지도", "⛵ 출항 브리핑", "✅ 섬 완료 브리핑", "🏁 최종 도착 브리핑"]:
                self.assertIn(milestone, text, path)


if __name__ == "__main__":
    unittest.main()
