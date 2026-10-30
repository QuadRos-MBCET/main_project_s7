import sys

def get_chapter5():
    return r"""
\chapter{Methodology and Implementation Details}
\label{ch:methodology}

\section{End-to-End Processing Workflow}
The SafeAd AI methodology executes a multi-stage, synchronized analysis pipeline that ingests raw advertisement video and image creatives, extracts intermediate neural representations across visual, typographic, and acoustic modalities, synthesizes these representations through late fusion and vision-language foundation models, and coordinates with a client-side biometric verification engine to gate delivery.

\section{Video Preprocessing and Adaptive Keyframe Selection}
To process video creatives within programmatic latency budgets, the system implements an adaptive keyframe selection algorithm driven by Farneb\"{a}ck dense optical flow. Let $I_t(x, y)$ and $I_{t+1}(x, y)$ denote consecutive video frames. Farneb\"{a}ck optical flow approximates the neighborhood of each pixel using quadratic polynomials, estimating displacement vector field $\mathbf{d} = (u, v)^T$. The mean kinetic motion energy $\bar{M}_t$ between consecutive frames is computed as:
\begin{equation}
\bar{M}_t = \frac{1}{H \cdot W} \sum_{x=1}^{W} \sum_{y=1}^{H} \sqrt{u(x, y)^2 + v(x, y)^2}
\end{equation}
A frame $I_t$ is selected as an informative keyframe if $\bar{M}_t$ exceeds the running median by a threshold $\tau_{\text{motion}} = 1.8$, or if the color histogram intersection distance $\mathcal{D}_{\text{hist}}(I_t, I_{t-1}) \ge 0.45$. This ensures that rapid action sequences and transient typographic overlays are preserved while static backgrounds are compressed.

\section{Optical Character Recognition and Typographic Enhancement}
On-screen text embedded in video frames often suffers from compression artifacts and low contrast. The preprocessing engine applies Contrast-Limited Adaptive Histogram Equalization (CLAHE) with a clipping limit of $2.0$ over an $8 \times 8$ grid tile, followed by adaptive Otsu binarization. Otsu's method maximizes the inter-class variance $\sigma_B^2(t)$ between foreground text pixels and background:
\begin{equation}
\sigma_B^2(t) = \omega_0(t) \, \omega_1(t) \left[ \mu_0(t) - \mu_1(t) \right]^2
\end{equation}
where $\omega_0(t), \omega_1(t)$ are cumulative class probabilities, and $\mu_0(t), \mu_1(t)$ are mean intensities. The enhanced text regions are processed by EasyOCR with English dictionaries, returning text strings $\mathbf{T} = \{t_1, t_2, \dots, t_N\}$ alongside spatial coordinates and confidence scores.

\section{Speech-to-Text Audio Transcription via Whisper}
The audio track $\mathbf{A}$ is extracted via FFmpeg, resampled to 16~kHz mono PCM format, and converted into 80-channel log-magnitude Mel-spectrograms:
\begin{equation}
S(f, t) = \log \left( 1 + \mathcal{M}_{\text{filter}} \cdot |\text{STFT}(\mathbf{A})|^2 \right)
\end{equation}
Whisper's encoder-decoder transformer processes $S(f, t)$ to generate timestamped text transcripts $\mathbf{X}$. This enables the framework to capture spoken disclaimers and voiceover promotional claims that never appear in on-screen text.

\section{Specialized Neural Safety Detectors}
The intermediate feature extraction layer deploys a suite of specialized, pre-trained neural networks:
\begin{itemize}
    \item \textbf{Adult Imagery (Falcon NSFW ViT):} Outputs continuous posterior probability $p_{\text{nsfw}} \in [0.0, 1.0]$.
    \item \textbf{Violent Dynamics (VideoMAE):} 3D video transformer operating on 16-frame tubelet embeddings to compute physical violence probability $p_{\text{violence}} \in [0.0, 1.0]$.
    \item \textbf{Text Toxicity (RoBERTa/DeBERTa):} Evaluates extracted text $\mathbf{T}$ and speech transcript $\mathbf{X}$ to output toxicity probability $p_{\text{toxic}} \in [0.0, 1.0]$.
    \item \textbf{Commercial Risk Analyzer:} Scans for deceptive guarantees and regulated goods, producing composite commercial risk score $p_{\text{fraud}} \in [0.0, 1.0]$.
\end{itemize}

Figure~\ref{fig:multimodal_feature_pipeline} illustrates the multi-stream feature extraction architecture.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{multimodal_feature_pipeline.png}
\caption{SafeAd AI Multimodal Feature Extraction Pipeline}
\label{fig:multimodal_feature_pipeline}
\end{figure}

\section{Phase 8E Learned Late Fusion (Random Forest)}
In Phase 8E, intermediate detector outputs are assembled into a 16-dimensional feature vector $\mathbf{v}_{\text{fusion}}$. A Random Forest ensemble comprising 100 decision trees is trained with balanced class weights to optimize multi-class log-loss:
\begin{equation}
\mathbf{p}_{\text{RF}} = \frac{1}{B} \sum_{b=1}^{B} T_b(\mathbf{v}_{\text{fusion}})
\end{equation}
Algorithm~\ref{alg:rf_fusion} outlines the late-fusion inference procedure, and Figure~\ref{fig:fusion_pipeline} illustrates the architecture.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.88\linewidth]{fusion_pipeline.png}
\caption{Phase 8E Learned Late Fusion Architecture}
\label{fig:fusion_pipeline}
\end{figure}

\begin{lstlisting}[language=Python, caption={Phase 8E Learned Random Forest Late Fusion}, label={alg:rf_fusion}]
def evaluate_rf_fusion(detector_telemetry):
    v = [
        detector_telemetry.nsfw_max, detector_telemetry.nsfw_mean,
        detector_telemetry.violence_max, detector_telemetry.violence_kinetic,
        detector_telemetry.text_toxicity_max, detector_telemetry.asr_toxicity_max,
        detector_telemetry.fraud_score, detector_telemetry.urgency_score,
        detector_telemetry.alcohol_keyword_flag, detector_telemetry.gambling_flag
    ]
    prob_dist = random_forest_model.predict_proba([v])[0]
    predicted_idx = np.argmax(prob_dist)
    labels = ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS", "UNSAFE_FOR_ALL"]
    return labels[predicted_idx], prob_dist
\end{lstlisting}

\section{Phase 10 Vision-Language Model Integration: Qwen3-VL-8B-Instruct}
In Phase 10, the system integrates Qwen3-VL-8B-Instruct via structured prompt engineering. Listing~\ref{lst:qwen_prompt} presents the policy prompt template.

\begin{lstlisting}[language=TeX, caption={Qwen3-VL Policy-Aligned Prompt Template}, label={lst:qwen_prompt}]
You are a senior digital advertising trust and safety compliance officer.
Analyze the provided advertisement keyframe, extracted on-screen text, and speech transcript.
Evaluate the content against four statutory policy tiers:
1. SAFE_FOR_ALL: General audience, FMCG, electronics, education. Zero adult or violent themes.
2. SAFE_14_PLUS: Mild action, competitive esports, teen rhetoric. No alcohol, gambling, or gore.
3. SAFE_18_PLUS: Alcoholic beverages, casino gambling, adult dating, high-risk finance. Must contain mandatory health disclaimers.
4. UNSAFE_FOR_ALL: Prohibited weapons, illicit narcotics, non-consensual content, deceptive investment scams.

Input Data:
- Extracted OCR Text: "{ocr_text}"
- Audio Speech Transcript: "{asr_transcript}"

Respond strictly in valid JSON format:
{
  "reasoning": "<concise step-by-step policy justification>",
  "predicted_class": "<SAFE_FOR_ALL | SAFE_14_PLUS | SAFE_18_PLUS | UNSAFE_FOR_ALL>",
  "confidence_scores": {
    "SAFE_FOR_ALL": <float>, "SAFE_14_PLUS": <float>,
    "SAFE_18_PLUS": <float>, "UNSAFE_FOR_ALL": <float>
  },
  "statutory_risk_score": <float 0-100>
}
\end{lstlisting}

\section{Hierarchical Safety Fusion Protocol (Strategy D)}
SafeAd AI implements the \textbf{Strategy D Hierarchical Safety Protocol} to combine the deep semantic reasoning of Qwen3-VL with the empirical robustness of the Random Forest:
\begin{enumerate}
    \item \textbf{Rule 1 (Safety Veto):} If either model predicts \texttt{UNSAFE\_FOR\_ALL} with confidence $\ge 0.50$, or if the Random Forest prohibited probability exceeds $0.40$, the asset is quarantined immediately as \texttt{UNSAFE\_FOR\_ALL}.
    \item \textbf{Rule 2 (VLM Dominance on Safe Tiers):} In the absence of an unsafe veto, Qwen3-VL's semantic classification governs the distinction between \texttt{SAFE\_FOR\_ALL}, \texttt{SAFE\_14\_PLUS}, and \texttt{SAFE\_18\_PLUS}.
    \item \textbf{Rule 3 (Human Review Abstention):} If the top two class probabilities differ by less than $0.10$ ($\Delta p < 0.10$), the decision is routed to human compliance officers.
\end{enumerate}

Algorithm~\ref{alg:hierarchical_fusion} formalizes the Strategy D arbitration logic.

\begin{lstlisting}[language=Python, caption={Strategy D Hierarchical Safety Fusion Protocol}, label={alg:hierarchical_fusion}]
def strategy_d_hierarchical_fusion(rf_probs, vlm_decision, vlm_probs):
    # Rule 1: Zero-tolerance safety veto
    if vlm_decision == "UNSAFE_FOR_ALL" or rf_probs[3] >= 0.40:
        return "UNSAFE_FOR_ALL", max(vlm_probs[3], rf_probs[3]), "RULE_1_SAFETY_VETO"
    
    # Rule 2: Adult-tier confirmation
    if vlm_decision == "SAFE_18_PLUS" or rf_probs[2] >= 0.60:
        return "SAFE_18_PLUS", vlm_probs[2], "RULE_2_ADULT_TIER"
        
    # Rule 3: Abstention routing
    sorted_probs = np.sort(vlm_probs)[::-1]
    if (sorted_probs[0] - sorted_probs[1]) < 0.10:
        return vlm_decision, sorted_probs[0], "RULE_3_HUMAN_REVIEW_ABSTAIN"
        
    return vlm_decision, sorted_probs[0], "VLM_DOMINANCE"
\end{lstlisting}

\section{Real-Time Vision Engine and Concurrency Control}
To prevent hardware thread lockups on client workstations during concurrent webcam capture and neural inference, the vision engine implements an isolated DirectShow worker thread architecture. Figure~\ref{fig:vision_engine_concurrency} details the multi-threaded synchronization architecture.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.88\linewidth]{vision_engine_concurrency.png}
\caption{Real-Time Vision Engine Concurrency Architecture}
\label{fig:vision_engine_concurrency}
\end{figure}

The dedicated DirectShow capture thread runs as an independent daemon, continually grabbing raw frames into a thread-safe double buffer while background workers execute inference at 10~Hz, as formalized in Algorithm~\ref{alg:vision_concurrency}.

\begin{lstlisting}[language=Python, caption={DirectShow Thread-Safe Concurrency Routine}, label={alg:vision_concurrency}]
class AsyncVisionWorker(threading.Thread):
    def __init__(self, camera_index=0):
        super().__init__(daemon=True)
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        self.lock = threading.Lock()
        self.latest_frame = None
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.latest_frame = frame
            time.sleep(0.01)

    def get_frame(self):
        with self.lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None
\end{lstlisting}

\section{Presentation Attack Detection and Biometric Age Verification}
The client-side demographic assurance engine implements a hybrid anti-spoofing and face verification routine:
\begin{enumerate}
    \item \textbf{Dual-Scale MiniFASNet Ensemble:} Processes $80 \times 80$ and $112 \times 112$ facial crops to compute spatial liveness probabilities.
    \item \textbf{2D FFT Moir\'{e} Frequency Analysis:} Computes 2D Fast Fourier Transform of the facial region to isolate high-frequency energy ratio $R_{\text{moir\'{e}}}$, rejecting screen replay spoofs when $R_{\text{moir\'{e}}} \ge \tau_{\text{freq}}$.
    \item \textbf{ArcFace Deep Metric Embedding:} Live faces are mapped to a 512-dimensional unit hypersphere via ArcFace, optimized using the Additive Angular Margin Loss:
    \begin{equation}
    \mathcal{L}_{\text{ArcFace}} = -\log \frac{e^{s \left( \cos(\theta_{y_i} + m) \right)}}{e^{s \left( \cos(\theta_{y_i} + m) \right)} + \sum_{j \neq y_i} e^{s \cos \theta_j}}
    \end{equation}
    Cosine distance between document face and live face confirms identity when $S_{\text{match}} \ge 0.45$.
\end{enumerate}

Algorithm~\ref{alg:biometric_pad} presents the combined anti-spoofing and verification procedure.

\begin{lstlisting}[language=Python, caption={Hybrid Biometric PAD and Identity Verification Routine}, label={alg:biometric_pad}]
def verify_user_biometrics(doc_image, live_frame):
    face_crop = face_detector.crop(live_frame)
    if face_crop is None:
        return False, "NO_FACE_DETECTED", 0.0
    
    # Dual-Scale MiniFASNet Liveness
    spatial_score = mini_fasnet_ensemble.predict(face_crop)
    
    # 2D FFT Moire Analysis
    gray_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    f_shift = np.fft.fftshift(np.fft.fft2(gray_crop))
    magnitude_spectrum = 20 * np.log(np.abs(f_shift) + 1e-6)
    moire_score = compute_high_freq_ratio(magnitude_spectrum)
    
    if spatial_score < 0.65 or moire_score > 0.42:
        return False, "SPOOF_ATTACK_REJECTED", 0.0
        
    # ArcFace Identity Matching
    doc_embedding = arcface_model.extract_embedding(doc_image)
    live_embedding = arcface_model.extract_embedding(face_crop)
    cosine_sim = np.dot(doc_embedding, live_embedding)
    
    if cosine_sim >= 0.45:
        return True, "GENUINE_VERIFIED", cosine_sim
    else:
        return False, "IDENTITY_MISMATCH", cosine_sim
\end{lstlisting}
"""
