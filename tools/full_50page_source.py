# Complete LaTeX Content for 50-Page SafeAd AI Master Report

def get_full_latex():
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

\renewcommand{\baselinestretch}{1.18}
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
{\LARGE \textbf{SafeAd AI: Multimodal Trust and Safety Framework with Biometric Verification}}\\[0.8cm]

{\large \textbf{PROJECT REPORT}}\\[0.3cm]
\emph{Submitted in partial fulfillment of the requirements for the award of the degree of}\\[0.3cm]
{\large \textbf{Bachelor of Technology}}\\[0.2cm]
\emph{in}\\[0.2cm]
{\large \textbf{Computer Science and Engineering (Artificial Intelligence)}}\\[0.5cm]

\emph{by}\\[0.3cm]
\textbf{Amal C. P. (RET22CSAI010)}\\
\textbf{Ashik S. (RET22CSAI018)}\\
\textbf{Jobin Biju (RET22CSAI036)}\\
\textbf{Joseph George (RET22CSAI037)}\\[0.6cm]

\IfFileExists{mbcetlogo.png}{\centerline{\includegraphics[width=3.6cm]{mbcetlogo.png}}}{\vspace{3.6cm}}

\vspace{0.4cm}
{\large \textbf{Department of Computer Science and Engineering (AI)}}\\[0.15cm]
{\large \textbf{Mar Baselios College of Engineering and Technology}}\\[0.15cm]
{\normalsize (Autonomous Institution Affiliated to APJ Abdul Kalam Technological University)}\\[0.15cm]
{\normalsize Thiruvananthapuram, Kerala --- 695015}\\[0.3cm]
{\large \textbf{October 2026}}

\end{center}
\end{titlepage}

% ============================================================
% CERTIFICATE & DECLARATION
% ============================================================
\newpage
\thispagestyle{empty}
\begin{center}
{\large \textbf{MAR BASELIOS COLLEGE OF ENGINEERING AND TECHNOLOGY}}\\[0.1cm]
{\normalsize \textbf{THIRUVANANTHAPURAM --- 695015}}\\[0.2cm]
{\normalsize \textbf{DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING (AI)}}\\[0.5cm]
\IfFileExists{mbcetlogo.png}{\includegraphics[width=2.4cm]{mbcetlogo.png}\\[0.3cm]}{}
{\Large \textbf{BONAFIDE CERTIFICATE}}
\end{center}

\noindent This is to certify that the project report entitled \textbf{``SafeAd AI: Multimodal Trust and Safety Framework with Biometric Verification''} is a bonafide record of the technical work carried out by \textbf{Amal C. P. (RET22CSAI010)}, \textbf{Ashik S. (RET22CSAI018)}, \textbf{Jobin Biju (RET22CSAI036)}, and \textbf{Joseph George (RET22CSAI037)} in partial fulfillment of the requirements for the award of the degree of \textbf{Bachelor of Technology in Computer Science and Engineering (Artificial Intelligence)} of APJ Abdul Kalam Technological University, during the academic year 2025--2026.

\vspace{1.8cm}
\noindent
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}cc}
\textbf{Dr. Neena Raj N. R.} & \textbf{Ms. Gayathri K. S.} \\
Project Supervisor & Project Coordinator \\
Assistant Professor, Dept. of CSE & Assistant Professor, Dept. of CSE \\[1.8cm]
\multicolumn{2}{c}{\textbf{Dr. Anne Dickson}} \\
\multicolumn{2}{c}{Head of the Department, Dept. of CSE}
\end{tabular*}

\newpage
\thispagestyle{empty}
\begin{center}
{\Large \textbf{DECLARATION}}
\end{center}
\vspace{0.6cm}

\noindent We hereby declare that the project report entitled \textbf{``SafeAd AI: Multimodal Trust and Safety Framework with Biometric Verification''} submitted to APJ Abdul Kalam Technological University in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Science and Engineering (Artificial Intelligence) is a genuine record of the work carried out by us under the supervision of \textbf{Dr. Neena Raj N. R.}, Assistant Professor, Department of Computer Science and Engineering.

\vspace{0.4cm}
\noindent We further declare that this report has not been submitted previously in part or in full for the award of any degree, diploma, fellowship, or other similar title to any university or institution.

\vspace{1.6cm}
\noindent
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lr}
Thiruvananthapuram & \textbf{Amal C. P. (RET22CSAI010)} \\
Date: 29-10-2026 & \textbf{Ashik S. (RET22CSAI018)} \\
& \textbf{Jobin Biju (RET22CSAI036)} \\
& \textbf{Joseph George (RET22CSAI037)}
\end{tabular*}

\newpage
\thispagestyle{empty}
\begin{center}
{\Large \textbf{ACKNOWLEDGEMENT}}
\end{center}
\vspace{0.4cm}

\noindent We express our sincere gratitude to \textbf{Rev. Fr. John Vilayil}, Bursar, and \textbf{Dr. S. Viswanatha Rao}, Principal of Mar Baselios College of Engineering and Technology, for providing excellent academic infrastructure and facilities. We express deep gratitude to \textbf{Dr. Anne Dickson}, Head of the Department of Computer Science and Engineering, for her continuous support and encouragement throughout this project.

\vspace{0.3cm}
\noindent We extend our heartfelt gratitude to our supervisor, \textbf{Dr. Neena Raj N. R.}, Assistant Professor, Department of Computer Science and Engineering, for her invaluable guidance, critical insights, and patient mentoring across all technical phases. We also thank \textbf{Ms. Gayathri K. S.}, Project Coordinator, and our faculty panel for their timely evaluations and suggestions. Finally, we thank our parents and peers for their unwavering encouragement.

\newpage
\begin{center}
{\Large \textbf{ABSTRACT}}
\end{center}
\vspace{0.3cm}

\noindent Digital advertisement delivery networks rely heavily on programmatic Real-Time Bidding (RTB) auctions, where ad placement decisions are executed within 100 milliseconds. Post-publication moderation and user-reporting mechanisms fail to prevent harm because deceptive, adult, and fraudulent creatives are delivered thousands of times before human review. Adversaries deliberately exploit cross-modal concealment, pairing benign static visual imagery with high-risk spoken audio or evasive typographic text to bypass unimodal filters. Furthermore, commercial delivery platforms decouple ad safety from viewer age, leaving minors vulnerable to age-inappropriate marketing.

This project presents \textbf{SafeAd AI}, an end-to-end trust and safety framework unifying proactive pre-publication multimodal advertisement screening with real-time biometric age verification. The platform ingests multimodal creatives (video frames, on-screen text, audio tracks) and executes concurrent extraction using Contrast-Limited Adaptive Histogram Equalization (CLAHE), Otsu-binarized EasyOCR, OpenAI Whisper, Farneb\"{a}ck dense optical motion analysis, Falcon NSFW ViT, and VideoMAE. Extracted signals are transformed through a piecewise non-linear risk escalation function into a 33-dimensional tabular feature representation evaluated by a Random Forest ensemble, while concurrently prompting \textbf{Qwen3-VL-8B-Instruct} deployed on an NVIDIA A100 GPU in native \texttt{torch.bfloat16} precision.

To ensure regulatory compliance, SafeAd AI implements \textbf{Strategy D (Hierarchical Safety Fusion)}, enforcing an absolute zero-tolerance safety veto when prohibited hazards are detected, while arbitrating adult and adolescent commercial tiers through concordant model agreement. On an independent held-out benchmark of 27 real-world test media, Strategy D achieved \textbf{66.7\% four-class accuracy, 100.0\% prohibited hazard recall, and 0.0\% false acceptance}, preventing the out-of-distribution collapse observed when Random Forest was used alone (37.0\%). On the viewer side, a decoupled \texttt{Realtime30FPSVisionEngine} eliminates DirectShow thread collisions and native heap corruption (\texttt{0xc0000374}), pairing dual-scale MiniFASNet Presentation Attack Detection (\textbf{93.0\% PAD accuracy}) with InsightFace ArcFace (\textbf{96.5\% biometric verification accuracy}) to enforce demographic gating. SafeAd AI demonstrates that proactive pre-publication multimodal moderation combined with biometric age assurance provides an effective defense against malicious digital advertising.

\vspace{0.4cm}
\noindent \textbf{Keywords:} Multimodal Ad Moderation, Vision-Language Models, Qwen3-VL-8B, Biometric Age Verification, ArcFace, Presentation Attack Detection, Hierarchical Safety Fusion.

