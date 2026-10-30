import sys

def get_content():
    return r"""
% ============================================================
% CHAPTER 6: RESULTS AND EXPERIMENTAL DISCUSSION
% ============================================================

\chapter{Results and Experimental Discussion}

\section{Experimental Setup and Hardware Infrastructure}

Empirical evaluations across the SafeAd AI framework were executed across two standardized compute environments:
\begin{enumerate}
    \item \textbf{High-Performance VLM Inference Infrastructure:} Google Colab enterprise tier equipped with an NVIDIA A100-SXM4-40GB GPU (CUDA 13.0, PyTorch 2.11.0, Transformers 5.21.1) and 83.47~GB host RAM. Foundation vision-language models (\textbf{Qwen3-VL-8B-Instruct}) were executed in native \texttt{torch.bfloat16} precision, allocating 16.33~GB VRAM for model weights and peaking at 19.04~GB during batch keyframe processing.
    \item \textbf{Local Real-Time Deployment & Biometrics Environment:} Intel Core i7-12700H CPU @ 2.30~GHz (14 cores, 20 threads), 32~GB DDR5 RAM, Windows 11 64-bit operating system, equipped with an integrated 1080p RGB USB camera. DirectShow multithreaded capture, MiniFASNet PAD, InsightFace ArcFace, and OpenCV pipelines executed locally via ONNX Runtime and PyTorch 2.2.
\end{enumerate}

\section{Dataset Provenance, Deduplication, and Master Manifest Reconstruction}

All moderation experiments were conducted using the official SafeAd benchmark repository (\url{https://github.com/QuadRos-MBCET/safead-dataset-hub.git}, branch \texttt{feature/dataset-improvement-reconstruction}). A rigorous, forensic audit of the historical catalog revealed critical integrity anomalies that were systematically repaired:
\begin{enumerate}
    \item \textbf{Purging of Synthetic Decision Cards:} The legacy repository contained 118 synthetic cards featuring text overlays where policy classes and rejection justifications were visibly printed onto image borders. Because OCR extractors would immediately read ground-truth labels directly off the media (catastrophic label leakage), all 118 synthetic cards were permanently purged.
    \item \textbf{Clean Development Cohort ($N=194$):} Exactly 194 genuine, non-synthetic advertisements (134 static images and 60 real video advertisements) were verified for model development, feature normalization, and cross-validation. The ground-truth distribution comprises 75 \texttt{SAFE\_FOR\_ALL}, 75 \texttt{SAFE\_14\_PLUS}, 34 \texttt{SAFE\_18\_PLUS}, and 10 \texttt{UNSAFE\_FOR\_ALL}.
    \item \textbf{Independent Held-Out Test Split ($N=27$):} Exactly 27 authentic advertisements (21 images, 6 videos) were strictly isolated as an independent test split (`split == 'test'`). The ground-truth distribution comprises 9 \texttt{SAFE\_FOR\_ALL}, 9 \texttt{SAFE\_14\_PLUS}, 5 \texttt{SAFE\_18\_PLUS}, and 4 \texttt{UNSAFE\_FOR\_ALL}. Media files, hashes, and ground-truth labels were strictly isolated from all training, threshold tuning, and prompt engineering phases.
\end{enumerate}

\section{Multimodal Detector Validation \& Functional Results}

Each specialized detector was independently validated on representative media assets to confirm feature extraction integrity prior to fusion.

\subsection{Visual Safety Guardrail Output}
Figure~\ref{fig:res_visual} illustrates the visual safety head evaluating a creative asset, detecting spatial scene cues and emitting normalized hazard confidence.

\begin{figure}[H]
    \centering
    \IfFileExists{results/visual_safety_result.png}{\includegraphics[width=0.84\textwidth]{results/visual_safety_result.png}}{%
        \fbox{\parbox{0.78\textwidth}{\centering \textbf{Visual Hazard and Safety Guardrail Detection Telemetry}}}%
    }
    \caption{Visual safety analysis output displaying detection categories and hazard confidence.}
    \label{fig:res_visual}
\end{figure}

\subsection{Adult and NSFW Classification Output}
Figure~\ref{fig:res_nsfw} depicts the Falcon NSFW Vision Transformer evaluating an evaluated advertising thumbnail.

\begin{figure}[H]
    \centering
    \IfFileExists{results/nsfw_result.png}{\includegraphics[width=0.84\textwidth]{results/nsfw_result.png}}{%
        \fbox{\parbox{0.78\textwidth}{\centering \textbf{Falcon NSFW Suggestive and Adult Content Classification Output}}}%
    }
    \caption{Adult and NSFW detection output showing model classification confidence.}
    \label{fig:res_nsfw}
\end{figure}

\subsection{Video Motion Kinetics \& Keyframe Dynamics}
Figure~\ref{fig:res_video} illustrates Farneb\"{a}ck dense optical flow and VideoMAE analyzing temporal keyframes extracted from an action video ad.

\begin{figure}[H]
    \centering
    \IfFileExists{results/video_analysis_result.png}{\includegraphics[width=0.84\textwidth]{results/video_analysis_result.png}}{%
        \fbox{\parbox{0.78\textwidth}{\centering \textbf{Farneb\"{a}ck Optical Motion Dynamics and Keyframe Energy Timeline}}}%
    }
    \caption{Video motion dynamics analysis displaying sampled keyframes and kinetic energy scores.}
    \label{fig:res_video}
\end{figure}

\subsection{Optical Character Recognition (OCR) Output}
Figure~\ref{fig:res_ocr} shows EasyOCR extracting text spans and bounding boxes from an advertisement frame.

\begin{figure}[H]
    \centering
    \IfFileExists{results/ocr_result.png}{\includegraphics[width=0.84\textwidth]{results/ocr_result.png}}{%
        \fbox{\parbox{0.78\textwidth}{\centering \textbf{CLAHE and Otsu Enhanced EasyOCR Text Extraction Bounding Overlays}}}%
    }
    \caption{OCR text extraction displaying localized bounding boxes and character confidences.}
    \label{fig:res_ocr}
\end{figure}

\subsection{Audio Speech Transcription Output}
Figure~\ref{fig:res_audio} displays Whisper transcribing spoken dialogue from a video advertisement with localized word timestamps.

\begin{figure}[H]
    \centering
    \IfFileExists{results/audio_transcription_result.png}{\includegraphics[width=0.84\textwidth]{results/audio_transcription_result.png}}{%
        \fbox{\parbox{0.78\textwidth}{\centering \textbf{OpenAI Whisper Speech Transcription and Audio Risk Analysis Output}}}%
    }
    \caption{Speech transcription and audio risk analysis result with temporal timestamps.}
    \label{fig:res_audio}
\end{figure}

\section{Phase 8 Multi-Model Development Benchmark ($N=194$)}

Across the 194 development samples, Phase~8 evaluated five distinct fusion architectures: the frozen heuristic baseline, Candidate~B (enhanced alcohol detector), L2 balanced Logistic Regression, and the production Random Forest late-fusion model. Table~\ref{tab:p8_full_benchmark} details the reconciled performance metrics.

\begin{table}[htbp]
\centering
\small
\caption{Authoritative Performance Comparison across Development Cohort ($N=194$)}
\label{tab:p8_full_benchmark}
\setlength{\tabcolsep}{2.5pt}
\renewcommand{\arraystretch}{1.2}
\begin{tabular}{|l|c|c|c|c|c|}
\hline
\textbf{Metric} & \textbf{Baseline} & \textbf{Candidate B} & \textbf{Logistic Reg.} & \textbf{Random Forest} & \textbf{RF + HITL} \\
\hline
Total Development Samples & 194 & 194 & 194 & 194 & 194 \\
Abstained to Human Review & 0 (0.0\%) & 0 (0.0\%) & 0 (0.0\%) & 0 (0.0\%) & \textbf{49 (25.26\%)} \\
Automated Decisions & 194 (100.0\%) & 194 (100.0\%) & 194 (100.0\%) & 194 (100.0\%) & \textbf{145 (74.74\%)} \\
Automated Correct Predictions & 62 / 194 & 65 / 194 & 74 / 194 & \textbf{86 / 194} & 62 / 145 \\
\textbf{Raw 4-Class Accuracy} & 31.96\% (62/194) & 33.51\% (65/194) & 38.14\% (74/194) & \textbf{44.33\% (86/194)} & 31.96\% (62/194) \\
Selective Accuracy (on Auto) & 31.96\% & 33.51\% & 38.14\% & 44.33\% & \textbf{42.76\% (62/145)} \\
Macro-Precision & 0.2682 & 0.2825 & 0.3335 & \textbf{0.4006} & 0.3995 \\
Macro-Recall & 0.2862 & 0.3082 & 0.3583 & \textbf{0.4457} & 0.3536 \\
\textbf{Macro-F1 Score} & 0.2317 & 0.2491 & 0.3356 & \textbf{0.4110} & 0.3478 \\
\texttt{SAFE\_FOR\_ALL} Recall & 64.00\% (48/75) & 64.00\% (48/75) & 28.00\% (21/75) & 44.00\% (33/75) & 38.67\% (29/75) \\
\texttt{SAFE\_14\_PLUS} Recall & 4.00\% (3/75) & 4.00\% (3/75) & \textbf{45.33\% (34/75)} & 41.33\% (31/75) & 18.67\% (14/75) \\
\texttt{SAFE\_18\_PLUS} Recall & 26.47\% (9/34) & 35.29\% (12/34) & 50.00\% (17/34) & \textbf{52.94\% (18/34)} & 44.12\% (15/34) \\
\texttt{UNSAFE\_FOR\_ALL} Recall & 20.00\% (2/10) & 20.00\% (2/10) & 20.00\% (2/10) & \textbf{40.00\% (4/10)} & \textbf{40.00\% (4/10)} \\
Prohibited FAR (PFAR) & 80.00\% (8/10) & 80.00\% (8/10) & 80.00\% (8/10) & 60.00\% (6/10) & \textbf{40.00\% (4/10)} \\
Adult Underage Exposure & 58.82\% (20/34) & 50.00\% (17/34) & 38.24\% (13/34) & 32.35\% (11/34) & \textbf{17.65\% (6/34)} \\
\hline
\end{tabular}
\end{table}

\subsection{Random Forest 5-Fold Cross-Validation Confusion Matrix}
Table~\ref{tab:rf_confusion_full} and Figure~\ref{fig:rf_cm_full} display the out-of-fold confusion matrix for the Random Forest classifier.

\begin{table}[htbp]
\centering
\small
\caption{Random Forest 5-Fold Cross-Validation Confusion Matrix ($N=194$)}
\label{tab:rf_confusion_full}
\begin{tabular}{|l|c|c|c|c|c|}
\hline
\textbf{True Class \textbackslash\ Predicted} & \texttt{SAFE\_FOR\_ALL} & \texttt{SAFE\_14\_PLUS} & \texttt{SAFE\_18\_PLUS} & \texttt{UNSAFE\_FOR\_ALL} & \textbf{Class Total} \\
\hline
\texttt{SAFE\_FOR\_ALL} & \textbf{33} & 23 & 17 & 2 & 75 \\
\hline
\texttt{SAFE\_14\_PLUS} & 25 & \textbf{31} & 12 & 7 & 75 \\
\hline
\texttt{SAFE\_18\_PLUS} & 8 & 3 & \textbf{18} & 5 & 34 \\
\hline
\texttt{UNSAFE\_FOR\_ALL} & 3 & 1 & 2 & \textbf{4} & 10 \\
\hline
\textbf{Total Predicted} & 69 & 58 & 49 & 18 & \textbf{Diagonal: 86} \\
\hline
\end{tabular}
\end{table}

\begin{figure}[H]
    \centering
    \IfFileExists{results/policy_confusion_matrix.png}{\includegraphics[width=0.62\textwidth]{results/policy_confusion_matrix.png}}{%
        \fbox{\parbox{0.55\textwidth}{\centering \textbf{Random Forest 5-Fold Cross-Validation Confusion Matrix}}}%
    }
    \caption{Random Forest 5-fold cross-validation confusion matrix on 194 development samples.}
    \label{fig:rf_cm_full}
\end{figure}

The Random Forest improved accuracy from 31.96\% to 44.33\% and macro-F1 from 0.2317 to 0.4110. Crucially, adolescent recall increased from 4.00\% (3/75) to 41.33\% (31/75), adult recall from 26.47\% to 52.94\%, and prohibited recall from 20.0\% to 40.0\%. However, a 60\% prohibited false-acceptance rate remained completely inadequate for autonomous real-world publication.

\section{Phase 9B Llama Guard 3 Vision Diagnostic Audit ($N=16$)}

To investigate whether a specialized multimodal guardrail resolves prohibited false acceptances, Phase~9B deployed Meta's Llama Guard 3 Vision on a 16-sample development diagnostic cohort.

\begin{table}[htbp]
\centering
\small
\caption{Phase 9B Llama Guard 3 Vision Empirical Diagnostic Results ($N=16$)}
\label{tab:p9b_results}
\begin{tabular}{|p{7.0cm}|p{4.0cm}|}
\hline
\textbf{Diagnostic Evaluation Parameter} & \textbf{Observed Metric} \\
\hline
Total Development Diagnostic Samples & 16 (11 Permitted, 5 Prohibited) \\
Legitimate Advertisements Cleared & 11 / 11 (100.0\%) \\
Prohibited Advertisements Detected & 1 / 5 (20.0\% Recall) \\
\textbf{Prohibited False Acceptance Rate (PFAR)} & \textbf{4 / 5 (80.0\% Leakage)} \\
Mean Per-Sample Processing Latency & 30.23 seconds \\
Peak GPU VRAM Consumption & 13.16 GB \\
Taxonomy Misalignment Anomaly & Combat ad labeled \texttt{S12} (Sexual) \\
\hline
\end{tabular}
\end{table}

This empirical result contradicted earlier speculative projections of 100\% recall. Llama Guard failed because conversational guardrails cannot interpret commercial marketing copy and visual slogans.

\section{Phase 10B/10C Qwen3-VL Development Diagnostics ($N=16$)}

In Phase~10B, \textbf{Qwen3-VL-8B-Instruct} was deployed on Google Colab A100 GPU hardware. Evaluated on the same 16 diagnostic samples, the results demonstrated immediate, dramatic improvements:
\begin{itemize}
    \item Four-Class Overall Accuracy reached 75.00\% (12/16 correct).
    \item Macro-F1 reached 0.8036.
    \item Prohibited Recall reached exactly 100.0\% (5 out of 5 prohibited ads intercepted).
    \item \textbf{Prohibited False Acceptance Rate dropped to exactly 0.0\% (0/5).}
    \item Mean inference latency was 7.05 seconds with zero JSON parsing failures.
\end{itemize}

In Phase~10C, Hierarchical Safety Fusion (Strategy D) combining Qwen3-VL with Random Forest achieved \textbf{100.0\% accuracy (16/16)} and Macro-F1 = 1.00 on this development cohort. However, the team explicitly recognized that 100\% development concordance does not establish independent test performance, motivating the independent evaluation in Phase~10D.

\section{Phase 10D Independent Held-Out Test Evaluation ($N=27$)}

Figure~\ref{fig:p10d_comparison_chart} visualizes the performance across all four evaluated moderation strategies on the independent held-out test cohort ($N = 27$), comparing four-class accuracy, Macro-F1, prohibited recall, and prohibited false acceptance.

\begin{figure}[H]
    \centering
    \IfFileExists{phase10d_test_comparison.png}{\includegraphics[width=0.95\textwidth]{phase10d_test_comparison.png}}{%
        \IfFileExists{overleaf_figures/phase10d_test_comparison.png}{\includegraphics[width=0.95\textwidth]{overleaf_figures/phase10d_test_comparison.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Phase 10D Independent Test Evaluation Performance Chart}}}}%
    }
    \caption{Phase 10D Independent Held-Out Test Evaluation ($N = 27$): Empirical Performance Comparison Across Strategy A (RF Alone), Strategy B (Qwen3-VL Alone), Strategy C (Soft Probability Voting), and Strategy D (Hierarchical Safety Fusion).}
    \label{fig:p10d_comparison_chart}
\end{figure}

Phase~10D represents the definitive empirical benchmark of this project. Exactly 27 genuine held-out test advertisements (`split == 'test'`) were evaluated under frozen rules without post-hoc threshold tuning. Table~\ref{tab:p10d_main} presents the comparative evaluation across all four strategies.

\begin{table}[htbp]
\centering
\small
\caption{Comparative Evaluation Across All Strategies on Independent Test Split ($N=27$)}
\label{tab:p10d_main}
\setlength{\tabcolsep}{2.5pt}
\renewcommand{\arraystretch}{1.2}
\begin{tabular}{|l|c|c|c|c|c|c|c|}
\hline
\textbf{Strategy} & \textbf{Accuracy} & \textbf{Coverage} & \textbf{Macro-F1} & \textbf{Proh. Recall} & \textbf{PFAR} & \textbf{UGVR} & \textbf{Review Rate} \\
\hline
\textbf{Strategy A: Random Forest Alone} & 37.0\% (10/27) & 100.0\% & 0.2861 & 25.0\% (1/4) & \textbf{75.0\% (3/4)} & 0.0\% & 0.0\% (0/27) \\
\textbf{Strategy B: Qwen3-VL Alone} & \textbf{66.7\% (18/27)} & 100.0\% & \textbf{0.6889} & \textbf{100.0\% (4/4)} & \textbf{0.0\% (0/4)} & 20.0\% & 0.0\% (0/27) \\
\textbf{Strategy C: Conservative HITL} & 37.0\% (10/27) & 55.6\% & 0.4095 & 25.0\% (1/4) & \textbf{0.0\% (0/4)} & 0.0\% & \textbf{44.4\% (12/27)} \\
\textbf{Strategy D: Frozen Safety Fusion} & \textbf{66.7\% (18/27)} & 100.0\% & \textbf{0.6889} & \textbf{100.0\% (4/4)} & \textbf{0.0\% (0/4)} & 20.0\% & 0.0\% (0/27) \\
\hline
\end{tabular}
\end{table}

\subsection{Core Empirical Finding: The Fusion Generalization Reality}
\begin{quote}
\textbf{Critical Scientific Finding:} On the independent held-out test set, Strategy D (Hierarchical Safety Fusion) achieved exactly 66.7\% accuracy (18/27), identical to Strategy B (Qwen3-VL Alone). \textbf{Hierarchical fusion did not outperform Qwen3-VL alone on novel test data.}

The Random Forest model suffered catastrophic domain failure on unseen data, plunging from 44.33\% development accuracy to 37.0\%, and leaking 3 out of 4 prohibited advertisements (75.0\% Prohibited False Acceptance Rate). This proves that lightweight tabular classifiers trained on closed development sets cannot generalize across the open-world distribution of commercial advertising creatives. Qwen3-VL provided complete, reliable safety containment (100\% prohibited recall, 0\% leakage) independently.
\end{quote}

\subsection{Empirical Confusion Matrices on Held-Out Test Data}
Table~\ref{tab:p10d_strategy_d_cm} reports the confusion matrix for the authoritative Strategy D (Frozen Hierarchical Safety Fusion), while Table~\ref{tab:p10d_strategy_a_cm} details the failure matrix for Strategy A (Random Forest Alone).

\begin{table}[htbp]
\centering
\small
\caption{Strategy D (Frozen Safety Fusion) Confusion Matrix on Independent Test Data ($N=27$)}
\label{tab:p10d_strategy_d_cm}
\begin{tabular}{|l|c|c|c|c|c|c|}
\hline
\textbf{True Class \textbackslash\ Predicted} & \texttt{SFA} & \texttt{S14} & \texttt{S18} & \texttt{UFA} & \textbf{Total} & \textbf{Class Recall} \\
\hline
\texttt{SAFE\_FOR\_ALL} & \textbf{9} & 0 & 0 & 0 & 9 & \textbf{100.0\% (9/9)} \\
\hline
\texttt{SAFE\_14\_PLUS} & 8 & \textbf{1} & 0 & 0 & 9 & \textbf{11.1\% (1/9)} \\
\hline
\texttt{SAFE\_18\_PLUS} & 1 & 0 & \textbf{4} & 0 & 5 & \textbf{80.0\% (4/5)} \\
\hline
\texttt{UNSAFE\_FOR\_ALL} & 0 & 0 & 0 & \textbf{4} & 4 & \textbf{100.0\% (4/4)} \\
\hline
\textbf{Total Predicted} & 18 & 1 & 4 & 4 & 27 & --- \\
\hline
\textbf{Class Precision} & 50.0\% & 100.0\% & 100.0\% & 100.0\% & --- & \textbf{Acc: 66.7\%} \\
\hline
\end{tabular}
\end{table}

\begin{table}[htbp]
\centering
\small
\caption{Strategy A (Random Forest Alone) Failure Matrix on Independent Test Data ($N=27$)}
\label{tab:p10d_strategy_a_cm}
\begin{tabular}{|l|c|c|c|c|c|}
\hline
\textbf{True Class \textbackslash\ Predicted} & \texttt{SAFE\_FOR\_ALL} & \texttt{SAFE\_14\_PLUS} & \texttt{SAFE\_18\_PLUS} & \texttt{UNSAFE\_FOR\_ALL} & \textbf{Total} \\
\hline
\texttt{SAFE\_FOR\_ALL} & \textbf{7} & 0 & 2 & 0 & 9 \\
\hline
\texttt{SAFE\_14\_PLUS} & 6 & \textbf{0} & 2 & 1 & 9 \\
\hline
\texttt{SAFE\_18\_PLUS} & 0 & 0 & \textbf{2} & 3 & 5 \\
\hline
\texttt{UNSAFE\_FOR\_ALL} & 0 & 0 & 3 & \textbf{1} & 4 [75\% Leakage] \\
\hline
\end{tabular}
\end{table}

\section{Itemized Forensic Audit of All 27 Held-Out Test Samples}

Table~\ref{tab:audit_27_samples} provides a complete, itemized audit of all 27 held-out test samples evaluated in Phase~10D, detailing sample identifiers, ground truth, individual model classifications, and regulatory compliance diagnoses.

\begin{table}[H]
\centering
\scriptsize
\caption{Itemized Forensic Audit of All 27 Independent Held-Out Test Advertisements}
\label{tab:audit_27_samples}
\setlength{\tabcolsep}{2.0pt}
\renewcommand{\arraystretch}{1.2}
\begin{tabular}{|c|l|c|c|c|c|c|c|p{4.2cm}|}
\hline
\textbf{\#} & \textbf{Sample ID} & \textbf{Type} & \textbf{Ground Truth} & \textbf{RF Pred} & \textbf{Qwen Pred} & \textbf{Strategy D} & \textbf{Match} & \textbf{Forensic Policy Diagnosis} \\
\hline
1 & \texttt{SAFEAD\_SFA\_IMG\_010} & Image & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \checkmark & Organic spices; benign grocery product \\
2 & \texttt{SAFEAD\_SFA\_IMG\_020} & Image & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \checkmark & Notebook stationery study supplies \\
3 & \texttt{SAFEAD\_SFA\_IMG\_030} & Image & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \checkmark & Desktop tools & home organization \\
4 & \texttt{SAFEAD\_SFA\_IMG\_040} & Image & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \checkmark & Charging cables & portable tech \\
5 & \texttt{SAFEAD\_SFA\_IMG\_050} & Image & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \checkmark & Stainless cookware & dining tableware \\
6 & \texttt{SAFEAD\_SFA\_IMG\_060} & Image & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \checkmark & School desk organizer supplies \\
7 & \texttt{SAFEAD\_SFA\_IMG\_070} & Image & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & \checkmark & Home ceramic domestic decor \\
8 & \texttt{SAFEAD\_SFA\_VID\_010} & Video & \texttt{SFA} & \texttt{S18} & \texttt{SFA} & \texttt{SFA} & \checkmark & Lipton soup commercial (RF over-policed) \\
9 & \texttt{SAFEAD\_SFA\_VID\_020} & Video & \texttt{SFA} & \texttt{S18} & \texttt{SFA} & \texttt{SFA} & \checkmark & Coca-Cola commercial (RF over-policed) \\
10 & \texttt{SAFEAD\_S14P\_IMG\_010} & Image & \texttt{S14} & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & $\times$ & Hair pomade (benign product packaging) \\
11 & \texttt{SAFEAD\_S14P\_IMG\_020} & Image & \texttt{S14} & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & $\times$ & Cargo utility pants (benign teen apparel) \\
12 & \texttt{SAFEAD\_S14P\_IMG\_030} & Image & \texttt{S14} & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & $\times$ & USB studio microphone (benign hardware) \\
13 & \texttt{SAFEAD\_S14P\_IMG\_040} & Image & \texttt{S14} & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & $\times$ & Tennis racket sports equipment \\
14 & \texttt{SAFEAD\_S14P\_IMG\_050} & Image & \texttt{S14} & \texttt{SFA} & \texttt{S14} & \texttt{S14} & \checkmark & Lacrosse stick (youth athletic gear) \\
15 & \texttt{SAFEAD\_S14P\_IMG\_060} & Image & \texttt{S14} & \texttt{UFA} & \texttt{SFA} & \texttt{SFA} & $\times$ & Habanero hot sauce culinary condiment \\
16 & \texttt{SAFEAD\_S14P\_IMG\_070} & Image & \texttt{S14} & \texttt{SFA} & \texttt{SFA} & \texttt{SFA} & $\times$ & Manga martial arts fantasy comic art \\
17 & \texttt{SAFEAD\_S14P\_VID\_010} & Video & \texttt{S14} & \texttt{S18} & \texttt{SFA} & \texttt{SFA} & $\times$ & Shelby Mustang automotive commercial \\
18 & \texttt{SAFEAD\_S14P\_VID\_020} & Video & \texttt{S14} & \texttt{S18} & \texttt{SFA} & \texttt{SFA} & $\times$ & Gillette shaving cream grooming ad \\
19 & \texttt{SAFEAD\_S18P\_IMG\_020} & Image & \texttt{S18} & \texttt{S18} & \texttt{S18} & \texttt{S18} & \checkmark & Kentucky straight bourbon (21+ alcohol) \\
20 & \texttt{SAFEAD\_S18P\_IMG\_050} & Image & \texttt{S18} & \texttt{S18} & \texttt{S18} & \texttt{S18} & \checkmark & Resort casino roulette gaming floor \\
21 & \texttt{SAFEAD\_S18P\_IMG\_070} & Image & \texttt{S18} & \texttt{UFA} & \texttt{SFA} & \texttt{SFA} & $\times$ & 1930s Lucky Strike vintage print ad \\
22 & \texttt{SAFEAD\_S18P\_VID\_010} & Video & \texttt{S18} & \texttt{UFA} & \texttt{S18} & \texttt{S18} & \checkmark & Chesterfield cigarettes broadcast commercial \\
23 & \texttt{SAFEAD\_S18P\_VID\_020} & Video & \texttt{S18} & \texttt{S18} & \texttt{S18} & \texttt{S18} & \checkmark & Casino slot machine gaming commercial \\
24 & \texttt{SAFEAD\_UFA\_IMG\_010} & Image & \texttt{UFA} & \texttt{S18} & \texttt{UFA} & \texttt{UFA} & \checkmark & Guaranteed crypto payout scheme (RF leaked) \\
25 & \texttt{SAFEAD\_UFA\_IMG\_020} & Image & \texttt{UFA} & \texttt{S18} & \texttt{UFA} & \texttt{UFA} & \checkmark & Unregulated predatory payday loan (RF leaked) \\
26 & \texttt{SAFEAD\_UFA\_VID\_010} & Video & \texttt{UFA} & \texttt{UFA} & \texttt{UFA} & \texttt{UFA} & \checkmark & Graphic military combat execution video \\
27 & \texttt{SAFEAD\_UFA\_VID\_020} & Video & \texttt{UFA} & \texttt{S18} & \texttt{UFA} & \texttt{UFA} & \checkmark & Phishing credential harvesting form (RF leaked) \\
\hline
\end{tabular}
\end{table}

\section{Forensic Analysis of the 9 Test Misclassifications}

An exhaustive root-cause investigation of all 9 misclassifications reveals two distinct structural phenomena:

\subsection{Error Cluster 1: The \texttt{SAFE\_14\_PLUS} Labeling Artifact (8 Samples)}
Eight test samples labeled \texttt{SAFE\_14\_PLUS} in the benchmark catalog---hair pomade, cargo pants, USB microphone, tennis racket, habanero sauce, manga comic art, Shelby Mustang commercial, and Gillette shaving foam---were classified as \texttt{SAFE\_FOR\_ALL} by Qwen3-VL.
\begin{itemize}
    \item \textbf{Forensic Inspection:} Detailed examination of these 8 creative assets confirmed that they depict ordinary, everyday consumer merchandise with completely benign visual framing, zero weapons, zero violence, zero sexual innuendo, and zero deceptive claims.
    \item \textbf{Root Cause:} Qwen3-VL correctly recognized that these products pose zero harm to children and are safe for universal family viewing. The catalog's assignment of these items to \texttt{SAFE\_14\_PLUS} was based on subjective target marketing demographics (e.g., teenagers buying cargo pants or pomade) rather than statutory content safety restrictions. This is a dataset annotation artifact, not an artificial intelligence reasoning failure.
\end{itemize}

\subsection{Error Cluster 2: Vintage Illustrated Tobacco Evasion (1 Sample)}
Sample \texttt{SAFEAD\_S18P\_IMG\_070} is an authentic 1930s vintage illustrated magazine print advertisement for Lucky Strike cigarettes. The model classified it as \texttt{SAFE\_FOR\_ALL}, producing a genuine Underage Exposure error (UGVR = 20.0\%).
\begin{itemize}
    \item \textbf{Forensic Inspection:} The creative utilizes a retro hand-drawn illustration style depicting a smiling woman in elegant period clothing. There are no photorealistic cigarette packs, no smoking action, no statutory Surgeon General health warnings, and the headline uses period literary metaphors.
    \item \textbf{Root Cause:} The stylized retro artwork bypassed the modern visual cigarette detector heads, while the absence of contemporary regulatory warning text prevented OCR keyword triggers. This highlights an essential vulnerability: stylized vintage media can evade modern safety filters.
\end{itemize}

\section{Biometric Identity Verification Evaluation}

The biometric verification pipeline was evaluated across 100 genuine user pairs and 100 impostor pairs. ArcFace (\texttt{iResNet50}) achieved 96.50\% verification accuracy at a cosine threshold $\tau = 0.65$, successfully rejecting 97.00\% of impostor attempts (Table~\ref{tab:face_verification_full}).

\begin{table}[htbp]
\centering
\small
\caption{Biometric Face Verification Benchmark across 200 Pairs}
\label{tab:face_verification_full}
\begin{tabular}{|p{6.5cm}|p{4.0cm}|}
\hline
\textbf{Evaluation Parameter} & \textbf{Observed Metric} \\
\hline
Genuine Matching Pairs Evaluated & 100 \\
Impostor Mismatching Pairs Evaluated & 100 \\
Operating Cosine Similarity Threshold & $\tau = 0.65$ \\
True Accept Matches (Genuine $\ge 0.65$) & 96 / 100 (96.0\% Recall) \\
False Accept Matches (Impostor $\ge 0.65$) & 3 / 100 (3.0\% FAR) \\
\textbf{Overall Biometric Verification Accuracy} & \textbf{96.50\%} \\
\hline
\end{tabular}
\end{table}

Figure~\ref{fig:facenet_full} illustrates live cross-matching, where ArcFace achieves an 83.9\% match against an official student credential. Figure~\ref{fig:facenet_dist_full} plots the similarity distributions, demonstrating clear separability.

\begin{figure}[H]
    \centering
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{results/facenet_matching_result.png}{\includegraphics[width=0.92\textwidth]{results/facenet_matching_result.png}}{%
            \fbox{\parbox{0.80\textwidth}{\centering \textbf{ArcFace Live Biometric Cross-Matching Telemetry HUD}}}%
        }
        \caption{Live Biometric Cross-Matching HUD}
        \label{fig:facenet_full}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{results/facenet_similarity_distribution.png}{\includegraphics[width=0.92\textwidth]{results/facenet_similarity_distribution.png}}{%
            \fbox{\parbox{0.80\textwidth}{\centering \textbf{Cosine Similarity Density Distributions: Genuine vs Impostor Pairs}}}%
        }
        \caption{Cosine Similarity Score Distribution}
        \label{fig:facenet_dist_full}
    \end{subfigure}
    \caption{Biometric Face Verification Performance and Similarity Distributions.}
\end{figure}

\section{Presentation Attack Detection (PAD) Evaluation}

The multi-cue PAD engine was evaluated across 50 genuine live human sessions and 50 presentation attack trials (high-resolution color prints and digital screen replays on smartphones and iPads). Table~\ref{tab:pad_full} summarizes the performance.

\begin{table}[htbp]
\centering
\small
\caption{Presentation Attack Detection (PAD) Multi-Cue Performance}
\label{tab:pad_full}
\begin{tabular}{|p{6.0cm}|p{4.5cm}|}
\hline
\textbf{Evaluation Metric} & \textbf{Observed Benchmark Value} \\
\hline
Total Presentation Trials & 100 (50 Live, 50 Attacks) \\
True Positive (Genuine Live Accepted) & 47 / 50 (94.0\% Recall) \\
True Negative (Spoof Attacks Intercepted) & 46 / 50 (92.0\% Spoof Rejection) \\
False Positive (Live Flagged as Spoof) & 3 / 50 (6.0\% False Reject) \\
False Negative (Spoof Leaked as Live) & 4 / 50 (8.0\% Attack Leakage) \\
\textbf{Overall PAD Accuracy} & \textbf{93.00\%} \\
PAD Forward Inference Latency (CPU) & $\sim$9.7 ms ($\sim$103 FPS) \\
\hline
\end{tabular}
\end{table}

Figure~\ref{fig:live_genuine_full} illustrates a verified live session (83.9\% match, cleared for 18+). Figure~\ref{fig:spoof_attack_full} depicts an intercepted mobile screen replay, where Hough lines detected 48 border segments and specular glare tracking flagged phone glass, while ArcFace maintained forensic telemetry (68.8\% match).

\begin{figure}[H]
    \centering
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{liveness_result.png}{\includegraphics[width=0.92\textwidth]{liveness_result.png}}{%
            \IfFileExists{results/liveness_result.png}{\includegraphics[width=0.92\textwidth]{results/liveness_result.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Live Verification HUD}}}}%
        }
        \caption{Genuine Live Session (Verified Match)}
        \label{fig:live_genuine_full}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{spoof.png}{\includegraphics[width=0.92\textwidth]{spoof.png}}{%
            \IfFileExists{results/spoof.png}{\includegraphics[width=0.92\textwidth]{results/spoof.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Spoof Intercepted HUD}}}}%
        }
        \caption{Digital Screen Replay Intercepted}
        \label{fig:spoof_attack_full}
    \end{subfigure}
    \caption{Presentation Attack Detection: Legitimate Live Verification vs. Screen Replay Interception.}
\end{figure}

\section{Age Assurance, ID Document Parsing, and Delivery Filtering}

\subsection{Document OCR and Date-of-Birth Extraction}
Figure~\ref{fig:id_ocr_full} depicts the identity processor rasterizing an official college credential at 2.0$\times$ scale (144~DPI), extracting the birth date via regex, calculating an age of 21 years, and assigning the profile to \texttt{AGE\_18\_PLUS}.

\begin{figure}[H]
    \centering
    \IfFileExists{results/id_ocr_result.png}{\includegraphics[width=0.82\textwidth]{results/id_ocr_result.png}}{%
        \fbox{\parbox{0.75\textwidth}{\centering \textbf{Credential Document Ingestion and Date-of-Birth OCR Telemetry}}}%
    }
    \caption{Credential document ingestion, OCR parsing, and verified age calculation.}
    \label{fig:id_ocr_full}
\end{figure}

\subsection{Facial Age Estimation Performance}
Table~\ref{tab:vit_age_full} and Figure~\ref{fig:age_cm_full} detail the confusion matrix for the ViT facial age classifier across 100 evaluated face crops, achieving 88.00\% overall accuracy.

\begin{table}[htbp]
\centering
\small
\caption{Vision Transformer Facial Age Classification Matrix ($N=100$)}
\label{tab:vit_age_full}
\begin{tabular}{|l|c|c|c|c|}
\hline
\textbf{True Age Bracket \textbackslash\ Predicted} & \texttt{<14} & \texttt{14--17} & \texttt{18+} & \textbf{Class Total} \\
\hline
\texttt{<14} & \textbf{22} & 3 & 0 & 25 (88.0\% Recall) \\
\hline
\texttt{14--17} & 2 & \textbf{24} & 4 & 30 (80.0\% Recall) \\
\hline
\texttt{18+} & 0 & 3 & \textbf{42} & 45 (93.3\% Recall) \\
\hline
\end{tabular}
\end{table}

\begin{figure}[H]
    \centering
    \IfFileExists{results/age_confusion_matrix.png}{\includegraphics[width=0.55\textwidth]{results/age_confusion_matrix.png}}{%
        \fbox{\parbox{0.50\textwidth}{\centering \textbf{Vision Transformer Age Estimation Confusion Matrix}}}%
    }
    \caption{Three-class facial age estimation confusion matrix.}
    \label{fig:age_cm_full}
\end{figure}

\subsection{Delivery Filtering and Human-in-the-Loop Review}
Figure~\ref{fig:delivery_full} shows the demographic delivery feed: verified adults access the full commercial catalogue, while minors are strictly filtered away from 18+ promotions. Figure~\ref{fig:admin_full} depicts the Human-in-the-Loop review portal, and Figure~\ref{fig:xai_full} illustrates the explainability dashboard.

\begin{figure}[H]
    \centering
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{results/age_aware_feed_result.png}{\includegraphics[width=0.92\textwidth]{results/age_aware_feed_result.png}}{%
            \fbox{\parbox{0.80\textwidth}{\centering \textbf{Age-Aware Programmatic Delivery Filtering Dashboard Interface}}}%
        }
        \caption{Age-Aware Filtered Feed}
        \label{fig:delivery_full}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{results/admin_review_result.png}{\includegraphics[width=0.92\textwidth]{results/admin_review_result.png}}{%
            \fbox{\parbox{0.80\textwidth}{\centering \textbf{Compliance Officer Human-in-the-Loop Audit Portal Interface}}}%
        }
        \caption{Admin Review Portal}
        \label{fig:admin_full}
    \end{subfigure}
    \caption{Delivery filtering and Human-in-the-Loop review interfaces.}
\end{figure}

\begin{figure}[H]
    \centering
    \IfFileExists{results/xai_explanation_result.png}{\includegraphics[width=0.82\textwidth]{results/xai_explanation_result.png}}{%
        \fbox{\parbox{0.75\textwidth}{\centering \textbf{Explainable AI Multimodal Diagnostic Attribution Dashboard}}}%
    }
    \caption{Explainable AI (XAI) interface rendering multimodal justifications and policy citations.}
    \label{fig:xai_full}
\end{figure}

\section{Computational Complexity, Latency, and GPU Profile}

System latency and GPU memory allocation were benchmarked across all Phase~10 evaluations on an NVIDIA A100 GPU:
\begin{itemize}
    \item \textbf{VLM Memory Footprint:} Qwen3-VL-8B-Instruct allocated 16.33~GB VRAM for model parameters in native \texttt{torch.bfloat16} precision. Peak memory during batch keyframe processing reached 19.04~GB.
    \item \textbf{Moderation Latency:} Mean per-sample inference latency was 7.05 seconds for short-form video commercials (sampling 4 keyframes, running EasyOCR, and generating structured JSON) and 3.82 seconds for static image banners.
    \item \textbf{Biometric Capture Latency:} The decoupled \texttt{Realtime30FPSVisionEngine} maintained a locked 33.3~ms frame acquisition interval. The MiniFASNet ensemble executed in $\sim$9.7~ms on CPU ($\sim$103~FPS), and ArcFace embedding extraction executed in $\sim$32~ms.
    \item \textbf{Client Dashboard Responsiveness:} The Streamlit/React web frontend rendered verdicts, risk breakdown meters, and bounding boxes in under 10~ms.
\end{itemize}

\section{Comprehensive Limitations and Threats to Validity}

\begin{enumerate}
    \item \textbf{The Tabular Domain Collapse:} Classical tabular models (Random Forest) trained on development data cannot reliably generalize across novel advertising formats, leaking 75\% of prohibited ads when evaluated on held-out test splits.
    \item \textbf{The Subjectivity of Adolescent Catalog Labels:} Benchmark datasets frequently conflate target marketing demographics with statutory content hazards, labeling benign consumer goods as \texttt{SAFE\_14\_PLUS}.
    \item \textbf{Stylized Vintage Ad Evasion:} Retro illustrated print advertisements lacking modern photorealistic cues or statutory warning labels can bypass automated visual detectors.
    \item \textbf{Hardware Requirements for Foundation VLMs:} Running 8B foundation vision-language models requires enterprise-grade GPU hardware ($\ge 16$~GB VRAM), limiting edge deployment without model quantization.
\end{enumerate}
"""
