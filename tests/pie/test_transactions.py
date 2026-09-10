import pytest
import os
import shutil
from fl_studio_mcp.pie.transactions import TransactionManager

def test_garbage_collect(tmp_path):
    manager = TransactionManager()
    # Override paths to use pytest temp directory for safety
    manager.snapshots_dir = str(tmp_path / "snapshots")
    os.makedirs(manager.snapshots_dir, exist_ok=True)

    # Create mock snapshots
    with open(os.path.join(manager.snapshots_dir, "snap1.json"), "w") as f:
        f.write("{}")
    with open(os.path.join(manager.snapshots_dir, "snap2.json"), "w") as f:
        f.write("{}")

    # Create mock project backup
    project_dir = str(tmp_path / "project")
    os.makedirs(project_dir, exist_ok=True)
    with open(os.path.join(project_dir, "test_proj.flp.pie_backup"), "w") as f:
        f.write("binary data")

    # Verify files exist
    assert len(os.listdir(manager.snapshots_dir)) == 2
    assert len(os.listdir(project_dir)) == 1

    # Run garbage collector
    res = manager.garbage_collect(project_dir=project_dir)

    assert res["status"] == "success"
    assert res["deleted_snapshots"] == 2
    assert res["deleted_backups"] == 1

    # Verify files deleted
    assert len(os.listdir(manager.snapshots_dir)) == 0
    assert len(os.listdir(project_dir)) == 0
