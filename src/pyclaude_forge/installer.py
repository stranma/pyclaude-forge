"""Core install/update/uninstall logic for pyclaude-forge."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from pyclaude_forge import __version__

MANIFEST_NAME = ".pyclaude-forge-manifest.json"

# Files that get appended to existing content instead of skipped.
APPENDABLE_FILES = {"CLAUDE.md", "DEVELOPMENT_PROCESS.md"}

# Separator inserted before appended content.
APPEND_SEPARATOR = "\n\n<!-- pyclaude-forge -->\n"


def _data_dir() -> Path:
    """Return the path to the bundled data directory."""
    return Path(__file__).parent / "data"


def _collect_data_files() -> list[str]:
    """Return relative paths of all files in data/, using forward slashes."""
    data = _data_dir()
    files: list[str] = []
    for path in sorted(data.rglob("*")):
        if path.is_file():
            files.append(path.relative_to(data).as_posix())
    return files


def _target_dir(global_install: bool) -> Path:
    """Return the target .claude/ directory."""
    if global_install:
        return Path.home() / ".claude"
    return Path.cwd() / ".claude"


def _docs_dir(global_install: bool) -> Path:
    """Return the target docs/ directory (for DEVELOPMENT_PROCESS.md)."""
    if global_install:
        return Path.home() / "docs"
    return Path.cwd() / "docs"


def _resolve_target(rel_path: str, global_install: bool) -> Path:
    """Map a data-relative path to its install target."""
    if rel_path == "CLAUDE.md":
        if global_install:
            return Path.home() / "CLAUDE.md"
        return Path.cwd() / "CLAUDE.md"
    if rel_path == "DEVELOPMENT_PROCESS.md":
        return _docs_dir(global_install) / "DEVELOPMENT_PROCESS.md"
    return _target_dir(global_install) / rel_path


def _is_appendable(rel_path: str) -> bool:
    return Path(rel_path).name in APPENDABLE_FILES


def _read_manifest(target_claude_dir: Path) -> dict | None:
    manifest_path = target_claude_dir / MANIFEST_NAME
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return None


def _write_manifest(
    target_claude_dir: Path,
    installed_files: list[str],
    scope: str,
) -> None:
    target_claude_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": __version__,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "scope": scope,
        "files": sorted(installed_files),
    }
    manifest_path = target_claude_dir / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def install(*, global_install: bool = False, force: bool = False) -> list[str]:
    """Install pyclaude-forge files to the target directory.

    :param global_install: If True, install to ~/.claude/ instead of ./.claude/.
    :param force: If True, overwrite existing files.
    :returns: List of actions taken (for display).
    """
    data = _data_dir()
    all_files = _collect_data_files()
    target_claude_dir = _target_dir(global_install)
    actions: list[str] = []
    installed: list[str] = []

    for rel_path in all_files:
        src = data / rel_path
        dst = _resolve_target(rel_path, global_install)

        if dst.exists() and not force:
            if _is_appendable(rel_path):
                content = src.read_text(encoding="utf-8")
                existing = dst.read_text(encoding="utf-8")
                if content.strip() in existing:
                    actions.append(f"SKIP: {rel_path} -- content already present")
                else:
                    with open(dst, "a", encoding="utf-8") as f:
                        f.write(APPEND_SEPARATOR)
                        f.write(content)
                    actions.append(f"APPEND: {rel_path}")
                installed.append(rel_path)
            else:
                actions.append(f"SKIP: {rel_path} exists -- merge manually")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            verb = "OVERWRITE" if dst.exists() and force else "INSTALL"
            actions.append(f"{verb}: {rel_path}")
            installed.append(rel_path)

    scope = "global" if global_install else "local"
    _write_manifest(target_claude_dir, installed, scope)
    actions.append(f"MANIFEST: wrote {MANIFEST_NAME}")

    return actions


def update(*, global_install: bool = False) -> list[str]:
    """Update previously installed files (per manifest).

    :param global_install: If True, update ~/.claude/ instead of ./.claude/.
    :returns: List of actions taken.
    """
    target_claude_dir = _target_dir(global_install)
    manifest = _read_manifest(target_claude_dir)
    if manifest is None:
        return ["ERROR: no manifest found -- run 'pyclaude-forge install' first"]

    data = _data_dir()
    actions: list[str] = []
    updated: list[str] = []

    for rel_path in manifest["files"]:
        src = data / rel_path
        if not src.exists():
            actions.append(f"SKIP: {rel_path} -- no longer in package")
            continue

        dst = _resolve_target(rel_path, global_install)
        if _is_appendable(rel_path):
            # For appendable files, replace the appended section.
            content = src.read_text(encoding="utf-8")
            if dst.exists():
                existing = dst.read_text(encoding="utf-8")
                if APPEND_SEPARATOR in existing:
                    # Replace everything after the separator marker.
                    base = existing.split(APPEND_SEPARATOR)[0]
                    dst.write_text(
                        base + APPEND_SEPARATOR + content, encoding="utf-8"
                    )
                    actions.append(f"UPDATE: {rel_path} (replaced appended section)")
                else:
                    with open(dst, "a", encoding="utf-8") as f:
                        f.write(APPEND_SEPARATOR)
                        f.write(content)
                    actions.append(f"APPEND: {rel_path}")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                actions.append(f"INSTALL: {rel_path}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            actions.append(f"UPDATE: {rel_path}")

        updated.append(rel_path)

    # Check for new files not in old manifest.
    all_files = _collect_data_files()
    new_files = [f for f in all_files if f not in manifest["files"]]
    for rel_path in new_files:
        dst = _resolve_target(rel_path, global_install)
        if dst.exists():
            actions.append(f"NEW (skipped): {rel_path} exists -- merge manually")
        else:
            src = data / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            actions.append(f"NEW: {rel_path}")
            updated.append(rel_path)

    scope = "global" if global_install else "local"
    _write_manifest(target_claude_dir, updated, scope)
    actions.append(f"MANIFEST: updated {MANIFEST_NAME}")

    return actions


def uninstall(*, global_install: bool = False) -> list[str]:
    """Remove previously installed files (per manifest).

    :param global_install: If True, uninstall from ~/.claude/ instead of ./.claude/.
    :returns: List of actions taken.
    """
    target_claude_dir = _target_dir(global_install)
    manifest = _read_manifest(target_claude_dir)
    if manifest is None:
        return ["ERROR: no manifest found -- nothing to uninstall"]

    data = _data_dir()
    actions: list[str] = []

    for rel_path in manifest["files"]:
        dst = _resolve_target(rel_path, global_install)
        if _is_appendable(rel_path):
            if dst.exists():
                existing = dst.read_text(encoding="utf-8")
                src = data / rel_path
                source_content = src.read_text(encoding="utf-8").strip()
                if APPEND_SEPARATOR in existing:
                    base = existing.split(APPEND_SEPARATOR)[0].rstrip()
                    if base:
                        dst.write_text(base + "\n", encoding="utf-8")
                        actions.append(
                            f"REMOVE (appended section): {rel_path}"
                        )
                    else:
                        dst.unlink()
                        actions.append(f"REMOVE: {rel_path}")
                elif existing.strip() == source_content:
                    dst.unlink()
                    actions.append(f"REMOVE: {rel_path}")
                else:
                    actions.append(
                        f"SKIP: {rel_path} -- has custom content, remove manually"
                    )
            else:
                actions.append(f"SKIP: {rel_path} -- not found")
        else:
            if dst.exists():
                dst.unlink()
                actions.append(f"REMOVE: {rel_path}")
            else:
                actions.append(f"SKIP: {rel_path} -- not found")

    # Remove empty directories left behind.
    _cleanup_empty_dirs(target_claude_dir)

    # Remove the manifest itself.
    manifest_path = target_claude_dir / MANIFEST_NAME
    if manifest_path.exists():
        manifest_path.unlink()
        actions.append(f"REMOVE: {MANIFEST_NAME}")

    return actions


def _cleanup_empty_dirs(root: Path) -> None:
    """Remove empty directories under root, bottom-up."""
    if not root.is_dir():
        return
    for dirpath in sorted(root.rglob("*"), reverse=True):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            dirpath.rmdir()
