#!/usr/bin/env python3
"""Build a disposable TOSEM submission package from source/."""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import shutil
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "source"
VENUE = Path(__file__).resolve().parent
TEMPLATE = VENUE / "template"


ABSTRACT = (
    "Metamorphic testing mitigates the test-oracle problem by checking "
    "relations among executions, but classical mutation score is defined over "
    "syntactic edits and does not say whether a metamorphic-relation set "
    "observes declared domain-semantic effects. This paper introduces Semantic "
    "Mutation Score (SMS), an MR-relative adequacy metric over an admitted "
    "universe of nonequivalent semantic mutants with explicit certificates and "
    "a degeneration path back to classical mutation score. We instantiate five "
    "semantic operator families on 12 single-output scientific-computing "
    "programs and audit the resulting 60-cell design with an SMS-to-MS proof, "
    "an AST-normalized syntactic comparison, aligned-versus-cross relation "
    "analysis, and boundary and adjoint studies. The semantic pool has 5.14% "
    "AST-normalized overlap with default first-order syntactic mutants. "
    "Aligned cells score above cross-pattern cells (Cliff's delta 0.314); "
    "a 100,000-draw PUT-cluster bootstrap gives a 95% interval of "
    "[0.045, 0.594], supporting the directional hypothesis while the "
    "pre-registered large-effect threshold remains unmet. The attribution "
    "threshold is not evaluable as registered because zero-kill cells make "
    "its per-cell share undefined. An industrial real-defect arm of reproduced, MR-detectable "
    "defects from widely used scientific-computing libraries then tests the "
    "central construct claim: a four-group mutation comparison pre-registered "
    "in the dataset protocol "
    "and a per-defect detection face show that aggregate kill-rate, semantic "
    "alignment, and real-defect detection are related but distinct "
    "constructs. SMS is therefore a construct-level diagnostic for "
    "declared semantic strata, with its construct separation supported on "
    "industrial code."
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def copy_tree(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, dirs_exist_ok=True)


def copy_used_figures(out_dir: Path) -> None:
    tex = read(out_dir / "main.tex") + "\n" + read(out_dir / "supplementary.tex")
    figure_paths = sorted(set(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^{}]+)\}", tex)))
    for rel in figure_paths:
        if not rel.startswith("figures/"):
            continue
        src = SOURCE / rel
        if not src.exists():
            raise FileNotFoundError(f"missing figure referenced by manuscript: {rel}")
        dst = out_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def write_supplement_readme(out_dir: Path) -> None:
    write(
        out_dir / "readme.txt",
        "Supplementary material for the TOSEM submission \"A Semantic Mutation "
        "Metric for Metamorphic-Relation Adequacy in Scientific Computing "
        "Programs\".\n\n"
        "Contents: supplementary.pdf (with LaTeX source supplementary.tex) "
        "provides Appendices A-I: notation and the operator catalogue, "
        "experimental subjects and operator specialisations, procedure "
        "details, statistical analysis details, deployment considerations, "
        "threats-to-validity mitigation, the full SMS-to-MS degeneration "
        "proof, the adjoint extension arm, and the result-level real-defect "
        "evidence summary supporting the main article.\n\n"
        "Usage: read supplementary.pdf alongside the main manuscript; the "
        "main text points to the relevant appendix at each use. To recompile, "
        "run xelatex and BibTeX with the ACM acmart class files included in "
        "this package.\n",
    )


TRACK_SLUGS = {
    "fastimpact": "fastimpact",
    "regular": "regular",
}


