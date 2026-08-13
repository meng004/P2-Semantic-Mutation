# P3 Task 4: Real CMake/Meson/Autotools Discovery Adapters Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. This is the next task of
> `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md`
> (the Exit-(b) charter); its Global Constraints apply verbatim.
> Worker subagents run on `gpt-5.6-sol-high`; the independent reviewer runs
> on `claude-fable-5-thinking-max` (user-fixed division of labor,
> 2026-08-13).

**Goal:** Replace the three fail-closed placeholder adapters
(`CMAKE_CTEST_V1`, `MESON_TEST_V1`, `AUTOTOOLS_MAKECHECK_V1`) with real,
frozen, source-derived discovery rules so the 28 delivered cmake/meson/
autotools subjects (23+1+4) can enter Phase 1 frame derivation; re-emit the
adapter registry and protocol (V4).

**Architecture:** Each adapter is one hash-bound, stdlib-only module
executed in-process through the verified registry seam
(`validate_adapter_registry` → exec → `discover(source_snapshot,
build_descriptor)`), exactly like the frozen `PYTHON_PEP517_V1` model
(`src/p3_v3/adapters/python_pep517_v1.py`). Discovery is purely textual and
static: build files are parsed as text; no build system, compiler, or
network is ever invoked. Shared logic (exclusion rule, site enumerators,
header/path-evidence rules) is inlined byte-identically into each adapter
file between frozen markers, with a drift-guard test, because the registry
seam forbids cross-module imports. A small production change extends the
frozen scale-language engine with Fortran and CUDA so `source_files` can
honestly cover LAPACK/Castro/MAGMA-class subjects.

**Tech Stack:** Python 3.12 (`/opt/anaconda3/bin/python`, pytest 8.4.2),
stdlib only (`re`, `hashlib`, `json`, `pathlib`); existing `p3_v3` modules
imported read-only in tests.

## Global Constraints

- Charter rails apply verbatim: no verifier/lock hardening; frozen
  acceptance list per task; independent review judges PASS/BLOCK only
  against that list; max two repair rounds per task; root-cause batching;
  full suite only at the freeze point, in a clean worktree, unsandboxed.
- All claims remain `blocked`. No scientific result is recorded. No
  network, no P12 repo access, no reveal-ledger access, no Cursor VM.
- Adapter seam contract (frozen, from `bridge_and_frames.py`):
  `discover(source_snapshot, build_descriptor) -> dict` with exactly the
  keys `{adapter_id, ecosystem, source_files, declarations, public_schemas,
  sites}` (`_ADAPTER_RESULT_SCHEMA`); paths must be safe-relative, unique,
  and not hit `_excluded_scale_path`; sites must satisfy `_SITE_SCHEMA`
  (`path, symbol, start_line, start_col, end_line, end_col`, ints ≥ 0);
  declarations must satisfy `_declaration_is_structurally_valid` (category
  in the five frozen behavior categories, non-empty entrypoint /
  normalized_entrypoint / provenance_span_or_key, 64-hex
  `declared_input_schema_sha256`, string-list `static_dependency_tags` and
  `prerequisites`, `declared_inputs` present).
- Adapters are stdlib-only, import no controller modules, print nothing,
  and fail closed (`raise ValueError`) on any malformed required build
  file. Category accounting retains zero-count categories: an ecosystem
  rule that legitimately discovers nothing for a category emits no row and
  that is correct behavior, not an error.
- E_COMMON-eligible schema kinds are only `JSON_SCHEMA_DRAFT2020_12_V1`,
  `CLI_TOKEN_GRAMMAR_V1`, `NUMERIC_ARRAY_DOMAIN_V1`, `TEXT_IO_SCHEMA_V1`,
  `BINARY_RECORD_SCHEMA_V1`; adapters emit `public_schemas` rows only for
  these kinds.
- The three real adapters replace placeholder bodies at their existing
  registered paths; adapter IDs, ecosystems, and paths are frozen by the
  site policy and may not change.

## Decision record (user gate at plan review)

1. **Scale-language extension (recommended: adopt).** The frozen
   `_source_language` supports only cmake/python/cpp, and
   `derive_source_scale` fails closed on any other suffix in
   `source_files`. Without extension, Fortran subjects (LAPACK ×3, parts
   of Castro/PETSc) and CUDA subjects (MAGMA) either fail scale derivation
   or must omit those files, understating `S/M/L` strata. Task A adds
   `fortran` (fixed- and free-form comment rules) and maps `.cu/.cuh` to
   the existing cpp rule. This is a Task-2-class rule-engine extension
   (new language rules only; no existing hash changes), not verifier/lock
   hardening.
