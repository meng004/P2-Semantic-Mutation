import tempfile
import pathlib
from p2.mutators.prompt_loader import load_prompt_template, render_prompt


def test_load_template_substitutes_variables():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "tmpl.txt"
        p.write_text("Inject {mut_intent} into {put_name}.")
        out = render_prompt(load_prompt_template(p), mut_intent="A", put_name="B")
        assert out == "Inject A into B."


def test_render_prompt_rejects_extra_vars():
    tmpl = "Hello {name}"
    out = render_prompt(tmpl, name="X")
    assert out == "Hello X"
