"""
Academic Diagram Generator: System Architecture & Model Workflows
SAFE-VISION (SafeAd AI) Trust and Safety Framework
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

# Global style configuration
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['mathtext.fontset'] = 'dejavusans'

# Academic Color Palette
COLOR_NAVY = '#1E3A8A'      # Primary accent / headings
COLOR_NAVY_LIGHT = '#EFF6FF'# Light background fill
COLOR_BORDER_BLUE = '#3B82F6'

COLOR_SLATE = '#334155'     # Structural boxes & dark text
COLOR_SLATE_LIGHT = '#F8FAFC'# Neutral canvas background
COLOR_BORDER_SLATE = '#94A3B8'

COLOR_TEAL = '#0F766E'      # Secondary process highlight
COLOR_TEAL_LIGHT = '#F0FDFA'
COLOR_BORDER_TEAL = '#14B8A6'

COLOR_AMBER = '#B45309'     # Warning / Intermediate tier
COLOR_AMBER_LIGHT = '#FFFBEB'
COLOR_BORDER_AMBER = '#F59E0B'

COLOR_RED = '#B91C1C'       # Prohibited / Veto
COLOR_RED_LIGHT = '#FEF2F2'
COLOR_BORDER_RED = '#EF4444'

COLOR_PURPLE = '#6D28D9'    # Experimental VLM
COLOR_PURPLE_LIGHT = '#FAF5FF'
COLOR_BORDER_PURPLE = '#A855F7'

TEXT_DARK = '#0F172A'
TEXT_MUTED = '#475569'

def draw_box(ax, x, y, w, h, title="", subtitle="", facecolor='#FFFFFF', edgecolor='#334155',
             title_color=TEXT_DARK, sub_color=TEXT_MUTED, title_size=10, sub_size=8,
             boxstyle="round,pad=0.15", linewidth=1.2, linestyle='-'):
    """Helper to draw academic standardized boxes with title and subtitle."""
    rect = FancyBboxPatch((x, y), w, h, boxstyle=boxstyle,
                          facecolor=facecolor, edgecolor=edgecolor,
                          linewidth=linewidth, linestyle=linestyle)
    ax.add_patch(rect)
    if title:
        cy = y + h * 0.65 if subtitle else y + h * 0.5
        ax.text(x + w * 0.5, cy, title, ha='center', va='center',
                fontsize=title_size, fontweight='bold', color=title_color)
    if subtitle:
        ax.text(x + w * 0.5, y + h * 0.32, subtitle, ha='center', va='center',
                fontsize=sub_size, color=sub_color)
    return rect

def draw_arrow(ax, x1, y1, x2, y2, label="", color='#475569', lw=1.2, label_color=TEXT_MUTED, label_size=7.5):
    """Helper to draw clean straight arrows with centered text label."""
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                            mutation_scale=12, color=color, linewidth=lw)
    ax.add_patch(arrow)
    if label:
        mx, my = (x1 + x2) * 0.5, (y1 + y2) * 0.5
        ax.text(mx, my + 0.12, label, ha='center', va='bottom',
                fontsize=label_size, color=label_color,
                bbox=dict(boxstyle='square,pad=0.1', facecolor='#FFFFFF', edgecolor='none', alpha=0.85))

# ==============================================================================
# 1. COMPLETE SAFE-VISION SYSTEM ARCHITECTURE
# ==============================================================================
def create_system_architecture(out_dir):
    fig, ax = plt.subplots(figsize=(16, 9.5), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Header
    ax.text(8.0, 9.15, 'SafeAd AI: Multimodal Pre-Publication Moderation & Biometric Age-Gated Delivery Architecture',
            ha='center', va='center', fontsize=14, fontweight='bold', color=COLOR_NAVY)
    ax.text(8.0, 8.85, 'Decoupled Production Backend & Experimental Foundation Model Arbitration',
            ha='center', va='center', fontsize=9.5, fontstyle='italic', color=TEXT_MUTED)

    # -------------------------------------------------------------
    # SUBSYSTEM 1: ADVERTISEMENT MODERATION PIPELINE (Top Half)
    # -------------------------------------------------------------
    sub1_bg = FancyBboxPatch((0.5, 4.2), 15.0, 4.3, boxstyle="round,pad=0.2",
                             facecolor=COLOR_SLATE_LIGHT, edgecolor=COLOR_BORDER_SLATE, linewidth=1.0)
    ax.add_patch(sub1_bg)
    ax.text(0.8, 8.25, 'SUBSYSTEM 1: MULTIMODAL ADVERTISEMENT MODERATION PIPELINE',
            ha='left', va='center', fontsize=10, fontweight='bold', color=COLOR_NAVY)

    # Block 1.1: Ingestion
    draw_box(ax, 0.8, 6.2, 2.2, 1.6, title='Media Submission',
             subtitle='MP4/MOV Video\nStatic JPEG/PNG\nCampaign Metadata',
             facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE)

    # Block 1.2: Preprocessing
    draw_box(ax, 3.4, 6.2, 2.6, 1.6, title='Media Preprocessing',
             subtitle='Farnebäck Optical Flow\nCLAHE & Otsu Binarization\nFFmpeg 16kHz PCM Audio',
             facecolor=COLOR_TEAL_LIGHT, edgecolor=COLOR_BORDER_TEAL)

    # Block 1.3: Specialized Detectors
    draw_box(ax, 6.4, 6.0, 3.0, 2.0, title='Specialized Detectors',
             subtitle='Falcon NSFW ViT (Visual Adult)\nVideoMAE (Kinetic Violence)\nEasyOCR (Typographic Text)\nWhisper (Speech Transcript)\nDeBERTa-v3 (Toxicity & Scams)',
             facecolor='#FFFFFF', edgecolor=COLOR_BORDER_SLATE, sub_size=7.5)

    # Block 1.4A: Production Random Forest Late Fusion
    draw_box(ax, 9.8, 6.8, 2.6, 1.3, title='Random Forest Fusion',
             subtitle='33-Dim Feature Vector\n100-Tree Balanced Forest\nProduction Backend',
             facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE)

    # Block 1.4B: Experimental Qwen3-VL VLM
    draw_box(ax, 9.8, 4.8, 2.6, 1.5, title='Qwen3-VL-8B-Instruct',
             subtitle='Experimental Colab (A100)\nStructured Policy Prompt\nChain-of-Thought Rationale',
             facecolor=COLOR_PURPLE_LIGHT, edgecolor=COLOR_BORDER_PURPLE, linestyle='--')

    # Block 1.5: Hierarchical Fusion Engine (Strategy D)
    draw_box(ax, 12.8, 5.4, 2.4, 2.0, title='Strategy D Fusion',
             subtitle='Rule 1: Safety Veto (UFA)\nRule 2: Adult-Tier Conf.\nRule 3: Human Abstention\nFour-Class Prediction',
             facecolor=COLOR_AMBER_LIGHT, edgecolor=COLOR_BORDER_AMBER, sub_size=7.5)

    # Arrows for Subsystem 1
    draw_arrow(ax, 3.0, 7.0, 3.4, 7.0, label='Raw Media')
    draw_arrow(ax, 6.0, 7.0, 6.4, 7.0, label='Keyframes/Audio')
    draw_arrow(ax, 9.4, 7.4, 9.8, 7.4, label='Scores')
    draw_arrow(ax, 9.4, 6.4, 9.8, 5.6, label='Multimodal Text')
    draw_arrow(ax, 12.4, 7.4, 12.8, 6.8, label='RF Vector')
    draw_arrow(ax, 12.4, 5.6, 12.8, 6.0, label='VLM Decision')

    # -------------------------------------------------------------
    # SUBSYSTEM 2: BIOMETRIC AGE ASSURANCE & DELIVERY (Bottom Half)
    # -------------------------------------------------------------
    sub2_bg = FancyBboxPatch((0.5, 0.4), 15.0, 3.5, boxstyle="round,pad=0.2",
                             facecolor='#F1F5F9', edgecolor=COLOR_BORDER_SLATE, linewidth=1.0)
    ax.add_patch(sub2_bg)
    ax.text(0.8, 3.65, 'SUBSYSTEM 2: BIOMETRIC IDENTITY VERIFICATION & AGE-AWARE DISPATCHING',
            ha='left', va='center', fontsize=10, fontweight='bold', color=COLOR_NAVY)

    # Block 2.1: Client Input
    draw_box(ax, 0.8, 1.2, 2.2, 1.8, title='Client Verification',
             subtitle='Live Webcam Stream\n(DirectShow Daemon)\nDigitized ID Card\n(Birthdate + Face)',
             facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE)

    # Block 2.2: Face Preprocessing
    draw_box(ax, 3.4, 1.2, 2.6, 1.8, title='Face Preprocessing',
             subtitle='MTCNN Face Crop\n5-Point Landmark Align\nNormalized 112x112 Crop\nTesseract ID OCR',
             facecolor=COLOR_TEAL_LIGHT, edgecolor=COLOR_BORDER_TEAL)

    # Block 2.3: Anti-Spoofing & Matching
    draw_box(ax, 6.4, 1.2, 3.0, 1.8, title='Biometric Security & PAD',
             subtitle='Dual MiniFASNet (Spatial)\n2D FFT Moiré Spectrum\nHough Bezel / Glare Detector\nArcFace (Cosine Sim >= 0.45)',
             facecolor='#FFFFFF', edgecolor=COLOR_BORDER_SLATE, sub_size=7.5)

    # Block 2.4: Demographic Verification
    draw_box(ax, 9.8, 1.2, 2.6, 1.8, title='Demographic Classification',
             subtitle='ViT Age Regressor\nID DOB vs Face Match\nVerified Tier:\nUNDER_14 | 14-17 | 18+',
             facecolor=COLOR_AMBER_LIGHT, edgecolor=COLOR_BORDER_AMBER)

    # Block 2.5: Age-Aware Delivery Dispatcher
    draw_box(ax, 12.8, 1.2, 2.4, 1.8, title='Delivery Dispatcher',
             subtitle='Deterministic Gating:\nDeliver | Suppress |\nQuarantine | Review\nZero Underage Exposure',
             facecolor=COLOR_TEAL_LIGHT, edgecolor=COLOR_BORDER_TEAL)

    # Arrows for Subsystem 2
    draw_arrow(ax, 3.0, 2.1, 3.4, 2.1, label='Live & ID')
    draw_arrow(ax, 6.0, 2.1, 6.4, 2.1, label='Crops & OCR')
    draw_arrow(ax, 9.4, 2.1, 9.8, 2.1, label='Liveness OK')
    draw_arrow(ax, 12.4, 2.1, 12.8, 2.1, label='Age Bracket')

    # Cross-Subsystem Gating Arrow: Moderation Verdict -> Delivery Dispatcher
    draw_arrow(ax, 14.0, 5.4, 14.0, 3.0, label='Statutory Class', color=COLOR_RED, lw=1.5, label_color=COLOR_RED)

    # Output paths from Delivery Dispatcher
    ax.text(14.0, 0.75, 'Feed Delivery Clearance / Administrative Audit Quarantine',
            ha='center', va='center', fontsize=8.5, fontweight='bold', color=TEXT_DARK)

    plt.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    fig.savefig(os.path.join(out_dir, 'safevision_system_architecture.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, 'safevision_system_architecture.svg'), bbox_inches='tight')
    plt.close(fig)
    print("Exported safevision_system_architecture.png & .svg")

# ==============================================================================
# 2. MULTIMODAL ADVERTISEMENT ANALYSIS PIPELINE
# ==============================================================================
def create_multimodal_processing_pipeline(out_dir):
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Title
    ax.text(7.0, 7.6, 'SAFE-VISION: Multimodal Feature Extraction & Modality Alignment Flowchart',
            ha='center', va='center', fontsize=13, fontweight='bold', color=COLOR_NAVY)

    # Modality 1: Video Frames
    draw_box(ax, 0.6, 5.6, 2.4, 1.2, title='Video Asset', subtitle='Temporal Stream (MP4/H.264)', facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE)
    draw_box(ax, 3.5, 5.6, 2.8, 1.2, title='Optical Flow Sampling', subtitle='Farnebäck Dense Motion Vector\nScene-Cut Detection', facecolor=COLOR_TEAL_LIGHT, edgecolor=COLOR_BORDER_TEAL)
    draw_box(ax, 6.8, 5.6, 3.0, 1.2, title='VideoMAE & Falcon ViT', subtitle='16-Frame Kinetic Tubelets\nAdult Image Probability', facecolor='#FFFFFF', edgecolor=COLOR_BORDER_SLATE)

    # Modality 2: On-Screen Text (OCR)
    draw_box(ax, 0.6, 3.8, 2.4, 1.2, title='On-Screen Visuals', subtitle='Typographic Overlays', facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE)
    draw_box(ax, 3.5, 3.8, 2.8, 1.2, title='CLAHE & Otsu Filter', subtitle='Contrast Clipping (Limit 2.0)\nAdaptive Binarization', facecolor=COLOR_TEAL_LIGHT, edgecolor=COLOR_BORDER_TEAL)
    draw_box(ax, 6.8, 3.8, 3.0, 1.2, title='EasyOCR Engine', subtitle='English Dictionary Lookup\nBounding Box & Confidence', facecolor='#FFFFFF', edgecolor=COLOR_BORDER_SLATE)

    # Modality 3: Audio Stream
    draw_box(ax, 0.6, 2.0, 2.4, 1.2, title='Audio Track', subtitle='16 kHz Mono PCM Waveform', facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE)
    draw_box(ax, 3.5, 2.0, 2.8, 1.2, title='STFT Spectrogram', subtitle='80-Channel Mel-Scale\nLog-Magnitude Matrix', facecolor=COLOR_TEAL_LIGHT, edgecolor=COLOR_BORDER_TEAL)
    draw_box(ax, 6.8, 2.0, 3.0, 1.2, title='Whisper ASR', subtitle='Encoder-Decoder Transformer\nSpoken Claim Transcription', facecolor='#FFFFFF', edgecolor=COLOR_BORDER_SLATE)

    # NLP Semantic Analysis (Combines OCR & Whisper)
    draw_box(ax, 10.3, 2.6, 3.2, 2.0, title='NLP & Claim Analysis', subtitle='RoBERTa / DeBERTa-v3\nToxicity, Scam & Urgency Heuristics\nRegulated Goods Pattern Scans\n(Alcohol, Betting, Tobacco)', facecolor=COLOR_AMBER_LIGHT, edgecolor=COLOR_BORDER_AMBER, sub_size=7.5)

    # Late Fusion Integration Box
    draw_box(ax, 10.3, 5.2, 3.2, 1.6, title='Fused Feature Vector', subtitle='Aligned Multimodal Evidence\nVisual + Motion + Text + Speech\nPassed to Decision Engines', facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE)

    # Connectors
    draw_arrow(ax, 3.0, 6.2, 3.5, 6.2)
    draw_arrow(ax, 6.3, 6.2, 6.8, 6.2)
    draw_arrow(ax, 9.8, 6.2, 10.3, 6.0, label='Visual/Motion')

    draw_arrow(ax, 3.0, 4.4, 3.5, 4.4)
    draw_arrow(ax, 6.3, 4.4, 6.8, 4.4)
    draw_arrow(ax, 9.8, 4.4, 10.3, 3.8, label='OCR Text')

    draw_arrow(ax, 3.0, 2.6, 3.5, 2.6)
    draw_arrow(ax, 6.3, 2.6, 6.8, 2.6)
    draw_arrow(ax, 9.8, 2.6, 10.3, 3.2, label='Speech Text')

    draw_arrow(ax, 11.9, 4.6, 11.9, 5.2, label='Semantic Risks')

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'multimodal_processing_pipeline.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, 'multimodal_processing_pipeline.svg'), bbox_inches='tight')
    plt.close(fig)
    print("Exported multimodal_processing_pipeline.png & .svg")

# ==============================================================================
# 3. RANDOM FOREST LATE FUSION ARCHITECTURE
# ==============================================================================
def create_random_forest_late_fusion(out_dir):
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Title
    ax.text(7.5, 8.0, 'Phase 8E Learned Late-Fusion Architecture: 33-Dimensional Random Forest Classifier',
            ha='center', va='center', fontsize=13, fontweight='bold', color=COLOR_NAVY)

    # Stage 1: Detector Outputs
    draw_box(ax, 0.5, 4.5, 3.0, 2.8, title='Detector Evidence Streams',
             subtitle='Visual (is_video, nsfw, violence, child_safety)\nVideo (motion kinetics, adult, child_safety)\nOCR (confidence, scam, adult, child_safety)\nAudio (violence, adult, child_safety, deceptive)\nText NLP (overall_risk, hate, gamble, alcohol)\nCommercial Claim Scans (urgency, return_guar)',
             facecolor=COLOR_SLATE_LIGHT, edgecolor=COLOR_BORDER_SLATE, sub_size=7.2)

    # Stage 2: 33-Dimensional Feature Vector
    draw_box(ax, 4.0, 4.2, 3.2, 3.4, title='33-Dim Feature Vector',
             subtitle='[01] is_video\n[02-05] visual_unsafe/violence/adult/child\n[06-08] video_violence/adult/child\n[09-14] ocr_conf/violence/adult/scam/decept\n[15-20] audio_viol/adult/child/scam/decept\n[21-28] text_risk/hate/gamble/alcohol/drugs\n[29-31] ad_risk_scam/decept/explicit\n[32-33] alcohol_detected/alcohol_score',
             facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE, sub_size=7.2)

    # Stage 3: Random Forest Classifier
    draw_box(ax, 7.8, 4.5, 3.4, 2.8, title='Random Forest Ensemble',
             subtitle='100 Decision Trees (n_estimators=100)\nBalanced Class Weights\nMax Depth = 4 | Min Samples Leaf = 3\nStratified 5-Fold Cross-Validation\nOut-of-Fold Probability Aggregation',
             facecolor=COLOR_TEAL_LIGHT, edgecolor=COLOR_BORDER_TEAL, sub_size=7.8)

    # Stage 4: Probability Distribution
    draw_box(ax, 11.8, 5.2, 2.8, 2.1, title='Calibrated Probability',
             subtitle='p(SAFE_FOR_ALL)\np(SAFE_14_PLUS)\np(SAFE_18_PLUS)\np(UNSAFE_FOR_ALL)\nargmax -> Initial Label',
             facecolor=COLOR_AMBER_LIGHT, edgecolor=COLOR_BORDER_AMBER, sub_size=7.5)

    # Stage 5: Optional Uncertainty HITL Routing
    draw_box(ax, 11.8, 1.8, 2.8, 1.8, title='Uncertainty Review Fallback',
             subtitle='If Entropy(p) > tau\nOR (p_top1 - p_top2) < 0.10\nRoute to Human Compliance Queue\nZero Blind False Acceptances',
             facecolor=COLOR_RED_LIGHT, edgecolor=COLOR_BORDER_RED, sub_size=7.5)

    # Connectors
    draw_arrow(ax, 3.5, 5.9, 4.0, 5.9, label='Feature Extraction')
    draw_arrow(ax, 7.2, 5.9, 7.8, 5.9, label='Input Vector')
    draw_arrow(ax, 11.2, 5.9, 11.8, 6.2, label='Inference')
    draw_arrow(ax, 13.2, 5.2, 13.2, 3.6, label='Uncertainty Check', color=COLOR_RED)

    # Baseline performance note
    note = ("Verified Phase 8E 5-Fold Benchmark (N=194):\n"
            "• Overall Accuracy: 44.33% (Macro-F1: 0.4110) | Automated Coverage: 100.0%\n"
            "• Policy-First HITL Variant: 49 abstentions (74.7% coverage) with reduced leakage")
    ax.text(0.5, 1.8, note, fontsize=8.5, color=TEXT_DARK,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8FAFC', edgecolor='#CBD5E1'))

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'random_forest_late_fusion.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, 'random_forest_late_fusion.svg'), bbox_inches='tight')
    plt.close(fig)
    print("Exported random_forest_late_fusion.png & .svg")

# ==============================================================================
# 4. QWEN3-VL INFERENCE ARCHITECTURE (A100 COLAB)
# ==============================================================================
def create_qwen3_vl_inference_pipeline(out_dir):
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Title
    ax.text(7.5, 8.0, 'Phase 10: Vision-Language Model (Qwen3-VL-8B-Instruct) Policy Reasoning Architecture',
            ha='center', va='center', fontsize=13, fontweight='bold', color=COLOR_NAVY)

    # Stage 1: Multimodal Context Assembly
    draw_box(ax, 0.5, 4.2, 3.2, 3.2, title='Multimodal Creative Input',
             subtitle='Keyframe Images (H x W x 3)\nAuthentic EasyOCR Text\nWhisper Spoken Transcript\nZero Label Exposure\nNeutral Context Formulation',
             facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE)

    # Stage 2: Fixed Policy System Prompt
    draw_box(ax, 4.2, 4.2, 3.4, 3.2, title='Fixed Policy Prompt Guardrail',
             subtitle='Role: Senior Ad Trust & Safety Officer\nDefinitions of 4 Statutory Tiers\nCommercial Nuance Rubrics:\n• Responsible Alcohol != Unsafe\n• Stylized Action != Real Violence\n• Deceptive Urgency == Unsafe',
             facecolor=COLOR_TEAL_LIGHT, edgecolor=COLOR_BORDER_TEAL, sub_size=7.5)

    # Stage 3: Qwen3-VL-8B Engine
    draw_box(ax, 8.1, 4.2, 3.3, 3.2, title='Qwen3-VL-8B-Instruct',
             subtitle='Google Colab (A100-SXM4-40GB)\nNative torch.bfloat16 (16.33 GB VRAM)\nAutoProcessor Visual Encoding\nAutoregressive Reasoning Tokens\nDeterministic Greedy Decoding',
             facecolor=COLOR_PURPLE_LIGHT, edgecolor=COLOR_BORDER_PURPLE, sub_size=7.5)

    # Stage 4: Structured Output & JSON Validation
    draw_box(ax, 11.9, 4.2, 2.7, 3.2, title='Structured Output Contract',
             subtitle='JSON Schema Validation:\n• reasoning (Chain-of-Thought)\n• predicted_class (4 Tiers)\n• confidence_scores (Floats)\n• statutory_risk_score (0-100)\nFallback on Parsing Failure',
             facecolor=COLOR_AMBER_LIGHT, edgecolor=COLOR_BORDER_AMBER, sub_size=7.5)

    # Connectors
    draw_arrow(ax, 3.7, 5.8, 4.2, 5.8, label='Asset Context')
    draw_arrow(ax, 7.6, 5.8, 8.1, 5.8, label='Aligned Prompt')
    draw_arrow(ax, 11.4, 5.8, 11.9, 5.8, label='Tokens')

    # Diagnostic Findings Box
    diag = ("Empirical Diagnostic Verification:\n"
            "• Phase 10B (Dev N=16): 75.0% accuracy (12/16) | 100% prohibited recall | Resolved Llama Guard concept blindness\n"
            "• Phase 10D (Test N=27): 66.7% accuracy (18/27) | 100% prohibited recall | 0% severe false acceptance")
    ax.text(0.5, 1.8, diag, fontsize=8.5, color=TEXT_DARK,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8FAFC', edgecolor='#CBD5E1'))

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'qwen3_vl_inference_pipeline.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, 'qwen3_vl_inference_pipeline.svg'), bbox_inches='tight')
    plt.close(fig)
    print("Exported qwen3_vl_inference_pipeline.png & .svg")

# ==============================================================================
# 5. HIERARCHICAL FUSION ARCHITECTURE (STRATEGY D)
# ==============================================================================
def create_hierarchical_fusion_architecture(out_dir):
    fig, ax = plt.subplots(figsize=(15, 9), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Title
    ax.text(7.5, 8.5, 'Strategy D: Frozen Hierarchical Safety Fusion Protocol',
            ha='center', va='center', fontsize=13, fontweight='bold', color=COLOR_NAVY)

    # Inputs
    draw_box(ax, 0.5, 6.0, 3.2, 1.8, title='Random Forest Classifier',
             subtitle='Production 33-Dim Model\np_rf = [SFA, S14P, S18P, UFA]\nHigh sensitivity to keywords',
             facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE)

    draw_box(ax, 0.5, 3.5, 3.2, 1.8, title='Qwen3-VL Foundation Model',
             subtitle='A100 GPU Vision-Language Model\nContextual Reasoning Verdict\np_vlm = [SFA, S14P, S18P, UFA]',
             facecolor=COLOR_PURPLE_LIGHT, edgecolor=COLOR_BORDER_PURPLE)

    # Arbitration Rules
    # Rule 1: Safety Veto
    draw_box(ax, 4.6, 6.2, 4.8, 1.6, title='Rule 1: Zero-Tolerance Safety Veto',
             subtitle='IF (vlm_pred == UNSAFE_FOR_ALL) OR (p_rf[UFA] >= 0.40)\n==> QUARANTINE as UNSAFE_FOR_ALL (Risk = 95.0)',
             facecolor=COLOR_RED_LIGHT, edgecolor=COLOR_BORDER_RED, sub_size=8.0)

    # Rule 2: Adult-Tier Confirmation
    draw_box(ax, 4.6, 4.3, 4.8, 1.6, title='Rule 2: Adult Commerce Arbitration',
             subtitle='IF (vlm_pred == SAFE_18_PLUS) OR (p_rf[S18P] >= 0.60)\n==> CONFIRM as SAFE_18_PLUS (Gated Delivery)',
             facecolor=COLOR_AMBER_LIGHT, edgecolor=COLOR_BORDER_AMBER, sub_size=8.0)

    # Rule 3 & 4: Safe Tiers & Abstention
    draw_box(ax, 4.6, 2.4, 4.8, 1.6, title='Rule 3 & 4: Safe Tiers & HITL Fallback',
             subtitle='IF (p_top1 - p_top2) < 0.10 ==> Route to Human Review\nELSE ==> Qwen3-VL Semantic Dominance (SFA / S14P)',
             facecolor=COLOR_TEAL_LIGHT, edgecolor=COLOR_BORDER_TEAL, sub_size=8.0)

    # Outputs
    draw_box(ax, 10.4, 6.2, 3.8, 1.6, title='UNSAFE_FOR_ALL',
             subtitle='Ad Quarantined | Auctions Halted\nAdvertiser Account Flagged for Audit',
             facecolor=COLOR_RED_LIGHT, edgecolor=COLOR_BORDER_RED)

    draw_box(ax, 10.4, 4.3, 3.8, 1.6, title='SAFE_18_PLUS / SAFE_14_PLUS',
             subtitle='Age Gating Activated | ArcFace Matching\nDelivery Suppressed for Minors',
             facecolor=COLOR_AMBER_LIGHT, edgecolor=COLOR_BORDER_AMBER)

    draw_box(ax, 10.4, 2.4, 3.8, 1.6, title='SAFE_FOR_ALL / HUMAN_REVIEW',
             subtitle='Unrestricted Family Audience Delivery\nOR Manual Compliance Officer Queue',
             facecolor=COLOR_TEAL_LIGHT, edgecolor=COLOR_BORDER_TEAL)

    # Arrows
    draw_arrow(ax, 3.7, 6.9, 4.6, 7.0, label='RF Vector')
    draw_arrow(ax, 3.7, 4.4, 4.6, 5.0, label='VLM Output')
    draw_arrow(ax, 9.4, 7.0, 10.4, 7.0, label='Veto Triggered', color=COLOR_RED)
    draw_arrow(ax, 9.4, 5.1, 10.4, 5.1, label='Adult Confirmed', color=COLOR_AMBER)
    draw_arrow(ax, 9.4, 3.2, 10.4, 3.2, label='Safe / Abstain', color=COLOR_TEAL)

    # Footer note
    note = ("Generalization Performance on Held-Out Test Data (Phase 10D, N=27):\n"
            "• 4-Class Accuracy: 66.7% (18/27) | Prohibited Recall: 100.0% (4/4) | Prohibited FAR: 0.0% (Zero Safety Breaches)\n"
            "• Rescued Vintage Tobacco ad from VLM evasion; eradicated RF's 75% safety leakage on physical demolition assets.")
    ax.text(0.5, 0.9, note, fontsize=8.5, color=TEXT_DARK,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8FAFC', edgecolor='#CBD5E1'))

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'hierarchical_fusion_architecture.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, 'hierarchical_fusion_architecture.svg'), bbox_inches='tight')
    plt.close(fig)
    print("Exported hierarchical_fusion_architecture.png & .svg")

# ==============================================================================
# 6. AGE VERIFICATION & ANTI-SPOOFING WORKFLOW
# ==============================================================================
def create_age_verification_workflow(out_dir):
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    # Title
    ax.text(7.5, 8.0, 'Biometric Age Assurance & Presentation Attack Detection (PAD) Workflow',
            ha='center', va='center', fontsize=13, fontweight='bold', color=COLOR_NAVY)

    # Step 1: Capture
    draw_box(ax, 0.5, 4.5, 2.6, 2.6, title='Decoupled Capture',
             subtitle='DirectShow Video Capture\nIndependent Daemon Thread\nLock-Protected Frame Buffer\nDigitized ID Card Capture',
             facecolor=COLOR_NAVY_LIGHT, edgecolor=COLOR_BORDER_BLUE)

    # Step 2: Detection & Alignment
    draw_box(ax, 3.5, 4.5, 2.7, 2.6, title='Face Preprocessing',
             subtitle='MTCNN Deep Face Detection\n5-Point Facial Landmarks\nSimilarity Transform Alignment\nNormalized 112x112 Crop',
             facecolor=COLOR_TEAL_LIGHT, edgecolor=COLOR_BORDER_TEAL)

    # Step 3: Multi-Evidence PAD
    draw_box(ax, 6.6, 4.5, 3.4, 2.6, title='Presentation Attack Detection',
             subtitle='Dual-Scale MiniFASNet (80 & 112)\n2D FFT High-Freq Moiré Ratio\nHough Probabilistic Line Bezel Check\nHSV Specular Glare Detection\nThreshold: p_live >= 0.65',
             facecolor='#FFFFFF', edgecolor=COLOR_BORDER_SLATE, sub_size=7.5)

    # Step 4: ArcFace & ID Verification
    draw_box(ax, 10.4, 4.5, 4.0, 2.6, title='Biometric Identity & Age Gating',
             subtitle='ArcFace Additive Angular Margin Loss\n512-Dim Cosine Distance (tau = 0.45)\nViT Facial Chronological Age Regressor\nTesseract OCR Date-of-Birth Extraction\nVerified Demographic Category Generation',
             facecolor=COLOR_AMBER_LIGHT, edgecolor=COLOR_BORDER_AMBER, sub_size=7.5)

    # Connectors
    draw_arrow(ax, 3.1, 5.8, 3.5, 5.8, label='Raw Frames')
    draw_arrow(ax, 6.2, 5.8, 6.6, 5.8, label='Aligned Face')
    draw_arrow(ax, 10.0, 5.8, 10.4, 5.8, label='Live Verified')

    # Liveness Rejection Fallback
    draw_box(ax, 6.6, 1.8, 3.4, 1.8, title='Spoof Rejection Fallback',
             subtitle='Screen Replay / Print Photo Blocked\nDelivery Immediate Quarantine\nAudit Record Serialized',
             facecolor=COLOR_RED_LIGHT, edgecolor=COLOR_BORDER_RED)
    draw_arrow(ax, 8.3, 4.5, 8.3, 3.6, label='Spoof Detected', color=COLOR_RED)

    # Empirical Metrics
    note = ("Verified Biometric Performance:\n"
            "• ArcFace Identity Matching: 96.50% True Accept Rate (TAR) at 0.1% False Accept Rate (FAR)\n"
            "• Presentation Attack Detection: 93.00% Detection Accuracy against 2D Screen Replay & Print Attacks")
    ax.text(0.5, 2.0, note, fontsize=8.5, color=TEXT_DARK,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8FAFC', edgecolor='#CBD5E1'))

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'age_verification_workflow.png'), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, 'age_verification_workflow.svg'), bbox_inches='tight')
    plt.close(fig)
    print("Exported age_verification_workflow.png & .svg")

def main():
    arch_dir = os.path.join('report_assets_final', 'architecture')
    wf_dir = os.path.join('report_assets_final', 'model_workflows')
    os.makedirs(arch_dir, exist_ok=True)
    os.makedirs(wf_dir, exist_ok=True)

    create_system_architecture(arch_dir)
    create_multimodal_processing_pipeline(wf_dir)
    create_random_forest_late_fusion(wf_dir)
    create_qwen3_vl_inference_pipeline(wf_dir)
    create_hierarchical_fusion_architecture(wf_dir)
    create_age_verification_workflow(wf_dir)

if __name__ == '__main__':
    main()