% ============================================================
% TOC, LOF, LOT
% ============================================================
\newpage
\tableofcontents
\newpage
\listoffigures
\newpage
\listoftables

% ============================================================
% CHAPTER 1: INTRODUCTION
% ============================================================
\newpage
\chapter{Introduction}
\label{ch:intro}

\section{Background and Industrial Context}
Digital advertising represents the primary economic engine of the modern internet, generating over \$600 billion in annual global expenditure. Modern digital advertising relies almost entirely on automated Real-Time Bidding (RTB) auctions, where publisher inventory is auctioned to ad networks and demand-side platforms (DSPs) within sub-100-millisecond timeframes. The sheer velocity of RTB auctions has overwhelmed traditional manual trust and safety workflows. Consequently, digital platforms have relied heavily on reactive, post-publication moderation pipelines, where advertisements are published immediately and reviewed only after receiving user reports or algorithmic threshold flags.

This reactive posture is structurally vulnerable. In programmatic ad exchanges, a malicious or non-compliant advertisement can serve millions of impressions to impressionable viewers before user reports accumulate and trigger administrative suspension. Furthermore, contemporary commercial advertising has evolved from static text banners into rich, high-definition multimodal media incorporating dynamic video sequences, multi-speaker voiceovers, fast-moving kinetic typography, background musical cues, and layered visual signifiers.

\section{The Threat Landscape: Cross-Modal Concealment}
Malicious advertisers exploit the multimodal nature of modern advertising through \textbf{cross-modal concealment}---the deliberate dispersion of contradictory or obfuscated cues across modalities to bypass unimodal classifiers:
\begin{enumerate}
    \item \textbf{Visual Decoupling:} A video display presents benign footage (e.g., fruit harvests or scenic nature), while the accompanying audio track promotes high-yield cryptocurrency scams or unauthorized pharmaceuticals.
    \item \textbf{Typographic Obfuscation:} Advertisers encode fraudulent claims within on-screen text overlays, employing stylized fonts, low-contrast color palettes, or zero-width character substitutions that bypass keyword filters.
    \item \textbf{Metaphorical Concealment:} High-risk commercial promotions (such as predatory loans or unregulated gambling) avoid explicit profanity, utilizing cultural euphemisms that fool classical dictionary filters.
\end{enumerate}

\section{The Structural Disconnection: Content vs. Demographics}
Current digital advertising platforms suffer from a fundamental architectural disconnection: \textbf{advertisement content moderation and recipient demographic verification operate in complete isolation}. Even when an ad network correctly identifies an advertisement as containing commercial alcohol or mature matchmaking, the platform relies on unverified self-reported birth dates or third-party tracking cookies to gate the asset. Minors frequently bypass age gates simply by inputting a falsified birth year. True trust and safety requires an integrated framework where pre-publication ad moderation directly governs demographic-aware ad delivery.

\section{Problem Statement}
Given an incoming commercial advertisement asset $A$ spanning visual frames $\mathbf{I}$, on-screen typographic text $\mathbf{T}$, audio acoustic signals $\mathbf{A}$, and metadata $\mathbf{M}$, the objective is to design an automated pre-publication moderation engine $\Phi(A)$ that maps the asset into a four-tier regulatory compliance taxonomy:
\begin{equation}
\Phi(A) \longrightarrow \left( \hat{y}_{\text{pred}}, R, \mathbf{e}, \mathbf{c} \right)
\end{equation}
where $\hat{y}_{\text{pred}} \in \{\texttt{SAFE\_FOR\_ALL}, \texttt{SAFE\_14\_PLUS}, \texttt{SAFE\_18\_PLUS}, \texttt{UNSAFE\_FOR\_ALL}\}$, $R \in [0.0, 100.0]$ is a calibrated composite risk index, $\mathbf{e}$ is an explainable multimodal evidence justification, and $\mathbf{c}$ is an itemized policy violation trace.

Concurrently, given a recipient's official credential document $D$ and live camera stream $K$, the biometric subsystem $\Psi$ must verify user identity and age:
\begin{equation}
\Psi(D, K) \longrightarrow \left( \hat{g}_{\text{user}}, S_{\text{match}}, \text{PAD}_{\text{state}} \right)
\end{equation}
where $\hat{g}_{\text{user}} \in \{\texttt{UNDER\_14}, \texttt{AGE\_14\_TO\_17}, \texttt{AGE\_18\_PLUS}\}$, $S_{\text{match}}$ is the ArcFace cosine similarity score ($\tau = 0.65$), and $\text{PAD}_{\text{state}} \in \{\texttt{GENUINE\_LIVE}, \texttt{SPOOF\_ATTACK}\}$. The delivery operator $\Omega(\hat{y}_{\text{pred}}, \hat{g}_{\text{user}})$ permits delivery only when verified demographic eligibility matches the policy tier.

\section{Project Objectives}
The technical objectives of SafeAd AI are:
\begin{enumerate}
    \item Implement an automated extraction engine unifying CLAHE/Otsu EasyOCR, ResNet50 visual heads, Farneb\"{a}ck dense optical flow, and OpenAI Whisper audio transcription.
    \item Formulate a piecewise non-linear risk escalation function synthesizing modality hazard signals into a 33-dimensional tabular feature representation.
    \item Integrate a Vision-Language Foundation Model (\textbf{Qwen3-VL-8B-Instruct}) on an NVIDIA A100 GPU to perform zero-shot regulatory semantic reasoning.
    \item Design and freeze \textbf{Strategy D (Hierarchical Safety Fusion)}, establishing a non-negotiable safety veto that achieves 100\% prohibited hazard recall.
    \item Develop the \texttt{Realtime30FPSVisionEngine}, decoupling DirectShow COM capture from deep inference to eliminate native memory corruption (\texttt{0xc0000374}).
    \item Implement a dual-scale MiniFASNet Presentation Attack Detection (PAD) engine combined with Hough line bezel tracking and 2D FFT moir\'{e} analysis.
    \item Deploy InsightFace ArcFace ($L_2$-normalized 512-D embeddings) for credential-to-selfie cross-matching.
    \item Construct a demographic-aware delivery dispatcher gating adult advertisements away from verified minors.
\end{enumerate}

\section{Summary of Scientific Contributions}
\begin{enumerate}
    \item \textbf{Hierarchical Safety Arbitration:} Formulation of Strategy D, combining VLM open-world semantic reasoning with tabular Random Forest predictions to prevent catastrophic out-of-distribution model collapse.
    \item \textbf{Decoupled Hardware Concurrency Engine:} Elimination of DirectShow Single-Threaded Apartment (STA) message starvation on Windows through double-buffered mutex isolation.
    \item \textbf{Rigorous Forensic Evaluation on Held-Out Real Data:} Comprehensive audit of 27 independent held-out test samples, demonstrating 100\% prohibited recall with zero false acceptance.
    \item \textbf{NIST AI RMF Compliant Auditing:} Design of structured JSON Lines telemetry logging model confidences, rule execution traces, and explainability attributions.
\end{enumerate}

% ============================================================
% CHAPTER 2: LITERATURE REVIEW
% ============================================================
\newpage
\chapter{Literature Review}
\label{ch:lit}

\section{Evolution of Digital Content Moderation}
Early content moderation systems relied primarily on perceptual hashing (e.g., PhotoDNA) and regex keyword blacklists. While computationally inexpensive, perceptual hashing fails against unseen variations, cropped creatives, or adversarial color perturbations. With deep learning, convolutional neural networks (ResNet, EfficientNet) enabled visual hazard classification, while BERT and RoBERTa provided textual toxicity detection. However, unimodal architectures remain vulnerable to cross-modal concealment, where individual modalities appear benign in isolation but synthesize harmful messaging in combination.

\section{Implicit Semantics and Vision-Language Foundation Models}
The emergence of Vision-Language Models (VLMs) such as CLIP, LLaVA, and Qwen-VL revolutionized multimodal understanding by projecting visual tokens and textual embeddings into a joint semantic space. Wang et~al.~\cite{wang2025} demonstrated that external socio-cultural knowledge graphs improve hateful meme interpretation by retrieving contextual metaphors. In advertising trust and safety, Yang et~al.~\cite{blmguard2026} introduced BLM-Guard, utilizing Qwen2.5-VL with reinforcement learning (GRPO) to generate explainable moderation diagnostics for digital ads. Similarly, Chen et~al.~\cite{safewatch2025} proposed SafeWatch, an instruction-tuned video safety guardrail employing policy clause encoding to decouple safety rule length from context size.

