import sys

def get_content():
    return r"""
% ============================================================
% CHAPTER 7: CONCLUSION AND FUTURE SCOPE
% ============================================================

\chapter{Conclusion and Future Scope}

\section{Summary of Findings and Key Contributions}

This project has designed, implemented, and empirically validated \textbf{SafeAd AI (SAFE-VISION)}, an end-to-end framework uniting proactive multimodal pre-publication advertisement moderation with real-time biometric age assurance. By addressing both creative content safety and recipient demographic eligibility within a unified architecture, SafeAd AI prevents inappropriate commercial exposures while maintaining high automated throughput for compliant advertisers.

The principal technical and scientific contributions are summarized as follows:
\begin{enumerate}
    \item \textbf{Multimodal Feature Extraction Engine:} Successfully unified EasyOCR (with CLAHE and Otsu binarization), ResNet50/MobileNetV3 deep visual backbones, Farneb\"{a}ck dense optical flow, and OpenAI Whisper audio transcription into an asynchronous, concurrent extraction architecture.
    \item \textbf{Empirical Audit of Narrow Safety Guardrails:} Demonstrated through empirical diagnostic testing that specialized conversational safety models (Meta's Llama Guard 3 Vision) fail catastrophically on commercial advertising ($80\%$ false acceptance), establishing that conversational alignment cannot interpret persuasive marketing rhetoric.
    \item \textbf{Foundation Vision-Language Integration:} Successfully deployed Qwen3-VL-8B-Instruct on Google Colab NVIDIA A100 GPU hardware in native \texttt{torch.bfloat16} precision, achieving 100\% prohibited recall and 0.0\% false acceptance on real-world advertising media.
    \item \textbf{Empirical Resolution of the Fusion Generalization Reality:} Proved that while learned tabular fusion (Random Forest) appears superior on development cohorts ($44.33\%$ accuracy), it collapses on novel held-out test data ($37.0\%$ accuracy, $75\%$ prohibited leakage), and hierarchical safety fusion achieves 66.7\% accuracy without outperforming standalone Qwen3-VL on novel distributions.
    \item \textbf{Concurrent Vision Engine Architecture:} Completely resolved longstanding Windows DirectShow multithreaded COM collisions and memory heap corruption (\texttt{0xc0000374}) via the decoupled, double-buffered \texttt{Realtime30FPSVisionEngine}, sustaining a locked 30~FPS display interval.
    \item \textbf{Multi-Cue Deep Anti-Spoofing Architecture:} Deployed a 103~FPS CPU-executable PAD engine fusing dual-scale MiniFASNet models with Hough line border tracking and 2D FFT moir\'{e} spatial frequency analysis, achieving 93.00\% liveness accuracy and securing 96.50\% ArcFace biometric cross-matching.
\end{enumerate}

\section{Lessons Learned Across Engineering Phases}

The progression through Phases~1 to 10D generated crucial scientific insights:
\begin{itemize}
    \item \emph{The Primacy of High-Capacity Foundation Models:} Narrow, task-specific classifiers and conversational guardrails overfit to closed training domains. Open-world commercial advertising requires the broad semantic reasoning of foundation vision-language models.
    \item \emph{The Danger of In-Distribution Development Optimism:} Cross-validated accuracy on development splits can induce false confidence. True generalization must be established on untouched held-out test sets under frozen rules.
    \item \emph{Dataset Labeling Rigor:} Advertisements cannot be categorized based on target marketing demographics. Ground-truth labels must strictly reflect statutory harm criteria to prevent artificial model penalization on benign consumer goods.
\end{itemize}

\section{Future Research Roadmap}

Future research will advance SafeAd AI along five strategic trajectories:
\begin{enumerate}
    \item \textbf{Parameter-Efficient Fine-Tuning (PEFT/LoRA):} Fine-tuning Qwen3-VL on a curated corpus of advertising creatives using Low-Rank Adaptation (LoRA) to calibrate four-tier policy boundaries directly into model weights.
    \item \textbf{End-to-End Temporal Video-Language Models:} Integrating native video-language architectures (e.g., Video-LLaVA) to process continuous temporal dynamics across long-form video advertisements.
    \item \textbf{Edge Model Distillation:} Distilling the 8B foundation model into compact 1.5B student architectures using knowledge distillation, enabling sub-500ms edge inference for real-time programmatic ad auctions.
    \item \textbf{Active Flash Liveness Detection:} Randomizing screen illumination color sequences during webcam capture to induce dynamic facial reflections, defeating 3D silicone mask attacks.
    \item \textbf{Zero-Knowledge Proofs for Privacy-Preserving Age Gating:} Implementing cryptographic zero-knowledge age proofs, allowing users to mathematically prove age eligibility without transmitting or storing identity credentials.
\end{enumerate}

% ============================================================
% REFERENCES
% ============================================================

\begin{thebibliography}{99}

\bibitem{gillespie2018custodians}
T.~Gillespie,
\emph{Custodians of the Internet: Platforms, Content Moderation, and the Hidden Decisions That Shape Social Media},
Yale University Press, New Haven, CT, USA, 2018.

\bibitem{roberts2019behind}
S.~T.~Roberts,
\emph{Behind the Screen: Content Moderation in the Shadows of Social Media},
Yale University Press, New Haven, CT, USA, 2019.

\bibitem{silva2020pre}
S.~Silva, L.~Santos, and M.~Ribeiro,
``Pre-publication auditing and enforcement in digital advertising exchanges,''
\emph{IEEE Trans. Comput. Soc. Syst.}, vol.~7, no.~4, pp.~912--924, Aug. 2020, doi: 10.1109/TCSS.2020.3001245.

\bibitem{zannettou2021characterizing}
S.~Zannettou, F.~Pierri, and G.~Gianvecchio,
``Characterizing deceptive and harmful advertisements in programmatic networks,''
in \emph{Proc. ACM Web Conf. (WWW)}, Ljubljana, Slovenia, Apr. 2021, pp.~2450--2461.

\bibitem{wang2025}
X.~Wang, L.~Wang, Y.~Su, H.~Tian, G.~Jin, and A.-A.~Liu,
``Few-shot in-context learning for implicit semantic multimodal content detection and interpretation,''
\emph{IEEE Trans. Circuits Syst. Video Technol.}, vol.~35, no.~9, pp.~9545--9558, Sep. 2025, doi: 10.1109/TCSVT.2025.3550900.

\bibitem{blmguard2026}
Y.~Yang \emph{et~al.},
``BLM-Guard: Explainable multimodal ad moderation with chain-of-thought and policy-aligned rewards,''
in \emph{Proc. 40th AAAI Conf. Artif. Intell. (AAAI-26)}, Feb. 2026, pp.~35985--35993.

\bibitem{safewatch2025}
Z.~Chen, F.~Pinto, M.~Pan, and B.~Li,
``SafeWatch: An efficient safety-policy following video guardrail model with transparent explanations,''
in \emph{Proc. Int. Conf. Learn. Represent. (ICLR)}, Singapore, May 2025, arXiv:2412.06878.

\bibitem{zhuang2025}
Y.~Zhuang \emph{et~al.},
``I know what you MEME! Understanding and detecting harmful memes with multimodal large language models,''
in \emph{Proc. Netw. Distrib. Syst. Secur. (NDSS) Symp.}, San Diego, CA, USA, Feb. 2025, doi: 10.14722/ndss.2025.240415.

\bibitem{kiela2020hateful}
D.~Kiela \emph{et~al.},
``The Hateful Memes Challenge: Detecting hate speech in multimodal memes,''
in \emph{Advances in Neural Information Processing Systems (NeurIPS)}, vol.~33, 2020, pp.~2611--2624.

\bibitem{nwasra2026}
N.~Nwasra and A.~Alharthy,
``Multimodal explainable AI (XAI) for hateful meme classification: A comprehensive framework for transparent content moderation,''
in \emph{Proc. 2nd Int. Conf. Comput. Intell. Approaches Appl. (ICCIAA)}, Jan. 2026, doi: 10.1109/ICCIAA68481.2026.11543858.

\bibitem{arya2024}
P.~Arya \emph{et~al.},
``MSCMGTB: A novel approach for multimodal social media content moderation using hybrid graph theory and bio-inspired optimization,''
\emph{IEEE Access}, vol.~12, pp.~73700--73718, May 2024, doi: 10.1109/ACCESS.2024.3400815.

\bibitem{baltrusaitis2018multimodal}
T.~Baltru\v{s}aitis, C.~Ahuja, and L.-P.~Morency,
``Multimodal machine learning: A survey and taxonomy,''
\emph{IEEE Trans. Pattern Anal. Mach. Intell.}, vol.~41, no.~2, pp.~423--443, Feb. 2018, doi: 10.1109/TPAMI.2018.2798607.

\bibitem{radford2021learning}
A.~Radford \emph{et~al.},
``Learning transferable visual models from natural language supervision (CLIP),''
in \emph{Proc. Int. Conf. Mach. Learn. (ICML)}, Jul. 2021, pp.~8748--8763.

\bibitem{liu2023visual}
H.~Liu, C.~Li, Q.~Wu, and Y.~J.~Lee,
``Visual instruction tuning (LLaVA),''
in \emph{Advances in Neural Information Processing Systems (NeurIPS)}, vol.~36, Dec. 2023, pp.~34892--34916.

\bibitem{bai2023qwen}
J.~Bai \emph{et~al.},
``Qwen-VL: A versatile vision-language model for understanding, localization, text reading, and beyond,''
\emph{arXiv preprint arXiv:2308.12966}, Aug. 2023.

\bibitem{inan2023llama}
H.~Inan \emph{et~al.},
``Llama Guard: LLM-based input-output safeguard for human-AI conversations,''
\emph{Meta AI Tech. Rep.}, Dec. 2023.

\bibitem{he2016deep}
K.~He, X.~Zhang, S.~Ren, and J.~Sun,
``Deep residual learning for image recognition,''
in \emph{Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR)}, Las Vegas, NV, USA, Jun. 2016, pp.~770--778.

\bibitem{devlin2019bert}
J.~Devlin, M.-W.~Chang, K.~Lee, and K.~Toutanova,
``BERT: Pre-training of deep bidirectional transformers for language understanding,''
in \emph{Proc. Conf. N. Am. Chapter Assoc. Comput. Linguist. (NAACL-HLT)}, Minneapolis, MN, USA, Jun. 2019, pp.~4171--4186.

\bibitem{breiman2001random}
L.~Breiman,
``Random Forests,''
\emph{Machine Learning}, vol.~45, no.~1, pp.~5--32, Oct. 2001, doi: 10.1023/A:1010933404324.

\bibitem{saraswat2026}
R.~Saraswat and S.~Tripathi,
``A multimodal approach for age estimation and verification of social media users,''
\emph{Int. J. Sci. Technol. (IJSAT)}, vol.~17, no.~2, Apr.--Jun. 2026, Art. ID IJSAT260210685.

\bibitem{safevision2026}
K.~Gopinath, R.~Divyesh, R.~Elangkumaran, T.~Kumanan, K.~K.~Rehkha, and G.~Victo Sudha George,
``SAFE VISION: Age-based social and web content management system to enhance child safety,''
\emph{Int. Sci. J. Eng. Manag. (ISJEM)}, vol.~5, no.~3, Mar. 2026, doi: 10.55041/ISJEM05763.

\bibitem{yu2023}
Z.~Yu, Y.~Qin, X.~Li, C.~Zhao, Z.~Lei, and G.~Zhao,
``Deep learning for face anti-spoofing: A survey,''
\emph{IEEE Trans. Pattern Anal. Mach. Intell.}, vol.~45, no.~5, pp.~5609--5631, May 2023, doi: 10.1109/TPAMI.2022.3215850.

\bibitem{deng2019arcface}
J.~Deng, J.~Guo, N.~Xue, and S.~Zafeiriou,
``ArcFace: Additive angular margin loss for deep face recognition,''
in \emph{Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)}, Long Beach, CA, USA, Jun. 2019, pp.~4690--4699.

\bibitem{schroff2015facenet}
F.~Schroff, D.~Kalenichenko, and J.~Philbin,
``FaceNet: A unified embedding for face recognition and clustering,''
in \emph{Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR)}, Boston, MA, USA, Jun. 2015, pp.~815--823.

\bibitem{nistairmf2023}
National Institute of Standards and Technology,
``Artificial Intelligence Risk Management Framework (AI RMF 1.0),''
\emph{NIST AI 100-1}, Jan. 2023. Available: \url{https://www.nist.gov/itl/ai-risk-management-framework}.

\bibitem{iso31000}
International Organization for Standardization,
``ISO 31000:2018: Risk management---Guidelines,''
ISO Standard, Feb. 2018. Available: \url{https://www.iso.org/standard/65694.html}.

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
\emph{16 CFR Part 255}, Jul. 2023. Available: \url{https://www.ftc.gov/legal-library/browse/rules/endorsement-guides}.

\end{thebibliography}

\end{document}
"""
