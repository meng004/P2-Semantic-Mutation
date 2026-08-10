"""Executable synthetic CMake adapter used to test the pinned loader."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def discover(source_root: Path, build_descriptor: Mapping[str, Any]) -> Mapping[str, Any]:
    value = json.loads((source_root / build_descriptor["manifest_path"]).read_text())
    collections = {
        key: list(reversed(value[key])) if build_descriptor.get("reverse") else value[key]
        for key in ("source_files", "declarations", "public_schemas", "sites")
    }
    return {
        "adapter_id": "CMAKE_CTEST_V1",
        "ecosystem": "cmake",
        **collections,
    }