2. **Execution mode:** subagent-driven (Tasks B/C/D in parallel after A;
   fresh `gpt-5.6-sol-high` worker per task; `claude-fable-5-thinking-max`
   reviewer gates each task against its frozen acceptance list).

## File Structure

- Modify: `src/p3_v3/bridge_and_frames.py` (only `_source_language`,
  `_effective_line_count`, and the suffix constants; Task A)
- Rewrite: `src/p3_v3/adapters/cmake_ctest_v1.py` (Task B)
- Rewrite: `src/p3_v3/adapters/meson_test_v1.py` (Task C)
- Rewrite: `src/p3_v3/adapters/autotools_makecheck_v1.py` (Task D)
- Test: `tests/p3_v3/test_scale_languages.py` (Task A),
  `tests/p3_v3/test_adapter_cmake.py` (B),
  `tests/p3_v3/test_adapter_meson.py` (C),
  `tests/p3_v3/test_adapter_autotools.py` (D),
  `tests/p3_v3/test_adapter_shared_blocks.py` (D, drift guard)
- Fixtures: `tests/p3_v3/fixtures/adapter_trees/{cmake_mini,meson_c_mini,
  meson_py_mini,autotools_mini}/…` (collection-shielded like the Task 2
  fixtures)
- Re-emit (Task E): `data/p3_v3/protocol/{adapter_registry.json,
  protocol.json}` via the unchanged deterministic builder
- Report: `docs/review_20260813/task4_adapters_task_report.md`

---

## Normative discovery rules (frozen texts)

These docstring rules are the scientific content of this task. Workers
implement them literally; the reviewer checks implementation against them
line by line. The structural template for all three files is
`src/p3_v3/adapters/python_pep517_v1.py` (result assembly, canonical
hashing, declaration row shapes).

### Shared frozen blocks (inlined byte-identically in all three adapters)

Delimited in each file by `# --- SHARED-ADAPTER-BLOCK-v1 begin ---` /
`# --- SHARED-ADAPTER-BLOCK-v1 end ---`; the drift-guard test asserts the
three delimited regions are byte-identical.

1. `_canonical_sha256(value)` and `_excluded(relative_path)` — verbatim
   copies from `python_pep517_v1.py` (the inlined controller exclusion
   rule, `_EXCLUDED_PARTS` + `cmake-build-`/`build-` prefixes).
2. `_SCALE_SUFFIXES` — exactly the union the engine supports after Task A:
   `.c .cc .cpp .cxx .h .hh .hpp .hxx .inl .cu .cuh .py .pyi .pyx .pxd
   .cmake .f .for .f77 .f90 .f95 .f03 .f08` plus basename
   `cmakelists.txt`. `source_files` = every non-excluded snapshot path
   whose casefolded basename is `cmakelists.txt` or whose casefolded
   suffix is in `_SCALE_SUFFIXES`, sorted.
3. `_c_family_sites(path, text) -> list[site]` — frozen textual function
   enumerator for suffixes `.c .cc .cpp .cxx .cu .h .hh .hpp .hxx .inl
   .cuh`: mask comments and string/char-literal contents with a
   character automaton (`//`, `/* */`, `"…"`, `'…'` with backslash
   escapes) that is strictly newline-preserving — an escaped newline
   inside a string keeps its newline in the mask, so line numbers stay
   true. Track brace depth on the mask with a per-brace stack; an opening
   brace is **transparent** when the masked text from line start to the
   brace matches `^\s*(?:inline\s+)?namespace(?:\s+[A-Za-z_][A-Za-z0-9_:]*)?\s*$`
   or `^\s*extern\s*"C(?:\+\+)?"\s*$`; effective depth counts only
   non-transparent braces. A site starts at a masked line whose first
   non-whitespace character is not `#`, `}`, or `;`, at effective depth
   0, whose text up to the first `(` ends in an identifier
   (`[A-Za-z_][A-Za-z0-9_]*` whose own token is not one of
   `if|else|for|while|switch|return|do`), and for which the next code
   token after the matching `)` is `{` (not `;`).
   `symbol = f"{path}:{identifier}"`; span runs from the identifier line
   to the line/col where that function's brace closes. Overloads repeat
   the same symbol; that is allowed (site identity later adds spans).
