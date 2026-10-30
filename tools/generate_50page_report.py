import os

def create_50page_report():
    out_path = "SAFE_VISION_Final_Project_Report.tex"

    # Pre-read existing modules or craft dedicated concise text
    # Let's write the complete unified LaTeX report directly
    with open("tools/build_50page_tex.py", "w", encoding="utf-8") as f:
        f.write('''# Build script for 50-page SafeAd AI Report
import os

PREAMBLE = r"""\\documentclass[12pt,a4paper]{report}

\\usepackage{ragged2e}
\\usepackage{setspace}
\\usepackage[T1]{fontenc}
\\usepackage{graphicx}
\\graphicspath{{./}{./overleaf_figures/}{./results/}{./sample_ad_media/}}
\\usepackage{url}
\\usepackage{times}
\\usepackage{hyperref}
\\usepackage[nottoc,notlot,notlof]{tocbibind}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{caption}
\\usepackage{subcaption}
\\usepackage{booktabs}
\\usepackage{array}
\\usepackage{float}
\\usepackage{listings}
\\usepackage{xcolor}
\\usepackage[left=3.5cm,top=2.0cm,right=2.5cm,bottom=2.5cm]{geometry}

\\setcounter{tocdepth}{2}

\\raggedbottom
\\widowpenalty=10000
\\clubpenalty=10000
\\brokenpenalty=10000

\\renewcommand{\\topfraction}{0.90}
\\renewcommand{\\bottomfraction}{0.85}
\\renewcommand{\\textfraction}{0.10}
\\renewcommand{\\floatpagefraction}{0.75}

\\renewcommand{\\baselinestretch}{1.18}
\\renewcommand{\\bibname}{References}
\\renewcommand\\listfigurename{\\centering {List of Figures}}
\\renewcommand\\listtablename{\\centering{List of Tables}}
\\hypersetup{hidelinks}

\\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\\definecolor{codepurple}{rgb}{0.58,0,0.82}
\\definecolor{backcolour}{rgb}{0.97,0.98,0.99}

\\lstdefinestyle{mystyle}{
    backgroundcolor=\\color{backcolour},   
    commentstyle=\\color{codegray},
    keywordstyle=\\color{blue},
    numberstyle=\\tiny\\color{codegray},
    stringstyle=\\color{codepurple},
    basicstyle=\\ttfamily\\scriptsize,
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=4pt,                  
    tabsize=2
}
\\lstset{style=mystyle}

\\begin{document}

\\justifying
\\setlength{\\emergencystretch}{3em}
\\tolerance=2000
\\hbadness=10000
"""

print("Build script initialized")
''')

create_50page_report()
print("Wrote builder stub")