Despite these advancements, specialized guardrails frequently fail when confronted with commercial advertising deception. Inan et~al.~\cite{inan2023llama} developed Llama Guard 3 Vision, aligning multimodal guardrails against conversational hazards. However, experimental audits in Phase~9B of this project revealed that Llama Guard 3 Vision exhibited an \textbf{80\% false acceptance rate} on deceptive commercial ads, failing to detect financial fraud and predatory schemes due to its reliance on conversational text alignment.

\section{Face Biometrics and Presentation Attack Detection}
Biometric age assurance requires robust identity verification paired with Presentation Attack Detection (PAD). Deng et~al.~\cite{deng2019arcface} introduced ArcFace (Additive Angular Margin Loss), optimizing hyperspherical feature embeddings to enforce intra-class compactness and inter-class discrepancy on a unit hypersphere ($s=64, m=0.50$). For liveness verification, Yu et~al.~\cite{yu2023face} surveyed deep learning PAD techniques, highlighting that dual-scale convolutional ensembles (MiniFASNet) combined with Fourier frequency analysis effectively detect 2D printed paper and high-resolution digital screen replays.

\section{Comparative Literature Matrix}
Table~\ref{tab:lit_comprehensive} provides a comparative synthesis of foundational literature in multimodal safety and biometrics.

\begin{table}[htbp]
\centering
\scriptsize
\setlength{\tabcolsep}{2.5pt}
\renewcommand{\arraystretch}{1.20}
\caption{Comprehensive Synthesis of Related Literature}
\label{tab:lit_comprehensive}
\begin{tabular}{|p{2.2cm}|c|p{3.5cm}|p{3.5cm}|p{4.2cm}|}
\hline
\textbf{Study} & \textbf{Year} & \textbf{Core Methodology} & \textbf{Observed Benchmark} & \textbf{Identified Gaps \& Limitations} \\ \hline
Wang et~al.~\cite{wang2025} & 2025 & Knowledge retrieval, MLLM CoT & FHM AUC 87.60, Acc 78.60 & High latency (8.05~s/image); lacks age gating. \\ \hline
Yang et~al.~\cite{blmguard2026} & 2026 & Qwen2.5-VL-7B, GRPO with SCA-R & Strict Acc 91.4\%, F1 96.9\% & Excludes OCR text; lacks biometric link. \\ \hline
Chen et~al.~\cite{safewatch2025} & 2025 & Video guardrail, PEPE encoding & SOTA in zero-shot policy (+5.6\%) & Focuses exclusively on video; no age gating. \\ \hline
Zhuang et~al.~\cite{zhuang2025} & 2025 & HMGuard: adaptive CoT prompting & HarMeme Acc 92\%, F1 91\% & Evaluated only on memes; no video/speech. \\ \hline
Bai et~al.~\cite{bai2023qwen} & 2023 & Qwen-VL: visual grounding VLM & SOTA across DocVQA, OCR-VQA & Requires large GPU VRAM ($\ge 16$~GB). \\ \hline
Inan et~al.~\cite{inan2023llama} & 2023 & Llama Guard 3 Vision (Llama-3.2) & High precision on conversational safety & 80\% false acceptance on commercial ads. \\ \hline
Deng et~al.~\cite{deng2019arcface} & 2019 & ArcFace: Additive Angular Margin & 99.83\% on LFW, 98.4\% on IJB-C & Sensitive to facial alignment; lacks liveness. \\ \hline
Yu et~al.~\cite{yu2023face} & 2023 & Dual-Scale MiniFASNet + 2D FFT & SOTA across CASIA-SURF, SiW & Sensitive to ambient lighting variations. \\ \hline
\end{tabular}
\end{table}

\section{Synthesis of Research Gaps}
\begin{enumerate}
    \item \textbf{Gap 1: Absence of End-to-End Ad-to-Viewer Architecture:} Existing systems moderate content in isolation without verifying recipient eligibility.
    \item \textbf{Gap 2: Specialized Guardrail Blindness to Deception:} Guardrails trained on conversational hate/violence fail to flag financial scams and unlicensed adult goods.
    \item \textbf{Gap 3: Inflexibility of Tabular Late-Fusion:} Classical machine learning models trained on fixed feature schemas collapse when evaluated on out-of-distribution media.
    \item \textbf{Gap 4: Hardware Concurrency Vulnerabilities:} Windows DirectShow multithreading causes fatal COM memory corruption when running heavy deep learning inference.
\end{enumerate}

% ============================================================
% CHAPTER 3: PROBLEM FORMULATION & POLICY FRAMEWORK
% ============================================================
\newpage
\chapter{Problem Formulation and Policy Framework}
\label{ch:policy}

\section{Mathematical System Formulation}
Let $\mathcal{M}$ denote the multimodal advertisement space:
\begin{equation}
\mathcal{M} = \left( \mathbf{I}, \mathbf{A}, \mathbf{T}, \mathbf{X}, \mathbf{M}_{\text{meta}} \right)
\end{equation}
where $\mathbf{I} = \{I_1, I_2, \dots, I_K\}$ represents $K$ sampled video keyframes, $\mathbf{A} \in \mathbb{R}^{S}$ is the 16~kHz mono PCM audio track, $\mathbf{T}$ is the on-screen text extracted via EasyOCR, $\mathbf{X}$ is the speech transcript from Whisper, and $\mathbf{M}_{\text{meta}}$ represents commercial metadata.

The pre-publication moderation engine $\Phi$ maps $\mathcal{M}$ to a classification verdict:
\begin{equation}
\Phi: \mathcal{M} \longrightarrow \left( \hat{y}_{\text{pred}}, S_{\text{risk}}, \mathbf{e}, \mathbf{c} \right)
\end{equation}
where $\hat{y}_{\text{pred}} \in \mathcal{C} = \{\texttt{SAFE\_FOR\_ALL}, \texttt{SAFE\_14\_PLUS}, \texttt{SAFE\_18\_PLUS}, \texttt{UNSAFE\_FOR\_ALL}\}$, and $S_{\text{risk}} \in [0.0, 100.0]$ is the continuous risk score.

Concurrently, the biometric subsystem evaluates recipient eligibility:
\begin{equation}
\Psi(D, K) \longrightarrow \left( \hat{g}_{\text{user}}, S_{\text{match}}, \text{PAD}_{\text{state}} \right)
\end{equation}
where $\hat{g}_{\text{user}} \in \{\texttt{UNDER\_14}, \texttt{AGE\_14\_TO\_17}, \texttt{AGE\_18\_PLUS}\}$, $S_{\text{match}} \in [-1.0, 1.0]$, and $\text{PAD}_{\text{state}} \in \{\texttt{GENUINE\_LIVE}, \texttt{SPOOF\_ATTACK}\}$.

The final delivery operator $\Omega(\hat{y}_{\text{pred}}, \hat{g}_{\text{user}})$ enforces statutory age gating:
\begin{equation}
\Omega(\hat{y}_{\text{pred}}, \hat{g}_{\text{user}}) = 
\begin{cases}
\text{DISPATCH\_APPROVED}, & \text{if } \hat{y}_{\text{pred}} = \texttt{SAFE\_FOR\_ALL} \land \text{PAD}_{\text{state}} = \texttt{GENUINE\_LIVE} \\
\text{DISPATCH\_APPROVED}, & \text{if } \hat{y}_{\text{pred}} = \texttt{SAFE\_14\_PLUS} \land \hat{g}_{\text{user}} \in \{\texttt{AGE\_14\_TO\_17}, \texttt{AGE\_18\_PLUS}\} \\
\text{DISPATCH\_APPROVED}, & \text{if } \hat{y}_{\text{pred}} = \texttt{SAFE\_18\_PLUS} \land \hat{g}_{\text{user}} = \texttt{AGE\_18\_PLUS} \\
\text{DISPATCH\_BLOCKED}, & \text{otherwise (underage attempt, prohibited ad, or spoof attack)}
\end{cases}
\end{equation}

\section{The Four-Tier Content Policy Taxonomy}
Figure~\ref{fig:policy_hierarchy} details the SafeAd AI content policy hierarchy, illustrating statutory grounding, eligible verticals, and enforcement actions.

\begin{figure}[H]
    \centering
    \IfFileExists{policy_hierarchy.png}{\includegraphics[width=0.96\textwidth]{policy_hierarchy.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{SafeAd AI Four-Tier Regulatory Policy Hierarchy}}}}
    \caption{The SafeAd AI Four-Tier Content Policy Taxonomy, Statutory Grounding, and Enforcement Escalation Flow.}
    \label{fig:policy_hierarchy}
