import re

def audit_tables():
    with open("SAFE_VISION_Final_Project_Report.tex", "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_tabular = False
    col_count = 0
    tab_start = 0

    for idx, line in enumerate(lines):
        l = line.strip()
        m_start = re.search(r"\\begin\{tabular\}\{([^}]+)\}", l)
        if m_start:
            in_tabular = True
            tab_start = idx + 1
            spec = m_start.group(1)
            clean_spec = re.sub(r"p\{[^}]*\}", "c", spec)
            clean_spec = re.sub(r"m\{[^}]*\}", "c", clean_spec)
            clean_spec = clean_spec.replace("|", "").replace("@{}", "").replace(" ", "")
            col_count = len(clean_spec)
            print(f"\nTabular at line {tab_start} (spec: '{spec}', cols: {col_count}):")
            continue
            
        if r"\end{tabular}" in l:
            in_tabular = False
            continue
            
        if in_tabular:
            if r"\\" in l:
                # count unescaped &
                amps = len(re.findall(r"(?<!\\)&", l))
                row_cols = amps + 1
                if row_cols != col_count:
                    print(f"  Line {idx+1}: ERROR! Expected {col_count} columns, found {row_cols} (&={amps})")
                    print(f"    Content: {l}")

if __name__ == "__main__":
    audit_tables()
