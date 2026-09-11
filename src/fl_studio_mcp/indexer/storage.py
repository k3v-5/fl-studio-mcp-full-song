"""Storage for the sample manifest.

Supports Parquet (fast & compact) when pyarrow is installed, with an automatic
JSON fallback so the MCP server works out of the box in any Python environment.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    HAS_PYARROW = True
except ImportError:
    pa = None
    pq = None
    HAS_PYARROW = False

__all__ = ["MANIFEST_SCHEMA", "save_manifest", "load_manifest", "empty_manifest"]

if HAS_PYARROW:
    MANIFEST_SCHEMA = pa.schema([
        pa.field("path", pa.string()),
        pa.field("filename", pa.string()),
        pa.field("relative_folder", pa.string()),
        pa.field("extension", pa.string()),
        pa.field("size_bytes", pa.int64()),
        pa.field("mtime", pa.int64()),
        pa.field("content_hash", pa.string()),
        pa.field("sample_type", pa.string()),
        pa.field("subtype", pa.string()),
        pa.field("genres", pa.list_(pa.string())),
        pa.field("moods", pa.list_(pa.string())),
        pa.field("key", pa.string()),
        pa.field("bpm", pa.int32()),
        pa.field("is_loop", pa.bool_()),
        pa.field("is_oneshot", pa.bool_()),
        pa.field("raw_tags", pa.list_(pa.string())),
        pa.field("indexed_at", pa.int64()),
    ])
else:
    MANIFEST_SCHEMA = None


def empty_manifest() -> list[dict]:
    return []


def _resolve_json_path(path: Path) -> Path:
    if path.suffix == ".parquet":
        return path.with_suffix(".json")
    return path


def save_manifest(path: Path | str, rows: Iterable[dict]) -> None:
    rows_list = list(rows)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    if HAS_PYARROW and target.suffix == ".parquet":
        columns: dict = {field.name: [] for field in MANIFEST_SCHEMA}
        for row in rows_list:
            for field in MANIFEST_SCHEMA:
                columns[field.name].append(row.get(field.name))

        table = pa.table(columns, schema=MANIFEST_SCHEMA)
        pq.write_table(table, target, compression="zstd")
    else:
        json_target = _resolve_json_path(target)
        with open(json_target, "w", encoding="utf-8") as f:
            json.dump(rows_list, f, indent=2, ensure_ascii=False)
        if json_target != target:
            with open(target, "w", encoding="utf-8") as f:
                json.dump(rows_list, f, indent=2, ensure_ascii=False)


def load_manifest(path: Path | str) -> list[dict]:
    target = Path(path)
    if HAS_PYARROW and target.suffix == ".parquet" and target.exists():
        try:
            table = pq.read_table(target)
            return table.to_pylist()
        except Exception:
            pass

    json_target = _resolve_json_path(target)
    if json_target.exists():
        try:
            with open(json_target, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    if target.exists():
        try:
            with open(target, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return []
