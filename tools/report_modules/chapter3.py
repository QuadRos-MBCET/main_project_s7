import sys

def get_content():
    return r"""
% ============================================================
% CHAPTER 3: PROBLEM FORMULATION AND POLICY FRAMEWORK
% ============================================================

\chapter{Problem Formulation and Policy Framework}

\section{Mathematical Formalization of the SafeAd Framework}

To establish a mathematically rigorous foundation for automated pre-publication moderation and age-gated distribution, SafeAd AI formalizes the problem as an optimization and constrained classification task over heterogeneous multimodal spaces.

\subsection{Multimodal Creative Asset Space}
Let the universe of all commercial advertising submissions be defined as $\mathcal{A}$. An individual advertisement creative $A \in \mathcal{A}$ is formalized as a structured five-tuple:
\begin{equation}
A = \left( I, V, T, O, S \right)
\end{equation}
where:
\begin{enumerate}
    \item $I \in \mathcal{X}_{\text{img}} = \mathbb{R}^{H_I \times W_I \times 3}$ denotes a standardized spatial RGB representation corresponding to static display banners or video cover thumbnails, normalized such that pixel intensities $I(x,y,c) \in [0.0, 1.0]$.
    \item $V = \{f_1, f_2, \dots, f_K\} \in \mathcal{X}_{\text{vid}}$ represents a finite ordered sequence of $K$ video keyframes sampled at temporal motion boundaries, where each keyframe $f_k \in \mathbb{R}^{H_V \times W_V \times 3}$. For static image ads, $K=1$ and $f_1 = I$.
    \item $T \in \mathcal{X}_{\text{text}}$ represents the unstructured natural language metadata supplied by the advertiser, including the campaign headline, body copy, descriptive caption, hashtags, and landing page uniform resource identifiers (URIs).
    \item $O = \{(w_i, \mathbf{b}_i, p_i)\}_{i=1}^M \in \mathcal{X}_{\text{ocr}}$ represents the set of $M$ discrete textual tokens extracted from visual frames via Optical Character Recognition (OCR), where $w_i \in \mathcal{V}_{\text{lex}}$ is the recognized word, $\mathbf{b}_i = (x_1, y_1, x_2, y_2)_i \in [0, 1]^4$ represents the normalized bounding box coordinates, and $p_i \in [0.0, 1.0]$ is the OCR recognition confidence.
    \item $S = \{(s_j, t_{\text{start}}^j, t_{\text{end}}^j)\}_{j=1}^N \in \mathcal{X}_{\text{asr}}$ represents the spoken acoustic transcript containing $N$ recognized words transcribed from the demuxed audio track, with word-level millisecond boundary timestamps $t_{\text{start}}^j, t_{\text{end}}^j \in \mathbb{R}^+$.
\end{enumerate}

\subsection{The Pre-Publication Moderation Mapping}
The primary objective of the pre-publication moderation engine is to learn an evaluation operator $\Phi: \mathcal{A} \rightarrow \mathcal{Y} \times \mathbb{R} \times \mathcal{E} \times [0, 1]^4$ that maps creative asset $A$ into a four-tuple:
\begin{equation}
\Phi(A) = \left( \hat{y}_{\text{pred}}, R(A), \mathbf{e}(A), \mathbf{c}(A) \right)
\end{equation}
where:
\begin{itemize}
    \item $\hat{y}_{\text{pred}}$ is the assigned discrete policy decision drawn from the target label space:
    \begin{equation}
    \mathcal{Y} = \{\texttt{SAFE\_FOR\_ALL},\, \texttt{SAFE\_14\_PLUS},\, \texttt{SAFE\_18\_PLUS},\, \texttt{UNSAFE\_FOR\_ALL}\} \cup \{\texttt{REQUIRES\_HUMAN\_REVIEW}\}
    \end{equation}
    \item $R(A) \in [0.0, 100.0]$ is the continuous, scalar composite risk index.
    \item $\mathbf{e}(A) \in \mathcal{E}$ represents the structured forensic evidence dictionary containing triggered regulatory policy violation codes, identified visual bounding boxes, flagged OCR text spans, and audio timestamps.
    \item $\mathbf{c}(A) = [c_{\text{SFA}}, c_{\text{S14}}, c_{\text{S18}}, c_{\text{UFA}}] \in [0.0, 1.0]^4$ is the class probability or confidence distribution over the four policy tiers, satisfying $\sum_{k} c_k = 1.0$.
\end{itemize}

\subsection{Biometric Age Assurance \& Recipient Verification Mapping}
Concurrently, let the set of all registered digital consumers seeking access to media feeds be denoted by $\mathcal{U}$. For a specific user claim $U \in \mathcal{U}$, the recipient submits an official biographical identity document $D \in \mathcal{D}$ (e.g., National ID, Driver's License, College Credential) and initiates a live video capture session $K \in \mathcal{K}$ through an uncalibrated client RGB webcam.

The biometric assurance subsystem executes a composite verification mapping:
\begin{equation}
\Psi(U, D, K) \longrightarrow \left( \hat{g}_{\text{user}}, S_{\text{match}}, \text{PAD}_{\text{state}} \right)
\end{equation}
where:
\begin{itemize}
    \item $\hat{g}_{\text{user}} \in \{\texttt{UNDER\_14}, \texttt{AGE\_14\_TO\_17}, \texttt{AGE\_18\_PLUS}, \texttt{REJECTED}\}$ represents the verified biological and chronological age profile.
    \item $S_{\text{match}} \in [-1.0, 1.0]$ is the geodesic cosine similarity between the facial embedding extracted from credential document $D$ and the live stream $K$.
    \item $\text{PAD}_{\text{state}} \in \{\texttt{GENUINE\_LIVE}, \texttt{SPOOF\_ATTACK}\}$ denotes the binary liveness classification produced by the Presentation Attack Detection ensemble.
\end{itemize}

\subsection{Age-Gated Delivery Dispatching Operator}
The final distribution of creative asset $A$ to recipient $U$ is governed by the deterministic dispatching rule $\Omega: \mathcal{Y} \times \mathcal{G} \rightarrow \{\text{PERMITTED}, \text{BLOCKED}\}$:
\begin{equation}
\Omega(\hat{y}_{\text{pred}}, \hat{g}_{\text{user}}) = 
\begin{cases}
\text{PERMITTED}, & \text{if } \hat{y}_{\text{pred}} = \texttt{SAFE\_FOR\_ALL} \land \text{PAD}_{\text{state}} = \texttt{GENUINE\_LIVE} \\
\text{PERMITTED}, & \text{if } \hat{y}_{\text{pred}} = \texttt{SAFE\_14\_PLUS} \land \hat{g}_{\text{user}} \in \{\texttt{AGE\_14\_TO\_17}, \texttt{AGE\_18\_PLUS}\} \\
\text{PERMITTED}, & \text{if } \hat{y}_{\text{pred}} = \texttt{SAFE\_18\_PLUS} \land \hat{g}_{\text{user}} = \texttt{AGE\_18\_PLUS} \\
\text{BLOCKED}, & \text{otherwise}
\end{cases}
\end{equation}

Under this dispatching rule, any advertisement classified as \texttt{UNSAFE\_FOR\_ALL} or routed to \texttt{REQUIRES\_HUMAN\_REVIEW} is universally blocked from publication across all publisher channels. Furthermore, minors are protected by design: an adult-restricted ad (\texttt{SAFE\_18\_PLUS}) is strictly suppressed from users in the \texttt{UNDER\_14} and \texttt{AGE\_14\_TO\_17} tiers.

\section{The Four-Tier Content Policy Taxonomy: Comprehensive Statutory \& Policy Defense}

Unlike generic computer vision research benchmarks that frame content moderation as a binary task (``toxic'' vs ``benign''), SafeAd AI establishes a four-tier content policy taxonomy directly aligned with international consumer protection statutes, age-rating frameworks, and digital advertising standards.

\begin{figure}[H]
    \centering
    \IfFileExists{policy_hierarchy.png}{\includegraphics[width=0.96\textwidth]{policy_hierarchy.png}}{%
        \IfFileExists{overleaf_figures/policy_hierarchy.png}{\includegraphics[width=0.96\textwidth]{overleaf_figures/policy_hierarchy.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{SafeAd AI Four-Tier Regulatory Policy Hierarchy}}}}%
    }
    \caption{The SafeAd AI Four-Tier Content Policy Taxonomy, Statutory Grounding, and Enforcement Escalation Flow.}
    \label{fig:policy_hierarchy}
\end{figure}

The four tiers are defined and defended in detail in the following subsections.

\subsection{Category 1: \texttt{SAFE\_FOR\_ALL} (Universal Commercial Audiences)}

\subsubsection{Operational Definition}
\texttt{SAFE\_FOR\_ALL} encompasses ordinary commercial advertising promoting general merchandise, services, brand awareness, or civic messaging that contains no age-restricted goods, no sexually suggestive imagery, no violence, no regulated stimulants, and no deceptive marketing claims. Advertisements in this category are deemed appropriate for unrestricted public broadcast across all demographic groups, including unaccompanied young children (<14 years of age).

\subsubsection{Commercial Scope and Product Verticals}
Permitted verticals include:
\begin{itemize}
    \item Everyday consumer apparel, footwear, athletic accessories, and domestic textiles.
    \item Consumer electronics, home appliances, smartphones, computing peripherals, and office supplies.
    \item Family grocery merchandise, non-alcoholic beverages, culinary goods, and organic produce.
    \item Educational software, academic learning platforms, primary and secondary school supplies.
    \item Family dining, hospitality, public transportation, and civic utility services.
\end{itemize}

\subsubsection{Statutory and Industry Alignment}
The definition of \texttt{SAFE\_FOR\_ALL} is grounded in authoritative regulatory sources:
\begin{enumerate}
    \item \textbf{Google Ads Editorial \& Professional Standards:} Creatives must be family-safe, clear, professional, and suitable for general display networks. Creatives cannot depict sexualized poses, gore, or shocking themes~\cite{googleadspolicy}.
    \item \textbf{International Age Rating Coalition (IARC):} Corresponds to rating categories \texttt{General} / \texttt{Everyone} (ESRB \emph{Everyone}; PEGI 3/7). The content contains no material requiring parental intervention~\cite{iarcratings}.
    \item \textbf{Meta Advertising Standards:} Conforms to unrestricted community guidelines, requiring authentic representations and respectful imagery~\cite{metaads}.
    \item \textbf{FTC Truth in Advertising Standards (16 CFR Part 255):} All commercial representations must be substantiated, clear, and non-deceptive~\cite{ftc2023guides}.
\end{enumerate}

\subsubsection{Forensic Test Case Walkthrough and Scoring Trace}
To evaluate the operational behavior of the \texttt{SAFE\_FOR\_ALL} policy specification, the pipeline processes commercial media assets such as organic grocery promotions and introductory software programming courses (\texttt{apples\_ad.jpg} and \texttt{safe\_python\_ad.jpg}).

\paragraph{Detector Response and Decision Trace:}
When evaluated through the SafeAd AI extraction pipeline:
\begin{itemize}
    \item \textbf{OCR Stream:} In \texttt{apples\_ad.jpg}, EasyOCR extracts the strings \texttt{"Fresh Honeycrisp Apples \$1.99/lb"} and \texttt{"Locally Sourced Organic Produce"}. Saliency scoring yields zero matches across prohibited hazard dictionaries ($S_{\text{ocr}} = 0.01$).
    \item \textbf{Visual Stream:} ResNet50 and Falcon NSFW ViT extract features representing natural fruit and domestic produce. Adult probability is negligible ($S_{\text{nsfw}} = 0.01$), weapon probability is zero ($S_{\text{visual}} = 0.00$), and optical flow is static ($S_{\text{violence}} = 0.00$).
    \item \textbf{Composite Risk Calculation:}
    \begin{equation}
    S_w = 100 \cdot (0.25 \cdot 0.01 + 0.20 \cdot 0.01 + 0.20 \cdot 0.00 + 0.15 \cdot 0.00 + 0.10 \cdot 0.00 + 0.10 \cdot 0.01) = 0.55
    \end{equation}
    \item \textbf{Final Policy Verdict:} Because $S_{\text{risk}} = 0.55 < 25.0$ and no restricted evidence is detected, the asset is decisively assigned to \texttt{SAFE\_FOR\_ALL}. It is cleared for unrestricted programmatic delivery to all viewers.
\end{itemize}

\subsection{Category 2: \texttt{SAFE\_14\_PLUS} (Adolescent Tier --- Project-Defined Engineering Boundary)}

\subsubsection{Operational Definition}
\texttt{SAFE\_14\_PLUS} designates advertisements promoting commercial goods, entertainment media, or lifestyle products that are permissible for adolescents and mature audiences (ages 14 and older) but are inappropriate for unaccompanied young children (<14 years). This tier covers themes with mild sensory intensity, high caffeine stimulants, stylized martial arts action, competitive gaming, and adolescent skincare.

\subsubsection{Critical Academic and Statutory Disclosure}
\begin{quote}
\textbf{Essential Academic Caveat:} It is vital to state explicitly that \textbf{14+ is a project-defined engineering threshold}. There is no single universal international statutory treaty that codifies ``14+'' as an immutable advertising standard. 

In SafeAd AI, 14+ is established as a defensible, principled engineering boundary bridging child-protective statutory regulations and lawful adult commerce. This boundary is harmonized with two distinct regulatory pillars:
\begin{enumerate}
    \item \emph{Child Privacy and Protection Thresholds:} The United States FTC Children's Online Privacy Protection Act (COPPA, 15 U.S.C. \S \S  6501--6506) defines a ``child'' as an individual under the age of 13, prohibiting automated tracking and behavioral profiling for children under 13 without verifiable parental consent~\cite{ftc2023guides}. Similarly, the Indian Digital Personal Data Protection (DPDP) Act establishes strict consent and advertising restrictions for minors. A 14+ boundary provides a robust safety margin protecting pre-adolescent children from commercial exploitation.
    \item \emph{Adolescent Media Rating Standards:} Global digital rating systems establish intermediate adolescent rating bands: ESRB \emph{Teen} (13+), PEGI 12/16, and BBFC 12A. These descriptors permit mild crude humor, stylized violence, and mild suggestive themes that are unsuitable for primary school children.
\end{enumerate}
\end{quote}

\subsubsection{Commercial Scope and Product Verticals}
Permitted verticals under \texttt{SAFE\_14\_PLUS} include:
\begin{itemize}
    \item Highly caffeinated beverages, performance energy drinks (>150 mg caffeine per serving), and pre-workout nutritional supplements.
    \item Adolescent dermatological and cosmetic treatments (e.g., active salicylic acid, benzoyl peroxide blemish treatments).
    \item Competitive esports equipment, stylized fantasy/martial arts video games, anime action media, and athletic combat sports (lacrosse, amateur wrestling).
    \item Teen fashion apparel, footwear, and youth lifestyle accessories.
\end{itemize}
\emph{Strict Prohibitions:} Content in \texttt{SAFE\_14\_PLUS} must strictly contain zero alcohol, zero tobacco/vaping, zero casino gambling, zero explicit nudity, zero lethal weapons, and zero financial schemes.

\subsubsection{Statutory and Industry Alignment}
\begin{enumerate}
    \item \textbf{UK Advertising Standards Authority (ASA) \& CAP Code:} Rule 15.18 strictly regulates high-caffeine energy drinks, mandating that advertisements must not be targeted at or feature children under 16~\cite{ftc2023guides}.
    \item \textbf{IARC / ESRB Teen (13+) \& PEGI 12 Content Descriptors:} Content may contain violence, suggestive themes, crude humor, and minimal blood, but no mature sexual content or severe gore~\cite{iarcratings}.
\end{enumerate}

\subsubsection{Forensic Test Case Walkthrough and Scoring Trace}
To evaluate adolescent boundary arbitration, the pipeline assesses commercial items such as competitive action athletics paired with high-caffeine energy drink branding (\texttt{SAFEAD\_S14P\_IMG\_050} and \texttt{violence\_combat\_ad.jpg}).

\paragraph{Detector Response and Decision Trace:}
In evaluating sample \texttt{SAFEAD\_S14P\_IMG\_050} (Lacrosse athletic gear and energy drink):
\begin{itemize}
    \item \textbf{OCR Stream:} OCR extracts text \texttt{"Titanium Attack Shaft - High Impact Power - Max Energy"}. Mild aggressive sporting rhetoric triggers sensory keyword rules ($S_{\text{ocr}} = 0.22$).
    \item \textbf{Visual Stream:} ResNet50 detects high-contrast sporting action, with zero weapons and zero adult nudity ($S_{\text{nsfw}} = 0.05, S_{\text{visual}} = 0.15$). Optical motion score is moderate ($S_{\text{violence}} = 0.28$).
    \item \textbf{Composite Risk Calculation:}
    \begin{equation}
    S_w = 100 \cdot (0.25 \cdot 0.05 + 0.20 \cdot 0.22 + 0.20 \cdot 0.28 + 0.15 \cdot 0.15 + 0.10 \cdot 0.00 + 0.10 \cdot 0.12) = 14.70
    \end{equation}
    \item \textbf{Policy Engine Decision:} Because the creative contains adolescent-targeted competitive themes, the Stage~2 policy engine evaluates youth criteria: while $S_w < 25$, the sensory athletic intensity and teen targeting rules map the ad to \texttt{SAFE\_14\_PLUS}. It is cleared for delivery to teenagers (14--17) and adults (18+), but suppressed from child feeds (<14).
\end{itemize}

\subsection{Category 3: \texttt{SAFE\_18\_PLUS} (Lawful Adult-Restricted Commercial Goods)}

\subsubsection{Operational Definition}
\texttt{SAFE\_18\_PLUS} designates legitimate, lawful commercial advertising for products or services that are legally restricted to adult consumers (age 18 and older) by statute or platform policy. These products are lawful to manufacture and market, but mandatory statutory regulations prohibit their display to minors. Delivery of an 18+ ad to a minor constitutes a severe regulatory and legal violation.

\subsubsection{Commercial Scope and Product Verticals}
Permitted verticals under \texttt{SAFE\_18\_PLUS} include:
\begin{itemize}
    \item Alcoholic beverages: beer, wine, distilled spirits, brewery hospitality, and pub dining.
    \item Licensed casino gaming, state lotteries, sports wagering, and online betting exchanges.
    \item Adult dating platforms, romantic matchmaking services, and mature social applications.
    \item Adult wellness products, intimate apparel, swimwear, and mature romantic fiction.
    \item Mature cinematic entertainment (R-rated movies, mature video games rated PEGI 18 / ESRB M).
\end{itemize}
\emph{Strict Prohibitions:} Content in \texttt{SAFE\_18\_PLUS} must never depict minors consuming alcohol or gambling, must not depict non-consensual sexual violence, and must not promote illegal narcotics or untaxed tobacco.

\subsubsection{Statutory and Industry Alignment}
\begin{enumerate}
    \item \textbf{Google Ads Alcohol Policy:} Mandatory geographic and age gating. Advertisements must not target individuals below the legal drinking age and must not imply that alcohol consumption enhances sexual, social, or athletic performance~\cite{googlealcohol}.
    \item \textbf{Meta Advertising Standards --- Restricted Goods \& Services:} Enforces strict 18+ audience gating for alcohol, online gaming/gambling, cosmetic surgery, and adult health products~\cite{metaads}.
    \item \textbf{IARC Mature (17+/18+) \& PEGI 18 Standards:} Classifies content containing explicit mature themes, intense violence, and adult commercial products~\cite{iarcratings}.
\end{enumerate}

\subsubsection{Forensic Test Case Walkthrough and Scoring Trace}
To analyze mature commercial gating, the framework evaluates licensed craft brewery promotions and consensual matchmaking advertisements (\texttt{beer\_pub.jpg} and \texttt{adult\_dating.jpg}).

\paragraph{Detector Response and Decision Trace:}
In evaluating \texttt{beer\_pub.jpg}:
\begin{itemize}
    \item \textbf{OCR Stream:} EasyOCR extracts the brand and copy: \texttt{"Craft Pale Ale - 5.4\% ABV - Served Cold at The Old Oak Pub"}. The alcohol keyword analyzer detects \texttt{"Ale"} and \texttt{"ABV"}, setting the explicit adult commercial indicator $M_{\text{explicit}} = 0.85$.
    \item \textbf{Visual Stream:} MobileNetV3 visual head detects beer glassware, bottles, and a bar environment ($S_{\text{visual}} = 0.35$). The Falcon NSFW classifier detects modest adult dining atmosphere ($S_{\text{nsfw}} = 0.15$). Violence is zero ($S_{\text{violence}} = 0.00$).
    \item \textbf{Policy Override Formulation:}
    Although the linear composite risk score $S_w \approx 26.25$ falls in the numerical teen range, the piecewise transformation rule evaluates:
    \begin{equation}
    Q = \max(N, M_{\text{explicit}}, O_{\text{adult}}, A_{\text{adult}}) = \max(0.15, 0.85, 0.80, 0.00) = 0.85
    \end{equation}
    Because $Q \ge 0.25$, Equation~\ref{eq:safeadpiecewise} elevates the score:
    \begin{equation}
    S_{\text{risk}} = \min(65.0, \max(S_w, 70 \cdot 0.85)) = \min(65.0, 59.50) = 59.50
    \end{equation}
    \item \textbf{Final Policy Verdict:} Because adult evidence $Q = 0.85 \ge 0.35$ and the product promotes regulated alcoholic beverages, the Stage~2 policy engine assigns \texttt{SAFE\_18\_PLUS}. Delivery is strictly restricted to verified adults who successfully pass ArcFace biometric verification.
\end{itemize}

\subsection{Category 4: \texttt{UNSAFE\_FOR\_ALL} (Universally Prohibited Hazards \& Scams)}

\subsubsection{Operational Definition}
\texttt{UNSAFE\_FOR\_ALL} designates advertisements containing universally unlawful, deceptive, fraudulent, predatory, or severe safety hazards that are prohibited from publication on digital platforms regardless of the viewer's age. These assets violate criminal statutes, consumer protection laws, or fundamental safety ethics. They are subject to immediate pre-publication rejection and permanent blocking across all delivery channels.

\subsubsection{Commercial Scope and Prohibited Violations}
Content triggering \texttt{UNSAFE\_FOR\_ALL} includes:
\begin{itemize}
    \item Financial fraud: cryptocurrency pump-and-dump schemes, Ponzi operations, fake binary options, phishing forms, and deceptive ``guaranteed daily return'' scams.
    \item Graphic violence: real-world physical combat, severe gore, decapitation, torture, and violent extremism.
    \item Child sexual exploitation and abuse material (CSAM) or predatory child targeting (absolute zero-tolerance ban).
    \item Illicit weapons, non-conventional CBRN devices, explosive blueprints, and unapproved narcotics/substances.
    \item Hate speech, dehumanizing racial/religious slurs, and malicious impersonation of public figures.
\end{itemize}

\subsubsection{Statutory and Industry Alignment}
\begin{enumerate}
    \item \textbf{Federal Trade Commission (FTC) Act Section 5(a) (15 U.S.C. \S  45):} Absolute prohibition of unfair or deceptive practices. Representations likely to mislead reasonable consumers regarding financial earnings or medical cures are illegal per se~\cite{ftcdeception}.
    \item \textbf{Google Ads Policies --- Prohibited Content \& Dishonest Behavior:} Zero-tolerance permanent bans on counterfeit goods, dangerous products/services, enabling dishonest behavior, and hateful content~\cite{googleadspolicy}.
    \item \textbf{Meta Advertising Standards --- Unacceptable Content:} Absolute prohibition of predatory fraud, weapon sales, malware, and exploitative material~\cite{metaads}.
    \item \textbf{NIST AI Risk Management Framework (NIST AI 100-1):} Mandates explicit harm mitigation and trustworthy risk containment across automated platforms~\cite{nistairmf2023}.
    \item \textbf{ISO 31000:2018 (Clause 5.4 Risk Treatment):} Enforces zero-tolerance risk avoidance protocols for catastrophic legal liability hazards~\cite{iso31000}.
\end{enumerate}

\subsubsection{Forensic Test Case Walkthrough and Scoring Trace}
To analyze pre-publication threat interception, the framework processes fraudulent marketing samples including predatory lottery schemes and high-yield Ponzi operations (\texttt{lucky\_draw.jpg} and \texttt{scam\_paisa\_double\_ad.jpg}).

\paragraph{Detector Response and Decision Trace:}
In evaluating \texttt{scam\_paisa\_double\_ad.jpg}:
\begin{itemize}
    \item \textbf{OCR Stream:} EasyOCR extracts high-risk financial fraud promises: \texttt{"Deposit \$500 - Get \$1000 Within 24 Hours Guaranteed - 100\% Risk Free Payout"}. The deceptive claim analyzer matches the phrase against FTC fraud dictionaries, triggering maximum scam risk ($M_{\text{scam}} = 0.95, M_{\text{deception}} = 0.90, O_{\text{scam}} = 0.92$).
    \item \textbf{Visual Stream:} Static imagery displays currency bundles and forged luxury signifiers ($S_{\text{visual}} = 0.40, S_{\text{nsfw}} = 0.10$).
    \item \textbf{Stage 1 Zero-Tolerance Evaluation:}
    The prohibited aggregator computes:
    \begin{equation}
    P = 100 \cdot \max(D, M_{\text{scam}}, M_{\text{deception}}, O_{\text{scam}}, A_{\text{scam}}) = 100 \cdot \max(0.0, 0.95, 0.90, 0.92, 0.0) = 95.0
    \end{equation}
    Because $P = 95.0 \ge 50.0$, the emergency escalation rule triggers:
    \begin{equation}
    S_{\text{risk}} = \min(100.0, \max(S_w, 95.0)) = 95.0
    \end{equation}
    \item \textbf{Final Policy Verdict:} Stage~1 intercepts the campaign: because $M_{\text{scam}} \ge 0.50$ and $S_{\text{risk}} \ge 75.0$, the ad is immediately flagged as \texttt{UNSAFE\_FOR\_ALL}. It is completely rejected from publication, and its hash is logged to the persistent compliance audit database.
\end{itemize}

\section{Disconnection Between Statutory Policies and Heuristic Scoring Formulations}

A critical scientific distinction defended in this report is the operational decoupling between qualitative statutory policies and empirical numerical risk scores:
\begin{quote}
\textbf{Crucial Academic Caveat:} No statutory international standard (neither FTC, IARC, NIST, nor ISO) prescribes SafeAd AI's specific linear weights ($0.25, 0.20, 0.20, 0.15, 0.10, 0.10$) or exact numerical cut-offs ($25.0, 55.0, 75.0$). 

The four categories are \textbf{grounded in statutory law, child welfare ethics, and platform advertising regulations}. Conversely, the numerical weighting equations and threshold bands are \textbf{development-calibrated engineering heuristics}. Conflating statutory policy legitimacy with empirical threshold numbers is scientifically invalid. SafeAd AI employs multi-stage hierarchical safety gates precisely to ensure that statutory safety vetoes supersede heuristic averages.
\end{quote}
"""
