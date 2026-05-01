"""Translate 论文初稿P2.md (Chinese) to English using Anthropic API.

Strategy:
- Split paper by '## 第 N 节' markers; translate one section per request.
- Send the terminology table (docs/terminology_zh_en.md) once via prompt
  caching (cache_control on the system block) so subsequent section
  requests reuse the same cached glossary.
- Use Claude Opus 4.7 with extended thinking; output to 论文初稿P2_EN.md.

Cost estimate (Opus 4.7, ~85 KB Chinese paper, ~12k Chinese chars ≈ 18k input
tokens after splitting + ~12k output tokens per section × 7 sections):
- Cache write: ~3k tokens × $18.75/M = $0.06 (one-shot)
- Cache read: ~3k × 7 × $1.50/M = $0.03
- Section input: ~3k × 7 × $15/M = $0.32
- Section output: ~12k × 7 × $75/M = $6.30
- Total ≈ $6.70

Run with:
  PYTHONPATH=src .venv/bin/python scripts/translate_paper.py [--section 1] [--dry-run]

Resumability: each section writes to 论文初稿P2_EN.md.s{N}.partial; the final
assembly step concatenates them. If a section fails, rerun with --section N.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER_ZH = ROOT / "论文初稿P2.md"
PAPER_EN = ROOT / "论文初稿P2_EN.md"
TERM_GLOSSARY = ROOT / "docs/terminology_zh_en.md"
PARTIAL_DIR = ROOT / ".translate_cache"

SYSTEM_PROMPT = """You are translating a peer-reviewed academic paper from
Chinese to English for a Q1 software engineering journal (Information and
Software Technology). The paper introduces the Semantic Mutation Score (SMS)
metric for metamorphic testing adequacy.

Translation requirements (priority order):
1. Preserve ALL technical terminology exactly as listed in the glossary below.
2. Keep code identifiers, filenames, ID labels (RQ1, H2, R-25, D1, MP3, AVP,
   LRCA), Greek letters (δ, χ², ε), and citations literal.
3. Markdown structure (heading levels, lists, tables, code fences) MUST be
   preserved byte-for-byte except for the natural-language content inside.
4. Use formal academic English, present tense for claims, past tense for
   methods/results, IS-style empirical paper voice.
5. Number formatting: decimal point (0.275 not 0,275), `p = 0.0041` style.
6. Do NOT add reviewer-pleasing hedges that aren't in the source. Do NOT
   restructure the argument. Do NOT delete content.
7. If a Chinese phrase has no clean English equivalent, use the gloss given
   in the "Phrases that must NOT be literal-translated" section of the
   glossary.

Output format: emit the translated section as raw markdown, no front matter,
no commentary, no surrounding code fences. Begin output with the translated
section heading (e.g., `## Section 1 · Paper Identity and Claims`).

The glossary follows; treat it as authoritative and non-negotiable.
"""


def split_sections(text: str) -> list[tuple[str, str]]:
    """Split paper into (label, body) pairs by '## 第 N 节' markers.

    Returns sections in source order, including the prelude (everything
    before §1) labeled 's0_prelude' and any tail content labeled 's8_tail'.
    """
    pattern = re.compile(r"^## 第 (\d+) 节[^\n]*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if not matches:
        return [("s0_full", text)]

    sections = []
    if matches[0].start() > 0:
        sections.append(("s0_prelude", text[: matches[0].start()]))

    for i, m in enumerate(matches):
        n = m.group(1)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((f"s{n}", text[m.start() : end]))

    return sections


def translate_section(client, label: str, body: str, glossary: str, dry_run: bool):
    """Translate one section via Anthropic API with prompt caching."""
    if dry_run:
        print(f"[DRY RUN] would translate {label}: {len(body)} chars")
        return f"<DRY RUN placeholder for {label}>\n"

    system_blocks = [
        {"type": "text", "text": SYSTEM_PROMPT},
        {
            "type": "text",
            "text": f"# Glossary (authoritative)\n\n{glossary}",
            "cache_control": {"type": "ephemeral"},
        },
    ]

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        system=system_blocks,
        messages=[
            {
                "role": "user",
                "content": f"Translate the following section to English, "
                f"preserving all markdown structure and applying the "
                f"glossary strictly:\n\n{body}",
            }
        ],
    )

    usage = response.usage
    print(
        f"  {label}: input={usage.input_tokens}, "
        f"cache_read={getattr(usage, 'cache_read_input_tokens', 0)}, "
        f"cache_create={getattr(usage, 'cache_creation_input_tokens', 0)}, "
        f"output={usage.output_tokens}"
    )
    return response.content[0].text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--section", type=int, default=None,
        help="Translate only section N (1-7). Omit to translate all.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Don't call API; print sizes and exit.",
    )
    parser.add_argument(
        "--assemble-only", action="store_true",
        help="Skip translation; concatenate cached partials into PAPER_EN.",
    )
    args = parser.parse_args()

    if not PAPER_ZH.exists():
        sys.exit(f"Paper not found: {PAPER_ZH}")
    if not TERM_GLOSSARY.exists():
        sys.exit(f"Glossary not found: {TERM_GLOSSARY}")

    text = PAPER_ZH.read_text(encoding="utf-8")
    glossary = TERM_GLOSSARY.read_text(encoding="utf-8")
    sections = split_sections(text)

    print(f"Paper: {len(text):,} chars, {len(sections)} sections")
    for label, body in sections:
        print(f"  {label}: {len(body):,} chars")

    PARTIAL_DIR.mkdir(exist_ok=True)

    if args.assemble_only:
        parts = []
        for label, _ in sections:
            p = PARTIAL_DIR / f"{label}.en.md"
            if not p.exists():
                sys.exit(f"Missing partial: {p}; run translation first")
            parts.append(p.read_text(encoding="utf-8"))
        PAPER_EN.write_text("\n\n".join(parts), encoding="utf-8")
        print(f"Assembled -> {PAPER_EN} ({PAPER_EN.stat().st_size:,} bytes)")
        return

    if not args.dry_run:
        try:
            from anthropic import Anthropic  # type: ignore[import-not-found]
        except ImportError:
            sys.exit("anthropic SDK not installed; pip install anthropic")
        from dotenv import load_dotenv  # type: ignore[import-not-found]
        load_dotenv(ROOT / ".env")
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("ANTHROPIC_API_KEY not set; see .env.example")
        client = Anthropic()
    else:
        client = None

    target_sections = sections
    if args.section is not None:
        label_target = f"s{args.section}"
        target_sections = [(l, b) for l, b in sections if l == label_target]
        if not target_sections:
            sys.exit(f"No section labeled {label_target}")

    for label, body in target_sections:
        out_path = PARTIAL_DIR / f"{label}.en.md"
        if out_path.exists() and args.section is None and not args.dry_run:
            print(f"  {label}: already translated, skipping (delete partial to redo)")
            continue
        print(f"Translating {label} ({len(body):,} chars) ...")
        translated = translate_section(client, label, body, glossary, args.dry_run)
        if not args.dry_run:
            out_path.write_text(translated, encoding="utf-8")
            print(f"  -> {out_path}")

    print(f"\nNext step: python {Path(__file__).name} --assemble-only")


if __name__ == "__main__":
    main()
