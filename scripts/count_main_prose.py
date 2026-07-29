from __future__ import annotations

import re
import sys
from pathlib import Path

COMMENT = re.compile(r"(?<!\\)%.*$")
DISPLAY_MATH = re.compile(
    r"\\\[.*?\\\]|"
    r"\\begin\{(?:equation|align\*?)\}.*?"
    r"\\end\{(?:equation|align\*?)\}",
    re.S,
)
INLINE_MATH = re.compile(r"\$.*?\$")
COMMAND = re.compile(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?")
BRACES = re.compile(r"[{}]")
WORD = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*")


def count_words(text: str) -> int:
    text = "\n".join(COMMENT.sub("", line) for line in text.splitlines())
    text = DISPLAY_MATH.sub(" ", text)
    text = INLINE_MATH.sub(" ", text)
    text = COMMAND.sub(" ", text)
    text = BRACES.sub(" ", text)
    return len(WORD.findall(text))


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "source/main.tex")
    print(count_words(path.read_text()))
