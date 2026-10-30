import sys

def get_content():
    return r"""\documentclass[12pt,a4paper]{report}

\usepackage{ragged2e}
\usepackage{setspace}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\graphicspath{{./}{./overleaf_figures/}{./results/}{./sample_ad_media/}{./joseph_safead_core/backend2jb/datasets/samples/}{./joseph_safead_core/backend2jb/system diagrams/}}
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
\usepackage[left=3.5cm,top=2cm,right=3cm,bottom=3cm]{geometry}

\setcounter{tocdepth}{2}

% ============================================================
% TYPOGRAPHY & FLOAT CONTROLS
% ============================================================

\raggedbottom
\widowpenalty=10000
\clubpenalty=10000
\brokenpenalty=10000

\renewcommand{\topfraction}{0.90}
\renewcommand{\bottomfraction}{0.85}
\renewcommand{\textfraction}{0.10}
\renewcommand{\floatpagefraction}{0.75}

\renewcommand{\baselinestretch}{1.30}
\renewcommand{\bibname}{References}
\renewcommand\listfigurename{\centering {List of Figures}}
\renewcommand\listtablename{\centering{List of Tables}}
\hypersetup{hidelinks}

% Code snippet styling
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.97,0.98,0.99}

\lstdefinestyle{mystyle}{
    backgroundcolor=\color{backcolour},   
    commentstyle=\color{codegray},
    keywordstyle=\color{blue},
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\footnotesize,
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=5pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
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

\IfFileExists{mbcetlogo.png}{\centerline{\includegraphics[width=4.2cm]{mbcetlogo.png}}}{\vspace{4.2cm}}

\vspace*{0.4cm}

{\bf \large Department of Computer Science and Engineering}\\

{\bf \large Mar Baselios College of Engineering and Technology}\\

{\bf \large (Autonomous)}\\

{\bf \large Mar Ivanios Vidya Nagar, Nalanchira}\\

{\bf \large Thiruvananthapuram--695015}\par

\vspace{0.2cm}

{\bf \large October 2026}\par

\end{center}
\end{titlepage}

\pagenumbering{gobble}

% ============================================================
% CERTIFICATE
% ============================================================

\newpage

\begin{center}
    \textbf{DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING}\\
    \textbf{MAR BASELIOS COLLEGE OF ENGINEERING AND TECHNOLOGY}\\
    \textbf{(AUTONOMOUS)}\\
    \textbf{MAR IVANIOS VIDYA NAGAR, NALANCHIRA,}\\
    \textbf{THIRUVANANTHAPURAM--695015}
\end{center}

\begin{center}
    \IfFileExists{mbcetlogo.png}{\includegraphics[width=2.5cm]{mbcetlogo.png}}{\vspace{2.5cm}}
\end{center}

\begin{center}
    \textbf{\Large \textsc{Certificate}}
\end{center}

{\justifying
\setlength{\emergencystretch}{3em}
\tolerance=2000
\hbadness=10000
\noindent
This is to certify that the report entitled \textbf{SafeAd AI: Multimodal Trust and Safety Framework for Advertisement Moderation} submitted by \textbf{Joseph~Benedict}~(B23CS2136), \textbf{Juwel~Jokesh}~(B23CS2138), \textbf{R~D~Sourav}~(B23CS2151) \& \textbf{Sooraj~Jose~George}~(B23CS2160), to the APJ Abdul Kalam Technological University in partial fulfillment of the B.Tech.\ degree in Computer Science and Engineering (Artificial Intelligence) is a bonafide record of the project work carried out by them under our guidance and supervision. This report in any form has not been submitted to any other University or Institute for any purpose.
\par}

\vspace{1.8cm}

\noindent
\begin{singlespacing}
\begin{tabular}{@{}p{0.50\textwidth}@{}p{0.50\textwidth}@{}}
\textbf{Dr. Neena Raj N. R.} & \textbf{Ms. Gayathri K. S.} \\
(Project Guide) & (Project Co-ordinator) \\
Assistant Professor & Assistant Professor \\
Department of CSE & Department of CSE \\
\end{tabular}

\vspace{1.5cm}

\begin{center}
\textbf{Dr. Anne Dickson}\\
(Head of the Department)\\
Associate Professor\\
Department of CSE
\end{center}

\vspace{1.0cm}

\noindent
\begin{tabular}{@{}p{0.50\textwidth}@{}p{0.50\textwidth}@{}}
Place: Thiruvananthapuram & Date: 29 October 2026
\end{tabular}
\end{singlespacing}

% ============================================================
% DECLARATION
% ============================================================

\newpage

\begin{center}
    \textbf{\Large \textsc{Declaration}}
\end{center}

\vspace{0.4cm}

\noindent
We hereby declare that the project report titled ``SafeAd AI: Multimodal Trust and Safety Framework for Advertisement Moderation'', submitted for partial fulfillment of the requirements for the award of the degree of Bachelor of Technology of the APJ Abdul Kalam Technological University, Kerala, is a bonafide work done by us under the supervision of Dr.~Neena Raj N.~R.

\par
\vspace{0.3cm}

\noindent
This submission represents our ideas in our own words and where ideas or words of others have been included, we have adequately and accurately cited and referenced the original sources.

\par
\vspace{0.3cm}

\noindent
We also declare that we have adhered to the ethics of academic honesty and integrity and have not misrepresented or fabricated any data, idea, fact, or source in our submission. We understand that any violation of the above will be a cause for disciplinary action by the institute and/or the University and can also evoke penal action from the sources which have thus not been properly cited or from whom proper permission has not been obtained.

\par
\vspace{0.3cm}

\noindent
This report has not previously formed the basis for the award of any degree, diploma, or similar title of any other University.

\vspace{1.0cm}

\noindent
\begin{minipage}[t]{0.45\linewidth}
    \vspace{0pt}
    Place: Thiruvananthapuram\\
    Date: 29 October 2026
\end{minipage}
\hfill
\begin{minipage}[t]{0.45\linewidth}
    \vspace{0pt}
    \raggedleft
    Joseph Benedict\\[0.4cm]
    Juwel Jokesh\\[0.4cm]
    R D Sourav\\[0.4cm]
    Sooraj Jose George
\end{minipage}

% ============================================================
% ACKNOWLEDGEMENT
% ============================================================

\newpage
\pagenumbering{roman}
\setcounter{page}{1}

\begin{center}
    \textbf{\Large Acknowledgement}
\end{center}

\vspace{0.4cm}

\noindent
We express our deepest gratitude to our Project Guide, Dr.~Neena Raj N.~R., Assistant Professor, Department of Computer Science and Engineering, for providing continuous guidance, critical feedback, and technical insights throughout the design, implementation, and rigorous experimental evaluation of this project.

\par
\vspace{0.3cm}

\noindent
We extend our heartfelt gratitude to Ms.~Gayathri K.~S., Project Co-ordinator, for her academic support, structured evaluation schedules, and valuable recommendations throughout the project lifecycle.

\par
\vspace{0.3cm}

\noindent
We sincerely thank Dr.~Anne Dickson, Head of the Department of Computer Science and Engineering, for her institutional encouragement, academic leadership, and for providing the high-performance computing facilities necessary to execute this work.

\par
\vspace{0.3cm}

\noindent
We also acknowledge the open-source artificial intelligence communities behind PyTorch, Hugging Face Transformers, Qwen3-VL, OpenAI Whisper, EasyOCR, OpenCV, InsightFace, and scikit-learn, whose tools formed the technical bedrock of this research.

\par
\vspace{0.3cm}

\noindent
Finally, we convey our sincere appreciation to our families, peers, and friends for their enduring patience, encouragement, and support throughout this major project endeavour.

\vspace{1cm}

\noindent
\begin{minipage}[t]{0.45\linewidth}
    \raggedright
    Joseph Benedict\\[0.3cm]
    R D Sourav
\end{minipage}
\hfill
\begin{minipage}[t]{0.45\linewidth}
    \raggedleft
    Juwel Jokesh\\[0.3cm]
    Sooraj Jose George
\end{minipage}

% ============================================================
% ABSTRACT
% ============================================================

\newpage

\begin{center}
    \textbf{\Large ABSTRACT}
\end{center}

\vspace{0.4cm}

\noindent
Digital advertising exchanges process tens of millions of creative assets every 24 hours across static banners, dynamic carousels, short-form vertical video (e.g., Instagram Reels, TikTok, YouTube Shorts), and high-definition commercial spots. Traditional trust and safety architectures rely almost entirely on post-publication user reporting or isolated unimodal filtering. Consequently, malicious advertisers deliberately exploit cross-modal evasion tactics, distributing harmful or deceptive signals across modalities such that benign visuals conceal predatory audio narration or deceptive fine-print typography. Furthermore, conventional age-gating mechanisms depend on easily manipulated self-declared user birth dates, exposing underage demographics to legally restricted commercial products such as alcohol, tobacco, and casino gambling. Webcam-based identity verification introduces severe hardware and security vulnerabilities: camera capture threads crash due to Windows DirectShow COM threading deadlocks (\texttt{0xc0000374}), while facial verification pipelines remain susceptible to physical print and digital screen replay spoofing attacks.

\par
\vspace{0.3cm}

\noindent
This project presents \textbf{SafeAd AI (SAFE-VISION)}, an end-to-end, proactive multimodal pre-publication advertisement moderation and real-time biometric age assurance framework. The pre-publication moderation subsystem evaluates incoming creative assets across Optical Character Recognition (EasyOCR), deep visual representations (ResNet50/MobileNetV3), temporal motion dynamics (Farneb\"{a}ck dense optical flow and VideoMAE), and speech-to-text audio transcription (OpenAI Whisper). Initial diagnostic evaluations revealed that specialized safety guardrails such as Meta's Llama Guard 3 Vision suffered severe false-acceptance rates ($80\%$) on commercial advertising due to conversational dialogue overfitting and category misalignments. In response, the architecture integrates the state-of-the-art \textbf{Qwen3-VL-8B-Instruct} foundation vision-language model deployed on Google Colab NVIDIA A100 GPU hardware in native \texttt{torch.bfloat16} precision, coupled with a learned Random Forest classifier in a multi-tiered hierarchical safety fusion protocol (Strategy D). A deterministic two-stage policy engine enforces a four-tier regulatory classification: \texttt{SAFE\_FOR\_ALL}, \texttt{SAFE\_14\_PLUS} (adolescent-restricted), \texttt{SAFE\_18\_PLUS} (adult-restricted), and \texttt{UNSAFE\_FOR\_ALL} (strictly prohibited).

\par
\vspace{0.3cm}

\noindent
For recipient verification, a custom \texttt{Realtime30FPSVisionEngine} decouples DirectShow camera acquisition from background deep learning inference using non-blocking double buffering, completely eliminating native heap corruption and sustaining a locked 30~FPS display interval. A multi-cue presentation attack detection (PAD) engine fuses a dual-scale MiniFASNet ensemble (\texttt{MiniFASNetV2} at 2.7$\times$ and \texttt{MiniFASNetV1SE} at 4.0$\times$) with Hough line border tracking, adaptive HSV specular glare detection, and 2D FFT spatial moir\'{e} analysis, executing in $\sim$9.7~ms per frame on CPU ($\sim$103~FPS). Biometric identity matching utilizes InsightFace ArcFace (\texttt{iResNet50}, 512-D normalized embeddings, cosine threshold $\ge 0.65$), paired with Vision Transformer (ViT) facial age estimation, mandibular Canny edge hair density validation, and automated government credential parsing via \texttt{pypdfium2} and EasyOCR.

\par
\vspace{0.3cm}

\noindent
Exhaustive empirical evaluations across multiple development and test cohorts delineate the operational performance boundaries of each subsystem:
\begin{enumerate}
    \item \textbf{Phase 8E Development Benchmark ($N=194$):} Across 194 verified development samples (134 images, 60 videos), the heuristic baseline achieved 31.96\% accuracy and 0.2317 macro-F1. A 33-feature Random Forest classifier evaluated under stratified 5-fold cross-validation improved performance to 44.33\% accuracy (86/194 correct) and 0.4110 macro-F1, reducing prohibited false acceptance from 80\% to 60\%.
    \item \textbf{Phase 10B/10C Qwen3-VL Development Diagnostics ($N=16$):} On a balanced 16-sample diagnostic cohort, Qwen3-VL-8B-Instruct achieved 75.00\% four-class accuracy (12/16) with 100\% prohibited recall (5/5), 0.0\% false acceptance, and 7.05~s mean latency. Hierarchical fusion (Strategy D) achieved 100.0\% diagnostic concordance (16/16).
    \item \textbf{Phase 10D Independent Held-Out Test Evaluation ($N=27$):} When evaluated on an untouched, held-out test split of 27 genuine advertisements under strictly frozen rules, the Random Forest model suffered catastrophic domain degradation, achieving only 37.0\% accuracy (10/27) and leaking 3 out of 4 prohibited advertisements (75.0\% Prohibited False Acceptance Rate). In contrast, both standalone Qwen3-VL and the Frozen Hierarchical Safety Fusion achieved \textbf{66.7\% four-class accuracy (18/27)}, \textbf{0.6889 Macro-F1}, \textbf{100.0\% Prohibited Recall (4/4)}, and \textbf{0.0\% Prohibited False Acceptance}.
    \item \textbf{Core Scientific Finding:} Hierarchical fusion did not outperform standalone Qwen3-VL on novel data. Detailed forensic auditing revealed that all 9 misclassifications stemmed from: (a) eight benign consumer products (hair pomade, cargo pants, USB mic, tennis racket, habanero sauce, manga art, Mustang car, shaving foam) labeled \texttt{SAFE\_14\_PLUS} in the catalog due to subjective marketing demographics rather than safety policy; and (b) one 1930s vintage Lucky Strike print ad whose retro illustrated artwork lacked modern photorealistic warning cues, bypassing visual tobacco detection (20.0\% Underage Exposure Rate).
    \item \textbf{Biometric Assurance Benchmarks:} The ArcFace verification pipeline achieved 96.50\% matching accuracy across 200 genuine and impostor pairs, while the multi-cue PAD engine achieved 93.00\% liveness accuracy across 100 physical and digital replay attack trials.
\end{enumerate}

\vspace{0.6cm}
\noindent \textbf{Keywords:} Multimodal Content Moderation, Vision-Language Models, Qwen3-VL, Random Forest, Hierarchical Safety Fusion, Trust and Safety, ArcFace Biometrics, Face Anti-Spoofing (PAD), MiniFASNet Ensemble, Vision Transformer Age Assurance, DirectShow Concurrency.

% ============================================================
% TOC, LIST OF FIGURES, LIST OF TABLES
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

% ============================================================
% CHAPTER 1: INTRODUCTION
% ============================================================

\chapter{Introduction}

\section{Background and Industrial Context}

The global digital advertising economy represents an unprecedented technological infrastructure generating over \$600 billion annually. High-velocity digital ad exchanges operate through programmatic Real-Time Bidding (RTB) protocols, linking Demand-Side Platforms (DSPs), Supply-Side Platforms (SSPs), and content publisher networks. In this high-throughput ecosystem, advertisers submit creative promotional assets in massive volumes. Over 50 million distinct advertising assets are submitted to global display networks, video streaming channels, and mobile platforms every 24 hours. These assets encompass complex static banners, dynamic HTML5 responsive units, interstitial carousels, and high-definition video advertisements ranging from 6-second bumper ads to 60-second broadcast commercials.

Concurrently, the consumer base interacting with digital media exhibits extraordinary demographic diversity. Users navigating internet platforms range from young children engaging with educational mobile software and adolescent gamers streaming esports content, to mature adults seeking regulated consumer goods. In traditional commercial media---such as linear broadcast television or print journalism---content distribution was centralized, heavily regulated by statutory broadcasting standards, and filtered through human editorial review prior to transmission. Conversely, in the decentralized, algorithmic programmatic advertising economy, creative assets are ingested, auctioned, and published to consumer feeds within milliseconds.

Historically, platform operators approached trust and safety through a reactive moderation paradigm. Platforms relied on post-publication user flagging, automated clickstream anomaly detection, and periodic retrospective manual auditing. Under this reactive paradigm, a policy-violating advertisement---such as an unapproved vaping device promotion, a fraudulent cryptocurrency Ponzi scheme, predatory high-interest loan offerings, or an R-rated combat video game trailer---is deployed live to thousands of concurrent users before algorithmic flags or human moderators intervene. Empirical investigations demonstrate that the ``moderation lag window'' in major social networks typically spans between 4 and 48 hours. During this latency window, an illicit advertisement achieves its primary commercial impression goals, inflicting severe psychological harm on minor audiences, facilitating financial victimization, and exposing publisher platforms to massive statutory liability under emerging global child safety legislation.

\section{The Threat Landscape: Cross-Modal Concealment Tactics}

Commercial advertisements are inherently multimodal communicative artifacts. Unlike standard user-generated text posts or isolated images, commercial ads deliberately synthesize visual typography, human motion, scenic aesthetics, background music, spoken dialogue, and textual metadata slogans to elicit emotional and psychological responses from viewers.

This intrinsic multimodality provides adversarial actors with powerful cross-modal concealment vectors designed to evade automated unimodal content filters:
\begin{enumerate}
    \item \textbf{Visual-Acoustic Semantic Splitting:} Adversarial campaigns deliberately decouple the visual and auditory streams. For example, an illicit online gambling or sports betting service creates an advertisement displaying pristine, family-friendly visual footage of teenagers playing soccer in a sunlit public park, while the spoken audio voice-over provides explicit promotional referral codes, bonus odds, and deposit instructions for an unregulated offshore sportsbook. Unimodal computer vision filters examining the video frames classify the asset as completely benign family leisure. Unimodal audio filters operating without visual grounding frequently misinterpret spoken promotional codes as generic gaming narration.
    \item \textbf{Typography-Steganography and Micro-Disclaimers:} Advertisers frequently conceal legally mandatory disclosures or deceptive claims through visual typographic manipulation. Substantive fraudulent claims (e.g., ``Guaranteed 300\% daily payout on crypto deposits'') are rendered in stylized, high-contrast headline fonts, whereas statutory disclaimers (e.g., ``High risk of total capital loss, unregulated instrument'') are embedded in microscopic, low-contrast text at the bottom edge of the frame, designed to fail optical character recognition (OCR) binarization thresholds. Conversely, illicit product names are obfuscated using leetspeak, homoglyphs, and typographic distortions (e.g., replacing Latin characters with Cyrillic lookalikes) that bypass static keyword blocklists.
    \item \textbf{Temporal Narrative Escalation:} In short-form video commercials (e.g., TikTok, Instagram Reels), malicious actors front-load the first three seconds with innocuous lifestyle content to satisfy automated ingestion scrapers that sample only initial frames, only to abruptly escalate into graphic violence, non-consensual sexual themes, or shock imagery during later intervals.
\end{enumerate}

These cross-modal attack vectors fundamentally undermine unimodal trust and safety filters, necessitating a proactive, multimodal inspection engine capable of synchronizing visual keyframe embeddings, optical text recognition, temporal motion energy, and speech-to-text transcripts into a unified semantic representation.

\section{The Structural Disconnection: Content Safety vs. Viewer Demographics}

A second, equally critical failure of modern moderation architectures is the operational disconnection between content safety categorization and recipient demographic eligibility.

In standard content moderation literature, content safety is frequently framed as a binary classification problem: content is either deemed ``safe'' (permissible) or ``toxic/unsafe'' (impermissible). In commercial advertising, however, this binary framing is fundamentally invalid:
\begin{itemize}
    \item \textbf{Lawful but Age-Restricted Goods:} Many major commercial product categories---including distilled spirits, craft beer, licensed casino gaming, sports wagering, mature cinema, and sexual wellness goods---are fully lawful commercial enterprises protected by commercial speech rights. However, statutory regulations strictly mandate that these promotions must never be displayed to minor audiences under legal age thresholds (e.g., 18+ or 21+).
    \item \textbf{Adolescent Lifestyle Demarcations:} Products such as highly caffeinated energy drinks (>150 mg caffeine per serving), teen acne treatments containing active medical compounds, and intense competitive combat gaming are suitable for adolescents aged 14 and older, but pose physical or psychological risks to young children under age 14.
    \item \textbf{Universally Prohibited Hazards:} Content such as illegal narcotics, unregistered firearms, child sexual abuse material (CSAM), non-consensual sexual exploitation, extreme graphic violence, and financial scams must be subjected to zero-tolerance universal pre-publication rejection across all publisher feeds.
\end{itemize}

Digital platforms attempt to enforce age gating through self-declared user registration birth dates. However, empirical studies demonstrate that over 80\% of underage users routinely misrepresent their age during account setup to bypass content gates. Consequently, even when an ad network accurately identifies an advertisement as containing adult themes, delivering that ad based on unverified, self-reported user profiles results in massive underage exposure (Underage Gating Violation Rate).

Conversely, attempts to integrate biometric age verification via client webcams introduce severe technical and security hurdles:
\begin{enumerate}
    \item \textbf{Multithreaded Capture Instability:} Executing compute-intensive deep neural networks (e.g., ArcFace, MTCNN, Vision Transformers) synchronously on the camera acquisition thread in desktop environments induces Windows DirectShow COM Single-Threaded Apartment (STA) collisions and fatal native memory heap corruption (\texttt{0xc0000374}), crashing moderation client dashboards.
    \item \textbf{Vulnerability to Presentation Attacks:} Standard webcam face recognition is easily bypassed through physical presentation attacks (high-resolution color printouts) and digital screen replay attacks (replaying video recordings of authorized adults on mobile phone or tablet displays).
\end{enumerate}

\section{The SafeAd AI Vision and Core Paradigms}

SafeAd AI (SAFE-VISION) is formulated as an enterprise-grade, proactive multimodal pre-publication advertisement moderation and real-time biometric age assurance framework. SafeAd AI bridges the gap between pre-publication creative screening and post-publication audience delivery, enforcing verified trust and safety across the entire commercial pipeline.

\begin{figure}[H]
    \centering
    \IfFileExists{system_architecture.png}{\includegraphics[width=0.92\textwidth]{system_architecture.png}}{%
        \fbox{\parbox{0.80\textwidth}{\centering \textbf{[SafeAd AI Dual-Pipeline Architectural Vision: Pre-Publication Multimodal Screening + Real-Time Biometric Age Assurance]}}}%
    }
    \caption{SafeAd AI End-to-End Multimodal Safety and Age-Aware Delivery Architecture.}
    \label{fig:intro_arch}
\end{figure}

The framework operates through two interconnected, synchronized subsystems:
\begin{enumerate}
    \item \textbf{Pre-Publication Multimodal Safety and Policy Engine:} Ingests multimedia advertisements (static images, short-form MP4/MOV videos, embedded text, speech audio) before publication. The engine extracts multimodal evidence across EasyOCR, deep visual CNNs, Farneb\"{a}ck optical motion vectors, and Whisper speech transcripts. To overcome the catastrophic false-acceptance limitations of specialized guardrails (such as Llama Guard 3 Vision), the architecture integrates the state-of-the-art \textbf{Qwen3-VL-8B-Instruct} vision-language foundation model on NVIDIA A100 GPU hardware, coupled with a 33-feature Random Forest classifier in a Frozen Hierarchical Safety Fusion protocol (Strategy D). A deterministic two-stage policy engine enforces a four-tier regulatory classification: \texttt{SAFE\_FOR\_ALL}, \texttt{SAFE\_14\_PLUS}, \texttt{SAFE\_18\_PLUS}, and \texttt{UNSAFE\_FOR\_ALL}.
    \item \textbf{Real-Time Biometric Identity Assurance and Concurrency Engine:} Decouples DirectShow camera acquisition from deep learning inference via the custom \texttt{Realtime30FPSVisionEngine}, sustaining a locked 30~FPS video stream without heap corruption. The live feed is secured by a multi-cue presentation attack detection (PAD) ensemble fusing dual-scale MiniFASNet models with Hough line border tracking, specular glare tracking, and 2D FFT moir\'{e} analysis. Recipient identities and biological ages are cross-verified using InsightFace ArcFace (\texttt{iResNet50}, 512-D, cosine threshold $\ge 0.65$) and Vision Transformer (ViT) age classification cross-checked against government credentials parsed via \texttt{pypdfium2} and EasyOCR.
\end{enumerate}

\section{Detailed Problem Statement \& Mathematical Objectives}

Let an incoming commercial advertisement campaign asset be formally denoted by the multimodal tuple:
\begin{equation}
A = \left( I, V, T, O, S \right)
\end{equation}
where:
\begin{itemize}
    \item $I \in \mathbb{R}^{H \times W \times 3}$ denotes a normalized RGB static image or thumbnail representation.
    \item $V = \{f_1, f_2, \dots, f_K\}$ represents a temporal sequence of $K$ video keyframes sampled at adaptive motion boundaries, where each $f_k \in \mathbb{R}^{H \times W \times 3}$.
    \item $T$ denotes text metadata provided by the advertiser (campaign title, caption, hashtags, target landing page URL).
    \item $O = \{(w_i, \mathbf{b}_i, p_i)\}_{i=1}^M$ represents a sequence of $M$ on-screen textual words detected via optical character recognition, where $w_i$ is the recognized string, $\mathbf{b}_i \in \mathbb{R}^4$ represents the bounding coordinates, and $p_i \in [0.0, 1.0]$ is the OCR detector confidence.
    \item $S = \{(s_j, t_{\text{start}}^j, t_{\text{end}}^j)\}_{j=1}^N$ represents an uncompressed speech audio transcript containing $N$ lexical tokens with localized temporal millisecond boundary timestamps.
\end{itemize}

The primary moderation objective is to evaluate $A$ through a composite analytical mapping:
\begin{equation}
\Phi(A) \longrightarrow \left( \hat{y}_{\text{pred}}, R, \mathbf{e}, \mathbf{c} \right)
\end{equation}
where:
\begin{itemize}
    \item $\hat{y}_{\text{pred}} \in \mathcal{Y}$ represents the predicted discrete policy category drawn from the formal four-tier regulatory taxonomy:
    \begin{equation}
    \mathcal{Y} = \{\texttt{SAFE\_FOR\_ALL},\, \texttt{SAFE\_14\_PLUS},\, \texttt{SAFE\_18\_PLUS},\, \texttt{UNSAFE\_FOR\_ALL}\} \cup \{\texttt{REQUIRES\_HUMAN\_REVIEW}\}
    \end{equation}
    \item $R \in [0.0, 100.0]$ is the bounded, continuous composite risk score.
    \item $\mathbf{e}$ denotes the structured forensic evidence dictionary detailing triggered policy codes, bounding boxes, text spans, and audio timestamps.
    \item $\mathbf{c} \in [0.0, 1.0]$ is the model confidence vector.
\end{itemize}

Simultaneously, for a registered user claim $U$ presenting an identity credential document $D$ and establishing a live webcam video stream $K$, the biometric assurance subsystem executes:
\begin{equation}
\Psi(U, D, K) \longrightarrow \left( \hat{g}_{\text{user}}, S_{\text{match}}, \text{PAD}_{\text{state}} \right)
\end{equation}
where $\hat{g}_{\text{user}} \in \{\texttt{UNDER\_14}, \texttt{AGE\_14\_TO\_17}, \texttt{AGE\_18\_PLUS}, \texttt{REJECTED}\}$, $S_{\text{match}} \in [-1.0, 1.0]$ is the ArcFace cosine similarity score between the document face crop and the live video stream, and $\text{PAD}_{\text{state}} \in \{\texttt{GENUINE\_LIVE}, \texttt{SPOOF\_ATTACK}\}$.

The final delivery dispatching operator $\Omega(\hat{y}_{\text{pred}}, \hat{g}_{\text{user}})$ enforces statutory age gating:
\begin{equation}
\Omega(\hat{y}_{\text{pred}}, \hat{g}_{\text{user}}) = 
\begin{cases}
\text{DISPATCH\_APPROVED}, & \text{if } \hat{y}_{\text{pred}} = \texttt{SAFE\_FOR\_ALL} \land \text{PAD}_{\text{state}} = \texttt{GENUINE\_LIVE} \\
\text{DISPATCH\_APPROVED}, & \text{if } \hat{y}_{\text{pred}} = \texttt{SAFE\_14\_PLUS} \land \hat{g}_{\text{user}} \in \{\texttt{AGE\_14\_TO\_17}, \texttt{AGE\_18\_PLUS}\} \\
\text{DISPATCH\_APPROVED}, & \text{if } \hat{y}_{\text{pred}} = \texttt{SAFE\_18\_PLUS} \land \hat{g}_{\text{user}} = \texttt{AGE\_18\_PLUS} \\
\text{DISPATCH\_BLOCKED}, & \text{otherwise (underage attempt, prohibited ad, or spoof attack)}
\end{cases}
\end{equation}

\section{Project Objectives}

The SafeAd AI project is structured to achieve eight rigorous, verifiable technical objectives:
\begin{enumerate}
    \item \textbf{Multimodal Extraction Pipeline:} Design and implement an automated extraction engine unifying EasyOCR (with CLAHE and Otsu binarization), deep visual feature extraction (ResNet50/MobileNetV3), temporal keyframe extraction (Farneb\"{a}ck dense optical flow), and speech transcription (Whisper) into a concurrent processing architecture.
    \item \textbf{Continuous Bounded Risk Indexing:} Formulate a mathematically verified, piecewise composite risk scoring function $S_{\text{risk}} \in [0.0, 100.0]$ mapping multidimensional hazard indicators into an interpretable risk index with non-linear emergency safety escalation.
    \item \textbf{Learned Tabular Classification (Phase 8E):} Construct a 33-dimensional feature representation capturing cross-modal detector outputs and train a balanced Random Forest late-fusion classifier under stratified 5-fold cross-validation.
    \item \textbf{Foundation VLM Deployment (Phase 10):} Deploy Qwen3-VL-8B-Instruct on Google Colab NVIDIA A100 GPU hardware in native \texttt{torch.bfloat16} precision, constructing zero-shot policy prompts that return structured JSON diagnostics.
    \item \textbf{Hierarchical Safety Fusion Protocol:} Formulate, freeze, and evaluate Strategy D (Hierarchical Safety Fusion) enforcing non-negotiable safety vetoes to eliminate prohibited-content leakage.
    \item \textbf{Rigorous Independent Held-Out Benchmark (Phase 10D):} Validate system performance on an untouched held-out test split of 27 genuine advertisements without ground-truth label leakage or post-hoc threshold tuning.
    \item \textbf{Decoupled 30~FPS Vision Engine:} Engineer a multithreaded DirectShow video engine isolating hardware capture from AI workers, eliminating native heap crashes (\texttt{0xc0000374}) and sustaining a locked 33.3~ms frame delivery interval.
    \item \textbf{Multi-Cue Liveness and Biometric Cross-Matching:} Deploy a dual-scale MiniFASNet ensemble with Hough line border tracking, specular glare tracking, and 2D FFT moir\'{e} analysis, paired with InsightFace ArcFace cosine matching ($\ge 0.65$) and ViT facial age estimation.
\end{enumerate}

\section{Scope, Boundary Conditions, and Exclusions}

The technical scope of SafeAd AI covers static image advertisements (PNG, JPEG, WebP) and short-form video advertisements (MP4, MOV, WebM) up to 60 seconds in duration with audio narration. The system enforces compliance across four discrete policy categories aligned with FTC advertising guidelines, IARC rating standards, and platform advertising rules.

The operational boundaries explicitly exclude:
\begin{itemize}
    \item Dynamic HTML5 interactive playable ads requiring real-time web browser sandbox execution.
    \item Live streaming broadcast feeds requiring sub-100ms real-time chunk filtering.
    \item Encrypted point-to-point private messaging advertisements.
\end{itemize}

\section{Summary of Scientific \& Engineering Contributions}

The key contributions of this work are summarized as follows:
\begin{enumerate}
    \item \textbf{Empirical Audit of Narrow Safety Guardrails:} We provide the first rigorous empirical diagnostic audit demonstrating that conversational safety guardrails (Meta's Llama Guard 3 Vision) fail catastrophically on commercial advertising ($80\%$ false-acceptance rate), establishing the necessity of foundation vision-language models.
    \item \textbf{The Tabular Fusion Generalization Reality:} We prove empirically that while learned tabular fusion (Random Forest) appears superior on development cohorts (improving accuracy from $31.96\%$ to $44.33\%$), it degrades severely on novel held-out test data ($37.0\%$ accuracy, $75\%$ prohibited leakage), and hierarchical fusion does not outperform standalone Qwen3-VL on novel distributions.
    \item \textbf{Zero-Leakage Foundation VLM Architecture:} We demonstrate that Qwen3-VL-8B-Instruct achieves 100\% prohibited recall and 0.0\% false acceptance on real-world advertising media.
    \item \textbf{Concurrent Vision Engine Architecture:} We solve the longstanding Windows DirectShow multithreaded COM collision problem, providing an open-source, thread-safe 30~FPS vision engine for deep learning web dashboards.
    \item \textbf{Multi-Cue Deep Anti-Spoofing Architecture:} We deploy a 103~FPS CPU-executable PAD engine fusing dual-scale MiniFASNet with spatial frequency (2D FFT) and geometric cues, preventing biometric bypass.
\end{enumerate}

\section{Report Organization}

The remainder of this report is organized as follows:
\begin{itemize}
    \item \textbf{Chapter 2 (Literature Review):} Surveys literature across multimodal content moderation, vision-language models, regulatory standards, and biometric liveness.
    \item \textbf{Chapter 3 (Problem Formulation \& Policy Framework):} Establishes formal mathematical models and delivers an exhaustive statutory defense of the four-tier policy categories with concrete illustrative figures.
    \item \textbf{Chapter 4 (System Architecture and Detailed Design):} Presents the complete system design, including UML use case, class diagrams, DFD Level 0/1, and immutable audit schemas.
    \item \textbf{Chapter 5 (Methodology and Implementation Details):} Delivers an exhaustive walkthrough of algorithms, neural architectures, Random Forest training, Qwen3-VL prompting, hierarchical fusion rules, DirectShow concurrency, and biometric PAD.
    \item \textbf{Chapter 6 (Results and Experimental Discussion):} Reports complete empirical results across Phase 8E, Phase 9B, Phase 10B/10C, and Phase 10D independent held-out test evaluations, complete with confusion matrices, itemized sample audits, biometric benchmarks, and GPU profiling.
    \item \textbf{Chapter 7 (Conclusion and Future Scope):} Synthesizes findings, technical limitations, and outlines future research trajectories.
\end{itemize}
"""