4. `_fortran_sites(path, text) -> list[site]` — for suffixes `.f .for .f77
   .f90 .f95 .f03 .f08`: comment lines are skipped (first non-blank `!`,
   or column-1 `c/C/*/d/D` for fixed-form suffixes `.f .for .f77`); on
   every other line, an inline trailing `!` comment is cut before
   matching. A site starts at a line matching
   `^\s*(?:(?:pure|impure|elemental|recursive|module)\s+)*
   (subroutine|function)\s+([a-z][a-z0-9_]*)` case-insensitively (also
   allowing a type prefix before `function`, e.g. `integer function x`);
   nesting counts starts vs. end lines matching
   `^\s*end\s*(?:(?:subroutine|function)(?:\s+[a-z][a-z0-9_]*)?)?\s*$`
   after the comment cut (bare `end` closes the innermost start; `end
   do`/`end if`/`end module` never match). The site is emitted when the
   outermost start unwinds (host procedures produce the site; contained
   procedures extend the host span). `symbol = f"{path}:{name.casefold()}"`.
5. `_header_declarations(paths)` — PUBLIC_API surface rule: every
   non-excluded file with a casefolded path component `include` and suffix
   in `.h .hh .hpp .hxx .inl .cuh` yields one declaration:
   `category=PUBLIC_API`, `entrypoint=<relpath>`,
   `normalized_entrypoint=f"header:{relpath}".casefold()`,
   `provenance_path=<relpath>`, `provenance_span_or_key="path"`,
   `declared_inputs={"header": relpath}`,
   `declared_input_schema_sha256=_canonical_sha256({"kind":
   "HEADER_SURFACE_V1", "path": relpath})`, empty tags/prerequisites. No
   `public_schemas` row (not an E_COMMON kind).
6. `_path_category(relpath)` — path-evidence rule: any casefolded
   component `examples` → `EXAMPLE`; any component in `{benchmarks,
   bench}` → `BENCHMARK`; else None. Evidence rows for files with suffix
   in `.c .cc .cpp .cxx .cu .f .f90 .py`:
   `entrypoint=<relpath>`, `normalized_entrypoint=
   f"{category.casefold()}:{relpath}".casefold()`, `provenance_span_or_key
   ="path"`, `declared_inputs={"source_path": relpath}`, schema hash of
   `{"kind": "SOURCE_EVIDENCED_V1", "path": relpath}`, no public_schemas
   row.
7. `_cli_grammar_schema(program)` — verbatim shape of the python adapter's
   scripts rule: `{"kind": "CLI_TOKEN_GRAMMAR_V1", "program": program,
   "tokens": {"min": 0, "max": 3}, "vocabulary": sorted({program,
   "--help", "--version"})}`.
8. Decodability rule: a snapshot file whose bytes do not decode as strict
   UTF-8 is excluded from `source_files` and from site enumeration (the
   frozen scale engine fails closed on non-UTF-8 `source_files` entries,
   so exclusion is the only deliverable form; completeness stays relative
   to the frozen rule). Required build files (root `CMakeLists.txt`,
   `meson.build`, root makefiles) still fail closed on decode errors.
9. Textual fidelity note: shared-block function bodies follow the python
   adapter verbatim except type annotations, which the shared block
   drops; behavior is byte-equivalent. The drift-guard compares the three
   adapters' marker-delimited regions pairwise (amendment 2026-08-13
   round 2: the untracked controller reference file is coordination
   scaffolding and must not be a test dependency — a clean worktree
   contains only tracked files). The namespace/extern transparency check
   matches the SOURCE segment position-aligned through the
   column-preserving mask, because masked string contents can never equal
   `"C"` (recorded per SB review; the only behavior-preserving reading).
   Rule 8 side-effect recorded: skipping a non-decodable meson python
   module also drops its declarations and schema rows — exclusion cannot
   parse what it cannot decode.
   (Amendment 2026-08-13, review round 1: items 3, 4, 8, 9 adjudicated
   after the Fable-5-Max task reviews; the fortran end-regex anchors and
   name group replace the earlier draft regex, whose word-boundary form
   over-popped on `end do`/`end if`.)

### CMAKE_CTEST_V1 (subjects: SUNDIALS ×9, LAPACK ×3, Trilinos, LAMMPS,
### Castro, Boost.Math, Eigen, GraphBLAS, SuiteSparse, OpenBLAS, MAGMA,
### pocketfft ×2 — 23)

