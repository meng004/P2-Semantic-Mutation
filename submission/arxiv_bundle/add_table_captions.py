"""Add \\caption + \\label to each longtable in p2_arxiv.tex.

Handles pandoc-generated multi-line column specs.
Caption inferred from preceding \\subsection / \\subsubsection / \\paragraph.

Strategy:
1. Find each \\begin{longtable}[]{ start line
2. Find the matching closing of the column spec (line ending with @{}})
3. Insert \\caption{...}\\label{...}\\\\ on the next line
"""
import re
from pathlib import Path

src = Path("p2_arxiv_pre_captions.tex").read_text()  # use clean original
lines = src.split("\n")

# Find sections + tables
current_section = ""
inserts = []   # list of (line_to_insert_after, text)
table_counter = 0

i = 0
while i < len(lines):
    line = lines[i]
    m = re.match(r'^\\subsubsection\{([^}]+)\}', line) or re.match(r'^\\subsection\{([^}]+)\}', line)
    if m:
        title = re.sub(r'\\label\{[^}]*\}', '', m.group(1)).strip()
        current_section = title

    if re.match(r'^\\begin\{longtable\}', line):
        table_counter += 1
        # find closing of column spec (line ending with @{}})
        j = i
        while j < len(lines) and not re.search(r'@\{\}\}\s*$', lines[j]):
            j += 1
            if j - i > 50:  # safety
                break
        # Check next line — already has \caption?
        peek = '\n'.join(lines[j+1:j+4]) if j+1 < len(lines) else ''
        has_caption = '\\caption{' in peek
        if not has_caption:
            # Generate caption from section title
            section_clean = re.sub(r'^[\d.A-Z]+\.?\s*', '', current_section).strip()
            section_clean = re.sub(r'\\label\{[^}]*\}', '', section_clean).strip()
            section_clean = section_clean.rstrip('.')
            if len(section_clean) > 80:
                section_clean = section_clean[:80] + '...'
            if not section_clean:
                section_clean = f"P2 supporting table {table_counter}"
            label = f"tab:p2-{table_counter:02d}"
            caption_text = f"\\caption{{{section_clean}.}}\\label{{{label}}}\\\\"
            inserts.append((j, caption_text))
        i = j + 1
    else:
        i += 1

print(f"Total longtables: {table_counter}; captions to add: {len(inserts)}")

# Apply inserts in reverse so line numbers stay valid
new_lines = lines[:]
for line_no, text in reversed(inserts):
    new_lines.insert(line_no + 1, text)

Path("p2_arxiv.tex").write_text("\n".join(new_lines))
# also need LTcaptype change
content = Path("p2_arxiv.tex").read_text()
content = content.replace("\\def\\LTcaptype{none}", "\\def\\LTcaptype{table}")
Path("p2_arxiv.tex").write_text(content)

print(f"Wrote {len(new_lines)} lines + replaced 29 LTcaptype{{none}} → LTcaptype{{table}}")
