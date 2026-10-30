import re

def find_bad_underscores():
    with open("SAFE_VISION_Final_Project_Report.tex", "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_lst = False
    in_eq = False
    
    bad = []

    for idx, line in enumerate(lines):
        line_num = idx + 1
        l = line.strip()

        if r"\begin{lstlisting}" in l:
            in_lst = True
            continue
        if r"\end{lstlisting}" in l:
            in_lst = False
            continue
        if in_lst:
            continue

        if r"\begin{equation}" in l or r"\begin{align}" in l:
            in_eq = True
            continue
        if r"\end{equation}" in l or r"\end{align}" in l:
            in_eq = False
            continue
        if in_eq:
            # Inside equation environment, underscores are math subscripts (legal)
            continue

        # Strip inline math $...$
        # But wait! If an underscore is outside $...$, let's find it!
        # First remove labels, refs, cites, urls, includegraphics, IfFileExists
        clean = re.sub(r"\\(?:url|label|ref|cite|pageref|includegraphics|IfFileExists)\{[^}]*\}", "", l)
        
        # Now remove inline math $...$
        clean = re.sub(r"\$[^$]*\$", "", clean)
        
        # Check for unescaped _
        m = list(re.finditer(r"(?<!\\)_", clean))
        if m:
            bad.append((line_num, l))

    print(f"Total lines with unescaped underscore in text mode: {len(bad)}")
    for line_num, l in bad:
        print(f"Line {line_num}: {l}")

if __name__ == "__main__":
    find_bad_underscores()
