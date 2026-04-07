"""Tests for .claude/skills/ -- validates skill files exist and have correct structure."""

from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills"

ALL_SKILLS = [
    "sync",
    "design",
    "done",
    "landed",
]


class TestSkillExistence:
    """Verify all expected skill directories and files exist."""

    def test_skills_directory_exists(self) -> None:
        assert SKILLS_DIR.exists(), f"{SKILLS_DIR} does not exist"
        assert SKILLS_DIR.is_dir(), f"{SKILLS_DIR} is not a directory"

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_skill_directory_exists(self, skill_name: str) -> None:
        skill_dir = SKILLS_DIR / skill_name
        assert skill_dir.exists(), f"Skill directory missing: {skill_name}"
        assert skill_dir.is_dir(), f"{skill_name} is not a directory"

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_skill_file_exists(self, skill_name: str) -> None:
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"SKILL.md missing for: {skill_name}"

    def test_no_unexpected_skills(self) -> None:
        actual_skills = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}
        expected_skills = set(ALL_SKILLS)
        unexpected = actual_skills - expected_skills
        assert not unexpected, f"Unexpected skill directories found: {unexpected}"


class TestSkillFrontmatter:
    """Verify skill files have correct frontmatter."""

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_skill_has_frontmatter(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        assert content.startswith("---"), f"{skill_name} missing YAML frontmatter"
        parts = content.split("---", 2)
        assert len(parts) >= 3, f"{skill_name} has unclosed frontmatter"

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_skill_has_name(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        assert "name:" in content, f"{skill_name} missing name in frontmatter"

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_skill_has_description(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        assert "description:" in content, f"{skill_name} missing description in frontmatter"

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_skill_has_allowed_tools(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        assert "allowed-tools:" in content, f"{skill_name} missing allowed-tools in frontmatter"


class TestSkillBody:
    """Verify skill files have meaningful body content."""

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_skill_body_not_empty(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        parts = content.split("---", 2)
        body = parts[2].strip() if len(parts) >= 3 else ""
        assert len(body) > 100, f"{skill_name} body is too short ({len(body)} chars)"

    @pytest.mark.parametrize("skill_name", ALL_SKILLS)
    def test_skill_has_markdown_heading(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        parts = content.split("---", 2)
        body = parts[2] if len(parts) >= 3 else ""
        assert "# " in body, f"{skill_name} missing markdown heading in body"


class TestSkillSideEffects:
    """Verify side-effect declarations are correct."""

    @pytest.mark.parametrize("skill_name", ["sync", "done", "landed"])
    def test_side_effect_skills_disable_model_invocation(self, skill_name: str) -> None:
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
        parts = content.split("---", 2)
        frontmatter = parts[1] if len(parts) >= 3 else ""
        assert "disable-model-invocation: true" in frontmatter, (
            f"{skill_name} should have disable-model-invocation: true (has side effects)"
        )

    def test_design_allows_model_invocation(self) -> None:
        content = (SKILLS_DIR / "design" / "SKILL.md").read_text(encoding="utf-8")
        parts = content.split("---", 2)
        frontmatter = parts[1] if len(parts) >= 3 else ""
        assert "disable-model-invocation" not in frontmatter, (
            "design should NOT have disable-model-invocation (intentionally model-invocable)"
        )


class TestSkillContent:
    """Verify specific content per skill."""

    # /sync
    def test_sync_runs_git_fetch(self) -> None:
        content = (SKILLS_DIR / "sync" / "SKILL.md").read_text(encoding="utf-8")
        assert "git fetch" in content, "sync should run git fetch"

    def test_sync_checks_git_status(self) -> None:
        content = (SKILLS_DIR / "sync" / "SKILL.md").read_text(encoding="utf-8")
        assert "git status" in content, "sync should check git status"

    def test_sync_shows_recent_commits(self) -> None:
        content = (SKILLS_DIR / "sync" / "SKILL.md").read_text(encoding="utf-8")
        assert "git log" in content, "sync should show recent commits"

    # /design
    def test_design_reads_decisions(self) -> None:
        content = (SKILLS_DIR / "design" / "SKILL.md").read_text(encoding="utf-8")
        assert "DECISIONS.md" in content, "design should read DECISIONS.md"

    def test_design_reads_implementation_plan(self) -> None:
        content = (SKILLS_DIR / "design" / "SKILL.md").read_text(encoding="utf-8")
        assert "IMPLEMENTATION_PLAN.md" in content, "design should read IMPLEMENTATION_PLAN.md"

    def test_design_classifies_scope(self) -> None:
        content = (SKILLS_DIR / "design" / "SKILL.md").read_text(encoding="utf-8")
        assert "**Q** (Quick)" in content and "**S** (Standard)" in content and "**P** (Project)" in content, (
            "design should classify scope as Q/S/P with descriptive labels"
        )

    def test_design_has_argument_hint(self) -> None:
        content = (SKILLS_DIR / "design" / "SKILL.md").read_text(encoding="utf-8")
        assert "argument-hint:" in content, "design should have argument-hint in frontmatter"

    # /done
    def test_done_has_four_phases(self) -> None:
        content = (SKILLS_DIR / "done" / "SKILL.md").read_text(encoding="utf-8")
        assert "Phase 1" in content, "done should have Phase 1 (Detect)"
        assert "Phase 2" in content, "done should have Phase 2 (Validate)"
        assert "Phase 3" in content, "done should have Phase 3 (Ship/Land/Deliver)"
        assert "Phase 4" in content, "done should have Phase 4 (Document)"

    def test_done_references_agents(self) -> None:
        content = (SKILLS_DIR / "done" / "SKILL.md").read_text(encoding="utf-8")
        assert "code-quality-validator" in content, "done should reference code-quality-validator agent"
        assert "test-coverage-validator" in content, "done should reference test-coverage-validator agent"
        assert "pr-writer" in content, "done should reference pr-writer agent"

    def test_done_has_blocker_tier(self) -> None:
        content = (SKILLS_DIR / "done" / "SKILL.md").read_text(encoding="utf-8")
        assert "Blocker" in content, "done should have Blockers validation tier"

    def test_done_has_high_priority_tier(self) -> None:
        content = (SKILLS_DIR / "done" / "SKILL.md").read_text(encoding="utf-8")
        assert "High Priority" in content, "done should have High Priority validation tier"

    def test_done_has_recommended_tier(self) -> None:
        content = (SKILLS_DIR / "done" / "SKILL.md").read_text(encoding="utf-8")
        assert "Recommended" in content, "done should have Recommended validation tier"

    def test_done_checks_secrets(self) -> None:
        content = (SKILLS_DIR / "done" / "SKILL.md").read_text(encoding="utf-8")
        assert "secret" in content.lower(), "done should scan for secrets"

    def test_done_checks_debug_code(self) -> None:
        content = (SKILLS_DIR / "done" / "SKILL.md").read_text(encoding="utf-8")
        assert "breakpoint()" in content, "done should check for breakpoint()"
        assert "pdb" in content, "done should check for pdb"

    def test_done_updates_changelog(self) -> None:
        content = (SKILLS_DIR / "done" / "SKILL.md").read_text(encoding="utf-8")
        assert "CHANGELOG.md" in content, "done should update CHANGELOG.md"

    def test_done_updates_decisions(self) -> None:
        content = (SKILLS_DIR / "done" / "SKILL.md").read_text(encoding="utf-8")
        assert "DECISIONS.md" in content, "done should update DECISIONS.md"

    def test_done_has_scope_detection(self) -> None:
        content = (SKILLS_DIR / "done" / "SKILL.md").read_text(encoding="utf-8")
        assert "ship" in content.lower(), "done should describe Q=ship"
        assert "land" in content.lower(), "done should describe S=land"
        assert "deliver" in content.lower(), "done should describe P=deliver"

    # /landed
    def test_landed_detects_merged_pr(self) -> None:
        content = (SKILLS_DIR / "landed" / "SKILL.md").read_text(encoding="utf-8")
        assert "gh pr list" in content, "landed should detect merged PR"

    def test_landed_verifies_ci(self) -> None:
        content = (SKILLS_DIR / "landed" / "SKILL.md").read_text(encoding="utf-8")
        assert "gh run" in content, "landed should verify CI runs"

    def test_landed_cleans_branches(self) -> None:
        content = (SKILLS_DIR / "landed" / "SKILL.md").read_text(encoding="utf-8")
        assert "git branch -d" in content, "landed should clean up branches"

    def test_landed_checks_deployment(self) -> None:
        content = (SKILLS_DIR / "landed" / "SKILL.md").read_text(encoding="utf-8")
        assert "deploy.json" in content, "landed should check deployment config"

    def test_landed_checks_next_phase(self) -> None:
        content = (SKILLS_DIR / "landed" / "SKILL.md").read_text(encoding="utf-8")
        assert "IMPLEMENTATION_PLAN" in content, "landed should check for next phase"

    def test_landed_produces_summary(self) -> None:
        content = (SKILLS_DIR / "landed" / "SKILL.md").read_text(encoding="utf-8")
        assert "# Landed" in content, "landed should produce a summary report"
