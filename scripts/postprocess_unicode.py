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


def main():
    if not TEX.exists():
        raise FileNotFoundError(TEX)
    text = TEX.read_text(encoding="utf-8")
    n_total = 0
    for src, dst in SUBSTITUTIONS:
        n = text.count(src)
        if n:
            text = text.replace(src, dst)
            n_total += n
    TEX.write_text(text, encoding="utf-8")
    print(f"Postprocessed {n_total} substitutions in {TEX}")


if __name__ == "__main__":
    main()
