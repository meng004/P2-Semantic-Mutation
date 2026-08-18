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

### Metadata Probes

Read-only metadata probes are allowed before the two qualification workload
jobs. They are not qualification workload jobs and must not be represented as
compile-link or binary-run results.

The allowed metadata probes are limited to:

- repository commit and clean-state inspection
- executable path resolution and filesystem identity inspection
- operating-system and kernel identity
- Python and Git version inspection
- exactly one `<resolved-cxx> --version` invocation

The compiler-version invocation must occur after the qualification intent has
been exclusive-created. Its argv, exit code, stdout, stderr, byte counts, and
SHA-256 values are bound into the terminal evidence.

No metadata probe may compile, link, execute generated code, invoke CMake,
access the network, install software, or modify the environment.

The phrase "exactly two qualification workload jobs" refers only to
`CXX_COMPILE_LINK` and `QUALIFIED_BINARY_RUN`. Metadata probes do not weaken
the no-retry rule for either workload job.

## Unique Execution

Exactly two qualification workload jobs are allowed, in order:

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

### Evidence Storage And Ordering

After repository and forbidden-environment checks pass, the qualification root
is created exclusively. It must not be deleted or reused.

Executable path resolution may use the controller's filesystem APIs without
executing the compiler. The qualification then exclusive-creates:

`/tmp/p3-cxx-link-qualification/qualification-intent.json`

The intent is created before `<resolved-cxx> --version` and before either
qualification workload job. It binds:

- this specification path and SHA-256
- repository commit
- requested compiler name and resolved compiler path
- exact source bytes and SHA-256
- exact workload argv arrays
- exact timeouts
- qualification root
- relevant environment-variable snapshot
- `no_retry=true`
- `formal_denominator_membership=false`
- `claims=blocked`
- `attempt_2_authorized=false`

If the requested compiler cannot be resolved, the root, intent, terminal
result, and manifest still record that terminal prerequisite failure without
executing a compiler.

All qualification evidence is written only beneath the qualification root:

```text
qualification-intent.json
qualification-result.json
qualification-manifest.json
METADATA_CXX_VERSION.stdout
METADATA_CXX_VERSION.stderr
CXX_COMPILE_LINK.stdout
CXX_COMPILE_LINK.stderr
QUALIFIED_BINARY_RUN.stdout
QUALIFIED_BINARY_RUN.stderr
qualify.cpp
qualify
```

A file for an unstarted job is absent and its result contains no invented
stdout, stderr, exit code, timestamp, or executable evidence.

The intent, result, and manifest are canonical UTF-8 JSON objects with sorted
keys, compact separators, exactly one terminal LF, no CR, and a self-hash over
the object without its self-hash field.

The terminal result is exclusive-created after the qualification reaches PASS
or FAIL. It binds the intent file SHA-256, metadata evidence, workload job
results, output executable evidence when present, final status,
`no_retry=true`, `formal_denominator_membership=false`, `claims=blocked`, and
`attempt_2_authorized=false`.

The manifest is exclusive-created last and binds the relative path, SHA-256,
and byte count of every evidence file present. It must not list absent or
unstarted-job files.

The repository remains unchanged throughout qualification execution. The
complete canonical intent, result, manifest, and every raw stdout/stderr file
are returned losslessly as Base64 for independent review.

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

Every failure after qualification-root creation must produce one terminal
result and one manifest. Existing evidence is never deleted, overwritten,
renamed, or supplemented by a second workload attempt.

A failure of the compiler-version metadata probe prevents both workload jobs.
A failure of `CXX_COMPILE_LINK` prevents `QUALIFIED_BINARY_RUN`.

No failed qualification evidence is rewritten as PASS after environment
repair.

## Workflow After PASS

After independent review of a qualification PASS:

1. define the minimal attempt-2 recovery protocol;
2. repair the build-preflight missing-dependency classification;
3. obtain a new implementation review and implementation verdict;
4. obtain separate user authorization for attempt-2;
5. execute attempt-2 exactly once.

Qualification PASS alone does not advance to any later step.

Before defining attempt-2, Sol independently validates the returned canonical
objects and raw byte hashes. A qualification verdict may then be archived in a
separate governance node. Neither the evidence return nor verdict archival may
rerun the compiler.
