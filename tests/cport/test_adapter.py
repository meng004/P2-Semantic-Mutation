"""Adapter round-trip: compile + run a known C kernel through CPutProgram."""
import math

import pytest

from p2.cport import CPutProgram, CCompileError, compile_c_source, load_c_put

ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]

_SQUARE = r"""
#include <stdio.h>
#include <stdlib.h>
double program(double x) { return x * x + 1.0; }
int main(int argc, char **argv) {
    if (argc > 1) { printf("%.17g\n", program(strtod(argv[1], NULL))); return 0; }
    char line[256];
    while (fgets(line, sizeof line, stdin)) {
        printf("%.17g\n", program(strtod(line, NULL)));
        fflush(stdout);
    }
    return 0;
}
"""


def test_compile_and_run_known_kernel(tmp_path):
    prog = CPutProgram(_SQUARE, build_dir=tmp_path)
    for x in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert prog(x) == pytest.approx(x * x + 1.0, rel=1e-12, abs=1e-12)
    prog.close()


def test_repeated_calls_reuse_process(tmp_path):
    prog = CPutProgram(_SQUARE, build_dir=tmp_path)
    vals = [prog(0.3) for _ in range(20)]
    assert all(v == pytest.approx(0.3 * 0.3 + 1.0) for v in vals)
    prog.close()


def test_compile_error_raised(tmp_path):
    with pytest.raises(CCompileError):
        compile_c_source("double program(double x) { return x + ; }", tmp_path)


def test_binary_is_content_addressed_cached(tmp_path):
    b1 = compile_c_source(_SQUARE, tmp_path)
    b2 = compile_c_source(_SQUARE, tmp_path)
    assert b1 == b2 and b1.exists()


def test_timeout_yields_nan(tmp_path):
    hang = r"""
#include <stdio.h>
#include <stdlib.h>
double program(double x) { while (x >= 0.0) { } return x; }
int main(void){ char l[64]; while(fgets(l,sizeof l,stdin)){ printf("%.17g\n",program(strtod(l,NULL))); fflush(stdout);} return 0; }
"""
    prog = CPutProgram(hang, build_dir=tmp_path, timeout=0.5)
    assert math.isnan(prog(0.5))
    prog.close()


def test_load_c_put_a2_matches_formula():
    prog = load_c_put("a2", ROOT)
    for x in (0.0, 0.5, 1.0):
        assert prog(x) == pytest.approx(6.0 + 3.0 * x, rel=1e-12)
    prog.close()
