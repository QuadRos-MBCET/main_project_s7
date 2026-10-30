import sys

def get_chapter3():
    return r"""
\chapter{Problem Formulation and Policy Framework}
\label{ch:policy}

\section{Mathematical System Formulation}
Let the multimodal creative asset space be denoted by the tuple:
\begin{equation}
\mathcal{M} = \left( \mathbf{I}, \mathbf{A}, \mathbf{T}, \mathbf{X}, \mathbf{M}_{\text{meta}} \right)
\end{equation}
where $\mathbf{I} = \{I_1, I_2, \dots, I_K\}$ represents $K$ sampled video keyframes, $\mathbf{A} \in \mathbb{R}^{S}$ is the 16~kHz mono PCM audio track, $\mathbf{T}$ is the on-screen text extracted via OCR, $\mathbf{X}$ is the speech transcript from Whisper ASR, and $\mathbf{M}_{\text{meta}}$ represents advertiser metadata.

The pre-publication moderation engine $\Phi$ maps $\mathcal{M}$ to a classification verdict:
\begin{equation}
\Phi: \mathcal{M} \longrightarrow \left( \hat{y}_{\text{pred}}, S_{\text{risk}}, \mathbf{e}, \mathbf{c} \right)
\end{equation}
where $\hat{y}_{\text{pred}} \in \mathcal{C} = \{\texttt{SAFE\_FOR\_ALL}, \texttt{SAFE\_14\_PLUS}, \texttt{SAFE\_18\_PLUS}, \texttt{UNSAFE\_FOR\_ALL}\}$, $S_{\text{risk}} \in [0.0, 100.0]$ is the continuous composite risk score, $\mathbf{e}$ is a natural language explanation articulating the policy rationale, and $\mathbf{c} \in [0.0, 1.0]^4$ represents the posterior probability distribution over $\mathcal{C}$.

Concurrently, the biometric age assurance subsystem evaluates client-side recipient eligibility:
\begin{equation}
\Psi(D_{\text{ID}}, K_{\text{live}}) \longrightarrow \left( \hat{g}_{\text{user}}, S_{\text{match}}, \text{PAD}_{\text{state}} \right)
\end{equation}
where $\hat{g}_{\text{user}} \in \{\texttt{UNDER\_14}, \texttt{AGE\_14\_TO\_17}, \texttt{AGE\_18\_PLUS}\}$, $S_{\text{match}} \in [-1.0, 1.0]$ is the ArcFace cosine similarity score between identity document photo $D_{\text{ID}}$ and live facial keyframe $K_{\text{live}}$, and $\text{PAD}_{\text{state}} \in \{\texttt{GENUINE\_LIVE}, \texttt{SPOOF\_ATTACK}\}$ denotes Presentation Attack Detection status.

The final age-aware delivery dispatching operator $\mathcal{D}(\hat{y}_{\text{pred}}, \hat{g}_{\text{user}})$ is formalized as a deterministic gating function:
\begin{equation}
\mathcal{D}(\hat{y}_{\text{pred}}, \hat{g}_{\text{user}}) = 
\begin{cases} 
\texttt{DELIVER}, & \text{if } \text{PAD}_{\text{state}} = \texttt{GENUINE\_LIVE} \land S_{\text{match}} \ge \tau_{\text{face}} \land \text{TierRank}(\hat{y}_{\text{pred}}) \le \text{UserRank}(\hat{g}_{\text{user}}) \\
\texttt{SUPPRESS}, & \text{if } \text{TierRank}(\hat{y}_{\text{pred}}) > \text{UserRank}(\hat{g}_{\text{user}}) \\
\texttt{QUARANTINE}, & \text{if } \hat{y}_{\text{pred}} = \texttt{UNSAFE\_FOR\_ALL} \lor \text{PAD}_{\text{state}} = \texttt{SPOOF\_ATTACK} \\
\texttt{FLAG\_REVIEW}, & \text{if } S_{\text{match}} < \tau_{\text{face}} \lor \text{Entropy}(\mathbf{c}) > \tau_{\text{uncertainty}}
\end{cases}
\end{equation}
where $\text{TierRank}(\cdot)$ maps $\{\texttt{SAFE\_FOR\_ALL} \mapsto 1, \texttt{SAFE\_14\_PLUS} \mapsto 2, \texttt{SAFE\_18\_PLUS} \mapsto 3, \texttt{UNSAFE\_FOR\_ALL} \mapsto \infty\}$, and $\text{UserRank}(\cdot)$ maps $\{\texttt{UNDER\_14} \mapsto 1, \texttt{AGE\_14\_TO\_17} \mapsto 2, \texttt{AGE\_18\_PLUS} \mapsto 3\}$.

\section{The Four-Tier Content Policy Taxonomy}
SafeAd AI establishes a four-tier policy hierarchy to operationalize statutory advertising codes.

\subsection{Category 1: \texttt{SAFE\_FOR\_ALL} (General Audience)}
\textbf{Definition and Criteria:} Unrestricted commercial content appropriate for all age groups (FMCG, educational tools, consumer electronics). Visual scenes must contain zero suggestive nudity, zero violence, and zero hazardous stunts. Audio and typography must be completely free of profanity, adult double entendres, and unregulated financial claims.

\textbf{Risk Calibration:} Risk score is computed linearly over benign baseline features:
\begin{equation}
S_{\text{risk}} = 100 \cdot \max \left( p_{\text{nsfw}}, p_{\text{violence}}, p_{\text{toxic}}, p_{\text{fraud}} \right) < 15.0
\end{equation}
When $S_{\text{risk}} < 15.0$ and no policy rule triggers, the asset is granted global delivery clearance.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{proc_safe_for_all.png}
\caption{End-to-End Processing Telemetry for Category 1: \texttt{SAFE\_FOR\_ALL}}
\label{fig:proc_safe_for_all}
\end{figure}

As shown in Figure~\ref{fig:proc_safe_for_all}, baseline detectors report negligible risk ($p_{\text{nsfw}}=0.00$, $p_{\text{violence}}=0.02$). The Random Forest assigns $0.98$ posterior probability to \texttt{SAFE\_FOR\_ALL}, producing a composite risk score of $0.55/100.0$ and unrestricted delivery clearance.

\subsection{Category 2: \texttt{SAFE\_14\_PLUS} (Adolescent Tier)}
\textbf{Definition and Criteria:} Content suitable for teenagers aged 14 and older (action cinema trailers, competitive esports, teen cosmetics, athletic apparel). Permits stylized non-lethal fantasy combat and kinetic motion, but strictly prohibits explicit sexuality, realistic blood and gore, gambling, alcohol, and illicit substances.

\textbf{Risk Calibration:} The risk score occupies the intermediate bracket:
\begin{equation}
15.0 \le S_{\text{risk}} < 45.0
\end{equation}
Assets in this tier are automatically suppressed for accounts categorized as \texttt{UNDER\_14}, but delivered to verified adolescents and adults.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{proc_safe_14_plus.png}
\caption{End-to-End Processing Telemetry for Category 2: \texttt{SAFE\_14\_PLUS}}
\label{fig:proc_safe_14_plus}
\end{figure}

Figure~\ref{fig:proc_safe_14_plus} traces a competitive sports ad. VideoMAE detects elevated kinetic motion ($0.28$), which Qwen3-VL contextualizes as athletic training rather than physical violence, outputting an intermediate risk of $24.80/100.0$ gated to viewers aged 14 and older.

\subsection{Category 3: \texttt{SAFE\_18\_PLUS} (Adult Restricted Commerce)}
\textbf{Definition and Criteria:} Lawful goods legally restricted to adults aged 18 and older (alcohol, licensed wagering, adult dating, high-risk financial instruments). Must comply strictly with statutory disclaimer rules and avoid appealing to minors.

\textbf{Risk Calibration:} Occupies the elevated risk bracket ($45.0 \le S_{\text{risk}} < 80.0$) using piecewise escalation when regulated keywords are detected:
\begin{equation}
S_{\text{risk}} = 45.0 + 35.0 \cdot \sigma \left( w_{\text{alc}} \cdot p_{\text{alc}} + w_{\text{gam}} \cdot p_{\text{gam}} - \theta_{\text{reg}} \right)
\end{equation}
Delivery requires live ArcFace facial verification with active Presentation Attack Detection.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{proc_safe_18_plus.png}
\caption{End-to-End Processing Telemetry for Category 3: \texttt{SAFE\_18\_PLUS}}
\label{fig:proc_safe_18_plus}
\end{figure}

Figure~\ref{fig:proc_safe_18_plus} traces a licensed craft brewery ad. Regulated terminology elevates risk to $59.50/100.0$, dispatching the creative strictly to verified adult recipients.

\subsection{Category 4: \texttt{UNSAFE\_FOR\_ALL} (Absolute Prohibition)}
\textbf{Definition and Criteria:} Strictly unlawful or hazardous content (firearms, illicit narcotics, hate speech, financial fraud, phishing). Governed by a zero-tolerance threshold and the \textbf{Rule 1 Safety Veto}:
\begin{equation}
\text{If } \max \left( p_{\text{prohibited}}^{\text{RF}}, p_{\text{prohibited}}^{\text{VLM}} \right) \ge 0.50 \implies \hat{y}_{\text{pred}} = \texttt{UNSAFE\_FOR\_ALL}, \quad S_{\text{risk}} = \max(S_{\text{risk}}, 95.0)
\end{equation}
The asset is immediately quarantined and advertiser accounts are flagged for administrative review.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{proc_unsafe_for_all.png}
\caption{End-to-End Processing Telemetry for Category 4: \texttt{UNSAFE\_FOR\_ALL}}
\label{fig:proc_unsafe_for_all}
\end{figure}

Figure~\ref{fig:proc_unsafe_for_all} depicts the interception of an unauthorized investment scheme. DeBERTa flags predatory urgency ($0.94$), and Rule 1 enforces immediate quarantine with a risk score of $95.0/100.0$.

\section{Statutory Policy Alignment and Precedence Rules}
The SafeAd AI policy taxonomy operationalizes statutory standards from the FTC Act Section 5, ASCI Code, COPPA, and the EU Digital Services Act~\cite{ftc2020guides, asci2021code}. Figure~\ref{fig:policy_hierarchy} illustrates the operational decision flow.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.88\linewidth]{policy_hierarchy.png}
\caption{SafeAd AI Policy Hierarchy and Decision Flow}
\label{fig:policy_hierarchy}
\end{figure}

The decision architecture operates under a hierarchical fail-safe principle: safety concerns always supersede commercial clearances, preventing adversaries from exploiting average-score blending in late fusion.
"""
