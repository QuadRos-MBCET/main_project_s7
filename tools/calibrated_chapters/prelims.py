import sys

def get_prelims():
    return r"""\documentclass[12pt,a4paper]{report}

\usepackage{ragged2e}
\usepackage{setspace}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\graphicspath{{./}{./overleaf_figures/}{./results/}{./sample_ad_media/}}
\usepackage{url}
\usepackage{times}
\usepackage{hyperref}
\usepackage[nottoc,notlot,notlof]{tocbibind}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{booktabs}
\usepackage{array}
\usepackage{float}
\usepackage{listings}
\usepackage{xcolor}
\usepackage[left=3.5cm,top=2.0cm,right=2.5cm,bottom=2.5cm]{geometry}

\setcounter{tocdepth}{2}

\raggedbottom
\widowpenalty=10000
\clubpenalty=10000
\brokenpenalty=10000

\renewcommand{\topfraction}{0.90}
\renewcommand{\bottomfraction}{0.85}
\renewcommand{\textfraction}{0.10}
\renewcommand{\floatpagefraction}{0.75}

\renewcommand{\baselinestretch}{1.20}
\renewcommand{\bibname}{References}
\renewcommand\listfigurename{\centering {List of Figures}}
\renewcommand\listtablename{\centering{List of Tables}}
\hypersetup{hidelinks}

\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.97,0.98,0.99}

\lstdefinestyle{mystyle}{
    backgroundcolor=\color{backcolour},   
    commentstyle=\color{codegray},
    keywordstyle=\color{blue},
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\scriptsize,
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=4pt,                  
    tabsize=2
}
\lstset{style=mystyle}

\begin{document}

\justifying
\setlength{\emergencystretch}{3em}
\tolerance=2000
\hbadness=10000

% ============================================================
% TITLE PAGE
% ============================================================

\begin{titlepage}
\begin{center}

\vspace*{0.2cm}

{\LARGE \textbf{SafeAd AI: Multimodal Trust and Safety Framework for Advertisement Moderation}}\\[0.4cm]

{\Large \textbf{A Project Report}}\\[0.2cm]

\large \textit{Submitted to the APJ Abdul Kalam Technological University}\\[0.1cm]

\large \textit{in partial fulfillment of requirements for the award of degree}\\[0.5cm]

{\Large \textbf{Bachelor of Technology}}\\[0.1cm]

\large {in}\\[0.1cm]

{\Large \textbf{Computer Science and Engineering}}\\[0.1cm]

{\large \textbf{(Artificial Intelligence)}}\\[0.2cm]

\large \textit{by}\\[0.2cm]

{\large \textbf{\scshape Joseph Benedict} \textbf{\textit{(B23CS2136, KTU Reg No: MBT23CA036)}}}\\

{\large \textbf{\scshape Juwel Jokesh} \textbf{\textit{(B23CS2138, KTU Reg No: MBT23CA038)}}}\\

{\large \textbf{\scshape R D Sourav} \textbf{\textit{(B23CS2151, KTU Reg No: MBT23CA052)}}}\\

{\large \textbf{\scshape Sooraj Jose George} \textbf{\textit{(B23CS2160, KTU Reg No: MBT23CA059)}}}\\[0.5cm]

\IfFileExists{mbcetlogo.png}{\centerline{\includegraphics[width=4.0cm]{mbcetlogo.png}}}{\vspace{4.0cm}}

\vspace*{0.4cm}

{\bf \large Department of Computer Science and Engineering}\\

{\bf \large Mar Baselios College of Engineering and Technology}\\

{\large Thiruvananthapuram -- 695015}\\[0.2cm]

{\large OCTOBER 2026}

\end{center}
\end{titlepage}

% ============================================================
% CERTIFICATE
% ============================================================

\newpage
\thispagestyle{empty}

\begin{center}
{\bf \large Department of Computer Science and Engineering}\\[0.1cm]
{\bf \large Mar Baselios College of Engineering and Technology}\\[0.1cm]
{\large Thiruvananthapuram -- 695015}\\[0.4cm]

\IfFileExists{mbcetlogo.png}{\centerline{\includegraphics[width=3.0cm]{mbcetlogo.png}}}{\vspace{3.0cm}}

\vspace{0.4cm}
{\bf \Large CERTIFICATE}
\end{center}

\noindent This is to certify that the project report entitled \textbf{``SafeAd AI: Multimodal Trust and Safety Framework for Advertisement Moderation''} is a bonafide record of the work carried out by \textbf{Joseph Benedict (MBT23CA036)}, \textbf{Juwel Jokesh (MBT23CA038)}, \textbf{R D Sourav (MBT23CA052)}, and \textbf{Sooraj Jose George (MBT23CA059)} in partial fulfillment of the requirements for the award of the degree of \textbf{Bachelor of Technology in Computer Science and Engineering (Artificial Intelligence)} of the \textbf{APJ Abdul Kalam Technological University} during the academic year 2025--2026.

\vspace{1.8cm}

\noindent
\begin{tabular}{@{}p{5.0cm}p{4.5cm}p{5.5cm}@{}}
\textbf{Ms. Gayathri K. S.} & \textbf{Dr. Neena Raj N. R.} & \textbf{Dr. Anne Dickson} \\
Assistant Professor & Associate Professor & Professor and Head \\
Project Guide & Project Coordinator & Dept. of CSE \\
MBCET, Thiruvananthapuram & MBCET, Thiruvananthapuram & MBCET, Thiruvananthapuram
\end{tabular}

% ============================================================
% DECLARATION
% ============================================================

\newpage
\thispagestyle{empty}

\begin{center}
{\bf \Large DECLARATION}
\end{center}

\vspace{0.8cm}

\noindent We hereby declare that the project report entitled \textbf{``SafeAd AI: Multimodal Trust and Safety Framework for Advertisement Moderation''}, submitted to the \textbf{APJ Abdul Kalam Technological University} in partial fulfillment of the requirements for the award of the Degree of \textbf{Bachelor of Technology in Computer Science and Engineering (Artificial Intelligence)}, is a record of original work done by us under the supervision and guidance of \textbf{Ms. Gayathri K. S.}, Assistant Professor, Department of Computer Science and Engineering, Mar Baselios College of Engineering and Technology, Thiruvananthapuram.

\vspace{0.4cm}

\noindent We further declare that this report has not previously formed the basis for the award of any degree, diploma, fellowship, or associateship of any other university or institute of higher learning.

\vspace{1.8cm}

\noindent
\begin{tabular}{@{}p{7.5cm}p{7.5cm}@{}}
\textbf{Joseph Benedict} (MBT23CA036) & \textbf{Juwel Jokesh} (MBT23CA038) \\[1.2cm]
\textbf{R D Sourav} (MBT23CA052) & \textbf{Sooraj Jose George} (MBT23CA059)
\end{tabular}

\vspace{1.0cm}
\noindent Thiruvananthapuram \\
\noindent Date: 30-10-2026

% ============================================================
% ACKNOWLEDGEMENT
% ============================================================

\newpage
\thispagestyle{empty}

\begin{center}
{\bf \Large ACKNOWLEDGEMENT}
\end{center}

\vspace{0.6cm}

\noindent We express our deepest gratitude to the Almighty for the grace, wisdom, and perseverance bestowed upon us throughout the execution of this research endeavor.

\vspace{0.3cm}

\noindent We extend our sincere gratitude to \textbf{Dr. Abraham T. Mathew}, Principal, Mar Baselios College of Engineering and Technology, for providing the institutional infrastructure, research computing environment, and high-performance computing facilities necessary to realize this project.

\vspace{0.3cm}

\noindent We convey our profound appreciation to \textbf{Dr. Anne Dickson}, Professor and Head of the Department of Computer Science and Engineering, for her administrative support, constructive advice, and scholarly encouragement.

\vspace{0.3cm}

\noindent We record our deep debt of gratitude to our project guide, \textbf{Ms. Gayathri K. S.}, Assistant Professor, Department of Computer Science and Engineering, whose meticulous technical guidance, critical insights, and unwavering dedication shaped the scientific direction of this research. We are also immensely grateful to our Project Coordinator, \textbf{Dr. Neena Raj N. R.}, Associate Professor, Department of Computer Science and Engineering, for her continuous coordination, structured reviews, and rigorous academic feedback.

\vspace{0.3cm}

\noindent Finally, we express heartfelt thanks to our families, fellow students, and academic peers whose constant encouragement, patience, and support sustained us throughout this intensive endeavor.

\vspace{1.0cm}
\noindent
\textbf{Joseph Benedict}\\
\textbf{Juwel Jokesh}\\
\textbf{R D Sourav}\\
\textbf{Sooraj Jose George}

% ============================================================
% ABSTRACT
% ============================================================

\newpage
\pagenumbering{roman}
\setcounter{page}{1}

\begin{center}
{\bf \Large ABSTRACT}
\end{center}

\vspace{0.5cm}

\noindent The rapid expansion of programmatic digital advertising networks has outpaced conventional reactive moderation systems, allowing deceptive, sexually suggestive, and age-inappropriate content to bypass safety guardrails. Modern adversarial advertisements exploit cross-modal semantic concealment, wherein benign visual assets are combined with predatory audio narrations or obscured typographic overlays, deliberately circumventing single-modality content filters. 

To overcome these critical security vulnerabilities, this project presents \textbf{SafeAd AI (SAFE-VISION)}, an end-to-end, pre-publication multimodal trust and safety framework designed for real-time advertisement verification and age-aware content dispatching. The framework implements a synchronized dual-engine architecture: (1) an automated multimodal content moderation engine that ingests video keyframes, optical character recognition (OCR) typography, and automatic speech recognition (ASR) audio transcripts to evaluate cross-modal policy compliance; and (2) a biometric age assurance and facial verification subsystem that enforces regulatory delivery boundaries across four distinct statutory tiers: \texttt{SAFE\_FOR\_ALL}, \texttt{SAFE\_14\_PLUS}, \texttt{SAFE\_18\_PLUS}, and \texttt{UNSAFE\_FOR\_ALL}.

The content moderation engine extracts high-dimensional representations across video kinetics (VideoMAE), adult visual concepts (Falcon NSFW ViT), textual semantics (RoBERTa and DeBERTa-v3), and commercial claim risk heuristics. In development benchmark evaluations ($N=194$), a learned late-fusion Random Forest achieved an overall 5-fold cross-validation accuracy of $44.33\%$ with a macro-F1 of $0.4496$. Rigorous error profiling revealed that generic visual safety guardrails (such as Llama Guard 3 Vision) fail on $80.0\%$ of diagnostic ad cohorts due to severe commercial concept blindness. To resolve this semantic bottleneck, the framework integrates Qwen3-VL-8B-Instruct, an 8-billion parameter vision-language foundation model with ad-policy prompt alignment, coupled with a hierarchical policy-aware late-fusion protocol (Strategy~D).

On a strictly independent, held-out test cohort of 27 verified advertisement assets evaluated on an NVIDIA A100 GPU without ground-truth leakage or rule post-tuning, Qwen3-VL and Hierarchical Fusion achieved $66.7\%$ four-class accuracy, successfully eliminating all severe false acceptances ($0.0\%$ false acceptance rate) and achieving a flawless $100.0\%$ recall on strictly prohibited content. The companion biometric subsystem combines dual-scale MiniFASNet with 2D Fast Fourier Transform (FFT) moir\'{e} analysis for Presentation Attack Detection ($93.0\%$ replay attack detection accuracy) and ArcFace embedding verification ($96.50\%$ True Accept Rate at $0.1\%$ False Accept Rate), guaranteeing that age-restricted advertisements are strictly inaccessible to minors. The resulting system bridges the divide between regulatory advertising standards and real-time automated enforcement.

\vspace{0.4cm}
\noindent \textbf{Keywords:} Multimodal Content Moderation, Trust and Safety, Vision-Language Models, Policy Enforcement, Late Fusion, Presentation Attack Detection, Biometric Age Assurance.

% ============================================================
% TOC, LOF, LOT
% ============================================================

\newpage
\tableofcontents

\newpage
\listoffigures

\newpage
\listoftables

\newpage
\pagenumbering{arabic}
\setcounter{page}{1}
"""
