# Cursor VM C++ Link Qualification Design

**Status:** Approved design; execution not yet authorized  
**Execution class:** `PILOT_TOOLCHAIN_QUALIFICATION_ONLY`  
**Formal denominator membership:** false  
**Claims:** blocked

## Purpose

Determine whether a fresh Cursor VM has a functional baseline C++14
compile-link-run toolchain before any Boost.Math build-preflight attempt-2
authorization is considered.

This qualification addresses the attempt-1 infrastructure failure in which
Clang 18 selected a GCC 14 installation prefix whose development-time
`libstdc++.so` was absent. It does not test Boost.Math or the frozen consumer
harness.

## Fixed Repository State

The qualification is designed against repository commit:

`7b653cb6803ea89d54e1c8afa7f6605538379449`

Attempt-1 Authorization, intent, result, logs, build root, and harness root are
immutable historical evidence. They must not be deleted, moved, overwritten,
or reclassified in place.

## Isolation

The qualification may write only beneath:

`/tmp/p3-cxx-link-qualification`

The path must be absent at entry. If it already exists, the qualification
stops without deleting or reusing it.

It must not write to the repository, Boost.Math source root, attempt-1 build
root, or attempt-1 harness root.

## Frozen Source

The source file is named `qualify.cpp` with the exact UTF-8 bytes:

```cpp
int main(){return 0;}
```

The file has exactly one terminal LF and no CR.

The source does not include Boost, the standard library, project headers,
network functionality, random input, or filesystem access.

## Compiler Binding

Resolve `c++` through the qualification process environment before creating
the qualification directory.

Record:

- requested executable name
- resolved absolute path
- realpath
- regular-file or symlink identity
- compiler version output
- operating-system and kernel identity
- Python and Git versions
- environment variables that influence compiler or linker search paths,
  limited to their names and non-secret values

The qualification must reject nonempty `CXX`, `CC`, `CPATH`,
`CPLUS_INCLUDE_PATH`, `LIBRARY_PATH`, `LD_LIBRARY_PATH`, `LDFLAGS`, and
`CXXFLAGS`. It must not silently unset them and continue.

## Unique Execution

Exactly two child processes are allowed, in order:

1. `CXX_COMPILE_LINK`
2. `QUALIFIED_BINARY_RUN`

The compile-link argv is:

```text
<resolved-cxx>
-std=c++14
/tmp/p3-cxx-link-qualification/qualify.cpp
-o
/tmp/p3-cxx-link-qualification/qualify
```

The run argv is:

```text
/tmp/p3-cxx-link-qualification/qualify
```

Both use argv arrays, `shell=false`, and a clean process group. Neither command
may be retried.

No CMake, package manager, dependency download, Boost source, production CLI,
mutant, MR, certification, profiling, or confirmatory runner is allowed.

## Evidence

Record independently for both child processes:

- exact argv
- start and end timestamps
- timeout
- process-started state
- exit code
- raw stdout and stderr bytes
- stdout and stderr byte counts and SHA-256 values
- wall time
- process-group cleanup state

Also record:

- exact source bytes and SHA-256
- output executable SHA-256 and byte count
- executable regular-file and non-symlink status
- resolved compiler identity
- VM, OS, and kernel identity
- final qualification status
- `formal_denominator_membership=false`
- `claims=blocked`
- `attempt_2_authorized=false`

Raw stdout and stderr must be returned losslessly as Base64 as well as readable
text so an independent reviewer can reproduce their hashes.

## Timeouts

- compile-link timeout: 60 seconds
- qualified-binary timeout: 10 seconds
- no automatic retry

A timeout terminates and reaps the corresponding process group.

## PASS Semantics

The qualification is PASS only if all of the following hold:

1. The compiler resolves to an absolute executable.
2. The exact source file is created under the frozen qualification root.
3. Compile-link starts and exits 0 within 60 seconds.
4. The output is a regular, non-symlink executable.
5. The executable starts and exits 0 within 10 seconds.
6. No unexpected stdout or stderr is produced.
7. All required hashes, byte counts, identities, and timings are present.
8. The repository remains byte-for-byte unchanged and clean.

PASS proves only that this fresh VM can compile, link, and execute one minimal
C++14 program.

PASS does not authorize or establish:

- Boost.Math build readiness
- build-preflight attempt-2
- package installation
- environment mutation
- mutant or MR execution
- formal denominator membership
- RQ4 support
- paper Results or Contributions

## Failure Semantics

Any unmet prerequisite or nonzero child exit produces a terminal FAIL and
stops. The second child is not started if compile-link is not PASS.

The VM must not be repaired and the qualification must not be rerun under the
same authorization. A failed VM is reported as unsuitable.

## Workflow After PASS

After independent review of a qualification PASS:

1. define the minimal attempt-2 recovery protocol;
2. repair the build-preflight missing-dependency classification;
3. obtain a new implementation review and implementation verdict;
4. obtain separate user authorization for attempt-2;
5. execute attempt-2 exactly once.

Qualification PASS alone does not advance to any later step.
