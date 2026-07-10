# Study-5 Family-XL third-party provenance (Amendment A1 companion)

All program-under-test code below is externally authored and vendored
UNMODIFIED (author-directed principle P1, PREREGISTRATION_STUDY5_v1.md §1.6).
Only the files needed by the frozen §2b roster candidates are vendored;
licenses are retained per source.

| Directory | Upstream | Commit / version | License |
|---|---|---|---|
| `thealgorithms-python/` | github.com/TheAlgorithms/Python | `c0db072a1323339e0d9148479f8818a1b9768d88` | MIT (`LICENSE.md`) |
| `thealgorithms-cpp/` | github.com/TheAlgorithms/C-Plus-Plus | `b9c118fb5dca86f6325e816481959e1e6c360373` | MIT (`LICENSE`) |
| `thealgorithms-java/` | github.com/TheAlgorithms/Java | `fd2858e7e6138d9f8940ee9820e172912a5acfb4` | MIT (`LICENSE`) |
| `thealgorithms-go/` | github.com/TheAlgorithms/Go | `5ba447ec5ff3d1213de65b92e726ee74c5d5cc19` | MIT (`LICENSE`) |
| `thealgorithms-rust/` | github.com/TheAlgorithms/Rust | `c65d014621a9d50b36b197f08bb1c8016ff505b0` | MIT (`LICENSE`) |
| `boost-math/` | github.com/boostorg/math (`include/` only) | `8ee12a5355935cbaac5d5338372d0d0e3311b473` | Boost Software License 1.0 (`LICENSE`) |
| `commons-math/` | Maven Central `org.apache.commons:commons-math3:3.6.1` | jar sha256 `1e56d7b058d28b65abd256b8458e3885b674c1d588fa43cd7d1cbb9c7ef2b308` | Apache-2.0 (`LICENSE.txt`, `NOTICE.txt`) |
| `gsl/` | GNU GSL via Ubuntu package `libgsl-dev` | `2.7.1+dfsg-6ubuntu2` (linked as a system library; sources not vendored, GPL-3.0 notice retained) | GPL-3.0 (`COPYRIGHT.debian`) |

Also recorded (toolchain, not program source): TheAlgorithms/C commit
`e5dad3fa8def3726ec850ca66a7f51521f8ad393` was enumerated but every C-repo
candidate was screened out pre-behaviorally (see the roster audit trail);
nothing from it is vendored. Julia 1.11.7 official binary tarball
(julialang-s3.julialang.org) provides the Julia toolchain + stdlib (MIT); the
Julia programs under test are stdlib entry points (`Statistics.quantile`,
`Base.sinc`).

Note on the GPL-3.0 C repo: TheAlgorithms/C is the only copyleft source in
the sweep; since all its candidates failed the registered pre-behavioral
screen, no GPL code from it is vendored. GNU GSL (GPL-3.0) is used via the
unmodified Ubuntu system library and is called only through the adapter shim
(`src/p2/xlport/shims/`), consistent with the registration's vendoring clause
(§2b Step 3 criterion 1).

## Amendment A3 note (2026-07-10)

The A3 roster-extension wave (module/pipeline-scale pairs; see
`docs/prereg_v2/STUDY5_XL_ROSTER.md` §A3) vendored **nothing new**: every
A3 pair links upstreams already pinned above — GNU GSL 2.7.1 as the
unmodified Ubuntu system library (interpolation, chebyshev, histogram,
multifit modules; GPL-3.0 notice retained, nothing GPL vendored, per the A1
precedent), Boost.Math `8ee12a53` vendored headers (interpolators module),
and the commons-math3 3.6.1 jar (analysis.interpolation, stat.descriptive
modules). This directory is byte-unchanged by A3.
