import importlib.util
from pathlib import Path


BUILD_PATH = Path(__file__).parents[1] / "venues" / "tosem" / "build.py"
SPEC = importlib.util.spec_from_file_location("tosem_build", BUILD_PATH)
assert SPEC and SPEC.loader
tosem_build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tosem_build)


def test_convert_fig_descriptions_does_not_duplicate_explicit_description():
    tex = r"""
    \includegraphics[width=\linewidth,alt={Generated fallback}]{figure.png}
    \Description{Author supplied description.}
    """
    converted = tosem_build.convert_fig_descriptions(tex)
    assert converted.count(r"\Description{") == 1
    assert r"\Description{Author supplied description.}" in converted
    assert "alt={" not in converted


def test_submission_abstract_reports_put_cluster_interval():
    assert "PUT-cluster" in tosem_build.ABSTRACT
    assert "[0.045, 0.594]" in tosem_build.ABSTRACT
