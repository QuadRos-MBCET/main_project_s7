import os
import sys

# Add repository root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.report_modules import (
    preamble_and_ch1,
    chapter2,
    chapter3,
    chapter4,
    chapter5,
    chapter6,
    chapter7_and_bib
)

def assemble():
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "SAFE_VISION_Final_Project_Report.tex"))
    print(f"Assembling report into {output_path}...")
    
    parts = [
        preamble_and_ch1.get_content(),
        chapter2.get_content(),
        chapter3.get_content(),
        chapter4.get_content(),
        chapter5.get_content(),
        chapter6.get_content(),
        chapter7_and_bib.get_content()
    ]
    
    full_text = "\n\n".join(parts)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    print(f"Assembly complete! Total characters: {len(full_text):,}")
    print(f"Total lines: {len(full_text.splitlines()):,}")
    print(f"Total words: {len(full_text.split()):,}")

if __name__ == "__main__":
    assemble()
