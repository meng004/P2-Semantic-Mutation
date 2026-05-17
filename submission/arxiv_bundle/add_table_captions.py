"""Add \\caption + \\label to each longtable in p2_arxiv.tex.

Handles pandoc-generated multi-line column specs AND multi-line section titles.
"""
import re
from pathlib import Path

src = Path("p2_arxiv_pre_captions.tex").read_text()
lines = src.split("\n")

# Pre-process: find all sections (handle multi-line titles)
section_starts = []  # list of (line_no, full_title)
joined = "\n".join(lines)
for m in re.finditer(r'\\(subsection|subsubsection)\{((?:[^{}]|\{[^{}]*\})*)\}\\label\{[^}]*\}', joined):
    cmd = m.group(1)
    title = re.sub(r'\s+', ' ', m.group(2)).strip()
    # Find line number
    line_no = joined.count('\n', 0, m.start())
    section_starts.append((line_no, title))

# Find longtables
current_section = ""
inserts = []
table_counter = 0
section_idx = 0

for i, line in enumerate(lines):
    # Advance section pointer
    while section_idx < len(section_starts) and section_starts[section_idx][0] <= i:
        current_section = section_starts[section_idx][1]
        section_idx += 1

    if re.match(r'^\\begin\{longtable\}', line):
        table_counter += 1
        # find end of column spec
        j = i
        while j < len(lines) and not re.search(r'@\{\}\}\s*$', lines[j]):
            j += 1
            if j - i > 50: break
        # check if already has caption
        peek = '\n'.join(lines[j+1:j+4]) if j+1 < len(lines) else ''
        if '\\caption{' not in peek:
            # Strip numeric prefix "1.2 " / "B.1 "
            clean = re.sub(r'^[\d.A-Z]+\.?\s*', '', current_section).strip()
            clean = clean.rstrip('.')
            if len(clean) > 100:
                clean = clean[:100] + '...'
            if not clean:
                clean = f"P2 supporting table {table_counter}"
            # Avoid LaTeX-special chars in caption
            clean = clean.replace('\\&', '\\&')  # already escaped is fine
            label = f"tab:p2-{table_counter:02d}"
            caption = f"\\caption{{{clean} (table {table_counter}).}}\\label{{{label}}}\\\\"
            inserts.append((j, caption))

print(f"Total longtables: {table_counter}; sections found: {len(section_starts)}; captions added: {len(inserts)}")

# Apply
new_lines = lines[:]
for line_no, text in reversed(inserts):
    new_lines.insert(line_no + 1, text)

content = "\n".join(new_lines)
content = content.replace("\\def\\LTcaptype{none}", "\\def\\LTcaptype{table}")
Path("p2_arxiv.tex").write_text(content)
print(f"Wrote {len(new_lines)} lines + replaced LTcaptype")