def make_clean_zip(out_dir: Path) -> Path:
    ignored_suffixes = {
        ".aux",
        ".blg",
        ".log",
        ".out",
        ".toc",
        ".fls",
        ".fdb_latexmk",
        ".synctex.gz",
    }
    zip_path = out_dir.with_name(f"{out_dir.name}_clean.zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out_dir.rglob("*")):
            if not path.is_file():
                continue
            name = path.name
            if any(name.endswith(suffix) for suffix in ignored_suffixes):
                continue
            archive.write(path, path.relative_to(out_dir.parent))
    return zip_path


def extract_after_frontmatter(tex: str) -> str:
    marker = r"\end{frontmatter}"
    if marker not in tex:
        raise ValueError("source file has no \\end{frontmatter}")
    # Split on the LAST occurrence: the venue-neutral header comment near the
    # top of source/main.tex also mentions \end{frontmatter}, and splitting on
    # the first match would drag the authoring preamble into the body.
    return tex.rsplit(marker, 1)[1].strip()


def strip_references_and_tail(tex: str) -> str:
    markers = [r"\subsection{References}", r"\bibliographystyle{plainnat}"]
    positions = [tex.find(marker) for marker in markers if tex.find(marker) >= 0]
    if not positions:
        return tex.replace(r"\end{document}", "").strip()
    return tex[: min(positions)].strip()


def sectionize_main(tex: str) -> str:
    tex = re.sub(r"\\subsection\{[0-9]+\.\s*", r"\\section{", tex)
    tex = re.sub(r"\\subsubsection\{[0-9]+(?:\.[0-9]+)+\s*", r"\\subsection{", tex)
    tex = sanitize_section_titles(tex)
    return tex


def sectionize_supplement(tex: str) -> str:
    tex = re.sub(r"\\subsection\{[A-Z]\.\s*", r"\\section{", tex)
    tex = re.sub(r"\\subsubsection\{[A-Z](?:\.[0-9]+)+\s*", r"\\subsection{", tex)
    tex = sanitize_section_titles(tex)
    return tex


def sanitize_section_titles(tex: str) -> str:
    replacements = {
        r"Equivalence judgement E1 $\wedge$ E2": "Equivalence judgement E1 and E2",
        r"SMS $\to$ MS degeneration: formal statement": "SMS-to-MS degeneration: formal statement",
        r"SMS $\to$ MS Degeneration Theorem, Full Proof": "SMS-to-MS Degeneration Theorem, Full Proof",
        r"Decoupling between R\_sem and R\_kill": "Decoupling between Rsem and Rkill",
    }
    for old, new in replacements.items():
        tex = tex.replace(old, new)
    return tex


def normalize_symbols(tex: str) -> str:
    replacements = {
        r"\checkmark": r"\ding{51}",
        r"\tightlist": "",
        r"\llbracket": r"\mathopen{\lbrack\!\lbrack}",
        r"\rrbracket": r"\mathclose{\rbrack\!\rbrack}",
        "∀": r"$\forall$",
        "∃": r"$\exists$",
        "∈": r"$\in$",
        "∪": r"$\cup$",
        "∧": r"$\wedge$",
        "→": r"$\rightarrow$",
        "⇔": r"$\Leftrightarrow$",
        "≠": r"$\neq$",
        "≡": r"$\equiv$",
        "≤": r"$\leq$",
        "≥": r"$\geq$",
        "−": r"$-$",
        "±": r"$\pm$",
        "×": r"$\times$",
        "✓": r"\ding{51}",
        "✗": r"\ding{55}",
        "⁺": r"$^{+}$",
        "Δ": r"$\Delta$",
        "ε": r"$\varepsilon$",
        "○": r"$\circ$",
        "●": r"$\bullet$",
        "═": "=",
        "̂": "",
    }
    for old, new in replacements.items():
        tex = tex.replace(old, new)
    tex = re.sub(
        r"\\begin\{enumerate\}\n\s*\\def\\labelenumi\{\(\\alph\{enumi\}\)\}",
        r"\\begin{enumerate}",
        tex,
    )
    tex = tex.replace(
        r"\begin{tabularx}{\textwidth}{p{0.22\textwidth}p{0.34\textwidth}X}",
        r"\begin{tabular}{p{0.22\textwidth}p{0.34\textwidth}p{0.34\textwidth}}",
    )
    tex = tex.replace(r"\end{tabularx}", r"\end{tabular}")
    tex = re.sub(
        r"\{\\scriptsize\\def\\LTcaptype\{table\} % do not increment counter\n",
        lambda _: "{\\scriptsize\n",
        tex,
    )
    tex = re.sub(
        r"\{\\def\\LTcaptype\{table\}(?: % do not increment counter)?\n",
        lambda _: "{%\n",
        tex,
    )
    tex = re.sub(
        r"^[ \t]*\\def\\_\{\\textunderscore\\penalty0\\hspace\{0pt\}\} % allow line break at underscore inside this table\n",
        "",
        tex,
        flags=re.M,
    )
    return tex


def convert_fig_descriptions(tex: str) -> str:
    def repl_include(match: re.Match[str]) -> str:
        options = match.group(1)
        description = match.group(2).replace(r"\textbackslash", "backslash")
        path = match.group(3)
        clean_options = re.sub(r",?\s*alt=\{[^{}]*\}", "", options).strip().strip(",")
        include = rf"\includegraphics[{clean_options}]{{{path}}}"
        following = tex[match.end() :]
        if re.match(r"\s*\\Description\{", following):
            return include
        return include + "\n" + r"\Description{" + description + "}"

    return re.sub(
        r"\\includegraphics\[([^\]]*?)\s*,\s*alt=\{([^{}]*)\}\]\{([^{}]+)\}",
        repl_include,
        tex,
        flags=re.S,
    )


def acm_preamble(title: str, short_title: str) -> str:
    return rf"""%!TEX TS-program = xelatex
%!TEX encoding = UTF-8 Unicode
\documentclass[manuscript,screen,review]{{acmart}}

\setcopyright{{none}}
\copyrightyear{{2026}}
\acmYear{{2026}}
\acmJournal{{TOSEM}}
\settopmatter{{printacmref=true, printccs=true, printfolios=true}}
\setcitestyle{{numbers,sort&compress,square}}

\usepackage{{amssymb,amsthm}}
\usepackage{{mathtools}}
\usepackage{{calc}}
\usepackage{{enumitem}}
\usepackage{{longtable}}
\usepackage{{array}}
\usepackage{{listings}}
\usepackage{{pifont}}

\setlength{{\emergencystretch}}{{3em}}
\lstset{{
  breaklines=true,
  breakatwhitespace=true,
  basicstyle=\ttfamily\small,
  frame=none,
  columns=fullflexible
}}

\title[{short_title}]{{{title}}}

\author{{Meng Li}}
\orcid{{0000-0002-1074-1502}}
\email{{mlemon@usc.edu.cn}}
\affiliation{{%
  \institution{{School of Computing, University of South China}}
  \city{{Hengyang}}
  \country{{China}}
}}
\affiliation{{%
  \institution{{Hunan Engineering Research Center of Software Evaluation and Testing for Intellectual Equipment}}
  \city{{Hengyang}}
  \country{{China}}
}}
\affiliation{{%
  \institution{{CNNC Key Laboratory on High Trusted Computing}}
  \city{{Hengyang}}
  \country{{China}}
}}

\author{{Xiaohua Yang}}
\orcid{{0000-0002-2977-1787}}
\email{{xiaohua1963@foxmail.com}}
\affiliation{{%
  \institution{{School of Computing, University of South China}}
  \city{{Hengyang}}
  \country{{China}}
}}

\author{{Jie Liu}}
\orcid{{0009-0008-1970-8347}}
\email{{jieliu@usc.edu.cn}}
\affiliation{{%
  \institution{{School of Computing, University of South China}}
  \city{{Hengyang}}
  \country{{China}}
}}

\author{{Shiyu Yan}}
\orcid{{0000-0001-7626-5185}}
\email{{yanshiyu@usc.edu.cn}}
\affiliation{{%
  \institution{{School of Computing, University of South China}}
  \city{{Hengyang}}
  \country{{China}}
}}

\begin{{CCSXML}}
<ccs2012>
 <concept>
  <concept_id>10011007.10011074.10011099.10011102</concept_id>
  <concept_desc>Software and its engineering~Software testing and debugging</concept_desc>
  <concept_significance>500</concept_significance>
 </concept>
 <concept>
  <concept_id>10011007.10011074.10011099</concept_id>
  <concept_desc>Software and its engineering~Software verification and validation</concept_desc>
  <concept_significance>300</concept_significance>
 </concept>
</ccs2012>
\end{{CCSXML}}

\ccsdesc[500]{{Software and its engineering~Software testing and debugging}}
\ccsdesc[300]{{Software and its engineering~Software verification and validation}}

\keywords{{metamorphic testing, mutation testing, semantic mutation testing, metamorphic relation adequacy, metamorphic relation assessment, scientific computing}}
"""


def main_statements() -> str:
    return r"""
\section*{Supplementary Material}

Appendices A--I (notation and operator catalogue; experimental subjects and
operator specialisations; experimental procedure details; statistical analysis
details; deployment considerations; detailed threats-to-validity mitigation;
the full SMS-to-MS degeneration proof; the adjoint extension arm; and a
result-level real-defect evidence summary) are provided as separate online
supplementary material.

\section*{Funding}

This work was supported by the National Natural Science Foundation of China
(NSFC) General Program (grant no. 12575176); the Hunan Provincial Education
Department Project, China (grant no. 202502000728); the Research Project on
Degree and Graduate Education Reform of the University of South China (grant
no. 2023JG030); the Natural Science Foundation of Hunan Province, China (grant
no. 2025JJ70193); and an industry-funded research project (grant no.
230KHX060001).

\section*{CRediT authorship contribution statement}

\textbf{Meng Li}: Conceptualization, Methodology, Software, Writing, original
draft. \textbf{Xiaohua Yang}: Supervision, Formal analysis, Writing, review
and editing. \textbf{Jie Liu}: Investigation, Validation. \textbf{Shiyu Yan}:
Data curation, Visualization.

\section*{Declaration of competing interest}

The authors declare that they have no known competing financial interests or
personal relationships that could have appeared to influence the work reported
in this paper.

\section*{Generative AI Disclosure}

The authors used AI tools under human direction for editorial proofreading,
LaTeX maintenance, consistency checks, and review-simulation support. All
research claims, methods, experimental data, analyses, and conclusions were
authored, verified, and approved by the human authors.
"""


def build_main() -> str:
    source = read(SOURCE / "main.tex")
    body = strip_references_and_tail(extract_after_frontmatter(source))
    body = sectionize_main(body)
    body = normalize_symbols(body)
    body = convert_fig_descriptions(body)
    return (
        acm_preamble(
            "A Semantic Mutation Metric for Metamorphic-Relation Adequacy in Scientific Computing Programs",
            "Semantic Mutation Score for MR Adequacy",
        )
        + "\n\\begin{document}\n\n"
        + "\\begin{abstract}\n"
        + ABSTRACT
        + "\n\\end{abstract}\n\n"
        + "\\maketitle\n\n"
        + body
        + "\n\n"
        + main_statements()
        + "\n\\bibliographystyle{ACM-Reference-Format}\n"
        + "\\bibliography{references}\n\n"
        + "\\end{document}\n"
    )


def build_supplement() -> str:
    source = read(SOURCE / "supplementary.tex")
    body = strip_references_and_tail(extract_after_frontmatter(source))
    body = sectionize_supplement(body)
    body = normalize_symbols(body)
    return (
        acm_preamble(
            "Supplementary Material for ``A Semantic Mutation Metric for Metamorphic-Relation Adequacy in Scientific Computing Programs''",
            "Supplementary Material",
        )
        + "\n\\begin{document}\n\n"
        + "\\maketitle\n\n"
        + body
        + "\n\n\\bibliographystyle{ACM-Reference-Format}\n"
        + "\\bibliography{references}\n\n"
        + "\\end{document}\n"
    )


def run(cmd: list[str], cwd: Path) -> None:
    runner = ["rtk"] if shutil.which("rtk") else []
    subprocess.run(runner + cmd, cwd=cwd, check=True)


def compile_tex(out_dir: Path, stem: str) -> None:
    run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"], out_dir)
    run(["bibtex", stem], out_dir)
    run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"], out_dir)
    run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"], out_dir)


def precheck(tex: str) -> list[str]:
    checks = [
        (r"\\documentclass\[manuscript,screen,review\]\{acmart\}", "missing ACM manuscript review documentclass"),
        (r"\\acmJournal\{TOSEM\}", "missing \\acmJournal{TOSEM}"),
        (r"\\begin\{CCSXML\}", "missing CCSXML"),
        (r"\\ccsdesc", "missing ccsdesc"),
        (r"\\keywords\{", "missing keywords"),
        (r"\\bibliographystyle\{ACM-Reference-Format\}", "missing ACM bibliography style"),
        (r"\\Description\{", "missing ACM figure descriptions"),
        (r"Generative AI Disclosure", "missing GenAI disclosure"),
        (r"arXiv:2605.17437", "missing prior-version disclosure"),
    ]
    return [message for pattern, message in checks if not re.search(pattern, tex)]


def package_precheck(out_dir: Path, track: str) -> list[str]:
    errors: list[str] = []
    if track != "fastimpact":
        return errors

    cover = read(out_dir / "cover_letter.md")
    declarations = read(out_dir / "declarations.md")
    combined = cover + "\n" + declarations
    checks = [
        (r"Journal-First", "missing Journal-First track statement"),
        (r"Fast-Impact", "missing Fast-Impact eligibility statement"),
        (r"novelty statement", "missing journal-first novelty statement"),
        (r"45-page", "missing 45-page length-threshold statement"),
        (r"arXiv:2605\.17437", "missing disclosed arXiv prior version"),
        (r"10\.5281/zenodo\.20250664", "missing artifact DOI"),
    ]
    errors.extend(message for pattern, message in checks if not re.search(pattern, combined))
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=_dt.date.today().strftime("%Y%m%d"))
    parser.add_argument(
        "--track",
        choices=sorted(TRACK_SLUGS),
        default="fastimpact",
        help="TOSEM submission track packaging label.",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-compile", action="store_true")
    args = parser.parse_args()

    out_dir = ROOT / "submission" / f"TOSEM_{TRACK_SLUGS[args.track]}_{args.date}"
    if out_dir.exists():
        if not args.force:
            raise SystemExit(f"{out_dir} already exists; use --force to rebuild it.")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    write(out_dir / "main.tex", build_main())
    write(out_dir / "supplementary.tex", build_supplement())
    shutil.copy2(SOURCE / "references.bib", out_dir / "references.bib")
    copy_used_figures(out_dir)
    for name in ("acmart.cls", "ACM-Reference-Format.bst", "acmsmall-submission.tex", "acmmanuscript.tex"):
        template_path = TEMPLATE / name
        if template_path.exists():
            shutil.copy2(template_path, out_dir / name)
    for name in ("cover_letter.md", "declarations.md"):
        shutil.copy2(VENUE / name, out_dir / name)
    write_supplement_readme(out_dir)

    errors = precheck(read(out_dir / "main.tex"))
    errors.extend(package_precheck(out_dir, args.track))
    if errors:
        for error in errors:
            print(f"TOSEM precheck: {error}")
        raise SystemExit(1)

    if not args.no_compile:
        compile_tex(out_dir, "main")
        compile_tex(out_dir, "supplementary")
        make_clean_zip(out_dir)

    print(out_dir)


if __name__ == "__main__":
    main()
