"""Design-standards rule engine.

Manifest-driven checks that enforce one canonical way to shape a UI/design
surface, mirroring the slop-be-gone contract so it drops into the same gates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

RULE_TYPES = frozenset(
    {
        "inline-styles",
        "single-h1",
        "filename-case",
        "max-exports",
    }
)

_MARKUP = (".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte")
_SCRIPT = (".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx")
_SKIP_DIRS = frozenset({".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"})


@dataclass
class Violation:
    rule_id: str
    path: str
    line: int | None
    message: str
    severity: str = "error"


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def _line_of(content: str, index: int) -> int:
    return content.count("\n", 0, index) + 1


def _inline_styles(rule: dict, rel: str, content: str) -> list[Violation]:
    if not rel.endswith(_MARKUP):
        return []
    hits = list(re.finditer(r"style\s*=\s*['\"]", content, re.IGNORECASE))
    rule_id = rule.get("id", "inline-styles")
    message = "inline style attribute; move it into a stylesheet"
    return [Violation(rule_id, rel, _line_of(content, m.start()), message) for m in hits]


def _single_h1(rule: dict, rel: str, content: str) -> list[Violation]:
    if not rel.endswith((".html", ".htm")):
        return []
    count = len(re.findall(r"<h1\b", content, re.IGNORECASE))
    if count == 1:
        return []
    rule_id = rule.get("id", "single-h1")
    return [Violation(rule_id, rel, None, f"expected exactly one <h1>, found {count}")]


def _max_exports(rule: dict, rel: str, content: str) -> list[Violation]:
    if not rel.endswith(_SCRIPT):
        return []
    limit = int(rule.get("max_exports", 8))
    count = len(re.findall(r"^\s*export\b", content, re.MULTILINE))
    if count <= limit:
        return []
    rule_id = rule.get("id", "max-exports")
    return [Violation(rule_id, rel, None, f"{count} exports exceeds {limit}; split the module")]


_CONTENT_RULES = {
    "inline-styles": _inline_styles,
    "single-h1": _single_h1,
    "max-exports": _max_exports,
}


def iter_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        files.append(path)
    return sorted(files)


def _stem_style(stem: str) -> str | None:
    if "-" in stem:
        return "kebab"
    if "_" in stem:
        return "snake"
    return None


def _filename_case(rule: dict, root: Path, files: list[Path]) -> list[Violation]:
    rule_id = rule.get("id", "filename-case")
    by_dir: dict[Path, set[str]] = {}
    for path in files:
        style = _stem_style(path.stem)
        if style is not None:
            by_dir.setdefault(path.parent, set()).add(style)
    out: list[Violation] = []
    for directory, styles in sorted(by_dir.items()):
        if len(styles) > 1:
            rel = directory.relative_to(root).as_posix() or "."
            joined = " and ".join(sorted(styles))
            out.append(Violation(rule_id, rel, None, f"mixed filename case ({joined})"))
    return out


class RuleEngine:
    def __init__(self, manifest: dict):
        self.rules = [r for r in manifest.get("rules", []) if r.get("enabled", True)]

    def scan(self, root: Path, strict: bool = False) -> list[Violation]:
        files = iter_files(root)
        contents = {path: _read(path) for path in files}
        violations: list[Violation] = []
        for rule in self.rules:
            violations.extend(self._apply(rule, root, files, contents))
        if strict:
            return violations
        return [v for v in violations if v.severity == "error"]

    def _apply(self, rule, root, files, contents) -> list[Violation]:
        rule_type = rule.get("type")
        severity = rule.get("severity", "error")
        handler = _CONTENT_RULES.get(rule_type)
        found: list[Violation] = []
        if handler is not None:
            for path in files:
                text = contents.get(path)
                if text is not None:
                    found.extend(handler(rule, path.relative_to(root).as_posix(), text))
        elif rule_type == "filename-case":
            found.extend(_filename_case(rule, root, files))
        for violation in found:
            violation.severity = severity
        return found


def validate_manifest(manifest: dict) -> list[str]:
    problems: list[str] = []
    rules = manifest.get("rules")
    if not isinstance(rules, list) or not rules:
        return ["manifest must define a non-empty 'rules' array"]
    for index, rule in enumerate(rules):
        label = rule.get("id", f"rule[{index}]")
        if rule.get("type") not in RULE_TYPES:
            problems.append(f"{label}: unknown rule type {rule.get('type')!r}")
        if rule.get("severity", "error") not in {"error", "warning"}:
            problems.append(f"{label}: severity must be error or warning")
    return problems
