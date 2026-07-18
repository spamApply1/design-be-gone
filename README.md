# design-be-gone (dbg)

**Stop AI-generated UI drift before it becomes a design system crime scene.**

`design-be-gone` is a manifest-driven design-standards gate for agentic
codebases: repos where humans write intent and agents write a lot of the code.
When generated UI scales, tiny inconsistencies multiply into archaeology.
`dbg` makes the boring design rules executable, local, and loud enough to catch
drift before review.

## ⚡ Quickstart

```bash
python3 -m pip install -e .
PYTHONPATH="$PWD" python3 -m dbg.cli check . --json --strict
```

Clean output is intentionally boring:

```json
[]
```

Validate the manifest you are about to enforce:

```bash
PYTHONPATH="$PWD" python3 -m dbg.cli validate --manifest dbg/data/default_manifest.json
# Manifest is valid.
```

Use your own policy file when your repo has stronger opinions:

```bash
PYTHONPATH="$PWD" python3 -m dbg.cli check path/to/project \
  --manifest my-design-manifest.json --json --strict
```

## 🧱 What it enforces

Every bundled rule is enabled at `error` severity in
`dbg/data/default_manifest.json`.

| Rule | What fails | Why nerds care |
| --- | --- | --- |
| `inline-styles` | `style=` attributes in HTML, JSX, TSX, Vue, or Svelte markup | Styling stays in one channel instead of leaking into every node. |
| `single-h1` | HTML documents with zero or multiple `<h1>` elements | One canonical document outline for accessibility and SEO sanity. |
| `filename-case` | Directories that mix `snake_case` and `kebab-case` filenames | Naming bikesheds become a failing check, not a review thread. |
| `max-exports` | JS/TS modules exporting more than `max_exports` items | Public surfaces stay small enough for agents and humans to reason about. |

## 🧠 How it works

- The CLI contract mirrors the sibling gates: `check`, `--manifest`, `--json`,
  and `--strict`.
- The engine walks the repo, skips common generated/vendor directories, and
  applies only the rules enabled in the manifest.
- Content checks are lightweight text/regex passes over relevant file types;
  `filename-case` is computed per directory.
- Exit code `0` means clean. Exit code `1` means at least one blocking violation.
  With `--strict`, warnings would block too.
- It is local-first: no hosted service required, no account signup, no dashboard
  dependency.

## 🧬 Part of the be-gone ecosystem

The family is a set of small, composable enforcement gates for codebases where
AI agents generate large chunks of the tree:

- [slop-be-gone](https://github.com/spamApply1/slop-be-gone) — code hygiene:
  comments, file shape, Python traps, secrets, debug leftovers, and more.
- [design-be-gone](https://github.com/spamApply1/design-be-gone) — design
  standards: markup shape, heading discipline, filename case, and exports.
- [chaos-be-gone](https://github.com/spamApply1/chaos-be-gone) — workflow
  sanity: CI, hooks, ignore files, README presence, and workflow secret checks.

They share the same mental model: write the standard once, run it everywhere,
and make drift fail early.

## 🧾 Manifest shape

A manifest is a JSON object with a non-empty `rules` array:

```json
{
  "version": 1,
  "rules": [
    { "id": "inline-styles", "type": "inline-styles", "enabled": true },
    { "id": "max-exports", "type": "max-exports", "max_exports": 8 }
  ]
}
```

Each rule supports `enabled` and `severity` (`error` or `warning`). Unknown rule
kinds fail manifest validation instead of silently doing nothing.

## 🧪 Development

```bash
PYTHONPATH="$PWD" python3 -m unittest discover -s tests -t .
PYTHONPATH="$PWD" python3 -m dbg.cli check . --json --strict
```

## 🧭 Philosophy

The north star is brutally simple: define reality with standards and intent.
Push enforcement outward until there is one canonical way for each thing to
exist, then let humans and local agents move fast inside that rail.

If that sounds useful, ⭐ star the repo, run it on a messy UI tree, and compose a
manifest that matches your taste.
