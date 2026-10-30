import sys

def get_content():
    return r"""
% ============================================================
% CHAPTER 4: SYSTEM ARCHITECTURE AND DETAILED DESIGN
% ============================================================

\chapter{System Architecture and Detailed Design}

\section{System Overview and Architectural Objectives}

The architectural design of SafeAd AI addresses the dual challenge of high-throughput pre-publication multimodal advertisement moderation and real-time biometric age verification. The architecture is engineered around four core requirements:
\begin{enumerate}
    \item \textbf{Modularity and Decoupling:} The pre-publication creative screening pipeline operates independently from the consumer-facing biometric verification pipeline, preventing synchronization deadlocks and allowing independent scaling.
    \item \textbf{Thread Safety and Concurrency:} Video capture operations must be isolated from heavy deep learning inference to prevent Windows DirectShow Single-Threaded Apartment (STA) collisions and memory corruption (\texttt{0xc0000374}).
    \item \textbf{Explainability and Auditability:} Moderation outputs must not terminate in opaque numeric scores; the system must emit structured JSON diagnostic trees logging all triggered policy codes, bounding boxes, text spans, and confidence vectors.
    \item \textbf{Fail-Closed Safety Gating:} In alignment with NIST AI RMF standards, when system components encounter unresolvable ambiguity, hardware timeouts, or model corruption, the architecture must fail closed, withholding content from publication.
\end{enumerate}

\section{Decoupled Three-Tier System Architecture}

SafeAd AI employs a decoupled three-tier architecture comprising the Client Presentation Layer, the Core Backend \& Detector Engine, and the High-Performance Vision-Language Inference Service. The complete architecture is illustrated in Figure~\ref{fig:arch_full}.

\begin{figure}[H]
    \centering
    \IfFileExists{system_architecture.png}{\includegraphics[width=0.92\textwidth]{system_architecture.png}}{%
        \IfFileExists{system_architecture.png}{\includegraphics[width=0.92\textwidth]{system_architecture.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{[SafeAd AI Three-Tier End-to-End System Architecture]}}}}%
    }
    \caption{SafeAd AI End-to-End System Architecture and Pipeline Interconnects.}
    \label{fig:arch_full}
\end{figure}

The functional responsibilities of each tier are defined as follows:

\subsection{Tier 1: Client Presentation Layer}
The presentation tier provides responsive web interfaces implemented in Streamlit and React 18:
\begin{itemize}
    \item \emph{Advertiser Campaign Portal:} Provides asynchronous drag-and-drop media ingestion for images (PNG, JPEG, WebP) and videos (MP4, MOV). Media is validated on the client side before streaming to the backend API.
    \item \emph{Compliance Officer Review Dashboard:} Displays synchronized video playback, detected OCR text bounding overlays, audio waveforms, risk dials, and one-click policy overrides.
    \item \emph{Recipient Verification HUD:} Renders the live webcam feed at a locked 30~FPS, overlaying real-time facial bounding boxes, ArcFace biometric matching meters, and active presentation attack warning banners.
\end{itemize}

\subsection{Tier 2: Backend Application \& Detector Engine}
Implemented in Python using FastAPI and PyTorch, this tier orchestrates local feature extraction and concurrency:
\begin{itemize}
    \item \emph{DirectShow Concurrency Daemon:} Houses the \texttt{Realtime30FPSVisionEngine}, running dedicated capture and worker threads.
    \item \emph{Multimodal Extraction Workers:} Concurrent subprocesses running EasyOCR, ResNet50/MobileNetV3 visual heads, Farneb\"{a}ck optical motion analyzers, and OpenAI Whisper audio transcription.
    \item \emph{Tabular Random Forest Classifier:} Evaluates the 33-dimensional feature representation extracted from the specialized detectors.
    \item \emph{Policy \& Audit Logging Broker:} Computes the composite risk score and persists cryptographic JSON Lines manifests to immutable storage.
\end{itemize}

\subsection{Tier 3: Vision-Language Foundation Model Service}
Because deep multimodal reasoning requires massive parameter capacity, Tier~3 deploys \textbf{Qwen3-VL-8B-Instruct} on Google Colab NVIDIA A100 GPU infrastructure in native \texttt{torch.bfloat16} precision. The model receives raw media and OCR text via secure API calls, executing zero-shot regulatory evaluation and returning structured JSON diagnostic trees.

\section{High-Level Context Modeling: Data Flow Diagram (Level 0)}

Figure~\ref{fig:dfd0_full} depicts the Level~0 Context Data Flow Diagram, establishing the operational boundary of SafeAd AI and its data exchanges with external entities.

\begin{figure}[H]
    \centering
    \IfFileExists{joseph_safead_core/backend2jb/system diagrams/dfd_level_0.jpg}{\includegraphics[width=0.82\textwidth]{joseph_safead_core/backend2jb/system diagrams/dfd_level_0.jpg}}{%
        \IfFileExists{joseph_safead_core/backend2jb/system diagrams/dfd_level_0.jpg}{\includegraphics[width=0.82\textwidth]{joseph_safead_core/backend2jb/system diagrams/dfd_level_0.jpg}}{\fbox{\parbox{0.75\textwidth}{\centering \textbf{SafeAd AI Level 0 Context Data Flow Diagram}}}}%
    }
    \caption{SafeAd AI Level 0 Data Flow Diagram: System Context Level.}
    \label{fig:dfd0_full}
\end{figure}

The four external entities interacting across the system boundary are:
\begin{enumerate}
    \item \textbf{Advertiser / Media Buyer:} Submits creative assets (images, videos, metadata copy) and receives pre-publication moderation certificates, risk diagnostics, or rejection notices.
    \item \textbf{Trust \& Safety Officer:} Inspects advertisements routed to the Human-in-the-Loop audit queue, examines forensic multimodal evidence, and logs administrative override decisions.
    \item \textbf{Compliance Administrator:} Manages policy taxonomy definitions, configures risk escalation thresholds, audits historical moderation manifests, and manages account access privileges.
    \item \textbf{End Consumer / Viewer:} Submits official identity credentials, provides a live facial camera feed during age assurance, and receives age-gated commercial advertisements matching verified demographic eligibility.
\end{enumerate}

\section{Detailed Process Decomposition: Data Flow Diagram (Level 1)}

Figure~\ref{fig:dfd1_full} illustrates the Level~1 Process Decomposition Diagram, decomposing the internal system into nine operational processes and four primary persistent data repositories.

\begin{figure}[H]
    \centering
    \IfFileExists{joseph_safead_core/backend2jb/system diagrams/dfd_level_1.jpg}{\includegraphics[width=0.92\textwidth]{joseph_safead_core/backend2jb/system diagrams/dfd_level_1.jpg}}{%
        \IfFileExists{joseph_safead_core/backend2jb/system diagrams/dfd_level_1.jpg}{\includegraphics[width=0.92\textwidth]{joseph_safead_core/backend2jb/system diagrams/dfd_level_1.jpg}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{SafeAd AI Level 1 Process Decomposition Diagram}}}}%
    }
    \caption{SafeAd AI Level 1 Data Flow Diagram: Internal Subsystem Decomposition.}
    \label{fig:dfd1_full}
\end{figure}

The operational processes and data stores are formalized as follows:
\begin{itemize}
    \item \textbf{Process 1.0 (Media Ingestion and Adaptive Preprocessing):} Ingests raw advertising media, executes container format validation, extracts adaptive keyframes using optical motion thresholds, normalizes visual frames to $224 \times 224$, and demuxes audio tracks to 16~kHz mono PCM.
    \item \textbf{Process 2.0 (Parallel Multimodal Feature Extraction):} Dispatches preprocessed streams to specialized detectors: EasyOCR extracts on-screen text, ResNet/MobileNet heads compute visual hazard probabilities, VideoMAE evaluates motion kinetics, and Whisper transcribes speech audio.
    \item \textbf{Process 3.0 (Evidence Vectorization \& Risk Scoring):} Normalizes modality outputs into the 6-dimensional evidence vector $\mathbf{x} = [V, D, N, O, A, M]$ and constructs the 33-dimensional feature representation $\mathbf{z}_i$. Computes the piecewise risk index $S_{\text{risk}}$.
    \item \textbf{Process 4.0 (Dual-Model Inference \& Policy Evaluation):} Evaluates $\mathbf{z}_i$ through the Random Forest classifier while concurrently prompting Qwen3-VL-8B-Instruct with the four-tier policy taxonomy. Executes the Two-Stage Policy Engine.
    \item \textbf{Process 5.0 (Hierarchical Safety Fusion \& HITL Routing):} Arbitrates decisions via Strategy D. If Qwen flags prohibited content ($\ge 0.70$), an absolute safety veto rejects the ad (\texttt{UNSAFE\_FOR\_ALL}). Borderline or conflicting cases are routed to Process 6.0.
    \item \textbf{Process 6.0 (Human-in-the-Loop Audit Portal):} Renders comprehensive multimodal evidence to compliance officers, logging manual confirmations or overrides.
    \item \textbf{Process 7.0 (Decoupled Video Capture \& Anti-Spoofing):} Operates the \texttt{Realtime30FPSVisionEngine}. The grabber thread polls DirectShow frames, while the AI worker executes the dual-scale MiniFASNet ensemble, Hough line border checks, and 2D FFT moir\'{e} filtering.
    \item \textbf{Process 8.0 (Biometric Matching \& Age Assurance):} Extracts 512-D ArcFace embeddings from ID crops and live frames, evaluating cosine similarity against $\tau = 0.65$. The ViT classifier estimates biological age, cross-checked against OCR dates of birth.
    \item \textbf{Process 9.0 (Age-Gated Delivery Dispatcher):} Intersects verified recipient age profiles ($\hat{g}_{\text{user}}$) with advertisement policy classifications ($\hat{y}_{\text{pred}}$) to gate delivery.
    \item \textbf{Data Repositories (D1--D4):}
    \begin{itemize}
        \item \emph{D1 (Media and Feature Store):} Persists hashed creative assets, extracted keyframes, bounding coordinates, and cached 33-D feature vectors.
        \item \emph{D2 (Policy Rules \& Threshold Repository):} Stores formal statutory definitions, hazard keyword dictionaries, and decision threshold parameters.
        \item \emph{D3 (Verified User Profiles):} Stores salted identity hashes, verified age categories, and active session tokens. Raw credential images are purged after verification to preserve privacy.
        \item \emph{D4 (Immutable Compliance Audit Logs):} Append-only JSON Lines repository logging SHA-256 hashes, raw model confidences, rule execution traces, and moderator overrides.
    \end{itemize}
\end{itemize}

\section{Object-Oriented System Architecture: UML Class Diagram}

Figure~\ref{fig:class_full} presents the static object-oriented architecture of SafeAd AI, detailing class attributes, method interfaces, inheritance hierarchies, and operational dependencies.

\begin{figure}[H]
    \centering
    \IfFileExists{joseph_safead_core/backend2jb/system diagrams/class_diagram.jpg}{\includegraphics[width=0.88\textwidth]{joseph_safead_core/backend2jb/system diagrams/class_diagram.jpg}}{%
        \IfFileExists{joseph_safead_core/backend2jb/system diagrams/class_diagram.jpg}{\includegraphics[width=0.88\textwidth]{joseph_safead_core/backend2jb/system diagrams/class_diagram.jpg}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{SafeAd AI Unified Object-Oriented Architecture Class Diagram}}}}%
    }
    \caption{SafeAd AI UML Class Diagram: Core Object-Oriented Architecture.}
    \label{fig:class_full}
\end{figure}

The primary classes and their responsibilities are:
\begin{enumerate}
    \item \texttt{AdModerationEngine}: Top-level facade class orchestrating the preprocessing, detector extraction, and policy arbitration pipelines. Exposes method \texttt{moderate\_asset(media\_path: str) -> ModerationVerdict}.
    \item \texttt{Realtime30FPSVisionEngine}: Implements thread-safe camera polling. Encapsulates \texttt{\_grabber\_thread()}, \texttt{\_worker\_thread()}, \texttt{get\_latest\_frame()}, and non-blocking mutex locks (\texttt{threading.Lock()}).
    \item \texttt{SafeAdFusionEngine}: Executes mathematical evidence aggregation, implementing Equations~\ref{eq:safeadweighted} and~\ref{eq:safeadpiecewise}. Contains methods \texttt{compute\_weighted\_base()} and \texttt{apply\_piecewise\_escalation()}.
    \item \texttt{RandomForestFusionClassifier}: Implements the 33-dimensional learned late-fusion model, encapsulating scikit-learn ensemble weights and method \texttt{predict\_proba(features: np.ndarray)}.
    \item \texttt{Qwen3VLInferenceClient}: Manages remote API interactions with the Google Colab A100 GPU service, handling prompt formatting, structured JSON response validation, and timeout retries.
    \item \texttt{TwoStagePolicyEngine}: Encapsulates the hierarchical rules for Stage~1 zero-tolerance filtering and Stage~2 audience stratification.
    \item \texttt{ArcFaceMatcher}: Loads the \texttt{iResNet50} backbone, extracts 512-D $L_2$-normalized embeddings, and computes cosine similarity via \texttt{compute\_similarity(img\_a, img\_b) -> float}.
    \item \texttt{SpoofDetector}: Implements the dual-scale MiniFASNet ensemble, Hough line border transform, and 2D FFT moir\'{e} analysis via method \texttt{predict\_liveness(frame: np.ndarray) -> LivenessResult}.
    \item \texttt{ViTAgeEstimator}: Wraps the Vision Transformer age classifier and mandibular Canny edge density analyzer.
    \item \texttt{IDDocumentProcessor}: Executes PDF rasterization via \texttt{pypdfium2}, binarization, EasyOCR parsing, regex date-of-birth extraction, and chronological age calculation.
\end{enumerate}

\section{System Dynamics: UML Use Case Modeling}

Figure~\ref{fig:usecase_full} details the UML Use Case Diagram, formalizing the functional boundaries, actor specializations, and execution triggers across the platform.

\begin{figure}[H]
    \centering
    \IfFileExists{joseph_safead_core/backend2jb/system diagrams/use_case_diagram.jpg}{\includegraphics[width=0.74\textwidth]{joseph_safead_core/backend2jb/system diagrams/use_case_diagram.jpg}}{%
        \IfFileExists{safead_use_case_diagram.png}{\includegraphics[width=0.74\textwidth]{safead_use_case_diagram.png}}{\fbox{\parbox{0.70\textwidth}{\centering \textbf{SafeAd AI Platform Actor UML Use Case Diagram}}}}%
    }
    \caption{SafeAd AI UML Use Case Diagram: Actor Interactions and System Boundaries.}
    \label{fig:usecase_full}
\end{figure}

Table~\ref{tab:use_case_specs} details the primary use case specifications across the four platform actors.

\begin{table}[htbp]
\centering
\small
\caption{Detailed SafeAd AI Use Case Specifications}
\label{tab:use_case_specs}
\begin{tabular}{|p{3.2cm}|p{3.0cm}|p{4.2cm}|p{4.2cm}|}
\hline
\textbf{Use Case Identifier} & \textbf{Primary Actor} & \textbf{Preconditions \& Triggers} & \textbf{Postconditions \& System Action} \\
\hline
\textbf{UC-01: Submit Creative Campaign} & Advertiser / Media Buyer & Advertiser authenticated; creative asset adheres to container specs. & Asset ingested; cryptographic hash computed; queued for moderation. \\
\hline
\textbf{UC-02: Pre-Publication Moderation} & Automated System & Media ingestion complete; extractors online. & Feature vectors generated; VLM evaluated; policy tier assigned. \\
\hline
\textbf{UC-03: Audit Flagged Campaign} & Trust \& Safety Officer & Campaign routed to review queue ($C < 0.60$ or signal conflict). & Forensic evidence inspected; manual decision logged to audit trail. \\
\hline
\textbf{UC-04: Recipient Age Onboarding} & End Consumer & User initiates age verification; webcam accessible. & Credential parsed; live face matched; verified age profile stored. \\
\hline
\textbf{UC-05: Intercept Presentation Attack} & Automated PAD Engine & Video stream active; user presents spoof artifact. & Spoof detected; verification blocked; biometric telemetry logged. \\
\hline
\textbf{UC-06: Age-Gated Ad Delivery} & End Consumer & User requests content feed; verified age profile active. & Feed filtered; adult ads restricted away from minors; compliant ads served. \\
\hline
\end{tabular}
\end{table}

\section{Data Contracts and Immutable Audit Trail Schemas}

In accordance with NIST AI RMF governance specifications~\cite{nistairmf2023}, SafeAd AI enforces an immutable, append-only JSON Lines data contract. Every automated moderation decision and human override emits a structured record formatted as follows:

\begin{lstlisting}[language=Python, caption={SafeAd AI Immutable Moderation Audit Record Schema}]
{
  "audit_version": "2.1.0",
  "sample_id": "SAFEAD_S18P_IMG_020",
  "timestamp": "2026-10-29T11:34:12.450Z",
  "media_sha256": "8f3b2c1e4d5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c",
  "media_type": "image/jpeg",
  "multimodal_detector_outputs": {
    "visual_unsafe_flag": 0.0,
    "nsfw_probability": 0.12,
    "violence_kinetic_score": 0.00,
    "ocr_toxicity_score": 0.05,
    "audio_risk_score": 0.00,
    "commercial_adrisk_score": 0.85,
    "detected_keywords": ["bourbon", "whiskey", "distillery", "45\% ABV"]
  },
  "random_forest_inference": {
    "predicted_class": "SAFE_18_PLUS",
    "class_probabilities": {"SFA": 0.05, "S14": 0.10, "S18": 0.82, "UFA": 0.03}
  },
  "qwen3_vl_inference": {
    "predicted_tier": "SAFE_18_PLUS",
    "confidence": 0.94,
    "policy_violations": ["ALCOHOL_COMMERCIAL_PROMOTION"],
    "justification": "The ad promotes Kentucky Straight Bourbon whiskey. Lawful adult product requiring mandatory age gating."
  },
  "hierarchical_fusion_ruling": {
    "invoked_rule": "RULE_2_ADULT_GATING_CONCORDANCE",
    "final_policy_tier": "SAFE_18_PLUS",
    "requires_human_review": false,
    "delivery_action": "RESTRICT_TO_VERIFIED_ADULTS_ONLY"
  }
}
\end{lstlisting}
"""
