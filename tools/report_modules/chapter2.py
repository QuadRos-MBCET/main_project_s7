import sys

def get_content():
    return r"""
% ============================================================
% CHAPTER 2: LITERATURE REVIEW
% ============================================================

\chapter{Literature Review}

\section{Evolution of Digital Content Moderation Architectures}

The governance of digital communications has evolved through distinct technological epochs. In the early architectural paradigms of Web 2.0 (circa 2005--2015), social platforms and programmatic advertising networks operated almost exclusively under a reactive moderation model~\cite{gillespie2018custodians,roberts2019behind}. Platforms functioned as passive hosting intermediaries, protected under statutory safe-harbor provisions such as Section 230 of the United States Communications Decency Act and the European Union E-Commerce Directive. Under reactive governance, moderation actions were triggered only after public exposure: user reports, platform flagging queues, or law enforcement notices initiated manual review by commercial content moderators~\cite{roberts2019behind}.

While reactive moderation demonstrated operational viability for low-velocity peer-to-peer textual interactions, empirical studies have proven that it fails catastrophically when applied to high-velocity commercial advertising exchanges~\cite{silva2020pre,zannettou2021characterizing}. Zannettou et~al.~\cite{zannettou2021characterizing} conducted a large-scale empirical audit of deceptive and fraudulent advertisements across major programmatic networks, revealing that malicious actors deliberately exploit the latency between creative submission and user reporting. In programmatic ad networks, an automated Real-Time Bidding (RTB) engine can disseminate millions of creative impressions within the first 60 minutes of campaign launch. By the time reactive user reports accumulate to trigger human moderator intervention, the fraudulent or harmful campaign has already extracted its financial return or delivered maximum psychological exposure to vulnerable viewers.

Consequently, research and industrial practice have pivoted decisively toward \emph{proactive, pre-publication gatekeeping}~\cite{blmguard2026,silva2020pre}. In a proactive pipeline, every advertising asset submitted by a media buyer is intercepted at the ingestion boundary and subjected to automated multimodal inspection prior to programmatic auctioning and CDN deployment. However, pre-publication auditing imposes severe engineering constraints: the verification pipeline must complete inspection within stringent latency budgets while sustaining high precision and recall across complex multimodal media.

\section{Implicit Semantics and Cross-Modal Concealment}

A primary technical barrier in automated advertisement moderation is the phenomenon of cross-modal concealment and implicit semantics. In digital communication, meaning is rarely confined to a single sensory channel. Adversarial actors exploit this by distributing policy-violating intent across multiple modalities, ensuring that no single channel triggers an isolated filter~\cite{wang2025,zhuang2025,kiela2020hateful}.

The foundational challenges of cross-modal semantics were formalized during the Facebook Hateful Memes Challenge organized by Kiela et~al.~\cite{kiela2020hateful}. The benchmark demonstrated that multimodal reasoning is inherently non-linear: an innocuous image (e.g., an animal sitting in an office) paired with an innocuous text caption (e.g., ``Look at this hard worker'') is benign, but pairing the same image with a derogatory historical trope creates an intensely harmful communicative act. Standard multimodal architectures that simply concatenate CNN visual vectors and BERT textual vectors fail because they cannot capture the non-linear semantic interference between the modalities~\cite{kiela2020hateful}.

Wang et~al.~\cite{wang2025} expanded this paradigm by examining memes and promotional media where harmful intent is mediated through implicit socio-cultural metaphors. The authors identify three governing factors in metaphorical multimodal communication: socio-cultural background knowledge, the metaphorical tenor, and the surface representation pattern. To interpret implicit semantics without expensive supervised retraining, Wang et~al. introduced a training-free framework comprising four interconnected modules: SCGen Search (using an LLM to generate targeted search queries and summarize external knowledge), SCRA-MTI (scoring socio-cultural relevance on a 0--2 scale), representative case retrieval, and chain-of-thought (CoT) prompting for multimodal LLMs. Evaluating their approach on the Facebook Hateful Memes (FHM), MAMI, and HarMeme benchmarks, the authors achieved an AUC/accuracy of 87.60/78.60 on FHM and 90.51/83.29 on HarMeme using GPT-4. Incorporating external socio-cultural knowledge elevated the AUC of Qwen-VL-Max by 11.3\%. However, this reasoning depth incurred substantial computational latency, raising average inference time from 3.0~s to 8.05~s per image. For SafeAd AI, this trade-off demonstrates that while external contextual grounding is essential for resolving implicit metaphors, pre-publication moderation engines must rely on frozen foundation models and cached knowledge to remain within high-throughput latency limits.

Zhuang et~al.~\cite{zhuang2025} investigated the structural failure modes of multimodal detectors on harmful internet content, identifying visual composition techniques (such as multi-panel collages and stitched sub-images) and subtle propaganda rhetoric as primary evasion vectors. In response, they proposed HMGuard, combining adaptive visual prompting with a seven-step chain-of-thought strategy (HMCoT) that progresses from domain alignment to compositional synthesis. HMGuard achieved 92\% accuracy and a 91\% F1-score on HarMeme, and 88\% accuracy on real-world test sets. This establishes that structured, multi-step prompt engineering enables vision-language models to deconstruct complex multimodal compositions effectively.

\section{Policy-Aligned Commercial Advertisement and Video Moderation}

While academic benchmarks like FHM and HarMeme focus predominantly on political hate speech and memes, commercial advertising moderation introduces distinct regulatory and structural complexities. Commercial ads are dynamic, persuasive, high-resolution multimedia productions governed by statutory consumer protection standards.

Yang et~al.~\cite{blmguard2026} addressed this domain directly with BLM-Guard, an explainable multimodal moderation framework designed specifically for short-video commercial advertisements. The authors constructed an extensive benchmark of real-world video ads annotated across seven regulatory risk scenarios (e.g., fraudulent claims, prohibited goods, unauthorized endorsements). BLM-Guard employs a two-stage training strategy: first, a vision-language model (Qwen2.5-VL-7B) is fine-tuned on interleaved chain-of-thought data derived from CLIP-selected keyframes and speech transcripts; second, the model is refined using Group Relative Policy Optimization (GRPO) with a hybrid reward combining rule correctness, structural formatting, and a critic-based self-consistency reward (SCA-R). BLM-Guard achieved 91.4\% strict accuracy and a 96.9\% F1-score on high-risk categories. However, a major architectural limitation of BLM-Guard is its complete exclusion of on-screen OCR typography. The authors explicitly omitted OCR tokens due to visual noise in short-form video overlays. In commercial advertising, however, deceptive claims and mandatory regulatory disclaimers are overwhelmingly embedded in on-screen typography. SafeAd AI directly rectifies this gap by preserving OCR as an active, enhanced evidence stream.

Chen et~al.~\cite{safewatch2025} proposed SafeWatch, an efficient safety-policy-following video guardrail model designed to enforce custom corporate and statutory content policies. SafeWatch introduced two architectural innovations: Parallel Equivalent Policy Encoding (PEPE), which eliminates positional token bias by encoding discrete policy clauses independently, and Policy-Aware Adaptive Pruning (PAP), which discards video tokens irrelevant to the queried policy to minimize compute overhead. Evaluated on the SafeWatch-Bench (spanning over two million video assets across 30 safety tasks), SafeWatch demonstrated superior zero-shot transferability to unseen policies (+5.6\%) and complex prompt tasks (+15.6\%). Both BLM-Guard and SafeWatch confirm the validity of conditioning vision-language models on explicit policy taxonomies. However, neither system addresses the connection between content moderation and viewer age eligibility.

\section{Vision-Language Foundation Models and Safety Guardrails}

The emergence of Foundation Vision-Language Models (VLMs) has transformed multimodal artificial intelligence. Prior to foundation VLMs, content moderation relied on task-specific models trained on static, closed-vocabulary label spaces (e.g., CNNs trained on ImageNet or toxic text classifiers trained on Jigsaw CivilComments)~\cite{devlin2019bert,he2016deep}. These models fail when confronted with out-of-vocabulary slang, novel deceptive marketing slogans, or unseen visual compositions.

Foundation VLMs bridge this chasm through large-scale contrastive pre-training and visual instruction tuning. Radford et~al.~\cite{radford2021learning} introduced CLIP (Contrastive Language-Image Pre-training), training dual image and text encoders on 400 million web-scraped pairs via symmetric InfoNCE loss. CLIP demonstrated remarkable zero-shot transfer across visual domains, but lacked fine-grained spatial grounding and generative reasoning. Liu et~al.~\cite{liu2023visual} introduced LLaVA (Visual Instruction Tuning), connecting a CLIP visual encoder to a LLaMA autoregressive language model via a simple linear projection layer. LLaVA proved that language models could follow complex visual instructions and generate open-ended semantic justifications.

Concurrently, the Qwen-VL family developed by Bai et~al.~\cite{bai2023qwen} set new benchmarks for open-source multimodal understanding. Qwen-VL incorporated a high-resolution visual receptor, position-aware vision-language adapter, and multilingual visual instruction tuning. Unlike standard VLMs that struggle with fine-grained text, Qwen-VL demonstrated outstanding capability in reading multilingual typography, resolving dense OCR text, and grounding visual objects with pixel-level bounding boxes. Subsequent iterations, including Qwen2.5-VL and \textbf{Qwen3-VL-8B-Instruct}, substantially expanded temporal video comprehension, visual-mathematical reasoning, and instruction adherence.

To enforce safety boundaries, researchers developed specialized safety guardrail models. Meta AI released Llama Guard~\cite{inan2023llama} and its multimodal successor, Llama Guard 3 Vision. Built upon the Llama-3-Vision backbone, Llama Guard 3 was instruction-tuned to classify multimodal inputs against the MLCommons standardized safety taxonomy (S1: Violent Crimes, S2: Non-Violent Crimes, S3: Sex-Related Crimes, S4: Child Exploitation, S5: Suicide/Self-Harm, S6: Cyberattacks, S7: CBRN Weapons).

\paragraph{Diagnostic Failure of Specialized Guardrails in Commercial Advertising:}
Despite its success in conversational dialogue moderation, our empirical investigations (Phase~9B) revealed that Llama Guard 3 Vision exhibits catastrophic failure when deployed on commercial advertisements. When evaluated on 16 authentic commercial advertising assets, Llama Guard 3 Vision failed to detect 4 out of 5 prohibited advertisements, producing an unacceptable 80\% Prohibited False Acceptance Rate. Root-cause analysis demonstrated two fatal failure mechanisms:
\begin{enumerate}
    \item \emph{Conversational Alignment Mismatch:} Llama Guard 3 was trained strictly on conversational user-agent dialogues (e.g., ``User asks how to make a bomb, Agent responds''). Commercial advertisements do not follow conversational dialogue structures; they employ persuasive slogans, brand metaphors, and commercial claims. The model consistently defaulted to clearing marketing rhetoric as benign commercial speech.
    \item \emph{Taxonomy and Semantic Confusion:} In video advertisements depicting violent military combat games, Llama Guard 3 returned hazard code \texttt{S12} (Sexual Content) instead of violence, caused by prompt parsing fragility and attention dispersion over commercial typography.
\end{enumerate}
These empirical findings conclusively proved that narrow conversational safety guardrails cannot generalize to commercial advertising, necessitating the adoption of high-capacity general foundation VLMs like Qwen3-VL-8B-Instruct.

\section{Explainability in Multimodal Content Safety}

In commercial advertising, automated moderation decisions carry significant economic consequences. A false rejection disrupts legitimate business commerce, while a false acceptance incurs legal penalties. Consequently, moderation systems cannot operate as opaque black boxes; they must satisfy statutory explainability and auditability standards.

Nwasra and Alharthy~\cite{nwasra2026} addressed explainable AI (XAI) for multimodal content moderation by extending a Vision-and-Language Transformer (ViLT). The authors implemented layer-wise attention aggregation and cross-modal relevance propagation, generating saliency heatmaps that visually identify which image patches and textual tokens triggered a classification. Evaluating their framework on the FHM benchmark, the model achieved 74.2\% accuracy and an AUC-ROC of 0.812. The authors evaluated explanation quality using perturbation-based faithfulness metrics (faithfulness score 0.234, Average Overlap Perturbation Curve [AOPC] 0.156) and human plausibility ratings (4.12/5). However, their findings highlighted that post-hoc gradient-based saliency methods frequently suffer from modest faithfulness, as pixel-level heatmaps do not articulate the underlying legal or policy rule that was violated.

In contrast, modern instruction-tuned VLMs (e.g., BLM-Guard~\cite{blmguard2026}, Qwen3-VL~\cite{bai2023qwen}) provide natural language explainability. By conditioning the generative decoder on formal policy clauses, the model produces chain-of-thought justifications and identifies explicit textual and visual evidence within structured JSON schemas, aligning directly with regulatory compliance requirements.

\section{Multimodal Fusion Paradigms: Early, Late, and Intermediate}

Multimodal machine learning architectures synthesize information across heterogeneous sensory channels. In a comprehensive survey, Baltru\v{s}aitis, Ahuja, and Morency~\cite{baltrusaitis2018multimodal} classified multimodal fusion into three primary paradigms:
\begin{enumerate}
    \item \textbf{Early Fusion (Feature-Level):} Raw feature representations from individual modalities (e.g., CNN spatial embeddings, TF-IDF vectors, audio spectrogram features) are concatenated into a single high-dimensional vector prior to classification. While early fusion allows models to capture low-level cross-modal correlations, it suffers from the curse of dimensionality, modality dominance (where dense visual vectors overpower sparse text signals), and vulnerability to missing modalities.
    \item \textbf{Late Fusion (Decision-Level):} Separate, unimodal neural models evaluate each channel independently to produce class probabilities or risk scores. These individual decisions are subsequently aggregated using fixed linear weighting, majority voting, or a secondary meta-classifier (e.g., Logistic Regression or Random Forest). Late fusion provides modularity, interpretability, and fault tolerance against missing channels.
    \item \textbf{Intermediate / Hybrid Fusion:} Modalities interact within intermediate layers through cross-attention mechanisms, cross-modal transformers, or joint tensor fusion.
\end{enumerate}

Arya et~al.~\cite{arya2024} implemented a hybrid fusion architecture (MSCMGTB) combining CNN visual features, Transformer textual features, bi-directional cross-attention, genetic algorithms for hyperparameter optimization, and Graph Neural Networks over social media posts. While achieving high benchmark accuracy (93.87--97.55\%), such complex hybrid architectures act as black-box systems with high computational latency, making them impractical for low-latency pre-publication screening.

In SafeAd AI, Phase~8E explored learned late fusion using Breiman's Random Forest algorithm~\cite{breiman2001random}. By extracting a 33-dimensional numerical feature representation from cached detector outputs, the Random Forest model learned non-linear decision boundaries that significantly outperformed fixed linear weights on development data.

\section{Age-Aware Demographic Classification and Minor Safety}

Protecting minor audiences from mature content requires reliable recipient demographic categorization.

Saraswat and Tripathi~\cite{saraswat2026} proposed a multimodal framework for estimating the age category of social media users (categorized as Young [<18], Adult [18--50], and Old [>50]). Their approach evaluated user profile images using a CNN paired with a Random Forest classifier, and vectorized profile description text using TF-IDF with an ensemble of Logistic Regression, Random Forest, and Bernoulli Naive Bayes. A platform-specific decision matrix resolved inter-modality disagreements, achieving 85\% image accuracy, 78\% text accuracy, and 90\% combined accuracy. However, a critical security vulnerability of their framework is its total reliance on user-manipulable profile metadata. Minors seeking access to restricted content routinely alter profile descriptions, while static profile pictures provide zero defense against identity impersonation.

Gopinath et~al.~\cite{safevision2026} developed SAFE VISION, a screen-monitoring content management system for child safety. The system captures desktop screen frames and camera feeds via OpenCV, evaluates motion energy via optical flow, calculates skin-color ratios in HSV color space, and scans for prohibited keywords via OCR. When predefined heuristic thresholds are breached, the system automatically locks the display. While demonstrating the utility of active client-side enforcement, the authors acknowledged that rigid heuristic thresholds suffer from extreme false-positive rates, frequently blocking legitimate medical, educational, or sports content. Furthermore, their architecture lacked biological age assurance.

\section{Face Presentation Attack Detection (PAD) and Biometrics}

Biometric age assurance and identity matching are fundamentally compromised if the verification pipeline cannot differentiate between a live human face and a presentation attack. In an authoritative survey, Yu et~al.~\cite{yu2023} reviewed deep learning methodologies for face presentation attack detection (PAD).

Presentation attacks fall into three primary threat categories:
\begin{itemize}
    \item \textbf{Print Attacks:} Presenting a high-resolution color photographic printout of an authorized individual's face (either flat or curved around a cylinder to simulate facial depth).
    \item \textbf{Screen Replay Attacks:} Replaying video footage of an authorized user on a high-definition mobile smartphone, tablet, or monitor display held before the camera.
    \item \textbf{3D Mask Attacks:} Wearing customized latex, silicone, or 3D-printed facial masks.
\end{itemize}

Yu et~al.~\cite{yu2023} noted that early handcrafted descriptors---such as Local Binary Patterns (LBP) and Histograms of Oriented Gradients (HOG)---have become entirely obsolete against modern 4K OLED and Retina displays. Contemporary deep PAD frameworks rely on convolutional neural networks trained with auxiliary supervision, such as pseudo-depth maps and binary mask regression. The authors highlighted the \textbf{MiniFASNet} architecture, an ultra-lightweight convolutional neural network utilizing depthwise separable convolutions and inverted residual blocks. MiniFASNet achieves state-of-the-art liveness classification while maintaining sub-10ms forward latency on standard CPU hardware.

Furthermore, Yu et~al. emphasized the necessity of multi-scale context. A tight facial crop captures micro-texture blur and skin pore degradation, but completely misses physical device bezels, user fingers, and room reflections. Conversely, a wide contextual crop captures device chassis boundaries and specular screen reflections. SafeAd AI directly operationalizes this insight by deploying a dual-scale MiniFASNet ensemble (\texttt{MiniFASNetV2} at 2.7$\times$ and \texttt{MiniFASNetV1SE} at 4.0$\times$) backed by geometric Hough line transforms and 2D FFT moir\'{e} spatial frequency analysis.

\paragraph{Hyperspherical Biometric Feature Discrimination (ArcFace vs. FaceNet):}
For cross-matching live video feeds against uploaded ID documents, early commercial pipelines utilized FaceNet~\cite{schroff2015facenet}, which trained Inception-ResNet backbones using triplet loss over Euclidean space. However, triplet loss suffers from high computational complexity and unstable convergence during large-scale training.

Deng et~al.~\cite{deng2019arcface} revolutionized deep face recognition by introducing \textbf{InsightFace ArcFace} (Additive Angular Margin Loss). Built upon an \texttt{iResNet50} backbone trained on MS1MV3 (5.1 million cleaned images, 93,000 identities), ArcFace adds an explicit angular margin $m$ directly in the cosine space on a normalized hypersphere. By enforcing:
\begin{equation}
L_{\text{ArcFace}} = -\log \frac{e^{s(\cos(\theta_{y_i} + m))}}{e^{s(\cos(\theta_{y_i} + m))} + \sum_{j \ne y_i} e^{s \cos \theta_j}}
\end{equation}
ArcFace maximizes intra-class compactness and inter-class discrepancy, producing 512-dimensional unit-normalized embeddings that yield extraordinary discriminative accuracy across severe variations in pose, illumination, and camera sensor quality.

\section{Statutory and Regulatory Advertising Standards}

Automated advertising moderation is uniquely subject to formal statutory codification across international legal jurisdictions:
\begin{enumerate}
    \item \textbf{Federal Trade Commission (FTC) Act (15 U.S.C. \S  45):} Section 5(a) establishes a universal prohibition against ``unfair or deceptive acts or practices in or affecting commerce.'' The FTC Policy Statement on Deception mandates that promotional representations or omissions likely to mislead a consumer acting reasonably under the circumstances constitute actionable legal violations~\cite{ftcdeception}. Commercial endorsements and health/financial claims require clear, conspicuous statutory disclosures (16 CFR Part 255)~\cite{ftc2023guides}.
    \item \textbf{Children's Online Privacy Protection Act (COPPA, 15 U.S.C. \S \S  6501--6506):} Establishes strict digital protections for children under age 13, prohibiting unauthorized profiling, behavioral ad targeting, and unverified commercial exploitation~\cite{ftc2023guides}.
    \item \textbf{International Age Rating Coalition (IARC):} Provides global, harmonized age classification criteria across digital platforms (ESRB in North America, PEGI in Europe, USK in Germany, ClassInd in Brazil). IARC establishes clear demarcation lines between general audience media (Everyone/PEGI 3), adolescent content (Teen 13+/PEGI 12), and mature content (Mature 17+/PEGI 18)~\cite{iarcratings}.
    \item \textbf{Commercial Platform Standards (Google Ads \& Meta Advertising Standards):} Google Ads policies strictly govern alcohol distribution, requiring affirmative geographic and age gating away from legal drinking age thresholds~\cite{googlealcohol}, while enforcing universal prohibitions on deceptive financial schemes, counterfeit products, and hate speech~\cite{googleadspolicy}. Meta's Advertising Standards enforce strict 18+ audience restrictions on online gambling, cosmetic surgery, and adult products~\cite{metaads}.
    \item \textbf{NIST Artificial Intelligence Risk Management Framework (AI RMF 1.0):} Published by the National Institute of Standards and Technology (NIST AI 100-1)~\cite{nistairmf2023}, this framework defines core requirements for trustworthy AI: validity, reliability, safety, security, accountability, transparency, and fairness.
    \item \textbf{ISO 31000:2018 (Risk Management --- Guidelines):} Provides international guidelines for risk identification, assessment, and treatment, serving as the architectural foundation for SafeAd AI's multi-stage risk escalation~\cite{iso31000}.
\end{enumerate}

\section{Comprehensive Comparative Literature Summary}

Table~\ref{tab:lit_comprehensive} synthesizes the reviewed literature across publication year, primary methodologies, performance metrics, key findings, and identified limitations.

\begin{table}[htbp]
\centering
\caption{Comprehensive Synthesis of Related Literature on Multimodal Safety, Moderation, and Biometrics}
\label{tab:lit_comprehensive}
\vspace*{3pt}
\scriptsize
\setlength{\tabcolsep}{2.0pt}
\renewcommand{\arraystretch}{1.25}

\begin{tabular}{|p{1.4cm}|c|p{3.2cm}|p{3.4cm}|p{4.2cm}|p{3.4cm}|}
\hline
\textbf{Study} & \textbf{Year} & \textbf{Core Methodology} & \textbf{Observed Performance} & \textbf{Primary Scientific Insight} & \textbf{Identified Gaps \& Limitations} \\ \hline

Wang et~al.~\cite{wang2025} & 2025 &
SCGen knowledge retrieval, SCRA-MTI relevance scoring, MLLM CoT &
FHM AUC 87.60, Acc 78.60; HarMeme AUC 90.51, Acc 83.29 &
External socio-cultural knowledge resolves implicit metaphors without supervised training. &
High latency (8.05~s/image) exceeds pre-publication ad auction budgets. \\ \hline

Yang et~al.~\cite{blmguard2026} & 2026 &
Qwen2.5-VL-7B, CLIP keyframes, GRPO with SCA-R reward &
Strict Acc 91.4\%; risky precision 97.6\%, recall 96.2\%, F1 96.9\% &
Policy-aligned VLM reasoning with critic rewards enables explainable ad moderation. &
Completely excludes on-screen OCR text; lacks audience age-tier gating. \\ \hline

Chen et~al.~\cite{safewatch2025} & 2025 &
Video guardrail, PEPE policy encoding, PAP token pruning (2M+ videos) &
Outperforms SOTA in zero-shot policy generalization (+5.6\%) &
Independent policy clause encoding eliminates token position bias in video guardrails. &
Focuses exclusively on video content; lacks recipient demographic validation. \\ \hline

Zhuang et~al.~\cite{zhuang2025} & 2025 &
HMGuard: adaptive prompting, 7-step HMCoT reasoning &
HarMeme Acc 92\%, F1 91\%; real-world Acc 88\%, F1 86\% &
Structured step-by-step composition reasoning improves multimodal meme detection. &
Evaluated strictly on static memes; does not handle temporal video or speech. \\ \hline

Bai et~al.~\cite{bai2023qwen} & 2023 &
Qwen-VL: high-res vision-language model, visual grounding &
State-of-the-art across DocVQA, OCR-VQA, multimodal captioning &
Large-scale visual instruction tuning resolves dense multilingual text and fine cues. &
Requires substantial GPU VRAM ($\ge 16$~GB) for native bfloat16 inference. \\ \hline

Inan et~al.~\cite{inan2023llama} & 2023 &
Llama Guard: LLM input-output safety guardrail (MLCommons) &
High precision on conversational dialogue safety benchmarks &
Instruction-tuned safety classifiers enforce discrete safety violation categories. &
Severe diagnostic failure on commercial ads ($80\%$ false-acceptance rate in Phase~9B). \\ \hline

Nwasra \& Alharthy~\cite{nwasra2026} & 2026 &
ViLT, layer-wise attention aggregation, relevance propagation &
FHM Acc 74.2\%, AUC 0.812; faithfulness 0.234; plausibility 4.12/5 &
Cross-modal relevance heatmaps provide transparent spatial visual explanations. &
Perturbation faithfulness remains modest (0.234); lacks policy categorization. \\ \hline

Arya et~al.~\cite{arya2024} & 2024 &
CNN, Transformer, bi-directional attention, genetic algorithms, GNN &
Accuracy 93.87--97.55\%; precision 86.78--98.82\% &
Complex hybrid cross-attention fusion improves accuracy over unimodal baselines. &
Black-box architecture; provides no explainability or age gating. \\ \hline

Saraswat \& Tripathi~\cite{saraswat2026} & 2026 &
CNN + Random Forest (images); TF-IDF + ensemble (text) &
Image 85\%, text 78\%, combined demographic accuracy 90\% &
Combining profile imagery and description text improves age-bracket estimation. &
Vulnerable to user deception; lacks biometric verification and liveness checks. \\ \hline

Gopinath et~al.~\cite{safevision2026} & 2026 &
OpenCV screen capture; optical flow, HSV skin, OCR thresholds &
Acc 93.5\%, sensitivity 94.8\%, specificity 92.2\% (200 samples) &
Client-side active screen blocking enforces child-protective content gating. &
Rigid heuristic thresholds cause over-blocking; biological age assurance missing. \\ \hline

Yu et~al.~\cite{yu2023} & 2023 &
Comprehensive survey of deep learning face anti-spoofing (PAD) &
Survey analysis across CASIA-FASD, Replay-Attack, OULU-NPU &
Deep convolutional ensembles outperform handcrafted descriptors against replays. &
Survey paper; does not deliver an integrated commercial moderation pipeline. \\ \hline

Deng et~al.~\cite{deng2019arcface} & 2019 &
ArcFace: Additive Angular Margin Loss on normalized hypersphere &
LFW 99.83\%, CFP-FP 98.37\%, AgeDB-30 98.15\% &
Angular margin directly optimizes geodesic distance, maximizing inter-class separation. &
Requires aligned facial crops via MTCNN/RetinaFace prior to embedding. \\ \hline

\end{tabular}
\end{table}

\section{Synthesis of Research Gaps}

The extensive review of academic literature and regulatory frameworks reveals four fundamental research gaps that motivate the architecture of SafeAd AI:
\begin{enumerate}
    \item \textbf{The Policy-Audience Disconnection:} Content moderation literature treats safety as an intrinsic, audience-independent property of media. Conversely, digital advertising law and child welfare ethics mandate that content suitability is fundamentally relational: an advertisement for single-malt whiskey is fully compliant when displayed to a 30-year-old adult, but constitutes a severe regulatory violation when displayed to an unaccompanied 12-year-old child. No existing framework bridges pre-publication moderation with verified demographic delivery.
    \item \textbf{Incomplete Multimodal Coverage:} Current state-of-the-art moderation models (e.g., BLM-Guard~\cite{blmguard2026}) omit on-screen typography, while meme-based systems (e.g., HMGuard~\cite{zhuang2025}) ignore temporal motion and speech. A complete advertising moderation framework must synthesize visual frames, on-screen OCR text, motion kinetics, and speech transcripts into a single unified assessment.
    \item \textbf{The Brittleness of Narrow Safety Guardrails:} Models trained exclusively on conversational dialogue (such as Llama Guard 3 Vision) fail on persuasive commercial advertising, exhibiting unacceptable false-acceptance rates ($80\%$) on real-world promotions. General-purpose foundation VLMs (e.g., Qwen3-VL) conditioned on explicit four-tier policies are mandatory.
    \item \textbf{The Tabular Fusion Illusion on Independent Test Data:} Systems combining specialized detectors through shallow tabular learners (e.g., Random Forests) frequently report high performance on cross-validated development splits, but suffer catastrophic generalization degradation when deployed against novel, held-out test distributions. A robust framework requires a frozen hierarchical safety architecture wherein foundation model vetoes prevent safety leakage.
\end{enumerate}
"""
