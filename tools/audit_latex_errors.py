import re
import sys

def audit(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    errors = []
    in_listing = False
    in_tabular = False
    in_align = False

    for idx, raw_line in enumerate(lines):
        line_num = idx + 1
        line = raw_line.strip()

        if r"\begin{lstlisting}" in line:
            in_listing = True
            continue
        if r"\end{lstlisting}" in line:
            in_listing = False
            continue
        if in_listing:
            continue

        # Check for tabular / align
        if r"\begin{tabular}" in line:
            in_tabular = True
        if r"\end{tabular}" in line:
            in_tabular = False

        if r"\begin{align}" in line:
            in_align = True
        if r"\end{align}" in line:
            in_align = False

        # Strip comments
        # A % not preceded by \
        m = re.search(r"(?<!\\)%", line)
        code = line[:m.start()] if m else line

        # 1. Check unescaped &
        # If not in tabular or align:
        if not in_tabular and not in_align:
            # & not preceded by \ and not inside \begin{cases}...\end{cases}
            # Note: cases might span lines, but let's check
            if re.search(r"(?<!\\)&", code):
                # Is it inside cases?
                # Let's check if the line has cases syntax or if it's a section / caption / text
                if not ("cases" in line or "\\\\" in line and ("=" in line or "\\text{" in line)):
                    errors.append((line_num, "UNESCAPED_AMPERSAND", line))

        # Inside tabular, check if & is inside \textbf{...} or \emph{...}
        if in_tabular:
            # find macros with arguments
            for macro in ["textbf", "emph", "textit", "texttt", "caption"]:
                for sub in re.finditer(r"\\" + macro + r"\{([^}]+)\}", code):
                    arg = sub.group(1)
                    if re.search(r"(?<!\\)&", arg):
                        errors.append((line_num, f"AMPERSAND_INSIDE_{macro.upper()}", line))

        # 2. Check unescaped _ outside math mode
        # Strip all math mode $...$
        non_math = re.sub(r"\$[^$]*\$", "", code)
        # Strip \url{...}, \lstinline{...}, \path{...}, \label{...}, \ref{...}, \cite{...}, \includegraphics{...}, \IfFileExists{...}
        non_math = re.sub(r"\\(?:url|lstinline|path|label|ref|cite|includegraphics|IfFileExists)\{[^}]*\}", "", non_math)
        
        # Now check for unescaped _ in non_math
        # But wait! Inside \texttt{...}, LaTeX text mode still requires \_ unless lstinline or verbatim!
        # If \texttt{SAFE_FOR_ALL} has _, LaTeX throws missing $ inserted!
        under_matches = list(re.finditer(r"(?<!\\)_", non_math))
        if under_matches:
            # Ignore if inside an equation environment on single line
            if not ("\\begin{equation}" in line or "\\end{equation}" in line or "\\begin{cases}" in line):
                errors.append((line_num, "UNESCAPED_UNDERSCORE", line))

        # 3. Check for unescaped % after numbers or text (not comment)
        if m:
            pre = line[:m.start()].strip()
            # If pre ends with a digit or word character
            if pre and re.search(r"[0-9a-zA-Z\)\}\]\.]\s*$", pre):
                # Check if this % was preceded by \
                # (m only matched (?<!\\)%, so it is unescaped)
                errors.append((line_num, "UNESCAPED_PERCENT", line))

        # 4. Check for backticks in captions or sections
        for tag in ["caption", "section", "subsection", "subsubsection"]:
            for match in re.finditer(r"\\" + tag + r"\{([^}]+)\}", line):
                header = match.group(1)
                if "`" in header:
                    errors.append((line_num, f"BACKTICK_IN_{tag.upper()}", line))
                if re.search(r"(?<!\\)&", header):
                    errors.append((line_num, f"AMPERSAND_IN_{tag.upper()}", line))
                if re.search(r"(?<!\\)_", header):
                    errors.append((line_num, f"UNDERSCORE_IN_{tag.upper()}", line))

    print(f"Total potential fatal errors found: {len(errors)}")
    for e in errors[:50]:
        print(f"Line {e[0]} [{e[1]}]: {e[2]}")
    if len(errors) > 50:
        print(f"... and {len(errors) - 50} more errors.")
    return errors

if __name__ == "__main__":
    audit("SAFE_VISION_Final_Project_Report.tex")
