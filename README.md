# agent-revert

**Undo any AI coding agent in one command.**

[![CI](https://github.com/kaia-cod/agent-revert/actions/workflows/ci.yml/badge.svg)](https://github.com/kaia-cod/agent-revert/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Stars](https://img.shields.io/github/stars/kaia-cod/agent-revert?style=social)](https://github.com/kaia-cod/agent-revert/stargazers)

> Your AI coding agent just rewrote your codebase. Git can't help you — those
> files were never committed. `agent-revert` snapshots your working tree
> before the agent runs and restores it in one command.

## Why this exists

Claude Code, Codex, Cursor and friends edit files directly, often without any
commit. When the result is broken, you have no clean way back:

- `git checkout` / `git stash` only cover **committed** (or fully untracked) work
- Most agents run in the same directory you work in, so damage is immediate
- There is no single "undo everything the agent just did" button

`agent-revert` fills exactly that gap: a content-addressed snapshot of your
tree, taken in milliseconds, with `revert`, `timeline`, `status` and `patch`
on top. Zero dependencies, works with or without git, no API key.

## Quick start

```bash
pip install agent-revert        # or: pipx install agent-revert
# or without installing:
#   git clone https://github.com/kaia-cod/agent-revert && cd agent-revert
#   python3 -m agent_revert ...

cd your-project

# 1. snapshot BEFORE the agent runs
agent-revert snapshot --label "before refactor"

# 2. let the agent do its thing... it breaks 3 files

# 3. preview the undo (changes nothing)
agent-revert revert --dry-run

# 4. undo it, for real
agent-revert revert
```

See the full reproducible demo: [`examples/demo.sh`](examples/demo.sh)
(`bash examples/demo.sh` — under 60 seconds, no network, no API key).

## Usage

```
agent-revert [--path DIR] [--store DIR] [--max-snapshots N] <command>

snapshot [--label TEXT]        take a snapshot of DIR
timeline                       list all snapshots (pinned ones are marked)
status [--json]                what changed since the latest snapshot?
revert [--snapshot ID] [--dry-run]
                               restore DIR to a snapshot (default: latest)
pin <ID> / unpin <ID>          protect (or release) a snapshot from pruning
patch [--snapshot ID]          export a unified diff vs a snapshot
```

- `--path` defaults to the current directory.
- `--store` defaults to `<path>/.agent-revert`. To keep the store **out** of
  the tracked tree (recommended), pass a directory outside `--path`, e.g.
  `--store ~/.agent-revert/myproject`. The store is content-addressed
  (`blobs/<sha256>` + `snapshots/<id>.json`), so unchanged files cost nothing
  across snapshots.
- `--max-snapshots` sets the retention limit (default: 5). When the limit is
  exceeded, the **oldest unpinned** snapshots are pruned (the CLI prints what
  was pruned); `--max-snapshots 0` disables pruning entirely.
- **Pinned snapshots are exempt from the limit** and never pruned — pin a
  "known good" state before long agent sessions: `agent-revert pin <ID>`.
- Ignored by default: `.git`, `__pycache__`, `.venv`, `venv`, `.mypy_cache`,
  `.pytest_cache`, `node_modules`.

### Example

```text
$ agent-revert snapshot --label "before agent"
snapshot 3f9a1c2b4d5e  files=128  label='before agent'

$ agent-revert status
snapshot: 3f9a1c2b4d5e (before agent)
added:    2
  + junk.txt
  + src/generated.py
modified: 3
  ~ app.py
  ~ config.yaml
  ~ src/util.py
deleted:  1
  - src/legacy.py

$ agent-revert revert --dry-run
would revert to snapshot 3f9a1c2b4d5e: 2 to remove, 3 to restore, 1 to recreate

$ agent-revert revert
reverted to snapshot 3f9a1c2b4d5e: 2 to remove, 3 to restore, 1 to recreate
```

## Architecture

```
agent_revert/
  __init__.py     version
  store.py        Store: snapshot / list / get / latest / diff / revert / export_patch
  cli.py          argparse CLI (snapshot, timeline, status, revert, patch)
  __main__.py     python -m agent_revert entry point
tests/
  test_store.py         pytest: snapshot→break→dry-run→revert, dedup, empty tree, patch
  test_cli.py           end-to-end CLI tests (full cycle, retention flag, pin/unpin)
  test_store_location.py default store placement (out of tree)
  test_pin_retention.py pin/unpin + retention pruning behavior
examples/
  demo.sh         60-second reproducible demo
```

Design principles:

1. **Stdlib only** — runs anywhere Python ≥ 3.10 runs. No install friction.
2. **Content-addressed** — one blob per unique file content (`sha256`), so
   repeated snapshots are cheap and deduplicated.
3. **Git-agnostic** — works on any directory; git integration is a roadmap
   item, never a requirement.
4. **Safe by default** — `revert --dry-run` previews exactly what will change;
   symlinks/devices/sockets are never followed or tracked.
5. **Bounded retention, explicit escape hatch** — the store keeps the newest
   N snapshots (default 5) and prunes transparently; pin what you want kept.

## Why not ... ?

| Alternative | What it does | Gap vs agent-revert |
|---|---|---|
| `git checkout` / `git stash` | restores committed work | misses uncommitted files — exactly what agents produce |
| LangGraph / Langfuse / Phoenix | agent tracing & time-travel | replays *conversations*, doesn't restore your *filesystem* |
| OrcaReplay | record/replay/fork agent runs | re-executes the agent; slower, model-dependent |
| vibe-revert | TS-based agent undo | different stack, tiny community |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: Python ≥ 3.10, stdlib-first,
`python3 -m pytest`, open an issue or a PR.

## Code of conduct / security

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md) — please do **not** open public issues for vulnerabilities.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Roadmap

Tracked as GitHub issues (see the `Roadmap` column of the project board):
git integration, binary/large-file handling, watch mode, IDE extension,
Windows test matrix.

## License

[MIT](LICENSE) © 2026 kaia-cod contributors.
