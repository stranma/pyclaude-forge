"""Tests for pyclaude_forge.installer -- install/update/uninstall logic."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pyclaude_forge import __version__
from pyclaude_forge.installer import (
    APPEND_SEPARATOR,
    MANIFEST_NAME,
    _collect_data_files,
    _data_dir,
    install,
    uninstall,
    update,
)


class TestDataDir:
    def test_data_dir_exists(self) -> None:
        assert _data_dir().is_dir()

    def test_data_dir_has_skills(self) -> None:
        assert (_data_dir() / "skills").is_dir()

    def test_data_dir_has_agents(self) -> None:
        assert (_data_dir() / "agents").is_dir()

    def test_data_dir_has_rules(self) -> None:
        assert (_data_dir() / "rules").is_dir()

    def test_data_dir_has_hooks(self) -> None:
        assert (_data_dir() / "hooks").is_dir()

    def test_collect_data_files_returns_list(self) -> None:
        files = _collect_data_files()
        assert len(files) > 0
        assert all(isinstance(f, str) for f in files)

    def test_collect_data_files_uses_forward_slashes(self) -> None:
        files = _collect_data_files()
        for f in files:
            assert "\\" not in f, f"Backslash in path: {f}"


class TestInstall:
    def test_install_creates_claude_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        install()
        assert (tmp_path / ".claude").is_dir()

    def test_install_copies_all_data_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        install()
        data_files = _collect_data_files()
        for f in data_files:
            if f in ("CLAUDE.md", "DEVELOPMENT_PROCESS.md"):
                continue
            assert (tmp_path / ".claude" / f).exists(), f"Missing: {f}"

    def test_install_creates_claude_md(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        install()
        assert (tmp_path / "CLAUDE.md").exists()

    def test_install_creates_development_process(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        install()
        assert (tmp_path / "docs" / "DEVELOPMENT_PROCESS.md").exists()

    def test_install_creates_manifest(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        install()
        manifest_path = tmp_path / ".claude" / MANIFEST_NAME
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["version"] == __version__
        assert manifest["scope"] == "local"
        assert len(manifest["files"]) > 0

    def test_install_skips_existing_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        # Pre-create a file that would be installed.
        settings_dir = tmp_path / ".claude"
        settings_dir.mkdir()
        settings_file = settings_dir / "settings.json"
        settings_file.write_text('{"custom": true}', encoding="utf-8")

        actions = install()

        skip_actions = [a for a in actions if a.startswith("SKIP:") and "settings.json" in a]
        assert len(skip_actions) == 1
        # Original content preserved.
        assert json.loads(settings_file.read_text(encoding="utf-8")) == {"custom": True}

    def test_install_force_overwrites(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        settings_dir = tmp_path / ".claude"
        settings_dir.mkdir()
        settings_file = settings_dir / "settings.json"
        settings_file.write_text('{"custom": true}', encoding="utf-8")

        install(force=True)

        content = json.loads(settings_file.read_text(encoding="utf-8"))
        assert "custom" not in content

    def test_install_appends_to_existing_claude_md(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        existing_content = "# My Project\n\nExisting content.\n"
        (tmp_path / "CLAUDE.md").write_text(existing_content, encoding="utf-8")

        install()

        result = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
        assert result.startswith("# My Project")
        assert APPEND_SEPARATOR in result
        assert "Development Process" in result

    def test_install_skips_append_if_content_already_present(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        # First install.
        install()
        first_content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
        # Second install should not double-append.
        install()
        second_content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
        assert second_content == first_content

    def test_install_global(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        install(global_install=True)
        assert (tmp_path / ".claude").is_dir()
        manifest = json.loads(
            (tmp_path / ".claude" / MANIFEST_NAME).read_text(encoding="utf-8")
        )
        assert manifest["scope"] == "global"


class TestUpdate:
    def test_update_without_manifest_returns_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        actions = update()
        assert any("ERROR" in a for a in actions)

    def test_update_refreshes_installed_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        install()
        # Corrupt an installed file.
        settings = tmp_path / ".claude" / "settings.json"
        settings.write_text("{}", encoding="utf-8")

        actions = update()

        assert any("UPDATE" in a for a in actions)
        content = json.loads(settings.read_text(encoding="utf-8"))
        assert content != {}

    def test_update_replaces_appended_section(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        existing = "# Project\n\nCustom content.\n"
        (tmp_path / "CLAUDE.md").write_text(existing, encoding="utf-8")
        install()

        # Verify append happened.
        after_install = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
        assert APPEND_SEPARATOR in after_install

        # Update should replace the appended section, not duplicate it.
        update()
        after_update = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
        assert after_update.count(APPEND_SEPARATOR) == 1
        assert after_update.startswith("# Project")


class TestUninstall:
    def test_uninstall_without_manifest_returns_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        actions = uninstall()
        assert any("ERROR" in a for a in actions)

    def test_uninstall_removes_installed_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        install()
        assert (tmp_path / ".claude" / "settings.json").exists()

        uninstall()

        assert not (tmp_path / ".claude" / "settings.json").exists()

    def test_uninstall_removes_manifest(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        install()
        uninstall()
        assert not (tmp_path / ".claude" / MANIFEST_NAME).exists()

    def test_uninstall_removes_appended_section_from_claude_md(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        existing = "# Project\n\nCustom content.\n"
        (tmp_path / "CLAUDE.md").write_text(existing, encoding="utf-8")
        install()
        uninstall()

        result = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
        assert APPEND_SEPARATOR not in result
        assert "# Project" in result
        assert "Custom content." in result

    def test_uninstall_deletes_claude_md_if_only_forge_content(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        install()
        uninstall()
        assert not (tmp_path / "CLAUDE.md").exists()

    def test_uninstall_cleans_empty_directories(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        install()
        uninstall()
        # Skills directory should be gone (was only forge files).
        assert not (tmp_path / ".claude" / "skills").exists()

    def test_full_lifecycle(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Install -> update -> uninstall leaves no trace."""
        monkeypatch.chdir(tmp_path)

        install()
        assert (tmp_path / ".claude" / MANIFEST_NAME).exists()

        update()
        assert (tmp_path / ".claude" / MANIFEST_NAME).exists()

        uninstall()
        # .claude dir may still exist but should have no forge files.
        manifest = tmp_path / ".claude" / MANIFEST_NAME
        assert not manifest.exists()