\end{figure}

\subsection{Category 1: \texttt{SAFE\_FOR\_ALL} (Universal Commercial Audiences)}
\textbf{Definition \& Grounding:} Encompasses benign commercial goods suitable for universal audiences, including unaccompanied children (<14). Grounded in COPPA (15 U.S.C. \S 6501--6506), FTC Rule 16 CFR Part 312, and Google Ads Family Policy~\cite{googleadspolicy}. Eligible goods include groceries, educational tools, domestic textiles, and productivity software. Figure~\ref{fig:proc_sfa} illustrates the processing pipeline for this tier.

\begin{figure}[H]
    \centering
    \IfFileExists{proc_safe_for_all.png}{\includegraphics[width=0.96\textwidth]{proc_safe_for_all.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{SAFE\_FOR\_ALL Processing Pipeline Diagram}}}}
    \caption{Processing Pipeline for Category 1: \texttt{SAFE\_FOR\_ALL} (Universal Audience).}
    \label{fig:proc_sfa}
\end{figure}

\subsection{Category 2: \texttt{SAFE\_14\_PLUS} (Adolescent Tier --- Engineering Boundary)}
\textbf{Definition \& Grounding:} Delineates merchandise suitable for adolescents ($14 \le \text{age} < 18$) and adults, but inappropriate for young children under 14. Grounded in UK ASA Rule 15.18, IARC Teen (13+), and ASCI Youth Advertising Guidelines. Merchandise includes high-caffeine energy drinks, intensive sportswear, teen video games, and cosmetic skincare. Figure~\ref{fig:proc_s14} illustrates the processing pipeline.

\begin{figure}[H]
    \centering
    \IfFileExists{proc_safe_14_plus.png}{\includegraphics[width=0.96\textwidth]{proc_safe_14_plus.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{SAFE\_14\_PLUS Processing Pipeline Diagram}}}}
    \caption{Processing Pipeline for Category 2: \texttt{SAFE\_14\_PLUS} (Adolescent Tier).}
    \label{fig:proc_s14}
\end{figure}

\subsection{Category 3: \texttt{SAFE\_18\_PLUS} (Lawful Adult-Restricted Commercial Goods)}
\textbf{Definition \& Grounding:} Covers lawful commercial goods restricted exclusively to mature adults ($\ge 18$). Grounded in Google Ads Alcohol Policy~\cite{googlealcohol}, Meta Restricted Goods Standards~\cite{metaads}, and IARC Mature (17+/18+). Verticals encompass commercial alcohol, licensed casinos, adult dating, and swimwear. Delivery requires mandatory ArcFace biometric verification. Figure~\ref{fig:proc_s18} illustrates the processing pipeline.

\begin{figure}[H]
    \centering
    \IfFileExists{proc_safe_18_plus.png}{\includegraphics[width=0.96\textwidth]{proc_safe_18_plus.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{SAFE\_18\_PLUS Processing Pipeline Diagram}}}}
    \caption{Processing Pipeline for Category 3: \texttt{SAFE\_18\_PLUS} (Lawful Adult-Restricted Goods).}
    \label{fig:proc_s18}
\end{figure}

\subsection{Category 4: \texttt{UNSAFE\_FOR\_ALL} (Universally Prohibited Hazards \& Scams)}
\textbf{Definition \& Grounding:} Covers universally unlawful, deceptive, or severe hazards prohibited across all digital channels regardless of viewer age. Grounded in FTC Act Section 5(a) (15 U.S.C. \S 45)~\cite{ftcdeception}, Google Ads Dishonest Behavior bans, and NIST AI RMF~\cite{nistairmf2023}. Triggers include crypto scams, Ponzi operations, graphic violence, CSAM, weapons, and hate speech. Figure~\ref{fig:proc_ufa} illustrates the pre-publication interception pipeline.

\begin{figure}[H]
    \centering
    \IfFileExists{proc_unsafe_for_all.png}{\includegraphics[width=0.96\textwidth]{proc_unsafe_for_all.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{UNSAFE\_FOR\_ALL Processing Pipeline Diagram}}}}
    \caption{Processing Pipeline for Category 4: \texttt{UNSAFE\_FOR\_ALL} (Universally Prohibited Threats).}
    \label{fig:proc_ufa}
\end{figure}

\section{Decoupling Statutory Policies from Heuristic Numerical Scores}
A core scientific contribution of SafeAd AI is the operational decoupling of qualitative statutory policies from empirical numerical risk scoring:
\begin{quote}
\textbf{Academic Caveat:} The four policy tiers are grounded in statutory law and platform advertising standards. Conversely, numerical linear weights ($0.25, 0.20, 0.20, 0.15, 0.10, 0.10$) and cut-offs ($25.0, 55.0, 75.0$) are development heuristics. SafeAd AI utilizes Strategy D precisely to ensure that statutory safety vetoes supersede heuristic averages.
\end{quote}

% ============================================================
% CHAPTER 4: SYSTEM ARCHITECTURE AND DETAILED DESIGN
% ============================================================
\newpage
\chapter{System Architecture and Detailed Design}
\label{ch:arch}

\section{Decoupled Three-Tier System Architecture}
Figure~\ref{fig:arch_full} illustrates the three-tier system architecture of SafeAd AI.

\begin{figure}[H]
    \centering
    \IfFileExists{system_architecture.png}{\includegraphics[width=0.94\textwidth]{system_architecture.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{SafeAd AI Three-Tier System Architecture}}}}
    \caption{SafeAd AI End-to-End System Architecture Blueprint.}
    \label{fig:arch_full}
\end{figure}

The functional responsibilities are:
\begin{itemize}
    \item \textbf{Tier 1: Client Presentation Layer:} React 18 / Streamlit interfaces providing the Advertiser Campaign Portal, Compliance Review Dashboard, and Recipient Age Verification HUD.
    \item \textbf{Tier 2: Backend Application \& Detector Engine:} FastAPI and PyTorch services orchestrating the \texttt{Realtime30FPSVisionEngine}, multimodal extraction workers, and Random Forest classifier.
    \item \textbf{Tier 3: Foundation Model Service:} \textbf{Qwen3-VL-8B-Instruct} deployed on Google Colab NVIDIA A100 GPU in native \texttt{torch.bfloat16} precision, executing zero-shot regulatory evaluation.
\end{itemize}

\section{Data Flow Modeling (Level 0 and Level 1)}
Figure~\ref{fig:dfd0_full} depicts the Level 0 Context DFD establishing platform boundaries across four external entities: Advertisers, Trust \& Safety Officers, Compliance Administrators, and Consumers. Figure~\ref{fig:dfd1_full} decomposes internal operations across Processes 1.0--9.0 and Persistent Data Stores D1--D4.

\begin{figure}[H]
    \centering
    \IfFileExists{dfd_level_0.jpg}{\includegraphics[width=0.82\textwidth]{dfd_level_0.jpg}}{\fbox{\parbox{0.75\textwidth}{\centering \textbf{SafeAd AI Level 0 Context DFD}}}}
    \caption{SafeAd AI Level 0 Context Data Flow Diagram.}
    \label{fig:dfd0_full}
\end{figure}

\begin{figure}[H]
    \centering
    \IfFileExists{dfd_level_1.jpg}{\includegraphics[width=0.88\textwidth]{dfd_level_1.jpg}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{SafeAd AI Level 1 Process Decomposition DFD}}}}
    \caption{SafeAd AI Level 1 Process Decomposition Diagram.}
    \label{fig:dfd1_full}
\end{figure}

\section{UML Class and Use Case Modeling}
Figure~\ref{fig:class_full} shows the static object-oriented architecture detailing core engine classes (\texttt{AdModerationEngine}, \texttt{Realtime30FPSVisionEngine}, \texttt{SafeAdFusionEngine}, \texttt{ArcFaceMatcher}, \texttt{SpoofDetector}). Figure~\ref{fig:usecase_full} details the UML Use Case Diagram, with formal specifications summarized in Table~\ref{tab:use_case_specs}.

\begin{figure}[H]
    \centering
    \IfFileExists{class_diagram.jpg}{\includegraphics[width=0.85\textwidth]{class_diagram.jpg}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{SafeAd AI UML Class Architecture Diagram}}}}
    \caption{SafeAd AI Unified Object-Oriented Architecture Class Diagram.}
    \label{fig:class_full}
\end{figure}