- Fail-closed guard: root `CMakeLists.txt` must exist and decode as UTF-8
  (with `errors="replace"` forbidden); otherwise `raise ValueError`.
- Build-file set: every non-excluded `CMakeLists.txt` and `*.cmake` file.
  Parse textually after stripping `#` line comments and cmake bracket
  comments `#[[ … ]]`.
- `PROJECT_TEST`: every `add_test(...)` occurrence. Grammar:
  `(?<![A-Za-z0-9_])add_test\s*\(\s*(?:NAME\s+)?([\"']?)([A-Za-z0-9_.:+/-]+)\1`
  (second group = test name; the lookbehind rejects wrapper macros such
  as `sundials_add_test`). Row: `entrypoint=f"ctest:{name}"`,
  `normalized_entrypoint` = its casefold, `provenance_path` = the build
  file, `provenance_span_or_key=f"L{lineno}"`, `declared_inputs=
  {"argv_tokens": ["ctest", "-R", f"^{name}$"]}`, schema =
  `_cli_grammar_schema("ctest")` (one shared `public_schemas` row per
  distinct provenance file+span — duplicate spans are emitted once),
  tags `[]`.
- `CLI` / `EXAMPLE` / `BENCHMARK`: every `(?<![A-Za-z0-9_])
  add_executable\s*\(\s*([\"']?)([A-Za-z0-9_.+-]+)\1` occurrence whose
  second group does not start with `${` and whose parenthesized argument
  group does not contain the standalone case-sensitive uppercase token
  `IMPORTED` or `ALIAS` (`\b(?:IMPORTED|ALIAS)\b` without IGNORECASE;
  lower-case file names such as `alias.c` never suppress). Category =
  `_path_category` of the declaring build file, else `CLI`. Row:
  `entrypoint=f"target:{name}"`, argv `[name]`, schema
  `_cli_grammar_schema(name)` with a `public_schemas` row for `CLI` rows
  only (deduplicated by provenance file+span like the test rows).
- `PUBLIC_API`: `_header_declarations`.
- `sites`: `_c_family_sites` over non-excluded `.c .cc .cpp .cxx .cu .h
  .hh .hpp .hxx .inl .cuh` files plus `_fortran_sites` over Fortran
  suffixes.
- `source_files`: shared rule 2.

### MESON_TEST_V1 (subject: B-POCKETFFT-004 — a meson-python SciPy tree)

- Fail-closed guard: root `meson.build` must exist; otherwise ValueError.
- Build-file set: every non-excluded `meson.build` and `*.meson` file,
  `#` comments stripped.
- `PROJECT_TEST`: `(?<![A-Za-z0-9_])test\s*\(\s*'([^']+)'` rows with
  `entrypoint=f"meson-test:{name}"`, argv `["meson", "test", name]`,
  schema `_cli_grammar_schema("meson")` and a `public_schemas` row.
  `(?<![A-Za-z0-9_])benchmark\s*\(\s*'([^']+)'` occurrences map to
  `BENCHMARK` with `entrypoint=f"meson-benchmark:{name}"`, argv
  `["meson", "test", "--benchmark", name]`, the same schema hash, and
  **no** `public_schemas` row (amendment 2026-08-13: benchmark row shape
  frozen as implemented).
- `CLI`/`EXAMPLE`/`BENCHMARK` targets:
  `(?<![A-Za-z0-9_])executable\s*\(\s*'([^']+)'` with `_path_category` of
  the declaring build file, else `CLI`; rows shaped as in the cmake rule
  (amendment 2026-08-13 round 2: the lookbehind literal was missing from
  this bullet while the code and the test/benchmark bullet carried it).
- Python-package branch: when root `pyproject.toml` exists with a
  non-empty `[project].name`, additionally apply — verbatim — the
  `PYTHON_PEP517_V1` module rules (package roots, public modules,
  `PUBLIC_API` declarations with signature-derived schemas,
  `[project.scripts]` CLI rows, path-evidenced `.py`
  EXAMPLE/BENCHMARK/PROJECT_TEST rows, python `sites`).
- In **both** branches the adapter additionally applies
  `_header_declarations`, `_c_family_sites`, and `_fortran_sites`
  (amendment 2026-08-13: the additive route is frozen — meson-python
  subjects like SciPy carry public C headers and compiled sources whose
  surface must not vanish because a pyproject exists). A
  `(category, provenance_path)` pair is emitted once; first writer wins.
