import sys

def get_chapter7():
    return r"""
\chapter{Conclusion and Future Scope}
\label{ch:conclusion}

\section{Summary of Findings and Key Contributions}
This research project presented \textbf{SafeAd AI (SAFE-VISION)}, an end-to-end multimodal trust and safety framework engineered specifically for pre-publication advertisement moderation and age-aware content dispatching. By moving beyond traditional unimodal and post-publication reactive approaches, SafeAd AI resolves critical security vulnerabilities in programmatic advertising exchanges.

The primary scientific and engineering contributions established by this project are:
\begin{enumerate}
    \item \textbf{A Four-Tier Statutory Policy Architecture:} Successfully formulated and operationalized a granular four-tier taxonomy (\texttt{SAFE\_FOR\_ALL}, \texttt{SAFE\_14\_PLUS}, \texttt{SAFE\_18\_PLUS}, and \texttt{UNSAFE\_FOR\_ALL}) that aligns automated classification directly with international advertising regulations (FTC Act Section 5, ASCI Code, COPPA, and EU DSA).
    \item \textbf{Empirical Demonstration of Commercial Blindness in Generic Safety VLMs:} Conducted the first systematic empirical safety audit demonstrating that generic open-weights safety guardrails (such as Meta's Llama Guard 3 Vision) fail on $80.0\%$ of commercial advertising cohorts due to commercial concept blindness.
    \item \textbf{Strategy D Hierarchical Safety Late Fusion:} Designed and validated a hierarchical arbitration protocol combining Qwen3-VL-8B-Instruct with a 16-dimensional Random Forest classifier. On an independent held-out test cohort of 27 samples evaluated on an NVIDIA A100 GPU without ground-truth leakage or rule post-tuning, the framework achieved $66.7\%$ four-class accuracy, eliminated all severe false acceptances ($0.0\%$), and achieved a flawless $100.0\%$ recall on strictly prohibited content.
    \item \textbf{Spoof-Resistant Biometric Demographic Dispatching:} Developed a synchronized client-side verification engine combining dual-scale MiniFASNet with 2D FFT moir\'{e} analysis for Presentation Attack Detection ($93.0\%$ replay attack accuracy) and ArcFace face verification ($96.50\%$ TAR at $0.1\%$ FAR), guaranteeing that age-restricted advertisements are inaccessible to minors.
    \item \textbf{Full-Stack Explainability and Compliance Auditability:} Deployed a complete web dashboard providing synchronized media playback, natural language policy rationales, and an immutable JSON audit log.
\end{enumerate}

\section{Lessons Learned Across Engineering Phases}
The multi-phase engineering progression of this project yielded vital technical insights:
\begin{itemize}
    \item \textbf{Limitations of Shallow Feature Fusion (Phase 8):} Relying solely on low-level statistical aggregates across neural detectors is insufficient for nuanced commercial categories like adolescent media (\texttt{SAFE\_14\_PLUS}), yielding an F1 score of only $0.2222$.
    \item \textbf{Necessity of Domain-Aligned Prompt Engineering (Phase 9--10):} Without explicit policy definitions and structured JSON output contracts, models either over-censor lawful commerce or overlook subtle financial scams.
    \item \textbf{The Independent Generalization Reality (Phase 10D):} Evaluating models exclusively on small development cohorts creates an illusion of perfection ($100\%$ accuracy in Phase 10C). Independent held-out evaluation ($66.7\%$ in Phase 10D) is indispensable for uncovering realistic boundary ambiguities.
\end{itemize}

\section{Future Research Roadmap}
Building upon the verified foundation of SafeAd AI, several promising research avenues emerge:
\begin{enumerate}
    \item \textbf{Multi-Lingual Advertising Moderation:} Extending Whisper ASR and typographic OCR models to support Indian regional languages (e.g., Malayalam, Hindi, Tamil) and colloquial code-switched dialects common in regional digital marketing.
    \item \textbf{Privacy-Preserving Federated Biometrics:} Implementing Zero-Knowledge Proofs (ZKPs) and client-side edge computing, allowing users to cryptographically prove age compliance without transmitting biometric face embeddings over the network.
    \item \textbf{Dense Spatio-Temporal Video Transformers:} Integrating lightweight 3D video transformers capable of performing full 60-fps temporal reasoning within sub-100~ms programmatic bidding windows.
    \item \textbf{Adversarial Generative Defense:} Developing automated red-teaming pipelines that generate synthetic adversarial ads to continuously harden the detector ensemble against future evasion techniques.
\end{enumerate}

% ============================================================
% REFERENCES (BIBLIOGRAPHY)
% ============================================================

\begin{thebibliography}{99}

\bibitem{kiela2020hateful}
D.~Kiela et~al.,
\newblock ``The hateful memes challenge: Detecting hate speech in multimodal memes,''
\newblock in \emph{NeurIPS}, vol.~33, pp.~2611--2624, 2020.

\bibitem{devlin2018bert}
J.~Devlin et~al.,
\newblock ``BERT: Pre-training of deep bidirectional transformers for language understanding,''
\newblock \emph{arXiv:1810.04805}, 2018.

\bibitem{tong2022videomae}
Z.~Tong et~al.,
\newblock ``VideoMAE: Masked autoencoders are data-efficient learners for self-supervised video pre-training,''
\newblock in \emph{NeurIPS}, vol.~35, pp.~10078--10093, 2022.

\bibitem{radford2021learning}
A.~Radford et~al.,
\newblock ``Learning transferable visual models from natural language supervision,''
\newblock in \emph{ICML}, pp.~8748--8763, 2021.

\bibitem{sharma2022survey}
C.~Sharma et~al.,
\newblock ``A survey on multimodal sentiment analysis and sarcasm detection,''
\newblock \emph{ACM Computing Surveys}, vol.~55, no.~7, pp.~1--38, 2022.

\bibitem{ftc2020guides}
Federal Trade Commission,
\newblock ``Guides concerning the use of endorsements in advertising,''
\newblock \emph{16 CFR Part 255}, Federal Register, 2020.

\bibitem{asci2021code}
ASCI,
\newblock ``The Code for Self-Regulation of Advertising Content in India,''
\newblock \emph{ASCI Technical Standards}, Mumbai, 2021.

\bibitem{hussein2020multimodal}
N.~Hussein et~al.,
\newblock ``Timeception for complex action recognition,''
\newblock in \emph{IEEE/CVF CVPR}, pp.~254--263, 2020.

\bibitem{metallama2024}
Meta AI Research,
\newblock ``Llama Guard 3 Vision: Safeguarding vision-language models,''
\newblock \emph{Meta AI Technical Report}, 2024.

\bibitem{bai2023qwen}
J.~Bai et~al.,
\newblock ``Qwen-VL: A versatile vision-language model for understanding,''
\newblock \emph{arXiv:2308.12966}, 2023.

\bibitem{gadzicki2020review}
K.~Gadzicki et~al.,
\newblock ``Early versus late fusion in multimodal convolutional neural networks,''
\newblock in \emph{IEEE MFI}, pp.~103--109, 2020.

\bibitem{deng2019arcface}
J.~Deng et~al.,
\newblock ``ArcFace: Additive angular margin loss for deep face recognition,''
\newblock in \emph{IEEE/CVF CVPR}, pp.~4690--4699, 2019.

\bibitem{zhang2020minifasnet}
Z.~Zhang et~al.,
\newblock ``A face anti-spoofing database with diverse attacks,''
\newblock in \emph{IEEE ICB}, pp.~1--8, 2020.

\bibitem{falcon2023nsfw}
Falcon AI,
\newblock ``Falcon NSFW Vision Transformer for adult content filtering,''
\newblock \emph{Hugging Face Hub}, 2023.

\bibitem{rothe2018dex}
R.~Rothe et~al.,
\newblock ``Deep expectation of apparent age from a single image,''
\newblock \emph{IJCV}, vol.~126, no.~2, pp.~144--157, 2018.

\bibitem{yu2020nasfas}
Z.~Yu et~al.,
\newblock ``Searching central difference convolutional networks for face anti-spoofing,''
\newblock in \emph{IEEE/CVF CVPR}, pp.~5295--5305, 2020.

\bibitem{he2016deep}
K.~He et~al.,
\newblock ``Deep residual learning for image recognition,''
\newblock in \emph{IEEE/CVF CVPR}, pp.~770--778, 2016.

\bibitem{vaswani2017attention}
A.~Vaswani et~al.,
\newblock ``Attention is all you need,''
\newblock in \emph{NeurIPS}, vol.~30, pp.~5998--6008, 2017.

\bibitem{radford2023robust}
A.~Radford et~al.,
\newblock ``Robust speech recognition via large-scale weak supervision,''
\newblock in \emph{ICML}, pp.~28492--28518, 2023.

\bibitem{jaegle2021perceiver}
A.~Jaegle et~al.,
\newblock ``Perceiver: General perception with iterative attention,''
\newblock in \emph{ICML}, pp.~4651--4664, 2021.

\bibitem{farneback2003two}
G.~Farneb{\"a}ck,
\newblock ``Two-frame motion estimation based on polynomial expansion,''
\newblock in \emph{SCIA}, pp.~363--370, 2003.

\bibitem{otsu1979threshold}
N.~Otsu,
\newblock ``A threshold selection method from gray-level histograms,''
\newblock \emph{IEEE Trans. SMC}, vol.~9, no.~1, pp.~62--66, 1979.

\bibitem{zuiderveld1994contrast}
K.~Zuiderveld,
\newblock ``Contrast limited adaptive histogram equalization,''
\newblock in \emph{Graphics Gems IV}, pp.~474--485, 1994.

\bibitem{breiman2001random}
L.~Breiman,
\newblock ``Random forests,''
\newblock \emph{Machine Learning}, vol.~45, no.~1, pp.~5--32, 2001.

\bibitem{schroff2015facenet}
F.~Schroff et~al.,
\newblock ``FaceNet: A unified embedding for face recognition,''
\newblock in \emph{IEEE/CVF CVPR}, pp.~815--823, 2015.

\bibitem{selvaraju2017grad}
R.~R.~Selvaraju et~al.,
\newblock ``Grad-CAM: Visual explanations from deep networks,''
\newblock in \emph{IEEE ICCV}, pp.~618--626, 2017.

\bibitem{lundberg2017unified}
S.~M.~Lundberg and S.-I.~Lee,
\newblock ``A unified approach to interpreting model predictions,''
\newblock in \emph{NeurIPS}, vol.~30, pp.~4765--4774, 2017.

\bibitem{coppa1998act}
United States Congress,
\newblock ``Children's Online Privacy Protection Act of 1998 (COPPA),''
\newblock \emph{Public Law 105-277}, 1998.

\bibitem{eudsa2022act}
European Parliament,
\newblock ``Digital Services Act (EU) 2022/2065,''
\newblock \emph{Official Journal of the European Union}, 2022.

\bibitem{hussain2017automatic}
Z.~Hussain et~al.,
\newblock ``Automatic understanding of image and video advertisements,''
\newblock in \emph{IEEE/CVF CVPR}, pp.~1705--1715, 2017.

\end{thebibliography}

\end{document}
"""
