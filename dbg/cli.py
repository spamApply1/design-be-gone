"""Command-line entry point for design-be-gone (dbg)."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .engine import RuleEngine, validate_manifest

_DEFAULT_MANIFEST = Path(__file__).resolve().parent / "data" / "default_manifest.json"


def _load_manifest(path: str | None) -> dict:
    manifest_path = Path(path).expanduser() if path else _DEFAULT_MANIFEST
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dbg", description="Design-standards gate.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="scan a tree for design violations")
    check.add_argument("repo_root", help="directory to scan")
    check.add_argument("--manifest", default=None, help="path to a custom manifest")
    check.add_argument("--json", action="store_true", help="emit violations as JSON")
    check.add_argument("--strict", action="store_true", help="fail on warnings too")
    validate = subparsers.add_parser("validate", help="validate a manifest")
    validate.add_argument("--manifest", default=None, help="path to a custom manifest")
    return parser


def _run_check(args: argparse.Namespace) -> int:
    engine = RuleEngine(_load_manifest(args.manifest))
    violations = engine.scan(Path(args.repo_root).expanduser(), strict=args.strict)
    if args.json:
        print(json.dumps([asdict(v) for v in violations], indent=2))
    elif not violations:
        print("No design violations found.")
    else:
        for v in violations:
            location = f"{v.path}:{v.line}" if v.line else v.path
            print(f"{location}: [{v.rule_id}] {v.message}")
    return 1 if violations else 0


def _run_validate(args: argparse.Namespace) -> int:
    problems = validate_manifest(_load_manifest(args.manifest))
    if problems:
        for problem in problems:
            print(problem)
        return 1
    print("Manifest is valid.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "check":
        return _run_check(args)
    return _run_validate(args)


if __name__ == "__main__":
    raise SystemExit(main())
