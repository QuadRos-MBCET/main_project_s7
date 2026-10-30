import sys

def get_content():
    return r"""
% ============================================================
% CHAPTER 5: METHODOLOGY AND IMPLEMENTATION DETAILS
% ============================================================

\chapter{Methodology and Implementation Details}

\section{End-to-End Processing Workflow}

The SafeAd AI operational workflow integrates two synchronized pipelines: the pre-publication advertising moderation pipeline and the real-time biometric age verification pipeline. The end-to-end execution progresses through eight deterministic phases:
\begin{enumerate}
    \item \textbf{Creative Ingestion and Codec Validation:} Advertising creatives are ingested via multipart asynchronous endpoints, standardized to $1280 \times 720$ resolution for video or $1080 \times 1080$ for static banners.
    \item \textbf{Adaptive Keyframe \& Audio Extraction:} Dynamic video advertisements undergo Farneb\"{a}ck dense optical flow analysis to extract salient keyframes at motion boundaries, while the primary audio stream is extracted to 16~kHz mono PCM.
    \item \textbf{Parallel Neural Feature Extraction:} Preprocessed media streams are evaluated across specialized detectors: EasyOCR extracts on-screen text, ResNet50/MobileNetV3 extracts visual spatial representations, Falcon NSFW ViT evaluates adult content, and Whisper transcribes speech audio.
    \item \textbf{Mathematical Risk Indexing \& Random Forest Evaluation:} Detector confidences are synthesized into the linear composite risk score $S_w$, transformed via piecewise escalation into $S_{\text{risk}}$, and vectorized into a 33-dimensional feature representation $\mathbf{z}_i$ evaluated by the trained Random Forest classifier.
    \item \textbf{Foundation Vision-Language Inference:} Qwen3-VL-8B-Instruct is prompted in native \texttt{torch.bfloat16} precision on NVIDIA A100 GPU hardware, returning structured JSON containing policy decisions and forensic justifications.
    \item \textbf{Hierarchical Safety Fusion (Strategy D):} Strategy D fuses tabular and VLM predictions, enforcing non-negotiable safety vetoes to eliminate prohibited false acceptance.
    \item \textbf{Decoupled Hardware Capture \& Anti-Spoofing:} The \texttt{Realtime30FPSVisionEngine} decouples DirectShow frame polling from AI inference, executing the dual-scale MiniFASNet ensemble, Hough line border checks, and 2D FFT moir\'{e} filtering.
    \item \textbf{Biometric Matching \& Age-Gated Delivery:} InsightFace ArcFace extracts 512-D embeddings to cross-match live faces against credential documents ($\tau = 0.65$), while ViT facial age estimation gates adult delivery.
\end{enumerate}

\section{Video Preprocessing and Adaptive Keyframe Selection}

Commercial video advertisements exhibit extreme temporal variability. Ingesting every frame of a 30-second commercial at 30~FPS yields 900 individual frames. Pushing all 900 frames through heavy deep vision backbones or vision-language models would require over 180 seconds per advertisement, completely violating pre-publication operational throughput requirements.

SafeAd AI implements an adaptive keyframe selection algorithm driven by inter-frame pixel differentials and Farneb\"{a}ck dense optical flow.

\subsection{Farneb\"{a}ck Dense Optical Flow Formulation}
Let $\text{Frame}_t(x, y)$ denote the image luminance intensity at spatial coordinates $(x, y)$ at time $t$. Under the classical optical flow brightness constancy assumption:
\begin{equation}
\text{Frame}_t(x, y) = \text{Frame}_{t+\delta t}(x + \delta x, y + \delta y)
\end{equation}
Farneb\"{a}ck's algorithm approximates the local neighborhood of each pixel using a quadratic polynomial expansion:
\begin{equation}
f_1(\mathbf{x}) = \mathbf{x}^T \mathbf{A}_1 \mathbf{x} + \mathbf{b}_1^T \mathbf{x} + c_1
\end{equation}
where $\mathbf{x} = [x, y]^T$, $\mathbf{A}_1$ is a symmetric $2 \times 2$ matrix, $\mathbf{b}_1$ is a $2 \times 1$ vector, and $c_1$ is a scalar coefficient estimated via weighted least-squares over a Gaussian window.

After an apparent displacement $\mathbf{d} = [u, v]^T$, the new polynomial becomes:
\begin{equation}
f_2(\mathbf{x}) = f_1(\mathbf{x} - \mathbf{d}) = (\mathbf{x} - \mathbf{d})^T \mathbf{A}_1 (\mathbf{x} - \mathbf{d}) + \mathbf{b}_1^T (\mathbf{x} - \mathbf{d}) + c_1
\end{equation}
Equating coefficients between $f_2(\mathbf{x})$ and the empirical polynomial approximation $\mathbf{x}^T \mathbf{A}_2 \mathbf{x} + \mathbf{b}_2^T \mathbf{x} + c_2$ yields:
\begin{equation}
\mathbf{A}_2 = \mathbf{A}_1, \quad \mathbf{b}_2 = \mathbf{b}_1 - 2 \mathbf{A}_1 \mathbf{d} \implies \mathbf{d} = -\frac{1}{2} \mathbf{A}_1^{-1} (\mathbf{b}_2 - \mathbf{b}_1)
\end{equation}

From the displacement field $\mathbf{V}(x, y) = (u(x, y), v(x, y))$, the scene kinetic motion score is computed as:
\begin{equation}
\text{Motion\_Score}(t, t+1) = \frac{1}{H \times W} \sum_{x=1}^H \sum_{y=1}^W \sqrt{u(x, y)^2 + v(x, y)^2}
\end{equation}

Algorithm~\ref{alg:keyframe} formalizes the adaptive keyframe extraction protocol.

\begin{lstlisting}[language=Python, caption={Algorithm 1: Adaptive Motion-Gated Keyframe Extraction Protocol}, label={alg:keyframe}]
def extract_adaptive_keyframes(video_path: str, max_frames: int = 16):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    keyframes = []
    prev_gray = None
    last_sampled_time = -1.0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        gray = cv2.cvtColor(cv2.resize(frame, (640, 360)), cv2.COLOR_BGR2GRAY)
        
        if prev_gray is None:
            keyframes.append((current_time, frame))
            prev_gray = gray
            last_sampled_time = current_time
            continue
            
        # Compute Farneback Optical Flow
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        motion_energy = np.mean(mag)
        
        # Scene Cut Detection Rule
        if motion_energy >= 28.0 and (current_time - last_sampled_time) >= 0.5:
            keyframes.append((current_time, frame))
            last_sampled_time = current_time
        # Action Burst Window Rule
        elif 12.5 <= motion_energy < 28.0 and (current_time - last_sampled_time) >= 1.0:
            keyframes.append((current_time, frame))
            last_sampled_time = current_time
        # Static Fallback Uniform Rule (1.0 Hz)
        elif (current_time - last_sampled_time) >= 2.0:
            keyframes.append((current_time, frame))
            last_sampled_time = current_time
            
        prev_gray = gray
        if len(keyframes) >= max_frames:
            break
            
    cap.release()
    return keyframes
\end{lstlisting}

\section{Optical Character Recognition \& Typographic Enhancement}

On-screen typography in commercial advertisements represents a primary vector for cross-modal deception. Advertisers embed high-risk marketing claims in stylized banners while concealing mandatory statutory disclaimers in low-contrast footer text.

\subsection{Contrast-Limited Adaptive Histogram Equalization (CLAHE)}
Standard global histogram equalization flattens subtle intensity gradients and amplifies high-frequency compression artifacts in flat background regions. SafeAd AI applies Contrast-Limited Adaptive Histogram Equalization (CLAHE) on the luminance channel.

The image is partitioned into non-overlapping rectangular contextual tiles of size $8 \times 8$ pixels. Within each tile, the local histogram $h(n)$ is computed. To prevent noise amplification, the histogram is clipped at a predetermined threshold $\beta = 2.0$:
\begin{equation}
h_{\text{clipped}}(n) = \min(h(n), \beta)
\end{equation}
The clipped pixels are redistributed uniformly across all gray-level bins. The cumulative distribution function (CDF) is computed locally, and pixel intensities are mapped via bilinear interpolation across tile boundaries to eliminate artificial block borders.

\subsection{Adaptive Otsu Binarization}
Following CLAHE enhancement, the grayscale image is binarized using Otsu's thresholding, which computes the optimal global threshold $t^*$ that maximizes inter-class variance $\sigma_B^2(t)$:
\begin{equation}
t^* = \arg\max_{0 \le t < L} \left[ \omega_0(t) \omega_1(t) (\mu_0(t) - \mu_1(t))^2 \right]
\end{equation}
where $\omega_0(t), \omega_1(t)$ are background and foreground class probabilities, and $\mu_0(t), \mu_1(t)$ are the corresponding class means.

Morphological opening with a $2 \times 2$ rectangular structuring element strips isolated salt-and-pepper artifacts, while a $3 \times 3$ dilation reconnects broken character strokes. Preprocessed frames are parsed via EasyOCR, which utilizes a CRAFT (Character Region Awareness for Text Detection) backbone to predict heatmaps of character centers and affinity links, followed by a CRNN (Convolutional Recurrent Neural Network) with CTC loss for sequence decoding.

\section{Speech-to-Text Audio Transcription via Whisper}

Audio channels are demuxed from MP4 containers via FFmpeg and decoded to uncompressed single-channel 16~kHz 16-bit PCM WAV formats:
\begin{lstlisting}[language=bash]
ffmpeg -i input_ad.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio_track.wav
\end{lstlisting}

Speech transcription is performed using OpenAI Whisper. Audio waveforms are transformed into 80-channel log-magnitude Mel-spectrograms computed over 25~ms windows with a 10~ms stride:
\begin{equation}
M(f, t) = \log \left( 1 + \sum_{k} |X(k, t)|^2 \cdot H_f(k) \right)
\end{equation}
where $H_f(k)$ denotes the triangular Mel weighting filter for channel $f$.

The Whisper encoder processes Mel-spectrogram frames through two 1D convolutional layers with GELU activations, followed by stacked Transformer encoder blocks using sinusoidal positional embeddings. The autoregressive decoder generates recognized text tokens conditioned on encoder hidden states, emitting word tokens with localized millisecond start and end timestamps.

\section{Specialized Neural Safety Detectors}

\subsection{Visual Scene Safety: Llama Guard 3 Vision \& Empirical Failure Analysis}
In initial iterations, scene safety was evaluated via Meta's Llama Guard 3 Vision (11B parameters). The model receives visual frames and prompt templates enforcing the MLCommons hazard taxonomy.

However, as audited in Phase~9B, the model exhibited severe diagnostic failures when applied to commercial advertising:
\begin{itemize}
    \item \textbf{Failure Mode 1: False Acceptance of Deceptive Schemes:} Because Llama Guard 3 was instruction-tuned exclusively on conversational chat dialogues, it treats persuasive advertising copy (such as guaranteed crypto returns or offshore casino bonuses) as legitimate commercial speech, failing to identify deceptive intent.
    \item \textbf{Failure Mode 2: S12 Sexual Misclassification of Combat Media:} In video ads depicting violent military action, Llama Guard 3 emitted violation code \texttt{S12} (Sexual Content) instead of violence codes, caused by attention confusion over saturated combat lighting and commercial text overlays.
\end{itemize}
These empirical findings motivated the replacement of specialized guardrails with high-capacity general foundation VLMs (Qwen3-VL-8B).

\subsection{Adult and Suggestive Imagery: Falcon NSFW ViT}
Explicit and suggestive imagery is evaluated using the Falcon NSFW Vision Transformer. The model decomposes $224 \times 224$ images into non-overlapping $16 \times 16$ patches, projecting each patch to a 768-dimensional embedding. After passing through 12 stacked Transformer encoder blocks, the final \texttt{[CLS]} representation is evaluated via a binary softmax classifier emitting probabilities $P(\text{Neutral})$ and $P(\text{NSFW})$. The adult score $S_{\text{nsfw}} \in [0.0, 1.0]$ triggers two distinct policy branches:
\begin{equation}
\text{Action}(S_{\text{nsfw}}) = 
\begin{cases}
\texttt{UNSAFE\_FOR\_ALL} \text{ (Direct Rejection)}, & \text{if } S_{\text{nsfw}} \ge 0.85 \text{ (Explicit Pornography)} \\
\texttt{SAFE\_18\_PLUS} \text{ (Adult Gating)}, & \text{if } 0.35 \le S_{\text{nsfw}} < 0.85 \text{ (Sensual / Swimwear)} \\
\text{PERMITTED}, & \text{if } S_{\text{nsfw}} < 0.35
\end{cases}
\end{equation}

\subsection{Video Action Anomaly and Violent Dynamics: VideoMAE}
Temporal violence dynamics are captured using VideoMAE. VideoMAE ingests 16 consecutive frames and extracts spatio-temporal tubelet embeddings spanning $2 \times 16 \times 16$ dimensions. The resulting temporal feature vector is blended with Farneb\"{a}ck kinetic energy:
\begin{equation}
S_{\text{violence}} = 0.70 \cdot P_{\text{violence}} + 0.30 \cdot \min\left( 1.0, \frac{E_{\text{kinetic}}}{45.0} \right)
\end{equation}

\subsection{OCR Text Safety \& Toxicity: RoBERTa \& DeBERTa}
Extracted typography is evaluated using fine-tuned RoBERTa and DeBERTa language models trained on the Jigsaw CivilComments dataset. The model evaluates toxic language, severe toxicity, obscenity, threats, and identity attacks, computing:
\begin{equation}
S_{\text{ocr}} = \max\left( P_{\text{toxic}}, P_{\text{severe}}, P_{\text{obscene}}, P_{\text{threat}}, P_{\text{identity}} \right)
\end{equation}

\subsection{Commercial Risk \& Deception Analyzer}
Deceptive claims that avoid toxic language (e.g., Ponzi schemes, fake giveaways, unapproved pharmaceuticals) are screened using regex-driven legal dictionaries grounded in FTC deception guidelines~\cite{ftcdeception}. The score $S_{\text{adrisk}} \in [0.0, 1.0]$ computes the normalized weighted density of fraudulent marketing indicators.

\section{Mathematical Formulation of Evidence Fusion}

Figure~\ref{fig:multimodal_pipeline} illustrates the synthesis of multimodal feature streams into the 33-dimensional feature representation and non-linear risk escalation score.

\begin{figure}[H]
    \centering
    \IfFileExists{multimodal_feature_pipeline.png}{\includegraphics[width=0.96\textwidth]{multimodal_feature_pipeline.png}}{%
        \IfFileExists{overleaf_figures/multimodal_feature_pipeline.png}{\includegraphics[width=0.96\textwidth]{overleaf_figures/multimodal_feature_pipeline.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Multimodal Evidence Extraction and Risk Escalation Architecture}}}}%
    }
    \caption{Multimodal Evidence Extraction, Vectorization into 33-D Representation, and Non-Linear Risk Escalation Architecture.}
    \label{fig:multimodal_pipeline}
\end{figure}

The evidence scores are synthesized into a linear composite base risk score $S_w \in [0.0, 100.0]$:
\begin{equation}
\label{eq:safeadweighted}
S_w = 100 \cdot \left( 0.25 V + 0.20 D + 0.20 N + 0.15 O + 0.10 A + 0.10 M \right)
\end{equation}
where $V = S_{\text{visual}}, D = S_{\text{violence}}, N = S_{\text{nsfw}}, O = S_{\text{ocr}}, A = S_{\text{audio}}, M = S_{\text{adrisk}}$.

Because linear averaging can dilute critical individual hazard triggers (e.g., an ad with zero nudity and zero toxicity but explicit firearms), SafeAd AI applies the piecewise non-linear transformation:
\begin{equation}
\label{eq:safeadpiecewise}
S_{\text{risk}} = 
\begin{cases}
\min(100.0, \max(S_w, P)), & \text{if } F_{\text{child}} \lor P \ge 50.0 \\
\min(65.0, \max(S_w, 70 Q)), & \text{else if } Q \ge 0.25 \\
\min(39.9, S_w), & \text{otherwise}
\end{cases}
\end{equation}
where:
\begin{align}
P &= 100 \cdot \max(D, M_{\text{scam}}, M_{\text{deception}}, O_{\text{scam}}, A_{\text{scam}}) \\
Q &= \max(N, M_{\text{explicit}}, O_{\text{adult}}, A_{\text{adult}})
\end{align}

Algorithm~\ref{alg:piecewise} details this transformation.

\begin{lstlisting}[language=Python, caption={Algorithm 2: Piecewise Non-Linear Risk Transformation}, label={alg:piecewise}]
def compute_piecewise_risk(V, D, N, O, A, M, F_child=False):
    # Linear composite weighted score
    S_w = 100.0 * (0.25*V + 0.20*D + 0.20*N + 0.15*O + 0.10*A + 0.10*M)
    
    # Prohibited hazard aggregator
    P = 100.0 * max(D, M.get('scam', 0), M.get('deception', 0), O.get('scam', 0), A.get('scam', 0))
    # Adult restricted aggregator
    Q = max(N, M.get('explicit', 0), O.get('adult', 0), A.get('adult', 0))
    
    if F_child or P >= 50.0:
        S_final = min(100.0, max(S_w, P))
    elif Q >= 0.25:
        S_final = min(65.0, max(S_w, 70.0 * Q))
    else:
        S_final = min(39.9, S_w)
        
    return round(S_final, 2)
\end{lstlisting}

\section{Phase 8E Learned Late Fusion (Random Forest)}

To capture non-linear feature interactions, Phase~8E constructed a 33-dimensional feature representation $\mathbf{z}_i \in \mathbb{R}^{33}$ from cached detector outputs. Table~\ref{tab:feature_schema} details the complete feature schema.

\begin{table}[htbp]
\centering
\small
\caption{SafeAd AI 33-Dimensional Feature Schema for Learned Fusion}
\label{tab:feature_schema}
\begin{tabular}{|l|p{4.2cm}|p{7.5cm}|}
\hline
\textbf{Index Range} & \textbf{Feature Domain} & \textbf{Specific Extracted Signals} \\
\hline
$\mathbf{z}[0:5]$ & Visual Scene & Binary unsafe flag, weapon score, hate symbol score, CBRN score, gore score. \\
\hline
$\mathbf{z}[5:10]$ & Adult / NSFW & Falcon NSFW probability, suggestive apparel score, nudity ratio, skin area ratio. \\
\hline
$\mathbf{z}[10:15]$ & Temporal Dynamics & VideoMAE violence score, Farneb\"{a}ck mean kinetic energy, motion variance, cut count. \\
\hline
$\mathbf{z}[15:20]$ & OCR Text Safety & Toxicity score, severe toxicity, identity attack, obscenity score, threat score. \\
\hline
$\mathbf{z}[20:25]$ & Speech & Audio & Audio toxicity score, profanity density, speech rate, deceptive phrase count. \\
\hline
$\mathbf{z}[25:30]$ & Commercial Risk & FTC scam density, urgency keyword count, guaranteed payout score, alcohol keyword flag. \\
\hline
$\mathbf{z}[30:33]$ & Composite Indicators & Linear weighted base score $S_w$, prohibited aggregator $P$, adult aggregator $Q$. \\
\hline
\end{tabular}
\end{table}

The Random Forest classifier was trained using scikit-learn with 100 bagged decision trees, max tree depth of 5, and balanced class weighting:
\begin{equation}
w_c = \frac{N_{\text{total}}}{|\mathcal{C}| \cdot N_c}
\end{equation}
The model was evaluated using Stratified 5-Fold Cross-Validation, ensuring that every out-of-fold prediction was generated by an ensemble that never observed that sample during training.

\section{Phase 10 Vision-Language Model Integration: Qwen3-VL-8B-Instruct}

To achieve true open-world semantic reasoning, Phase~10 integrated \textbf{Qwen3-VL-8B-Instruct}. The model was deployed on Google Colab utilizing an NVIDIA A100-SXM4-40GB GPU in native \texttt{torch.bfloat16} precision.

\subsection{VLM Policy Prompt Design}
The model is prompted with the complete four-tier policy specification, regulatory guidelines, authentic OCR text, and sampled video keyframes. The system prompt is engineered to eliminate hallucination and enforce structured JSON output:

\begin{lstlisting}[language=Python, caption={Qwen3-VL-8B Regulatory System Prompt Template}]
QWEN_SYSTEM_PROMPT = \"\"\"
You are SafeAd AI, an expert multimodal advertising moderation engine.
Your task is to evaluate the provided commercial advertisement (images/keyframes and OCR text) 
against our formal four-tier advertising compliance policy:

1. SAFE_FOR_ALL: General consumer goods, educational tools, benign electronics, apparel. 
   Completely free of mature, violent, or deceptive themes. Suitable for young children (<14).
2. SAFE_14_PLUS: Adolescent merchandise, high-caffeine energy drinks, teen skincare, 
   competitive action sports, teen gaming. No alcohol, tobacco, gambling, or adult content.
3. SAFE_18_PLUS: Lawful commercial adult products: commercial alcohol, licensed casino gaming, 
   adult dating, swimwear. Prohibits underage targeting or illegal goods.
4. UNSAFE_FOR_ALL: Universally prohibited content: financial scams, Ponzi schemes, 
   crypto fraud, weapons, illicit drugs, CSAM, hate speech, severe graphic violence.

EXTRACTED OCR TEXT FROM MEDIA:
"{ocr_text}"

You MUST output ONLY a valid JSON object matching this schema:
{
  "predicted_tier": "SAFE_FOR_ALL" | "SAFE_14_PLUS" | "SAFE_18_PLUS" | "UNSAFE_FOR_ALL",
  "confidence": <float between 0.0 and 1.0>,
  "policy_violations": [<list of triggered policy strings>],
  "visual_cues": [<list of specific visual elements observed>],
  "justification": "<detailed forensic rationale grounded in policy rules>"
}
\"\"\"
\end{lstlisting}

\section{Hierarchical Safety Fusion Protocol (Strategy D)}

Strategy D establishes a hierarchical safety protocol that fuses Qwen3-VL semantic reasoning with Random Forest tabular predictions. The protocol is formalized in Algorithm~\ref{alg:fusion} and visually diagrammed in Figure~\ref{fig:fusion_flowchart}.

\begin{figure}[H]
    \centering
    \IfFileExists{fusion_pipeline.png}{\includegraphics[width=0.96\textwidth]{fusion_pipeline.png}}{%
        \IfFileExists{overleaf_figures/fusion_pipeline.png}{\includegraphics[width=0.96\textwidth]{overleaf_figures/fusion_pipeline.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Strategy D Hierarchical Safety Fusion Protocol Flowchart}}}}%
    }
    \caption{Strategy D Hierarchical Safety Fusion Protocol: Arbitration Logic between Qwen3-VL Zero-Tolerance Safety Veto and Random Forest Tabular Prediction.}
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
        # If models agree on the specific benign tier, adopt it
        if qwen_pred == rf_pred:
            return qwen_pred, "RULE_3A_BENIGN_EXACT_AGREEMENT"
        # If Qwen indicates teen restrictions, prioritize higher protection
        if qwen_pred == "SAFE_14_PLUS":
            return "SAFE_14_PLUS", "RULE_3B_BENIGN_CONSERVATIVE_TEEN"
        return rf_pred, "RULE_3C_BENIGN_RF_PREFERENCE"
        
    # Rule 4: High-Confidence VLM Resolution
    if qwen_conf >= 0.85:
        return qwen_pred, "RULE_4_HIGH_CONFIDENCE_VLM_OVERRIDE"
        
    # Rule 5: Conflict Arbitration / Human Review
    return "REQUIRES_HUMAN_REVIEW", "RULE_5_CONFLICT_ARBITRATION_ROUTED"
\end{lstlisting}

\section{Realtime Vision Engine \& DirectShow Concurrency Control}

In standard multithreaded Python applications on Windows, concurrent invocation of deep neural networks (e.g., MTCNN, ArcFace) within OpenCV video capture callbacks induces severe thread deadlocks and fatal memory corruption:
\begin{equation}
\text{Error: Fatal native memory heap corruption (\texttt{0xc0000374}) in DirectShow videoio driver.}
\end{equation}
Root-cause profiling revealed that OpenCV's DirectShow backend utilizes COM Single-Threaded Apartment (STA) threading. When heavy inference blocks the capture callback, the DirectShow message pump starves, causing buffer overflows and unhandled memory corruption.

The \texttt{Realtime30FPSVisionEngine} eliminates this failure through architectural decoupling:
\begin{enumerate}
    \item \textbf{Thread 1 (Grabber Daemon):} Operates in a lightweight, non-blocking loop polling raw frames from DirectShow at 30~FPS. It never executes deep learning models; it writes frames into a shared memory buffer protected by \texttt{threading.Lock()}.
    \item \textbf{Thread 2 (AI Worker Daemon):} Operates asynchronously downstream. It pulls the latest frame copy, rescales it to proxy resolution ($640 \times 480$), and executes MTCNN, MiniFASNet PAD, and ArcFace feature extraction.
    \item \textbf{Main Display Loop:} Queries the shared buffer every 33.3~ms ($1/30$~s), rendering the synchronized HUD overlay at a locked 30~FPS with zero frame drops.
\end{enumerate}

Figure~\ref{fig:vision_concurrency} details the decoupled thread architecture of the \texttt{Realtime30FPSVisionEngine}, illustrating how DirectShow frame ingestion is separated from downstream AI inference to guarantee stable 30 FPS playback. Algorithm~\ref{alg:engine} formalizes the underlying Python concurrency implementation.

\begin{figure}[H]
    \centering
    \IfFileExists{vision_engine_concurrency.png}{\includegraphics[width=0.96\textwidth]{vision_engine_concurrency.png}}{%
        \IfFileExists{overleaf_figures/vision_engine_concurrency.png}{\includegraphics[width=0.96\textwidth]{overleaf_figures/vision_engine_concurrency.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Realtime30FPSVisionEngine Decoupled DirectShow Concurrency Blueprint}}}}%
    }
    \caption{Realtime30FPSVisionEngine Decoupled Thread Architecture: Isolation of DirectShow COM STA Polling Thread from Downstream Deep Learning Workers to Eliminate Native Heap Corruption.}
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
        
        # Start Decoupled Threads
        self.grabber_thread = threading.Thread(target=self._frame_grabber, daemon=True)
        self.worker_thread = threading.Thread(target=self._ai_worker, daemon=True)
        self.grabber_thread.start()
        self.worker_thread.start()
        
    def _frame_grabber(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.latest_frame = frame
            time.sleep(0.005) # Prevent CPU spinning
            
    def _ai_worker(self):
        while self.running:
            frame_to_process = None
            with self.lock:
                if self.latest_frame is not None:
                    frame_to_process = self.latest_frame.copy()
            if frame_to_process is not None:
                # Run MTCNN, MiniFASNet PAD, and ArcFace without blocking video capture
                ai_output = execute_deep_biometrics(frame_to_process)
                with self.lock:
                    self.latest_ai_result = ai_output
            time.sleep(0.02)
\end{lstlisting}

\section{Presentation Attack Detection (PAD) \& Biometrics}

\subsection{Dual-Scale MiniFASNet Ensemble}
The PAD engine deploys two parallel MiniFASNet models through ONNX Runtime:
\begin{itemize}
    \item \texttt{MiniFASNetV2} at 2.7$\times$ context: processes an $80 \times 80$ face crop, evaluating high-frequency skin pore texture and OLED/LCD subpixel lattice artifacts.
    \item \texttt{MiniFASNetV1SE} at 4.0$\times$ context: processes an $80 \times 80$ crop at 4.0 times face scale with Squeeze-and-Excitation channel attention, capturing device chassis bezels, user fingers, and ambient room reflections.
\end{itemize}
The models output 3-class softmax vectors: $P(\text{Print}), P(\text{Live}), P(\text{Replay})$. Mean CPU execution latency is $\sim$9.7~ms ($\sim$103~FPS).

\subsection{Geometric Bezel Detection via Probabilistic Hough Line Transform}
Mobile smartphone displays introduce rigid linear geometric edges. Canny edge detection followed by the Probabilistic Hough Line Transform scans for:
\begin{itemize}
    \item Near-horizontal lines ($|\theta| < 10^\circ$) spanning $>50\%$ of face width (phone chin and navigation bars).
    \item Near-vertical lines ($|\theta| > 80^\circ$) matching phone chassis borders.
\end{itemize}
Detecting $\ge 3$ aligned collinear border segments raises an active screen replay alert.

\subsection{2D FFT Moir\'{e} Interference Analysis}
When a camera records a digital screen, spatial aliasing between the camera Bayer filter and the screen pixel matrix generates periodic moir\'{e} patterns. The 2D Fast Fourier Transform is computed:
\begin{equation}
F(u, v) = \sum_{x=0}^{M-1} \sum_{y=0}^{N-1} f(x, y) e^{-j 2\pi \left( \frac{ux}{M} + \frac{vy}{N} \right)}
\end{equation}
High-pass filtering the log-magnitude spectrum $\log(1 + |F(u, v)|)$ isolates periodic high-frequency spikes. If high-frequency spectral energy exceeds $\tau_{\text{moire}} = 0.42$ with high Laplacian variance, a digital screen replay is confirmed.

\subsection{InsightFace ArcFace Biometric Matching}
Face cross-matching between the uploaded ID credential and the live camera stream utilizes InsightFace ArcFace (\texttt{iResNet50} backbone trained on MS1MV3). Both faces are aligned to 5 facial landmarks via MTCNN. ArcFace produces 512-dimensional unit-normalized embeddings ($\mathbf{u}, \mathbf{v} \in \mathbb{R}^{512}$, $\|\mathbf{u}\|_2 = \|\mathbf{v}\|_2 = 1.0$). Biometric similarity is evaluated via geodesic cosine similarity:
\begin{equation}
S(\mathbf{u}, \mathbf{v}) = \sum_{k=1}^{512} u_k v_k
\end{equation}
The operating match threshold is $\tau_{\text{match}} = 0.65$ (65.0\%). During spoof attacks, ArcFace continues computing and displaying similarity telemetry on the HUD to provide audit officers with full forensic data.

\subsection{ViT Facial Age Estimation \& Mandibular Edge Density}
Biological age is estimated using a fine-tuned Vision Transformer (\texttt{nateraw/vit-age-classifier}). Because predictions near the 17-to-19 boundary can be influenced by cosmetic makeup, SafeAd AI extracts a secondary physical cue: mandibular facial hair edge density. A Canny edge detector ($T_{\text{low}}=50, T_{\text{high}}=150$) evaluates the lower third of the face:
\begin{equation}
\rho_{\text{beard}} = \frac{\sum_{x, y} \text{Canny}(x, y)}{\text{Area}(\text{Mandibular\_Region})}
\end{equation}
If $\rho_{\text{beard}} \ge 0.14$, adulthood (\texttt{AGE\_18\_PLUS}) is confirmed even if the ViT estimates a borderline age near 17. The estimate is cross-checked against credential dates of birth extracted via \texttt{pypdfium2} and EasyOCR. If $\Delta_{\text{age}} = |\text{Age}_{\text{DOB}} - \text{Age}_{\text{ViT}}| > 8$ years, an age-fraud alert is logged.
"""
