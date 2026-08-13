import hashlib
from pathlib import Path

from p3_v3.adapters import cmake_ctest_v1
from p3_v3.bridge_and_frames import SourceSnapshot, SourceSnapshotEntry


_ROOT = Path(__file__).parents[2]
_ADAPTER_DIR = _ROOT / "src" / "p3_v3" / "adapters"
_BLOCK_BEGIN = b"# --- SHARED-ADAPTER-BLOCK-v1 begin ---"
_BLOCK_END = b"# --- SHARED-ADAPTER-BLOCK-v1 end ---"


def _shared_block(path: Path) -> bytes:
    raw = path.read_bytes()
    start = raw.index(_BLOCK_BEGIN)
    end = raw.index(_BLOCK_END, start) + len(_BLOCK_END)
    return raw[start:end]


def _snapshot(entries: dict[str, bytes]) -> SourceSnapshot:
    return SourceSnapshot(
        entries=tuple(
            SourceSnapshotEntry(
                relative_path=path,
                mode="100644",
                sha256=hashlib.sha256(raw).hexdigest(),
                content=raw,
            )
            for path, raw in sorted(entries.items())
        )
    )


def _discover_with_sources(entries: dict[str, bytes]) -> dict:
    return cmake_ctest_v1.discover(
        _snapshot({"CMakeLists.txt": b"cmake_minimum_required(VERSION 3.20)\n", **entries}),
        {},
    )


def test_shared_adapter_blocks_match_controller_bytes():
    adapter_blocks = [
        _shared_block(_ADAPTER_DIR / name)
        for name in (
            "cmake_ctest_v1.py",
            "meson_test_v1.py",
            "autotools_makecheck_v1.py",
        )
    ]
    controller_block = _shared_block(
        _ROOT
        / ".superpowers"
        / "sdd"
        / "2026-08-13-p3-task4-real-build-adapters"
        / "shared_adapter_block_v1.py"
    )

    assert adapter_blocks[0] == adapter_blocks[1] == adapter_blocks[2]
    assert adapter_blocks[0] == controller_block


def test_c_family_sites_cross_transparent_wrappers_but_not_classes():
    result = _discover_with_sources(
        {
            "wrapped.cpp": b"""namespace foo {
  int namespaced() {
    return 1;
  }
}
extern "C" {
  int exported() {
    return 2;
  }
}
class X {
  int method() {
    return 3;
  }
};
""",
        }
    )

    assert [(site["symbol"], site["start_line"]) for site in result["sites"]] == [
        ("wrapped.cpp:namespaced", 2),
        ("wrapped.cpp:exported", 7),
    ]


def test_c_string_line_continuation_preserves_later_site_line_number():
    result = _discover_with_sources(
        {
            "continued.c": (
                b'const char *message = "continued\\\n'
                b'line";\n'
                b"int later(void) {\n"
                b"  return 0;\n"
                b"}\n"
            ),
        }
    )

    assert [(site["symbol"], site["start_line"]) for site in result["sites"]] == [
        ("continued.c:later", 3),
    ]


def test_fortran_inline_comment_closes_and_end_do_does_not_close():
    result = _discover_with_sources(
        {
            "commented.f90": b"""subroutine foo()
  integer :: value
end subroutine foo ! note
""",
            "loop.f90": b"""subroutine loop_host()
  do index = 1, 3
    value = index
  end do
  value = 4
end subroutine loop_host
""",
        }
    )

    assert [
        (site["symbol"], site["start_line"], site["end_line"])
        for site in result["sites"]
    ] == [
        ("commented.f90:foo", 1, 3),
        ("loop.f90:loop_host", 1, 6),
    ]


def test_non_utf8_source_is_skipped_from_scale_and_sites():
    result = _discover_with_sources(
        {
            "bad.c": b"\xff\xfe garbage",
            "good.c": b"int good(void) {\n  return 0;\n}\n",
        }
    )

    assert "bad.c" not in result["source_files"]
    assert "good.c" in result["source_files"]
    assert [site["symbol"] for site in result["sites"]] == ["good.c:good"]
