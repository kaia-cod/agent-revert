"""Tests for snapshot pinning and retention pruning visibility."""
from pathlib import Path

import pytest

from agent_revert.store import Store


@pytest.fixture()
def project(tmp_path: Path):
    root = tmp_path / "proj"
    root.mkdir()
    (root / "app.py").write_text("v0\n")
    return root


def test_pin_protects_snapshot_from_prune(project):
    store = Store(project / "store", max_snapshots=2)
    a = store.snapshot(project, label="known good")
    store.pin(a["id"])
    for i, label in enumerate(("b", "c", "d"), start=1):
        (project / "app.py").write_text(f"v{i}\n")
        store.snapshot(project, label=label)

    ids = {s["id"] for s in store.list_snapshots()}
    assert a["id"] in ids, "pinned snapshot must survive retention"
    # pinned is exempt from the quota: newest 2 unpinned (c, d) are kept,
    # the oldest unpinned (b) is dropped
    kept_labels = [s.get("label") for s in store.list_snapshots()]
    assert kept_labels == ["known good", "c", "d"], kept_labels
    assert len(store.last_pruned) == 1


def test_unpin_allows_prune_again(project):
    store = Store(project / "store", max_snapshots=2)
    a = store.snapshot(project, label="a")
    store.pin(a["id"])
    store.unpin(a["id"])
    (project / "app.py").write_text("v1\n")
    store.snapshot(project, label="b")
    (project / "app.py").write_text("v2\n")
    store.snapshot(project, label="c")

    ids = {s["id"] for s in store.list_snapshots()}
    assert a["id"] not in ids, "unpinned snapshot is prunable again"


def test_pin_is_idempotent(project):
    store = Store(project / "store")
    snap = store.snapshot(project)
    assert store.pin(snap["id"])["pinned"] is True
    assert store.pin(snap["id"])["pinned"] is True
    assert store.unpin(snap["id"])["pinned"] is False
    assert "pinned" not in store.get(snap["id"]) or store.get(snap["id"])["pinned"] is False


def test_pin_unknown_id_raises(project):
    store = Store(project / "store")
    with pytest.raises(KeyError):
        store.pin("nope")


def test_pruned_blobs_do_not_break_pinned_revert(project):
    """Reverting to a pinned snapshot must work even after other prunes."""
    store = Store(project / "store", max_snapshots=1)
    a = store.snapshot(project, label="pinned")
    store.pin(a["id"])
    (project / "app.py").write_text("v1\n")
    store.snapshot(project, label="b")  # prunes 'a' would-be, but pinned
    store.revert(a, project)
    assert (project / "app.py").read_text() == "v0\n"