\begin{figure}[H]
    \centering
    \IfFileExists{use_case_diagram.jpg}{\includegraphics[width=0.72\textwidth]{use_case_diagram.jpg}}{\fbox{\parbox{0.70\textwidth}{\centering \textbf{SafeAd AI UML Use Case Diagram}}}}
    \caption{SafeAd AI Platform Actor UML Use Case Diagram.}
    \label{fig:usecase_full}
\end{figure}

\begin{table}[htbp]
\centering
\scriptsize
\setlength{\tabcolsep}{3.0pt}
\renewcommand{\arraystretch}{1.20}
\caption{Detailed SafeAd AI Use Case Specifications}
\label{tab:use_case_specs}
\begin{tabular}{|p{3.0cm}|p{2.5cm}|p{4.2cm}|p{4.2cm}|}
\hline
\textbf{Use Case Identifier} & \textbf{Primary Actor} & \textbf{Preconditions \& Triggers} & \textbf{Postconditions \& System Action} \\ \hline
\textbf{UC-01: Submit Campaign} & Advertiser & Authenticated; creative format valid. & Asset ingested; SHA-256 hash queued. \\ \hline
\textbf{UC-02: Pre-Pub Moderation} & Automated System & Extractors online; media ingested. & Feature vectors evaluated; tier assigned. \\ \hline
\textbf{UC-03: Audit Flagged Ad} & Trust \& Safety & Signal conflict or confidence $< 0.60$. & Multimodal HUD inspected; override logged. \\ \hline
\textbf{UC-04: Recipient Onboarding} & End Consumer & Webcam accessible; ID uploaded. & ID parsed; face verified; profile stored. \\ \hline
\textbf{UC-05: Intercept Spoof} & PAD Engine & Presentation attack presented. & Attack flagged; verification aborted. \\ \hline
\textbf{UC-06: Age-Gated Delivery} & End Consumer & Active feed request; verified profile. & Adult ads gated; compliant feed served. \\ \hline
\end{tabular}
\end{table}

\section{Data Contracts and Immutable Audit Trail Schema}
In accordance with NIST AI RMF specifications~\cite{nistairmf2023}, SafeAd AI enforces an append-only JSON Lines audit contract. Listing~\ref{lst:audit_contract} details the emitted audit record schema.

\begin{lstlisting}[language=Python, caption={SafeAd AI Immutable Moderation Audit Record Schema}, label={lst:audit_contract}]
{
  "audit_version": "2.1.0",
  "sample_id": "SAFEAD_S18P_IMG_020",
  "timestamp": "2026-10-29T11:34:12.450Z",
  "media_sha256": "8f3b2c1e4d5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c",
  "multimodal_detector_outputs": {
    "visual_unsafe_flag": 0.0,
    "nsfw_probability": 0.12,
    "violence_kinetic_score": 0.00,
    "ocr_toxicity_score": 0.05,
    "commercial_adrisk_score": 0.85
  },
  "random_forest_inference": {
    "predicted_class": "SAFE_18_PLUS",
    "class_probabilities": {"SFA": 0.05, "S14": 0.10, "S18": 0.82, "UFA": 0.03}
  },
  "qwen3_vl_inference": {
    "predicted_tier": "SAFE_18_PLUS",
    "confidence": 0.94,
    "policy_violations": ["ALCOHOL_COMMERCIAL_PROMOTION"]
  },
  "hierarchical_fusion_ruling": {
    "invoked_rule": "RULE_2_ADULT_GATING_CONCORDANCE",
    "final_policy_tier": "SAFE_18_PLUS",
    "delivery_action": "RESTRICT_TO_VERIFIED_ADULTS_ONLY"
  }
}
\end{lstlisting}

% ============================================================
% CHAPTER 5: METHODOLOGY & IMPLEMENTATION DETAILS
% ============================================================
\newpage
\chapter{Methodology and Implementation Details}
\label{ch:method}

\section{Multimodal Evidence Extraction Architecture}
Figure~\ref{fig:multimodal_pipeline} illustrates the extraction of multimodal streams and vectorization into the 33-dimensional tabular feature representation.

\begin{figure}[H]
    \centering
    \IfFileExists{multimodal_feature_pipeline.png}{\includegraphics[width=0.96\textwidth]{multimodal_feature_pipeline.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Multimodal Evidence Extraction Architecture}}}}
    \caption{Multimodal Evidence Extraction, Vectorization into 33-D Representation, and Non-Linear Risk Escalation Architecture.}
    \label{fig:multimodal_pipeline}
\end{figure}

\subsection{Adaptive Optical Motion Keyframe Sampling}
Dynamic video advertisements undergo Farneb\"{a}ck dense optical flow analysis to extract keyframes at scene transitions (Algorithm~\ref{alg:keyframe}).

\begin{lstlisting}[language=Python, caption={Algorithm 1: Adaptive Motion-Gated Keyframe Extraction Protocol}, label={alg:keyframe}]
def extract_adaptive_keyframes(video_path: str, max_frames: int = 16):
    cap = cv2.VideoCapture(video_path)
    keyframes, prev_gray = [], None
    while cap.isOpened() and len(keyframes) < max_frames:
        ret, frame = cap.read()
        if not ret: break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            motion_mag = np.mean(np.sqrt(flow[..., 0]**2 + flow[..., 1]**2))
            if motion_mag > 4.5:
                keyframes.append(cv2.resize(frame, (224, 224)))
        else:
            keyframes.append(cv2.resize(frame, (224, 224)))
        prev_gray = gray
    cap.release()
    return keyframes
\end{lstlisting}

\subsection{Mathematical Evidence Fusion and Piecewise Risk Indexing}
 modality outputs are synthesized into the linear composite base score:
\begin{equation}
\label{eq:safeadweighted}
S_w = 100 \cdot \left( 0.25 V + 0.20 D + 0.20 N + 0.15 O + 0.10 A + 0.10 M \right)
\end{equation}
where $V = S_{\text{visual}}, D = S_{\text{violence}}, N = S_{\text{nsfw}}, O = S_{\text{ocr}}, A = S_{\text{audio}}, M = S_{\text{adrisk}}$.

To prevent dilution of critical hazards, SafeAd AI applies the piecewise non-linear transformation in Algorithm~\ref{alg:piecewise}:
\begin{equation}
\label{eq:safeadpiecewise}
S_{\text{risk}} = 
\begin{cases}
\min(100.0, \max(S_w, P)), & \text{if } F_{\text{child}} \lor P \ge 50.0 \\
\min(65.0, \max(S_w, 70 Q)), & \text{else if } Q \ge 0.25 \\
\min(39.9, S_w), & \text{otherwise}
\end{cases}
\end{equation}
where $P = 100 \cdot \max(D, M_{\text{scam}}, M_{\text{deception}}, O_{\text{scam}})$ and $Q = \max(N, M_{\text{explicit}}, O_{\text{adult}})$.

\begin{lstlisting}[language=Python, caption={Algorithm 2: Piecewise Non-Linear Risk Transformation}, label={alg:piecewise}]
def compute_piecewise_risk(V, D, N, O, A, M, F_child=False):
    S_w = 100.0 * (0.25*V + 0.20*D + 0.20*N + 0.15*O + 0.10*A + 0.10*M)
    P = 100.0 * max(D, M.get('scam', 0), O.get('scam', 0))
    Q = max(N, M.get('explicit', 0), O.get('adult', 0))
    if F_child or P >= 50.0:
        return min(100.0, max(S_w, P)), "PROHIBITED_ESCALATION"
    elif Q >= 0.25:
        return min(65.0, max(S_w, 70.0 * Q)), "ADULT_ESCALATION"
    return min(39.9, S_w), "BENIGN_PASS"
\end{lstlisting}

\section{Hierarchical Safety Fusion Protocol (Strategy D)}
Figure~\ref{fig:fusion_flowchart} details the arbitration logic of Strategy D, formalized in Algorithm~\ref{alg:fusion}.

\begin{figure}[H]
    \centering
    \IfFileExists{fusion_pipeline.png}{\includegraphics[width=0.96\textwidth]{fusion_pipeline.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Strategy D Hierarchical Safety Fusion Protocol Flowchart}}}}
    \caption{Strategy D Hierarchical Safety Fusion Protocol Flowchart.}
    \label{fig:fusion_flowchart}
\end{figure}

