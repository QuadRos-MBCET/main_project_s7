import sys
import os
import re

# Import all modules
import prelims
import ch1_intro
import ch2_lit_review
import ch3_policy
import ch4_architecture
import ch5_methodology
import ch6_results
import ch7_conclusion_refs

def assemble():
    p = prelims.get_prelims()
    c1 = ch1_intro.get_chapter1()
    c2 = ch2_lit_review.get_chapter2()
    c3 = ch3_policy.get_chapter3()
    c4 = ch4_architecture.get_chapter4()
    c5 = ch5_methodology.get_chapter5()
    c6 = ch6_results.get_chapter6()
    c7 = ch7_conclusion_refs.get_chapter7()

    full_tex = p + "\n" + c1 + "\n" + c2 + "\n" + c3 + "\n" + c4 + "\n" + c5 + "\n" + c6 + "\n" + c7

    output_path = "SAFE_VISION_Final_Project_Report.tex"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_tex)

    print(f"Successfully assembled {output_path}!")
    
    # Detailed analysis
    words = len(full_tex.split())
    chars = len(full_tex)
    lines = len(full_tex.splitlines())
    
    figs = re.findall(r'\\includegraphics\[.*?\]\{(.*?)\}', full_tex)
    tables = re.findall(r'\\begin\{table\}', full_tex)
    lsts = re.findall(r'\\begin\{lstlisting\}', full_tex)
    eqs = re.findall(r'\\begin\{equation\}', full_tex)
    
    print("=" * 60)
    print("DOCUMENT METRICS REPORT:")
    print("=" * 60)
    print(f"Total Characters: {chars:,}")
    print(f"Total Words:      {words:,}")
    print(f"Total Lines:      {lines:,}")
    print(f"Total Figures:    {len(figs)} (Unique: {len(set(figs))})")
    print(f"Total Tables:     {len(tables)}")
    print(f"Total Listings:   {len(lsts)} (Algorithms / Schemas)")
    print(f"Total Equations:  {len(eqs)}")
    print("-" * 60)
    
    # Page estimation based on empirical Overleaf points:
    # 6,049 words = 33 pages
    # 20,806 words = 125 pages
    # Delta = 160.4 words / page
    est_pages = 33.0 + (words - 6049) / 160.4
    print(f"ESTIMATED OVERLEAF PAGE COUNT: {est_pages:.1f} PAGES (TARGET: 50 PAGES)")
    print("=" * 60)

    # Word count breakdown per chapter
    chs = [
        ("Preliminaries", p),
        ("Chapter 1: Introduction", c1),
        ("Chapter 2: Literature Review", c2),
        ("Chapter 3: Policy Framework", c3),
        ("Chapter 4: System Architecture", c4),
        ("Chapter 5: Methodology", c5),
        ("Chapter 6: Experimental Results", c6),
        ("Chapter 7 & References", c7),
    ]
    for name, text in chs:
        w = len(text.split())
        print(f" - {name:<35}: {w:>5} words")
    print("=" * 60)

if __name__ == "__main__":
    assemble()
