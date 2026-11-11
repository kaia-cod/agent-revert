# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- `--max-snapshots N` CLI flag: configure the retention limit without writing
  Python (`--max-snapshots 0` disables pruning). Previously hard-coded to 5.
- `pin <ID>` / `unpin <ID>` CLI commands and `Store.pin()` / `Store.unpin()`:
  pinned snapshots are never dropped by retention pruning, so a "known good"
  state survives unbounded agent runs.
- `timeline` now marks pinned snapshots.
- `snapshot` prints which snapshots (if any) were pruned by the retention
  limit — pruning is no longer silent (`Store.last_pruned` exposes the ids).

## [0.1.0] - 2026-11-11

### Added

- First public release.
- `agent-revert snapshot` / `timeline` / `status` / `revert` / `patch` CLI
  (Python stdlib only, ≥ 3.10).
- Content-addressed snapshot store (sha256 blobs + JSON manifests).
- `revert --dry-run`, `--path` / `--store` options, default ignore list.
- pytest suite (`tests/test_store.py`) and reproducible 60-second demo
  (`examples/demo.sh`).
- GitHub Actions CI, MIT license, contributing/security/code-of-conduct docs.

### Roadmap (not yet implemented)

- Git integration (commit-aware snaps), watch mode, IDE extension,
  large/binary file handling, Windows CI matrix.