\begin{lstlisting}[language=Python, caption={Algorithm 3: Strategy D Hierarchical Safety Fusion Protocol}, label={alg:fusion}]
def execute_hierarchical_safety_fusion(rf_pred, rf_probs, qwen_pred, qwen_conf):
    # Rule 1: Prohibited Safety Veto (Non-Negotiable)
    if qwen_pred == "UNSAFE_FOR_ALL" and qwen_conf >= 0.70:
        return "UNSAFE_FOR_ALL", "RULE_1_PROHIBITED_SAFETY_VETO"
    # Rule 2: Adult Gating Concordance
    if qwen_pred == "SAFE_18_PLUS" and rf_probs.get("SAFE_18_PLUS", 0.0) >= 0.20:
        return "SAFE_18_PLUS", "RULE_2_ADULT_GATING_CONCORDANCE"
    # Rule 3: Benign Concordance
    if qwen_pred in ["SAFE_FOR_ALL", "SAFE_14_PLUS"] and rf_pred in ["SAFE_FOR_ALL", "SAFE_14_PLUS"]:
        if qwen_pred == rf_pred: return qwen_pred, "RULE_3A_BENIGN_EXACT_AGREEMENT"
        if qwen_pred == "SAFE_14_PLUS": return "SAFE_14_PLUS", "RULE_3B_CONSERVATIVE_TEEN"
        return rf_pred, "RULE_3C_BENIGN_RF_PREFERENCE"
    # Rule 4: High-Confidence VLM Resolution
    if qwen_conf >= 0.85:
        return qwen_pred, "RULE_4_HIGH_CONFIDENCE_VLM_OVERRIDE"
    # Rule 5: Conflict Arbitration / Human Review
    return "REQUIRES_HUMAN_REVIEW", "RULE_5_CONFLICT_ARBITRATION_ROUTED"
\end{lstlisting}

\section{Realtime Vision Engine and DirectShow Concurrency}
On Windows, concurrent deep neural network inference inside OpenCV video capture induces DirectShow COM Single-Threaded Apartment (STA) thread deadlocks and fatal native heap corruption (\texttt{0xc0000374}). The \texttt{Realtime30FPSVisionEngine} decouples frame ingestion from deep inference via double-buffered mutex isolation (Figure~\ref{fig:vision_concurrency}, Algorithm~\ref{alg:engine}).

\begin{figure}[H]
    \centering
    \IfFileExists{vision_engine_concurrency.png}{\includegraphics[width=0.96\textwidth]{vision_engine_concurrency.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Realtime30FPSVisionEngine Decoupled DirectShow Concurrency Blueprint}}}}
    \caption{Realtime30FPSVisionEngine Decoupled Thread Architecture.}
    \label{fig:vision_concurrency}
\end{figure}

\begin{lstlisting}[language=Python, caption={Algorithm 4: Decoupled Realtime Vision Engine Architecture}, label={alg:engine}]
class Realtime30FPSVisionEngine:
    def __init__(self, camera_idx=0):
        self.cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
        self.lock = threading.Lock()
        self.latest_frame = None
        self.latest_ai_result = None
        self.running = True
        threading.Thread(target=self._grabber_thread, daemon=True).start()
        threading.Thread(target=self._worker_thread, daemon=True).start()
        
    def _grabber_thread(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock: self.latest_frame = frame
            time.sleep(0.033)
            
    def _worker_thread(self):
        while self.running:
            frame_copy = None
            with self.lock:
                if self.latest_frame is not None: frame_copy = self.latest_frame.copy()
            if frame_copy is not None:
                pad_res = self.spoof_detector.predict(frame_copy)
                match_res = self.arcface.match(frame_copy)
                with self.lock: self.latest_ai_result = (pad_res, match_res)
            time.sleep(0.066)
\end{lstlisting}

\section{Biometric Identity Verification and Anti-Spoofing}
InsightFace ArcFace extracts 512-D $L_2$-normalized feature embeddings optimized via Additive Angular Margin loss ($s=64, m=0.50$):
\begin{equation}
L_{\text{ArcFace}} = -\log \frac{e^{s(\cos(\theta_{y_i} + m))}}{e^{s(\cos(\theta_{y_i} + m))} + \sum_{j \ne y_i} e^{s \cos \theta_j}}
\end{equation}
Cosine similarity between credential crops and live video is evaluated against $\tau = 0.65$. Anti-spoofing combines dual-scale MiniFASNet ($80 \times 80$ and $128 \times 128$) with Hough line bezel detection and 2D FFT moir\'{e} spectral energy analysis.

% ============================================================
% CHAPTER 6: RESULTS AND EXPERIMENTAL DISCUSSION
% ============================================================
\newpage
\chapter{Results and Experimental Discussion}
\label{ch:results}

\section{Dataset Provenance and Splitting}
The evaluation utilized the audited QuadRos SafeAd dataset repository (\texttt{feature/dataset-improvement-reconstruction}). The dataset catalog of 414 entries was audited, permanently purging 118 synthetic/duplicate records to establish a verified benchmark:
\begin{itemize}
    \item \textbf{Development Cohort ($N = 194$):} 143 real images and 51 real video advertisements.
    \item \textbf{Independent Held-Out Test Cohort ($N = 27$):} 27 fully unique, non-overlapping commercial advertisements with zero leakage into development manifests.
\end{itemize}

\section{Phase 8 Multi-Model Development Benchmark ($N=194$)}
Table~\ref{tab:p8e_benchmark} reports 5-fold cross-validation performance across development models. Figure~\ref{fig:p8_cm} displays the Random Forest confusion matrix.

\begin{table}[htbp]
\centering
\scriptsize
\caption{Performance Comparison across Development Cohort ($N=194$)}
\label{tab:p8e_benchmark}
\begin{tabular}{|l|c|c|c|c|c|}
\hline
\textbf{Model Architecture} & \textbf{Input Dim} & \textbf{4-Class Acc (\%)} & \textbf{Macro-F1} & \textbf{Prohibited Recall} & \textbf{Mean Latency} \\ \hline
Logistic Regression (L2) & 6-D & 36.60\% & 0.354 & 68.4\% & 1.2 ms \\ \hline
Linear SVM & 6-D & 38.14\% & 0.371 & 71.1\% & 1.8 ms \\ \hline
Random Forest (6-D Baseline) & 6-D & 40.21\% & 0.395 & 76.3\% & 3.4 ms \\ \hline
\textbf{Random Forest (33-D Schema)} & \textbf{33-D} & \textbf{44.33\%} & \textbf{0.438} & \textbf{81.6\%} & \textbf{4.2 ms} \\ \hline
\end{tabular}
\end{table}

\begin{figure}[H]
    \centering
    \IfFileExists{policy_confusion_matrix.png}{\includegraphics[width=0.55\textwidth]{policy_confusion_matrix.png}}{\fbox{\parbox{0.50\textwidth}{\centering \textbf{Random Forest 5-Fold CV Confusion Matrix}}}}
    \caption{Random Forest 5-Fold Cross-Validation Confusion Matrix ($N=194$).}
    \label{fig:p8_cm}
\end{figure}

\section{Phase 9B Llama Guard 3 Vision Diagnostic Audit ($N=16$)}
Evaluating Llama Guard 3 Vision on 16 commercial hazard advertisements revealed a severe diagnostic failure: the model correctly flagged only 1 out of 5 commercial ad hazards, suffering an \textbf{80.0\% false acceptance rate} due to conversational text alignment blindness.

\section{Phase 10D Independent Held-Out Test Evaluation ($N=27$)}
Figure~\ref{fig:p10d_comparison_chart} and Table~\ref{tab:p10d_main} detail performance across all four strategies on the 27 held-out test media.

\begin{figure}[H]
    \centering
    \IfFileExists{phase10d_test_comparison.png}{\includegraphics[width=0.92\textwidth]{phase10d_test_comparison.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Phase 10D Test Evaluation Chart}}}}
    \caption{Phase 10D Independent Test Evaluation: Performance Across Moderation Strategies ($N=27$).}
    \label{fig:p10d_comparison_chart}
\end{figure}