- `source_files`: shared rule 2 (meson.build files themselves are not
  scale-countable and stay out).

### AUTOTOOLS_MAKECHECK_V1 (subjects: BLIS ×2, PETSc ×2)

- Fail-closed guard: a root `configure` file must exist; otherwise
  ValueError.
- `PROJECT_TEST` (make targets): scan root makefiles in the frozen name
  order `GNUmakefile`, `makefile`, `Makefile`, plus `gmakefile` and
  `gmakefile.test` when present; a line matching `^(check|test)\s*:` (not
  `:=`) yields one row per distinct target name over all files:
  `entrypoint=f"make:{target}"`, provenance = the first file (in frozen
  order) declaring it with `provenance_span_or_key=f"L{lineno}"`, argv
  `["make", target]`, schema `_cli_grammar_schema("make")`.
- `PROJECT_TEST` (path evidence): files with suffix in `.c .cc .cpp .cxx
  .f .f90 .py` under any casefolded component in `{tests, testsuite}` →
  source-evidenced rows (shared rule 6 shape, category `PROJECT_TEST`).
- `EXAMPLE`/`BENCHMARK`: `_path_category` source-evidenced rows.
- `PUBLIC_API`: `_header_declarations`.
- `CLI`: no static rule (autotools target enumeration requires configure
  execution, which is forbidden) — zero-count, retained by the frame.
- `sites`: `_c_family_sites` + `_fortran_sites`.
- `source_files`: shared rule 2.

---

### Task A: Fortran + CUDA scale-language extension

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py` (suffix constants +
  `_source_language` + `_effective_line_count` only)
- Test: `tests/p3_v3/test_scale_languages.py`

**Interfaces:**
- Consumes: existing `_effective_line_count(relative_path, raw)`.
- Produces: `_source_language` returning `"fortran"` for suffixes
  `.f .for .f77 .f90 .f95 .f03 .f08`; `.cu`/`.cuh` added to
  `_CPP_SOURCE_SUFFIXES`; fortran effective-line rule = count lines that
  are non-blank, whose first non-blank character is not `!`, and — for
  fixed-form suffixes `.f .for .f77` only — whose column-1 character is
  not in `{c, C, *, d, D}`.

- [ ] **Step A1: failing tests** — `test_scale_languages.py` with exact
  cases: free-form `.f90` (code + `! comment` + blank → 1), fixed-form
  `.f` (`C comment` line + `      x = 1` → 1), `.cu` kernel with `//`
  comment (cpp rule), unsupported `.jl` still raises
  `E_SCALE_SOURCE_LANGUAGE`, and byte-identical re-run determinism over a
  shuffled file list via `derive_source_scale`.
- [ ] **Step A2: run tests, verify FAIL** (`pytest
  tests/p3_v3/test_scale_languages.py -q`).
- [ ] **Step A3: implement** — add `_FORTRAN_SOURCE_SUFFIXES`,
  `_FORTRAN_FIXED_FORM_SUFFIXES`, extend `_CPP_SOURCE_SUFFIXES` with
  `{".cu", ".cuh"}`, add the fortran branch to `_source_language` and
  `_effective_line_count`.
- [ ] **Step A4: run tests, verify PASS; run
  `tests/p3_v3/test_bridge_and_frames.py` for no regression.**
- [ ] **Step A5: commit** `feat(p3-v3): extend scale engine with fortran
  and cuda line rules`.

**Acceptance (frozen):** (1) the five test cases above pass; (2) no
existing test changes behavior; (3) no schema, verifier, lock, or protocol
constant touched.

### Task B: CMAKE_CTEST_V1 real discovery

**Files:**
- Rewrite: `src/p3_v3/adapters/cmake_ctest_v1.py`
- Test: `tests/p3_v3/test_adapter_cmake.py`
- Fixture: `tests/p3_v3/fixtures/adapter_trees/cmake_mini/` —
  `CMakeLists.txt` (2 `add_test` incl. one `NAME` form, 2
  `add_executable` incl. one under `examples/`), `include/mini/api.h`
  (2 prototypes), `src/lib.c` (2 function definitions + 1 `static`
  helper + an `if (…) {` distractor), `examples/demo.c`,
  `bench/perf.cu`, `fortran/solver.f90` (1 subroutine + 1 function),
  `build/generated.c` (must be excluded).

