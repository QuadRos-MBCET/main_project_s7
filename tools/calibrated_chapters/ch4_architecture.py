import sys

def get_chapter4():
    return r"""
\chapter{System Architecture and Detailed Design}
\label{ch:architecture}

\section{System Overview and Architectural Objectives}
SafeAd AI is engineered as a high-throughput, decoupled, microservice-based architecture designed to meet the strict sub-second latency constraints of programmatic ad bidding exchanges while maintaining rigorous trust and safety guarantees. The system design satisfies four core architectural objectives:
\begin{enumerate}
    \item \textbf{Decoupled Modularity:} Individual neural feature extractors operate as isolated, stateless functional components, allowing independent model upgrades and horizontal scaling.
    \item \textbf{Asynchronous Non-Blocking Processing:} Heavy video decompression, optical flow computation, and audio transcription are executed via asynchronous worker pools.
    \item \textbf{Graceful Degradation:} If an optional modality (such as an audio track or on-screen text) is absent, the late fusion engine dynamically adapts feature weights without throwing pipeline exceptions.
    \item \textbf{Immutable Auditability:} Every moderation verdict, detector score, and biometric verification event is cryptographically serialized into an immutable audit schema.
\end{enumerate}

\section{Decoupled Three-Tier System Architecture}
The system is structured across three distinct operational tiers, as illustrated in Figure~\ref{fig:system_architecture}.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\linewidth]{system_architecture.png}
\caption{SafeAd AI Decoupled Three-Tier System Architecture}
\label{fig:system_architecture}
\end{figure}

\subsection{Tier 1: Client Presentation Layer}
The presentation layer provides responsive web interfaces built with HTML5, Tailwind CSS, and JavaScript:
\begin{itemize}
    \item \textbf{Advertiser Submission Portal:} Allows advertisers to upload media creatives and view real-time pre-flight policy compliance reports.
    \item \textbf{Administrative Review Dashboard:} Provides compliance officers with a centralized queue of quarantined ads, displaying synchronized keyframes, extracted text, audio transcripts, and automated policy explanations.
    \item \textbf{User Demographic Client Simulator:} Simulates edge delivery, integrating a webcam feed for facial verification, Presentation Attack Detection (PAD), and ID document scanning.
\end{itemize}

\subsection{Tier 2: Backend Application and Detector Engine}
The backend application tier is built on FastAPI (Python 3.10), leveraging ASGI asynchronous request handling and PyTorch 2.4. It coordinates media ingestion, executes local computer vision preprocessing (OpenCV, FFmpeg), and hosts the specialized neural detector suite:
\begin{itemize}
    \item \textbf{Media Ingestion Service:} Validates MIME types, checks container integrity, and transcodes video streams to standardized 720p H.264 formats.
    \item \textbf{Computer Vision Pipeline:} Performs Farneb\"{a}ck optical flow estimation, adaptive keyframe sampling, CLAHE image enhancement, and EasyOCR typographic extraction.
    \item \textbf{Acoustic Extraction Worker:} Extracts 16~kHz mono PCM audio and executes Whisper speech-to-text transcription.
    \item \textbf{Learned Late Fusion Engine:} Hosts the serialized scikit-learn Random Forest ensemble that combines intermediate detector probability vectors into the Phase 8E baseline classification.
\end{itemize}

\subsection{Tier 3: Vision-Language Foundation Model Service}
The third tier hosts the Qwen3-VL-8B-Instruct vision-language foundation model. Deployed on high-performance GPU infrastructure (NVIDIA A100-SXM4-40GB), this tier accepts keyframes, OCR typography, and audio transcripts within a structured, policy-aligned prompt. It generates deep contextual reasoning tokens, outputs calibrated four-class probabilities, and articulates natural language policy explanations.

\section{High-Level Context Modeling: Data Flow Diagram (Level 0)}
Figure~\ref{fig:dfd_level_0} depicts the Level 0 Data Flow Diagram (Context Diagram) defining external entity interactions.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\linewidth]{dfd_level_0.png}
\caption{Data Flow Diagram (Level 0): Context Diagram}
\label{fig:dfd_level_0}
\end{figure}

The diagram identifies three external entities: the \textbf{Advertiser}, who submits media creatives and receives policy feedback; the \textbf{End User / Viewer}, who provides biometric verification telemetry and receives personalized age-appropriate ad streams; and the \textbf{Compliance Auditor}, who inspects flagged assets and audits compliance logs.

\section{Detailed Process Decomposition: Data Flow Diagram (Level 1)}
Figure~\ref{fig:dfd_level_1} presents the detailed Level 1 decomposition of internal system processes.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.90\linewidth]{dfd_level_1.png}
\caption{Data Flow Diagram (Level 1): Detailed Process Decomposition}
\label{fig:dfd_level_1}
\end{figure}

The Level 1 DFD decomposes system operations into seven functional processes: (1.0) Media Preprocessing, (2.0) Typographic and Acoustic Extraction, (3.0) Specialized Neural Safety Classification, (4.0) Multimodal Fusion and Policy Enforcement, (5.0) Client Biometric Identity and PAD Verification, (6.0) Age-Aware Delivery Dispatching, and (7.0) Compliance Audit Trail Generation.

\section{Object-Oriented Structure and System Dynamics}
Figure~\ref{fig:class_diagram} shows the UML Class Diagram defining object relationships across domain entities (\texttt{AdAsset}, \texttt{DetectorEngine}, \texttt{FusionPipeline}, \texttt{BiometricVerifier}, and \texttt{AuditLogger}). Figure~\ref{fig:use_case_diagram} depicts the UML Use Case Diagram illustrating actor workflows across the system lifecycle.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\linewidth]{class_diagram.png}
\caption{UML Class Diagram of the SafeAd AI Architecture}
\label{fig:class_diagram}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.82\linewidth]{use_case_diagram.png}
\caption{UML Use Case Diagram: Actor Interactions and System Workflows}
\label{fig:use_case_diagram}
\end{figure}

\section{Data Contracts and Immutable Audit Trail Schemas}
To ensure regulatory accountability under FTC, ASCI, and EU DSA frameworks, every moderation transaction produces an immutable JSON audit record adhering to Listing~\ref{lst:audit_schema}.

\begin{lstlisting}[language=json, caption={Cryptographic Audit Trail JSON Schema}, label={lst:audit_schema}]
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SafeAdAuditRecord",
  "type": "object",
  "required": ["ad_id", "timestamp", "statutory_verdict", "risk_score", "detector_telemetry"],
  "properties": {
    "ad_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" },
    "statutory_verdict": { 
      "type": "string", 
      "enum": ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS", "UNSAFE_FOR_ALL"] 
    },
    "risk_score": { "type": "number", "minimum": 0.0, "maximum": 100.0 },
    "action_dispatch": { 
      "type": "string", 
      "enum": ["DELIVER", "SUPPRESS", "QUARANTINE", "FLAG_REVIEW"] 
    },
    "detector_telemetry": {
      "type": "object",
      "properties": {
        "nsfw_score": { "type": "number" },
        "violence_kinetic_score": { "type": "number" },
        "text_toxicity_score": { "type": "number" },
        "deceptive_claim_score": { "type": "number" }
      }
    }
  }
}
\end{lstlisting}
"""