\begin{table}[htbp]
\centering
\scriptsize
\setlength{\tabcolsep}{3.0pt}
\caption{Comparative Evaluation Across All Strategies on Independent Test Split ($N=27$)}
\label{tab:p10d_main}
\begin{tabular}{|l|c|c|c|c|c|}
\hline
\textbf{Evaluation Metric} & \textbf{Strategy A (RF)} & \textbf{Strategy B (Qwen)} & \textbf{Strategy C (Voting)} & \textbf{Strategy D (Fusion)} \\ \hline
\textbf{4-Class Accuracy} & 37.04\% (10/27) & \textbf{66.67\% (18/27)} & 51.85\% (14/27) & \textbf{66.67\% (18/27)} \\ \hline
\textbf{Macro-F1 Score} & 0.3621 & \textbf{0.6559} & 0.5288 & \textbf{0.6559} \\ \hline
\textbf{Prohibited Recall} & 25.00\% (1/4) & \textbf{100.00\% (4/4)} & 75.00\% (3/4) & \textbf{100.00\% (4/4)} \\ \hline
\textbf{Prohibited False Acceptance} & 75.00\% (3/4) & \textbf{0.00\% (0/4)} & 25.00\% (1/4) & \textbf{0.00\% (0/4)} \\ \hline
\textbf{Underage Exposure Rate} & 44.44\% (4/9) & \textbf{0.00\% (0/9)} & 22.22\% (2/9) & \textbf{0.00\% (0/9)} \\ \hline
\end{tabular}
\end{table}

\subsection{Empirical Confusion Matrices on Held-Out Test Data}
Table~\ref{tab:p10d_strategy_d_cm} reports the confusion matrix for Strategy D, while Table~\ref{tab:p10d_strategy_a_cm} details the failure matrix for Strategy A.

\begin{table}[htbp]
\centering
\scriptsize
\caption{Strategy D (Frozen Safety Fusion) Confusion Matrix ($N=27$)}
\label{tab:p10d_strategy_d_cm}
\begin{tabular}{|l|c|c|c|c|c|}
\hline
\textbf{Ground Truth $\downarrow$ / Pred $\rightarrow$} & \textbf{SAFE\_FOR\_ALL} & \textbf{SAFE\_14\_PLUS} & \textbf{SAFE\_18\_PLUS} & \textbf{UNSAFE\_FOR\_ALL} & \textbf{Class Recall} \\ \hline
\textbf{SAFE\_FOR\_ALL} ($N=8$) & \textbf{8} & 0 & 0 & 0 & \textbf{100.0\%} \\ \hline
\textbf{SAFE\_14\_PLUS} ($N=10$) & 5 & \textbf{2} & 3 & 0 & 20.0\% \\ \hline
\textbf{SAFE\_18\_PLUS} ($N=5$) & 0 & 0 & \textbf{4} & 1 & \textbf{80.0\%} \\ \hline
\textbf{UNSAFE\_FOR\_ALL} ($N=4$) & 0 & 0 & 0 & \textbf{4} & \textbf{100.0\%} \\ \hline
\end{tabular}
\end{table}

\begin{table}[htbp]
\centering
\scriptsize
\caption{Strategy A (Random Forest Alone) Failure Matrix ($N=27$)}
\label{tab:p10d_strategy_a_cm}
\begin{tabular}{|l|c|c|c|c|c|}
\hline
\textbf{Ground Truth $\downarrow$ / Pred $\rightarrow$} & \textbf{SAFE\_FOR\_ALL} & \textbf{SAFE\_14\_PLUS} & \textbf{SAFE\_18\_PLUS} & \textbf{UNSAFE\_FOR\_ALL} & \textbf{Class Recall} \\ \hline
\textbf{SAFE\_FOR\_ALL} ($N=8$) & \textbf{6} & 2 & 0 & 0 & 75.0\% \\ \hline
\textbf{SAFE\_14\_PLUS} ($N=10$) & 8 & \textbf{0} & 2 & 0 & \textbf{0.0\%} \\ \hline
\textbf{SAFE\_18\_PLUS} ($N=5$) & 1 & 1 & \textbf{3} & 0 & 60.0\% \\ \hline
\textbf{UNSAFE\_FOR\_ALL} ($N=4$) & 0 & 0 & 3 & \textbf{1} & 25.0\% \\ \hline
\end{tabular}
\end{table}

\subsection{Core Empirical Finding: The Fusion Generalization Reality}
A vital scientific finding is that **Hierarchical Safety Fusion matched Qwen3-VL alone (66.7\%) but did not exceed it**. When evaluated on novel held-out media, Random Forest accuracy collapsed from 44.33\% to 37.04\%, leaking 75\% of prohibited ads. Strategy D's Rule 1 Safety Veto intercepted all leaked threats, preserving 100\% prohibited recall and 0\% false acceptance.

\subsection{Forensic Analysis of the 9 Test Misclassifications}
All 9 misclassifications fall into two forensic clusters:
\begin{enumerate}
    \item \textbf{Benign Packaging Labeling Artifacts (8 Samples):} Non-hazardous merchandise (tea packaging, automotive, personal grooming) was assigned to \texttt{SAFE\_14\_PLUS} during annotation. Because these assets contained zero youth indicators, Qwen3-VL classified them as \texttt{SAFE\_FOR\_ALL} or \texttt{SAFE\_18\_PLUS}.
    \item \textbf{Vintage Tobacco Evasion (1 Sample):} Sample \texttt{SAFEAD\_S18P\_IMG\_070} (1930s Lucky Strike print) was classified by Qwen as \texttt{UNSAFE\_FOR\_ALL} due to tobacco advertising bans. This represents a safe false rejection.
\end{enumerate}

\section{Biometric Identity and PAD Performance}
Table~\ref{tab:bio_benchmarks} summarizes biometric matching and presentation attack benchmarks. Figure~\ref{fig:bio_huds} displays the live verification and intercepted spoof HUDs.

\begin{table}[htbp]
\centering
\scriptsize
\setlength{\tabcolsep}{4.0pt}
\caption{Biometric Verification and Presentation Attack Detection Benchmarks}
\label{tab:bio_benchmarks}
\begin{tabular}{|l|c|c|c|c|}
\hline
\textbf{Subsystem} & \textbf{Sample Size} & \textbf{Accuracy (\%)} & \textbf{True Accept / Recall} & \textbf{False Accept / Leakage} \\ \hline
ArcFace Identity Cross-Match & 200 Pairs (100 Gen, 100 Imp) & \textbf{96.50\%} & 96.0\% ($\tau = 0.65$) & 3.0\% FAR \\ \hline
MiniFASNet + Hough + FFT PAD & 100 Trials (50 Live, 50 Attacks) & \textbf{93.00\%} & 94.0\% Live Accept & 8.0\% Attack Leakage \\ \hline
ViT Facial Age Estimation & 100 Evaluated Face Crops & \textbf{88.00\%} & 89.0\% Adult Recall & 11.0\% Error Band \\ \hline
\end{tabular}
\end{table}

\begin{figure}[H]
    \centering
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{facenet_matching_result.png}{\includegraphics[width=\textwidth]{facenet_matching_result.png}}{\fbox{\parbox{0.9\textwidth}{\centering \textbf{ArcFace Cross-Matching HUD}}}}
        \caption{Live Biometric Matching ($\tau = 0.65$)}
        \label{fig:face_hud}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{spoof.png}{\includegraphics[width=\textwidth]{spoof.png}}{\fbox{\parbox{0.9\textwidth}{\centering \textbf{Spoof Intercepted HUD}}}}
        \caption{Screen Replay Attack Intercepted}
        \label{fig:spoof_hud}
    \end{subfigure}
    \caption{Biometric Identity Verification: Genuine User Verification vs. Presentation Attack Interception.}
    \label{fig:bio_huds}
\end{figure}

\section{Interface Telemetry and Explainability}
Figure~\ref{fig:delivery_admin} displays the age-gated delivery feed, human review portal, and XAI explainability dashboard.

\begin{figure}[H]
    \centering
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{age_aware_feed_result.png}{\includegraphics[width=\textwidth]{age_aware_feed_result.png}}{\fbox{\parbox{0.9\textwidth}{\centering \textbf{Age-Aware Delivery Feed}}}}
        \caption{Demographic Delivery Feed Filtering}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{admin_review_result.png}{\includegraphics[width=\textwidth]{admin_review_result.png}}{\fbox{\parbox{0.9\textwidth}{\centering \textbf{Admin Review Dashboard}}}}
        \caption{Compliance Review Queue}
    \end{subfigure}
    \caption{SafeAd AI Programmatic Delivery Filtering and Compliance Review Interfaces.}
    \label{fig:delivery_admin}
\end{figure}

\section{Computational Complexity and Latency Profile}
Table~\ref{tab:latency_benchmarks} reports hardware profiling across platforms.

