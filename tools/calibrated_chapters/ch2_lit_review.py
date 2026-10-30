import sys

def get_chapter2():
    return r"""
\chapter{Literature Review}
\label{ch:lit_review}

\section{Evolution of Digital Content Moderation Architectures}
Automated digital content moderation has evolved through three distinct technological paradigms over the past two decades. The earliest architectures relied heavily on rule-based keyword blacklists, regular expression pattern matching, and visual perceptual hashing algorithms such as PhotoDNA and perceptual hashing (pHash)~\cite{kiela2020hateful}. While computationally lightweight and deterministic, these systems suffered from extreme fragility. Malicious users easily evaded text filters through leetspeak substitutions, zero-width spaces, and phonetic transliterations, while simple image affine transformations, cropping, and color jittering defeated perceptual hashing techniques.

The second paradigm emerged with deep convolutional neural networks (CNNs) and transformer-based language representations. Models such as ResNet, EfficientNet, and BERT enabled semantic classification of text toxicity and visual obscenity~\cite{devlin2018bert}. Specialized vision models, including Falcon NSFW ViT, introduced fine-grained classification of sexually explicit imagery. Similarly, temporal video architectures such as VideoMAE~\cite{tong2022videomae} enabled the detection of violent combat and kinetic anomalies across consecutive video frames. Despite their high accuracy on isolated tasks, these models operated within unimodal silos, rendering them blind to cross-modal relationships.

The third paradigm centers on multimodal foundation models. Systems like CLIP~\cite{radford2021learning} demonstrated the power of contrastive visual-language pre-training for zero-shot classification. However, standard foundation models are trained on general internet distributions and frequently fail to interpret domain-specific commercial advertising policies, deceptive marketing claims, or fine-grained statutory age restrictions.

\section{Implicit Semantics and Cross-Modal Concealment}
A major vulnerability in automated trust and safety systems is implicit semantics, including sarcasm, double entendre, and cross-modal discordance. The Facebook Hateful Memes Benchmark introduced by Kiela et al.~\cite{kiela2020hateful} empirically established that unimodal state-of-the-art architectures degrade significantly when evaluating multimodal assets where neither image nor text is harmful independently, but their juxtaposition forms a policy violation.

In digital advertising, adversarial creators employ analogous techniques to bypass pre-publication review. An advertisement promoting unauthorized pharmaceutical supplements may display an image of wholesome agricultural produce while embedding deceptive health claims entirely within the audio narration. Conversely, an advertisement for adult dating services may pair clean stock photography with sexually suggestive double entendres in the on-screen typography. Resolving such cross-modal concealment requires joint semantic fusion mechanisms capable of cross-referencing acoustic, visual, and typographic features simultaneously~\cite{sharma2022survey}.

\section{Policy-Aligned Commercial Advertisement Moderation}
While generic content moderation focuses on extreme harms such as terrorism and hate speech, commercial advertisement moderation operates under highly nuanced statutory standards. Organizations such as the Federal Trade Commission (FTC) in the United States and the Advertising Standards Council of India (ASCI) enforce strict guidelines governing truth in advertising, substantiation of commercial claims, conspicuous disclosure of disclaimers, and restriction of age-sensitive goods~\cite{ftc2020guides, asci2021code}.

Automated systems must therefore evaluate legal and commercial dimensions beyond vulgarity. Commercial deception detection requires cross-referencing extracted OCR claims against recognized fraud patterns. In video advertising, temporal dynamics play a crucial role. Studies by Hussein et al.~\cite{hussein2020multimodal} demonstrate that video moderation must incorporate keyframe extraction algorithms capable of capturing rapid visual transitions without incurring the computational overhead of decoding every frame.

\section{Vision-Language Foundation Models and Safety Guardrails}
The advent of autoregressive Vision-Language Models (VLMs), such as Llama Guard 3 Vision~\cite{metallama2024} and Qwen-VL~\cite{bai2023qwen}, has opened new frontiers for automated policy enforcement. Llama Guard 3 Vision was introduced specifically as an open-weights safety guardrail designed to identify safety violations across standardized taxonomy categories.

However, empirical investigations reveal critical domain limitations when generic safety VLMs are applied directly to commercial advertising moderation. Because safety guardrails are fine-tuned on extreme web safety benchmarks, they suffer from severe commercial concept blindness. They lack the granular taxonomy required to differentiate between benign consumer products, restricted adult commerce (such as alcohol, casino gambling, or adult dating), and deceptive financial frauds. Adapting VLMs for commercial trust and safety requires structured prompt engineering, policy-aligned chain-of-thought elicitation, and integration with specialized downstream discriminative detectors.

\section{Multimodal Fusion Paradigms: Early, Late, and Intermediate}
In multimodal machine learning, the fusion paradigm dictates how representations from disparate modalities are combined:
\begin{itemize}
    \item \textbf{Early Fusion (Feature-Level):} Raw sensory features or low-level embedding vectors are concatenated into a single joint vector prior to classification. While early fusion captures low-level cross-modal correlations, it suffers from the curse of dimensionality and is highly vulnerable to missing modalities.
    \item \textbf{Intermediate Fusion (Cross-Attention):} Modalities interact through intermediate cross-attention layers. While expressive, cross-attention networks demand massive paired training corpora and substantial computational resources.
    \item \textbf{Late Fusion (Decision-Level):} Specialized unimodal models generate independent posterior probability distributions, which are subsequently combined via learned meta-classifiers or heuristic policy rules~\cite{gadzicki2020review}.
\end{itemize}

Late fusion provides superior resilience in production advertising networks. It allows modular replacement of individual detector components, operates gracefully when specific media streams are absent, and supports deterministic hierarchical override rules (such as zero-tolerance safety vetoes).

\section{Biometrics and Presentation Attack Detection (PAD)}
Enforcing age-aware advertising policies necessitates verifiable client-side demographic assurance. Machine learning approaches to demographic assurance leverage facial analysis, wherein deep feature extractors estimate chronological age brackets from facial morphology~\cite{rothe2018dex}. To provide statutory compliance, modern systems implement hybrid identity verification, wherein facial embeddings extracted via deep metric learning (e.g., ArcFace~\cite{deng2019arcface}) are compared against digitized national identity documents.

Any biometric verification system deployed on consumer webcams is susceptible to Presentation Attacks (print attacks and screen replays)~\cite{yu2020nasfas}. Standard 2D Presentation Attack Detection architectures utilize lightweight convolutional networks, such as MiniFASNet~\cite{zhang2020minifasnet}, trained on multi-scale spatial features. In addition, digital screens display periodic pixel grids that generate high-frequency moir\'{e} interference patterns under camera re-capture. Applying 2D Fast Fourier Transforms (FFT) enables real-time isolation of artificial high-frequency energy spikes indicative of screen replay spoofing.

\section{Comparative Literature Summary and Research Gaps}
Table~\ref{tab:lit_comparison} provides a comparative summary of existing content moderation and biometric verification architectures.

\begin{table}[htbp]
\centering
\caption{Comprehensive Comparison of Content Moderation and Safety Architectures}
\label{tab:lit_comparison}
\scriptsize
\begin{tabular}{@{}p{2.6cm}p{1.0cm}p{2.6cm}p{2.6cm}p{5.5cm}@{}}
\toprule
\textbf{Study / Architecture} & \textbf{Year} & \textbf{Target Domain} & \textbf{Modalities} & \textbf{Key Capabilities and Critical Gaps} \\
\midrule
Kiela et al.~\cite{kiela2020hateful} & 2020 & Social Memes & Image + Text & Introduced Hateful Memes Benchmark; lacks audio, video kinetics, and ad policies. \\
Tong et al.~\cite{tong2022videomae} & 2022 & Action Recognition & Video & Self-supervised video pre-training; computationally intensive, no audio/text integration. \\
Falcon NSFW ViT~\cite{falcon2023nsfw} & 2023 & Visual Safety & Image & High-precision adult imagery detection; binary output, completely blind to text/audio context. \\
Meta Llama Guard 3~\cite{metallama2024} & 2024 & LLM Safety & Image + Text & Open safety guardrail; suffers $80\%$ failure on commercial ad fraud and adult retail. \\
Bai et al. (Qwen-VL)~\cite{bai2023qwen} & 2023 & Multimodal VLM & Image + Text & Strong visual reasoning; requires policy prompt alignment and safety veto wrappers. \\
Deng et al. (ArcFace)~\cite{deng2019arcface} & 2019 & Face Recognition & Facial Images & Angular margin loss for face matching; requires companion PAD to prevent replay spoofing. \\
Zhang et al. (MiniFASNet)~\cite{zhang2020minifasnet} & 2020 & Face Anti-Spoofing & Video Streams & Lightweight mobile PAD network; vulnerable to high-definition screen replays without FFT analysis. \\
\bottomrule
\end{tabular}
\end{table}

This review reveals five critical research gaps: (1) unimodal evaluation blindness, (2) commercial concept blindness of generic foundation models, (3) decoupling of content safety from viewer demographics, (4) vulnerability to replay presentation attacks, and (5) lack of explainable, tamper-evident audit trails. SafeAd AI is engineered specifically to bridge these five gaps.
"""
