"""Postprocess generated p2_ist.tex to wrap missing-glyph Unicode in math.

After build_ist_submission.sh produces submission/p2_ist.tex via pandoc,
many Unicode math operators (∧, ⊄, ∈, etc.) and ornament glyphs (✓, ✗,
△, ●, ○) render as missing characters in Times New Roman. This script
performs a literal substitution to wrap them in $...$ (math) or
\textsymbol-style commands so they render correctly.

Run AFTER build_ist_submission.sh and BEFORE xelatex compile.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "submission" / "p2_ist.tex"

# Map of literal Unicode → LaTeX replacement (math-mode for math operators,
# text-mode \textsymbol for ornaments, $...$ to keep them inline).
SUBSTITUTIONS = [
    # math operators
    ("∧", r"$\wedge$"),
    ("∨", r"$\vee$"),
    ("∩", r"$\cap$"),
    ("∪", r"$\cup$"),
    ("⊂", r"$\subset$"),
    ("⊃", r"$\supset$"),
    ("⊆", r"$\subseteq$"),
    ("⊇", r"$\supseteq$"),
    ("⊄", r"$\not\subset$"),
    ("⊅", r"$\not\supset$"),
    ("∈", r"$\in$"),
    ("∉", r"$\notin$"),
    ("∅", r"$\emptyset$"),
    ("∞", r"$\infty$"),
    ("∑", r"$\sum$"),
    ("∏", r"$\prod$"),
    ("∫", r"$\int$"),
    ("∎", r"$\blacksquare$"),
    ("∀", r"$\forall$"),
    ("∃", r"$\exists$"),
    ("★", r"$\star$"),
    ("≥", r"$\geq$"),
    ("≤", r"$\leq$"),
    ("≈", r"$\approx$"),
    ("≠", r"$\neq$"),
    ("≪", r"$\ll$"),
    ("≫", r"$\gg$"),
    ("→", r"$\to$"),
    ("←", r"$\leftarrow$"),
    ("↔", r"$\leftrightarrow$"),
    ("·", r"$\cdot$"),
    ("×", r"$\times$"),
    ("÷", r"$\div$"),
    # Greek letters (lowercase)
    ("α", r"$\alpha$"),
    ("β", r"$\beta$"),
    ("γ", r"$\gamma$"),
    ("δ", r"$\delta$"),
    ("ε", r"$\varepsilon$"),
    ("ζ", r"$\zeta$"),
    ("η", r"$\eta$"),
    ("θ", r"$\theta$"),
    ("ι", r"$\iota$"),
    ("κ", r"$\kappa$"),
    ("λ", r"$\lambda$"),
    ("μ", r"$\mu$"),
    ("ν", r"$\nu$"),
    ("ξ", r"$\xi$"),
    ("π", r"$\pi$"),
    ("ρ", r"$\rho$"),
    ("σ", r"$\sigma$"),
    ("τ", r"$\tau$"),
    ("υ", r"$\upsilon$"),
    ("φ", r"$\varphi$"),
    ("χ", r"$\chi$"),
    ("ψ", r"$\psi$"),
    ("ω", r"$\omega$"),
    # Greek letters (uppercase, those needed)
    ("Δ", r"$\Delta$"),
    ("Γ", r"$\Gamma$"),
    ("Λ", r"$\Lambda$"),
    ("Σ", r"$\Sigma$"),
    ("Ω", r"$\Omega$"),
    # ornaments / table markers
    ("✓", r"\checkmark"),
    ("✗", r"$\times$"),
    ("△", r"$\bigtriangleup$"),
    ("●", r"\textbullet"),
    ("○", r"$\circ$"),
    ("◎", r"$\bullet$"),
    # superscript/subscript digits commonly seen
    ("²", r"$^{2}$"),
    ("³", r"$^{3}$"),
    ("⁰", r"$^{0}$"),
    ("¹", r"$^{1}$"),
    ("⁴", r"$^{4}$"),
    ("⁵", r"$^{5}$"),
    ("₀", r"$_{0}$"),
    ("₁", r"$_{1}$"),
    ("₂", r"$_{2}$"),
    # double bar, vertical bar
    ("‖", r"$\|$"),
    # box-drawing → ASCII
    ("┌", "+"), ("┐", "+"), ("└", "+"), ("┘", "+"),
    ("─", "-"), ("│", "|"),
    ("├", "+"), ("┤", "+"), ("┬", "+"), ("┴", "+"), ("┼", "+"),
    # other ops occasionally seen
    ("⊔", r"$\sqcup$"),
    ("⊓", r"$\sqcap$"),
    # whitespace-like
    (" ", " "),  # NBSP → regular
]


def _split_verbatim(text):
    """Split TeX text into segments, marking verbatim blocks so substitutions
    skip them. Returns list of (is_verbatim, segment) tuples.

    Verbatim blocks in LaTeX render their content literally. If we substitute
    Unicode glyphs to LaTeX commands inside verbatim, the commands show as
    raw text instead of the glyph. So we must preserve the original Unicode
    inside verbatim — xelatex with the right font actually renders them fine
    when in verbatim (Menlo / Courier supports the Unicode glyphs we use).
    """
    import re
    segments = []
    # Match \begin{verbatim}...\end{verbatim} (single-line content allowed)
    pattern = re.compile(r"(\\begin\{verbatim\}.*?\\end\{verbatim\})", re.DOTALL)
    last_end = 0
    for m in pattern.finditer(text):
        if m.start() > last_end:
            segments.append((False, text[last_end:m.start()]))
        segments.append((True, m.group(0)))
        last_end = m.end()
    if last_end < len(text):
        segments.append((False, text[last_end:]))
    return segments


def main():
    if not TEX.exists():
        raise FileNotFoundError(TEX)
    text = TEX.read_text(encoding="utf-8")
    n_total = 0
    n_skipped_verbatim = 0
    segments = _split_verbatim(text)
    for i, (is_verb, seg) in enumerate(segments):
        if is_verb:
            # Count what we're skipping for telemetry
            for src, _ in SUBSTITUTIONS:
                n_skipped_verbatim += seg.count(src)
            continue
        for src, dst in SUBSTITUTIONS:
            n = seg.count(src)
            if n:
                seg = seg.replace(src, dst)
                n_total += n
        segments[i] = (False, seg)
    text = "".join(seg for _, seg in segments)
    TEX.write_text(text, encoding="utf-8")
    print(f"Postprocessed {n_total} substitutions in {TEX} "
          f"({n_skipped_verbatim} preserved inside verbatim blocks)")


if __name__ == "__main__":
    main()