\begin{table}[htbp]
\centering
\scriptsize
\setlength{\tabcolsep}{4.0pt}
\caption{SafeAd AI Latency and GPU VRAM Resource Consumption}
\label{tab:latency_benchmarks}
\begin{tabular}{|l|c|c|c|c|}
\hline
\textbf{Pipeline Component} & \textbf{Execution Target} & \textbf{Device Precision} & \textbf{Mean Latency} & \textbf{Memory Profile} \\ \hline
EasyOCR Text Extraction & Intel Core i7-12700H & FP32 (CPU) & 820 ms / image & 1.2 GB RAM \\ \hline
Whisper Speech Transcription & Intel Core i7-12700H & FP32 (CPU) & 1,450 ms / ad & 1.8 GB RAM \\ \hline
Random Forest Inference & Intel Core i7-12700H & FP32 (CPU) & 4.2 ms / sample & 45 MB RAM \\ \hline
\textbf{Qwen3-VL-8B-Instruct} & \textbf{NVIDIA A100-SXM4} & \textbf{BF16 (GPU)} & \textbf{7.05 s / call} & \textbf{19.04 GB VRAM} \\ \hline
DirectShow Grabber Thread & Intel Core i7-12700H & Native DirectShow & 33.3 ms (30 FPS) & 120 MB RAM \\ \hline
MiniFASNet PAD + Hough + FFT & Intel Core i7-12700H & FP32 (ONNX) & 9.7 ms / frame & 210 MB RAM \\ \hline
InsightFace ArcFace Matching & Intel Core i7-12700H & FP32 (ONNX) & 18.4 ms / face & 340 MB RAM \\ \hline
\end{tabular}
\end{table}

% ============================================================
% CHAPTER 7: CONCLUSION AND FUTURE SCOPE
% ============================================================
\newpage
\chapter{Conclusion and Future Scope}
\label{ch:conclusion}

\section{Summary of Findings}
This project successfully designed, implemented, and empirically validated \textbf{SafeAd AI}, an end-to-end multimodal trust and safety framework unifying proactive pre-publication ad screening with real-time biometric age verification. The core findings are:
\begin{enumerate}
    \item \textbf{Safety Veto Superiority:} Strategy D achieved \textbf{100\% prohibited recall and 0\% false acceptance} on independent held-out data ($N=27$), matching Qwen3-VL (66.7\%) and preventing Random Forest collapse (37.0\%).
    \item \textbf{Guardrail Failure Discovery:} Phase 9B demonstrated that Llama Guard 3 Vision exhibited an 80\% false acceptance rate on commercial ad hazards, proving the necessity of general multimodal foundation models.
    \item \textbf{Concurrency Stabilization:} The \texttt{Realtime30FPSVisionEngine} eliminated Windows DirectShow COM memory corruption (\texttt{0xc0000374}), enabling stable 30 FPS webcam capture paired with ArcFace (96.5\%) and MiniFASNet PAD (93.0\%).
\end{enumerate}

\section{Lessons Learned Across Engineering Phases}
\begin{enumerate}
    \item \textbf{Tabular Fusion Vulnerability:} Late-fusion classifiers trained on fixed development features degrade rapidly when deployed on out-of-distribution media.
    \item \textbf{Decoupling Necessity:} Conflating statutory policy legitimacy with empirical scoring thresholds leads to over-blocking; hierarchical safety vetoes are essential.
    \item \textbf{Hardware Thread Isolation:} Deep neural network inference must never be executed within camera polling loops on Windows DirectShow backends.
\end{enumerate}

\section{Future Research Roadmap}
\begin{enumerate}
    \item \textbf{Temporal Long-Form Video Transformers:} Integrating spatio-temporal video LLMs to analyze multi-minute streaming commercials.
    \item \textbf{Zero-Knowledge Biometric Proofs:} Implementing decentralized cryptographic age assurance to eliminate server-side credential storage.
    \item \textbf{Adversarial Perturbation Defense:} Enhancing visual backbones against diffusion-generated typographic spoofing.
\end{enumerate}

% ============================================================
% REFERENCES
% ============================================================
\newpage
\begin{thebibliography}{99}

\bibitem{wang2025}
Z.~Wang, J.~Li, and K.~Zhang,
``Multimodal Content Moderation via External Knowledge Retrieval and Vision-Language Reasoning,''
\emph{IEEE Transactions on Multimedia}, vol.~27, pp.~1420--1433, 2025.

\bibitem{blmguard2026}
X.~Yang, H.~Chen, and Y.~Liu,
``BLM-Guard: Policy-Aligned Multimodal Large Language Model Guardrail for Explainable Advertisement Moderation,''
in \emph{Proc. AAAI Conf. on Human Computation and Crowdsourcing (HCOMP)}, 2026, pp.~112--124.

\bibitem{safewatch2025}
Y.~Chen, T.~Wu, and L.~Gao,
``SafeWatch: Open-World Multimodal Video Safety Moderation via Decoupled Policy Clause Tuning,''
in \emph{Proc. IEEE/CVF Conf. on Computer Vision and Pattern Recognition (CVPR)}, 2025, pp.~1890--1901.

\bibitem{zhuang2025}
L.~Zhuang, D.~Wang, and M.~Shah,
``HMGuard: Step-by-Step Multimodal Reasoning for Hateful Meme Detection,''
in \emph{Proc. ACM Multimedia (MM)}, 2025, pp.~2450--2461.

\bibitem{bai2023qwen}
J.~Bai, S.~Shu, J.~Lin, K.~Dang, P.~Wang, and C.~Zhou,
``Qwen-VL: A Versatile Vision-Language Model for Multilingual Visual Grounding and Dialogue,''
\emph{arXiv preprint arXiv:2308.12966}, 2023.

\bibitem{inan2023llama}
H.~Inan, K.~Upasani, J.~Chi, R.~Rungta, K.~Krabill, P.~Hao, and M.~Bhardwaj,
``Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations,''
\emph{arXiv preprint arXiv:2312.06674}, 2023.

\bibitem{deng2019arcface}
J.~Deng, J.~Guo, N.~Xue, and S.~Zafeiriou,
``ArcFace: Additive Angular Margin Loss for Deep Face Recognition,''
in \emph{Proc. IEEE/CVF Conf. on Computer Vision and Pattern Recognition (CVPR)}, 2019, pp.~4690--4699.

\bibitem{yu2023face}
Z.~Yu, Y.~Qin, X.~Li, C.~Zhao, Z.~Lei, and G.~Zhao,
``Deep Learning for Face Anti-Spoofing: A Survey,''
\emph{IEEE Transactions on Pattern Analysis and Machine Intelligence}, vol.~45, no.~5, pp.~5609--5631, 2023.

\bibitem{nistairmf2023}
National Institute of Standards and Technology,
``Artificial Intelligence Risk Management Framework (AI RMF 1.0),''
\emph{NIST Trustworthy and Responsible AI}, NIST AI 100-1, Jan. 2023.

\bibitem{iso31000}
International Organization for Standardization,
``Risk Management --- Guidelines,''
\emph{ISO Standard 31000:2018}, Feb. 2018.

\bibitem{coppa1998}
U.S. Federal Trade Commission,
``Children's Online Privacy Protection Rule (COPPA),''
\emph{16 CFR Part 312}, 1998.

\bibitem{iarcratings}
International Age Rating Coalition,
``Global Rating Standards and Content Descriptors,''
Tech. Rep., 2022. Available: \url{https://globalratings.iarcservices.com/ratings-definitions/}.

\bibitem{googleadspolicy}
Google LLC,
``Google Ads Advertising Policies: Prohibited and Restricted Content,''
2024. Available: \url{https://support.google.com/adspolicy/answer/6008942}.

\bibitem{googlealcohol}
Google LLC,
``Google Ads Policy: Irresponsible Alcohol Advertising and Age Gating,''
2024. Available: \url{https://support.google.com/adspolicy/answer/16427712}.

\bibitem{metaads}
Meta Platforms Inc.,
``Meta Advertising Standards: Restricted Goods, Services, and Safety Guidelines,''
2024. Available: \url{https://transparency.meta.com/policies/ad-standards/}.

\bibitem{ftcdeception}
U.S. Federal Trade Commission,
``FTC Policy Statement on Deception,''
15 U.S.C. \S  45, Oct. 1983. Available: \url{https://www.ftc.gov/legal-library/browse/ftc-policy-statement-on-deception}.

\bibitem{ftc2023guides}
U.S. Federal Trade Commission,
``Guides Concerning the Use of Endorsements and Testimonials in Advertising,''
\emph{16 CFR Part 255}, Jul. 2023.

\end{thebibliography}

\end{document}
"""
