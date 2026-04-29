from pathlib import Path


def load_prompt_template(template_path: Path) -> str:
    return Path(template_path).read_text()


def render_prompt(template: str, **variables) -> str:
    return template.format(**variables)