**Interfaces:**
- Consumes: shared frozen blocks (normative text above); the seam calls
  `discover(source_snapshot, build_descriptor)` where `source_snapshot`
  exposes `.entries` with `.relative_path`/`.content`.
- Produces: result dict passing `_normalize_adapter_result` for
  `adapter_id="CMAKE_CTEST_V1"`, `ecosystem="cmake"`.

- [ ] **Step B1: failing tests** — exact expected counts on the fixture:
  declarations: 2 PROJECT_TEST (`ctest:mini_smoke`, `ctest:mini_named`),
  2 CLI (`target:mini_tool`; `target:mini_alias` whose `alias.c` argument
  must not suppress — amendment 2026-08-13 round 1), no `ctest:phantom`
  row from a `sundials_add_test(NAME phantom …)` distractor (word-boundary
  guard), 1 EXAMPLE from `add_executable` in `examples/` + 1 EXAMPLE
  source-evidenced (`examples/demo.c`), 1 BENCHMARK (`bench/perf.cu`),
  1 PUBLIC_API header row; sites: exactly the 3 C functions + 2 fortran
  sites, none from `build/`; source_files exclude `build/generated.c`;
  every declaration passes `_declaration_is_structurally_valid`;
  public_schemas kinds ⊆ the five E_COMMON kinds; determinism: two runs
  byte-identical via `canonical_json_bytes`.
- [ ] **Step B2: run, verify FAIL.**
- [ ] **Step B3: implement the module** per the normative rule text, with
  the rule text as the module docstring (the python adapter is the
  structural template).
- [ ] **Step B4: run, verify PASS.**
- [ ] **Step B5: commit** `feat(p3-v3): implement real cmake/ctest
  discovery adapter`.

**Acceptance (frozen):** (1) fixture expectations above; (2) fail-closed
on a tree without root `CMakeLists.txt` (ValueError); (3) stdlib-only, no
controller imports, no I/O; (4) docstring equals the normative rule text.

### Task C: MESON_TEST_V1 real discovery

**Files:**
- Rewrite: `src/p3_v3/adapters/meson_test_v1.py`
- Test: `tests/p3_v3/test_adapter_meson.py`
- Fixtures: `meson_c_mini/` (meson.build with `test('t1', …)`,
  `benchmark('b1', …)`, `executable('mtool', …)`, `include/m/m.h`,
  `src/m.c`) and `meson_py_mini/` (meson.build + pyproject.toml
  `[project] name="mini"` + `src/mini/__init__.py` with one public
  function `def go(x: int) -> int` + `tests/test_go.py`).

**Interfaces:** as Task B with `adapter_id="MESON_TEST_V1"`,
`ecosystem="meson"`.

- [ ] **Step C1: failing tests** — `meson_c_mini`: 1 PROJECT_TEST
  (`meson-test:t1`), 1 BENCHMARK (`b1`), 1 CLI (`mtool`), 1 PUBLIC_API
  header, C sites from `src/m.c`. `meson_py_mini`: PEP517-branch rows
  present — `PUBLIC_API mini:go` with `NUMERIC_ARRAY_DOMAIN_V1` schema
  row, 1 PROJECT_TEST for `tests/test_go.py` (pytest argv form), python
  site for `go`; plus `meson-test` rows. Determinism check.
- [ ] **Step C2: run, verify FAIL.**
- [ ] **Step C3: implement per rule text.**
- [ ] **Step C4: run, verify PASS.**
- [ ] **Step C5: commit** `feat(p3-v3): implement real meson discovery
  adapter`.

**Acceptance (frozen):** (1) both fixture expectation sets; (2)
fail-closed without root `meson.build`; (3) python-branch rules verbatim
PEP517-equivalent on the shared fixture shapes; (4) stdlib-only/no
imports/no I/O; (5) docstring equals the normative text.

### Task D: AUTOTOOLS_MAKECHECK_V1 real discovery + drift guard

**Files:**
- Rewrite: `src/p3_v3/adapters/autotools_makecheck_v1.py`
- Test: `tests/p3_v3/test_adapter_autotools.py`,
  `tests/p3_v3/test_adapter_shared_blocks.py`
- Fixture: `autotools_mini/` (`configure` (any content), `Makefile` with
  `check:` and `test:` targets and a `test:=` distractor line placed
  ABOVE the `test:` target — so a lookahead regression binds the target's
  provenance to the distractor line and fails the span assertions
  (amendment 2026-08-13, review round 1) — `include/a/a.h`, `src/a.c`,
  `testsuite/t_a.c`, `examples/e.f`).

