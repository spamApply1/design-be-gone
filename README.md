# design-be-gone (dbg)

A manifest-driven **design-standards gate** for agentic codebases — a sibling to
[slop-be-gone](https://github.com/spamApply1/slop-be-gone). Where slop-be-gone
enforces code hygiene, `dbg` enforces **design consistency** so a UI/design
surface has one canonical shape.

It is built to drop into the same gates as slop-be-gone: a `check` subcommand
that scans a tree against a manifest, emits JSON or text, and exits non-zero on
violations.

## Rules

| rule | what it enforces |
| --- | --- |
| `inline-styles` | no inline `style=` attributes — styling lives in stylesheets |
| `single-h1` | every HTML document has exactly one `<h1>` |
| `filename-case` | a directory uses one filename case (no snake/kebab mixing) |
| `max-exports` | a module exposes a bounded public surface |

Every rule ships enabled at `error` severity in the default manifest.

## Usage

```bash
# scan a tree with the bundled default manifest
python3 -m dbg.cli check path/to/project

# machine-readable output for a harness gate
python3 -m dbg.cli check path/to/project --json --strict

# validate a custom manifest
python3 -m dbg.cli validate --manifest my-manifest.json
```

Exit code is `0` when clean and `1` when any violation is found (with
`--strict`, warnings count as failures too).

## Manifest

A manifest is `{"rules": [{"id", "type", "enabled", "severity", ...}]}`. See
`dbg/data/default_manifest.json`. Point `--manifest` at your own to tune
thresholds (for example `max_exports`).

## Tests

```bash
PYTHONPATH="$PWD" python3 -m unittest discover -s tests -t .
```

## Why

This is one repo in a family of standards frameworks. The goal is to keep
pushing enforcement outward — code, design, workflow — until intent itself is
expressible as an executable standard.
