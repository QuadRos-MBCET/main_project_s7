import os
import sys

# Let's inspect the backup we made earlier: SAFE_VISION_Final_Project_Report_125pages_extended.tex
extended_path = "SAFE_VISION_Final_Project_Report_125pages_extended.tex"
with open(extended_path, "r", encoding="utf-8") as f:
    ext_text = f.read()

print(f"Extended text: {len(ext_text):,} chars, {len(ext_text.split()):,} words")

short_path = "SAFE_VISION_Final_Project_Report.tex"
with open(short_path, "r", encoding="utf-8") as f:
    short_text = f.read()

print(f"Short text: {len(short_text):,} chars, {len(short_text.split()):,} words (which gave 33 pages)")