**Interfaces:** as Task B with `adapter_id="AUTOTOOLS_MAKECHECK_V1"`,
`ecosystem="autotools"`.

- [ ] **Step D1: failing tests** — 2 make PROJECT_TEST rows
  (`make:check`, `make:test`; the `check:=` line yields nothing), 1
  source-evidenced PROJECT_TEST (`testsuite/t_a.c`), 1 EXAMPLE
  (`examples/e.f`), 1 PUBLIC_API header, 0 CLI rows, C sites + fortran
  sites, fail-closed without root `configure`. Drift-guard test: read the
  three adapter files, extract the `SHARED-ADAPTER-BLOCK-v1` regions,
  assert byte equality.
- [ ] **Step D2: run, verify FAIL.**
- [ ] **Step D3: implement per rule text.**
- [ ] **Step D4: run, verify PASS (both test files).**
- [ ] **Step D5: commit** `feat(p3-v3): implement real autotools
  discovery adapter with shared-block drift guard`.

**Acceptance (frozen):** (1) fixture expectations; (2) drift guard green
across all three files; (3) stdlib-only/no imports/no I/O; (4) docstring
equals the normative text.

### Task E: Registry + protocol V4 re-emit, neutral-archive smoke, freeze

**Files:**
- Regenerate: `data/p3_v3/protocol/adapter_registry.json`,
  `data/p3_v3/protocol/protocol.json` (builder is unchanged: it re-hashes
  the three implementation files)
- Create: `docs/review_20260813/task4_adapters_task_report.md`
- Modify: charter Task-3/Task-4 checkboxes + decision ledger

- [ ] **Step E1:** run `/opt/anaconda3/bin/python
  scripts/p3_v3/build_phase0_protocol.py`; expect changed
  `adapter_registry.json` (3 new source hashes) and `protocol.json`
  (adapter_registry_sha256 + artifact_sha256 only).
- [ ] **Step E2:** `PYTHONPATH=src /opt/anaconda3/bin/python
  scripts/p3_v3/evidence.py validate-protocol --protocol
  data/p3_v3/protocol/protocol.json` → `{"status": "PASS"}`.
- [ ] **Step E3: blind smoke over the 28 delivered subjects** — ad-hoc
  harness (not committed): for each `data/p3_v3/p12_intake/archives/
  <neutral>.tar` whose descriptor ecosystem is cmake/meson/autotools,
  extract to a temp dir, build a `SourceSnapshot`, call the matching
  adapter's `discover`, and record per neutral ID: status, per-category
  declaration counts, site count, source_files count, elapsed seconds.
  Expected: 28/28 return (no unhandled exception); any ValueError is
  recorded verbatim as a fail-closed receipt, not patched around. Labels
  never enter the receipts (neutral IDs only).
- [ ] **Step E4:** freeze-point full suite in a clean worktree,
  unsandboxed: `git worktree add .worktrees/p3-v3-task4-freeze <HEAD>`
  then `PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3
  -q`; expect all passed (868 + new), exit 0.
- [ ] **Step E5:** task report (receipt table: registry hashes, protocol
  V4 sha, smoke table, suite receipt) + charter ledger entry + commits:
  one `feat(p3-v3)` for the re-emit, one `docs(p3-v3)` for
  report/charter.

**Acceptance (frozen):** (1) validate-protocol PASS on V4; (2) 28/28
smoke rows recorded with zero unhandled exceptions and zero label
leakage; (3) clean-worktree suite green; (4) diff scope of the re-emit
confined to the two protocol artifacts.

## Self-review

- Spec coverage: site-policy discovery duties (5 categories, zero-count
  retention, no hand-selection) → normative rule texts; scale honesty →
  Task A; hash-bound registry → Task E; blinding → Step E3 neutral-ID
  receipts; charter rails → Global Constraints.
- No placeholders: every fixture, expected count, command, and rule is
  literal. Implementation code is intentionally specified by normative
  docstring + the frozen `PYTHON_PEP517_V1` structural template rather
  than inline listings; the reviewer gate checks docstring-to-code
  fidelity per task.
- Type consistency: all rows use the exact declaration/site schemas from
  `bridge_and_frames.py` constants quoted in Global Constraints.
