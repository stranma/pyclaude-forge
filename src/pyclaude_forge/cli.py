"""CLI entry point for pyclaude-forge."""

from __future__ import annotations

import argparse
import sys

from pyclaude_forge import __version__
from pyclaude_forge.installer import install, uninstall, update


def _print_actions(actions: list[str]) -> None:
    for action in actions:
        print(f"  {action}")


def cmd_install(args: argparse.Namespace) -> int:
    scope = "global" if args.global_install else "local"
    target = "~/.claude/" if args.global_install else "./.claude/"
    print(f"Installing pyclaude-forge v{__version__} ({scope}) to {target}")

    actions = install(global_install=args.global_install, force=args.force)
    _print_actions(actions)

    skipped = sum(1 for a in actions if a.startswith("SKIP:"))
    if skipped:
        print(f"\n{skipped} file(s) skipped. Use --force to overwrite.")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    scope = "global" if args.global_install else "local"
    print(f"Updating pyclaude-forge ({scope})...")

    actions = update(global_install=args.global_install)
    _print_actions(actions)

    if any(a.startswith("ERROR:") for a in actions):
        return 1
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    scope = "global" if args.global_install else "local"
    print(f"Uninstalling pyclaude-forge ({scope})...")

    actions = uninstall(global_install=args.global_install)
    _print_actions(actions)

    if any(a.startswith("ERROR:") for a in actions):
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pyclaude-forge",
        description="Install Claude Code workflow (skills, agents, rules, hooks) into your project.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # install
    p_install = sub.add_parser("install", help="Install workflow files")
    p_install.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Install to ~/.claude/ instead of ./.claude/",
    )
    p_install.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )

    # update
    p_update = sub.add_parser("update", help="Update previously installed files")
    p_update.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Update ~/.claude/ instead of ./.claude/",
    )

    # uninstall
    p_uninstall = sub.add_parser("uninstall", help="Remove installed files")
    p_uninstall.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Uninstall from ~/.claude/ instead of ./.claude/",
    )

    args = parser.parse_args(argv)

    commands = {
        "install": cmd_install,
        "update": cmd_update,
        "uninstall": cmd_uninstall,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
