"""Tests for pyclaude_forge.cli -- CLI argument parsing and commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pyclaude_forge.cli import main
from pyclaude_forge.installer import MANIFEST_NAME


class TestCliInstall:
    def test_install_returns_zero(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        assert main(["install"]) == 0

    def test_install_creates_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        main(["install"])
        assert (tmp_path / ".claude" / MANIFEST_NAME).exists()
        assert (tmp_path / ".claude" / "settings.json").exists()

    def test_install_force(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        main(["install"])
        # Second install with --force should succeed.
        assert main(["install", "--force"]) == 0

    def test_install_global(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        assert main(["install", "--global"]) == 0
        assert (tmp_path / ".claude" / MANIFEST_NAME).exists()


class TestCliUpdate:
    def test_update_without_install_returns_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        assert main(["update"]) == 1

    def test_update_after_install_returns_zero(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        main(["install"])
        assert main(["update"]) == 0


class TestCliUninstall:
    def test_uninstall_without_install_returns_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        assert main(["uninstall"]) == 1

    def test_uninstall_after_install_returns_zero(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        main(["install"])
        assert main(["uninstall"]) == 0

    def test_uninstall_removes_manifest(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        main(["install"])
        main(["uninstall"])
        assert not (tmp_path / ".claude" / MANIFEST_NAME).exists()


class TestCliVersion:
    def test_version_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit, match="0"):
            main(["--version"])
        captured = capsys.readouterr()
        assert "pyclaude-forge" in captured.out


class TestCliNoCommand:
    def test_no_command_exits_with_error(self) -> None:
        with pytest.raises(SystemExit, match="2"):
            main([])
