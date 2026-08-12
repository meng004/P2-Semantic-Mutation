"""CMAKE_CTEST_V1 adapter placeholder: fail-closed, not implemented.

The frozen adapter allowlist requires all four confirmatory adapters to be
registered. The CMake/CTest discovery rule is not implemented yet; this stub
is a declared-open item (charter Task 2 report) and fails closed on any
invocation so no CMake subject can silently receive empty or invented
discovery. It carries no fallback data.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

ADAPTER_ID = "CMAKE_CTEST_V1"


def discover(source_snapshot, build_descriptor: Mapping[str, Any]) -> dict[str, Any]:
    raise ValueError(
        "CMAKE_CTEST_V1 discovery is not implemented; the ecosystem stays "
        "fail-closed until a frozen CMake discovery rule is supplied"
    )
