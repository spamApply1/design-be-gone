"""Tests for the design-be-gone engine and CLI."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from dbg.cli import main
from dbg.engine import RuleEngine, validate_manifest

_MANIFEST = {
    "rules": [
        {"id": "inline-styles", "type": "inline-styles", "severity": "error"},
        {"id": "single-h1", "type": "single-h1", "severity": "error"},
        {"id": "filename-case", "type": "filename-case", "severity": "error"},
        {"id": "max-exports", "type": "max-exports", "severity": "error", "max_exports": 2},
    ]
}


class EngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())

    def _write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def _scan(self) -> list:
        return RuleEngine(_MANIFEST).scan(self.root, strict=True)

    def test_inline_styles_flagged(self) -> None:
        self._write("page.html", '<h1>Hi</h1><div style="color:red">x</div>')
        ids = {v.rule_id for v in self._scan()}
        self.assertIn("inline-styles", ids)

    def test_single_h1_enforced(self) -> None:
        self._write("a.html", "<h1>one</h1><h1>two</h1>")
        ids = {v.rule_id for v in self._scan()}
        self.assertIn("single-h1", ids)

    def test_clean_html_passes(self) -> None:
        self._write("ok.html", "<h1>title</h1><p>body</p>")
        self.assertEqual([v for v in self._scan() if v.rule_id != "filename-case"], [])

    def test_mixed_filename_case_flagged(self) -> None:
        self._write("a_b.js", "export const x = 1;")
        self._write("c-d.js", "export const y = 2;")
        ids = {v.rule_id for v in self._scan()}
        self.assertIn("filename-case", ids)

    def test_max_exports_flagged(self) -> None:
        self._write("mod.js", "export a\nexport b\nexport c\n")
        ids = {v.rule_id for v in self._scan()}
        self.assertIn("max-exports", ids)


class ManifestTests(unittest.TestCase):
    def test_valid_manifest(self) -> None:
        self.assertEqual(validate_manifest(_MANIFEST), [])

    def test_unknown_type_rejected(self) -> None:
        problems = validate_manifest({"rules": [{"id": "x", "type": "bogus"}]})
        self.assertTrue(problems)


class CliTests(unittest.TestCase):
    def test_clean_tree_exits_zero(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / "ok.html").write_text("<h1>t</h1>", encoding="utf-8")
        code = main(["check", str(root), "--json"])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
