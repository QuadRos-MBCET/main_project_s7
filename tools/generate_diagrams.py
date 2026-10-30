import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

# Set font and style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

os.makedirs('overleaf_figures', exist_ok=True)

# ==============================================================================
# DIAGRAM 1: End-to-End System Architecture Pipeline
# ==============================================================================
def create_system_architecture():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Color palette
    bg_color = '#F8FAFC'
    border_color = '#CBD5E1'
    t1_color = '#EFF6FF' # Blue
    t1_border = '#3B82F6'
    t2_color = '#F0FDF4' # Green
    t2_border = '#10B981'
    t3_color = '#FAF5FF' # Purple
    t3_border = '#8B5CF6'
    dark_text = '#0F172A'
    sub_text = '#475569'

    # Canvas background
    fig.patch.set_facecolor('#FFFFFF')

    # Header Title
    ax.text(8.0, 9.6, 'SafeAd AI: Multimodal Pre-Publication Moderation & Biometric Age-Gated Delivery Architecture',
            ha='center', va='center', fontsize=16, fontweight='bold', color=dark_text)
    ax.text(8.0, 9.25, 'Decoupled Three-Tier Architecture with Zero-Tolerance Safety Veto and Dual-Stream Concurrency',
            ha='center', va='center', fontsize=11, fontstyle='italic', color=sub_text)

    # -------------------------------------------------------------
    # TIER 1: CLIENT PRESENTATION LAYER (Top / Left)
    # -------------------------------------------------------------
    rect1 = patches.FancyBboxPatch((0.5, 5.0), 3.2, 3.8, boxstyle="round,pad=0.15",
                                  facecolor=t1_color, edgecolor=t1_border, linewidth=2.0)
    ax.add_patch(rect1)
    ax.text(2.1, 8.5, 'TIER 1: PRESENTATION LAYER', ha='center', va='center', fontsize=11, fontweight='bold', color=t1_border)

    t1_boxes = [
        ('Advertiser Portal', 'Media Asset Ingestion (Images/Video)\nClient-side validation & hashing', 7.7),
        ('Compliance Dashboard', 'Forensic Multimodal Telemetry HUD\nHITL Audit Queue & Manual Overrides', 6.6),
        ('Recipient Age HUD', 'DirectShow 30 FPS Camera Feed\nLive Biometric & Liveness Meters', 5.5)
    ]
    for title, desc, y in t1_boxes:
        box = patches.FancyBboxPatch((0.7, y - 0.4), 2.8, 0.8, boxstyle="round,pad=0.08",
                                     facecolor='#FFFFFF', edgecolor='#94A3B8', linewidth=1.0)
        ax.add_patch(box)
        ax.text(2.1, y + 0.1, title, ha='center', va='center', fontsize=9, fontweight='bold', color=dark_text)
        ax.text(2.1, y - 0.18, desc, ha='center', va='center', fontsize=7.5, color=sub_text)

    # -------------------------------------------------------------
    # TIER 2: CORE BACKEND & DETECTOR ENGINE (Middle)
    # -------------------------------------------------------------
    rect2 = patches.FancyBboxPatch((4.2, 0.8), 7.2, 8.0, boxstyle="round,pad=0.15",
                                  facecolor=t2_color, edgecolor=t2_border, linewidth=2.0)
    ax.add_patch(rect2)
    ax.text(7.8, 8.5, 'TIER 2: CORE BACKEND & DETECTOR ENGINE (Python / FastAPI / PyTorch)',
            ha='center', va='center', fontsize=11, fontweight='bold', color=t2_border)

    # Sub-block A: Multimodal Extraction Pipeline
    box_a = patches.FancyBboxPatch((4.5, 5.7), 6.6, 2.4, boxstyle="round,pad=0.1",
                                  facecolor='#FFFFFF', edgecolor='#64748B', linewidth=1.2)
    ax.add_patch(box_a)
    ax.text(7.8, 7.85, 'Subsystem A: Multimodal Extraction Workers', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1E293B')

    extractors = [
        ('EasyOCR + CLAHE', 'Text extraction & toxicity dictionaries', 5.3, 7.2),
        ('ResNet50 / ViT', 'Visual hazard & Falcon NSFW heads', 7.8, 7.2),
        ('Whisper Audio', '16 kHz speech transcription', 10.3, 7.2),
        ('Farnebäck Flow', 'Motion energy & adaptive keyframes', 5.3, 6.2),
        ('VideoMAE ViT', 'Temporal action & violent kinetics', 7.8, 6.2),
        ('AdRisk Regex', 'Deception, scam & lottery rules', 10.3, 6.2),
    ]
    for name, desc, x, y in extractors:
        eb = patches.FancyBboxPatch((x - 1.1, y - 0.35), 2.2, 0.7, boxstyle="round,pad=0.05",
                                   facecolor='#F1F5F9', edgecolor='#CBD5E1', linewidth=0.8)
        ax.add_patch(eb)
        ax.text(x, y + 0.08, name, ha='center', va='center', fontsize=8, fontweight='bold', color=dark_text)
        ax.text(x, y - 0.15, desc, ha='center', va='center', fontsize=6.5, color=sub_text)

    # Sub-block B: Evidence Vector & Scoring
    box_b = patches.FancyBboxPatch((4.5, 4.2), 6.6, 1.2, boxstyle="round,pad=0.08",
                                  facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1.2)
    ax.add_patch(box_b)
    ax.text(7.8, 5.15, 'Evidence Vectorization & Risk Score Transformation', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#92400E')
    ax.text(7.8, 4.75, r'Linear Composite Base: $S_w = 100 \cdot (0.25V + 0.20D + 0.20N + 0.15O + 0.10A + 0.10M)$',
            ha='center', va='center', fontsize=8.5, color='#78350F')
    ax.text(7.8, 4.42, r'Piecewise Non-Linear Escalation: $S_{\mathrm{risk}} = f(S_w, P, Q, F_{\mathrm{child}}) \in [0.0, 100.0]$ | 33-D Vector $\mathbf{z}_i$',
            ha='center', va='center', fontsize=8.0, color='#78350F')

    # Sub-block C: Biometrics & Realtime Vision Engine
    box_c = patches.FancyBboxPatch((4.5, 1.1), 6.6, 2.8, boxstyle="round,pad=0.1",
                                  facecolor='#FFFFFF', edgecolor='#64748B', linewidth=1.2)
    ax.add_patch(box_c)
    ax.text(7.8, 3.65, 'Subsystem B: Realtime30FPSVisionEngine (DirectShow Concurrency)', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1E293B')

    bio_items = [
        ('DirectShow Grabber Thread', 'Locked 30 FPS non-blocking polling\nThread-safe mutex buffer', 5.6, 2.9),
        ('Dual-Scale MiniFASNet PAD', 'Multi-cue liveness + Hough lines\n2D FFT moiré spectral analysis', 10.0, 2.9),
        ('ArcFace iResNet50', '512-D hyperspherical embeddings\nCosine threshold tau = 0.65', 5.6, 1.8),
        ('ViT Age Estimator + OCR', 'Credential regex DOB extraction\nCross-verified age gating profile', 10.0, 1.8),
    ]
    for name, desc, x, y in bio_items:
        bb = patches.FancyBboxPatch((x - 2.0, y - 0.4), 4.0, 0.8, boxstyle="round,pad=0.06",
                                   facecolor='#F8FAFC', edgecolor='#CBD5E1', linewidth=0.8)
        ax.add_patch(bb)
        ax.text(x, y + 0.1, name, ha='center', va='center', fontsize=8, fontweight='bold', color=dark_text)
        ax.text(x, y - 0.18, desc, ha='center', va='center', fontsize=6.8, color=sub_text)

    # -------------------------------------------------------------
    # TIER 3: HIGH-PERFORMANCE VLM SERVICE (Top / Right)
    # -------------------------------------------------------------
    rect3 = patches.FancyBboxPatch((11.9, 5.0), 3.6, 3.8, boxstyle="round,pad=0.15",
                                  facecolor=t3_color, edgecolor=t3_border, linewidth=2.0)
    ax.add_patch(rect3)
    ax.text(13.7, 8.5, 'TIER 3: FOUNDATION MODEL SERVICE', ha='center', va='center', fontsize=11, fontweight='bold', color=t3_border)

    t3_boxes = [
        ('Qwen3-VL-8B-Instruct', 'Google Colab NVIDIA A100-SXM4 GPU\nNative torch.bfloat16 precision (19 GB VRAM)', 7.7),
        ('Multimodal Policy Prompt', 'Four-tier statutory compliance rules\nAuthentic OCR text + sampled keyframes', 6.6),
        ('Structured JSON Diagnostics', 'Predicted policy tier + confidence\nViolations list + forensic explanation', 5.5)
    ]
    for title, desc, y in t3_boxes:
        box = patches.FancyBboxPatch((12.1, y - 0.4), 3.2, 0.8, boxstyle="round,pad=0.08",
                                     facecolor='#FFFFFF', edgecolor='#C084FC', linewidth=1.0)
        ax.add_patch(box)
        ax.text(13.7, y + 0.1, title, ha='center', va='center', fontsize=8.5, fontweight='bold', color=dark_text)
        ax.text(13.7, y - 0.18, desc, ha='center', va='center', fontsize=7.2, color=sub_text)

    # -------------------------------------------------------------
    # DECISION ARBITRATION & AGE GATING (Bottom Right)
    # -------------------------------------------------------------
    arb_box = patches.FancyBboxPatch((11.9, 0.8), 3.6, 3.8, boxstyle="round,pad=0.15",
                                    facecolor='#FFF1F2', edgecolor='#F43F5E', linewidth=2.0)
    ax.add_patch(arb_box)
    ax.text(13.7, 4.3, 'STRATEGY D: SAFETY FUSION & GATING', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#BE123C')

    arb_items = [
        ('Rule 1: Prohibited Safety Veto', 'Qwen UNSAFE (conf >= 0.70) -> Reject', 3.6),
        ('Rule 2: Adult Gating Concordance', 'Qwen S18 + RF S18 (>= 0.20) -> 18+ Gate', 2.8),
        ('Rule 3: Benign Concordance', 'Agree SFA/S14 -> SFA or Safe 14+', 2.0),
        ('Delivery Dispatcher Omega', 'Crosses verified user age with ad tier', 1.2),
    ]
    for title, desc, y in arb_items:
        ab = patches.FancyBboxPatch((12.1, y - 0.3), 3.2, 0.65, boxstyle="round,pad=0.06",
                                    facecolor='#FFFFFF', edgecolor='#FDA4AF', linewidth=0.8)
        ax.add_patch(ab)
        ax.text(13.7, y + 0.08, title, ha='center', va='center', fontsize=8, fontweight='bold', color='#9F1239')
        ax.text(13.7, y - 0.12, desc, ha='center', va='center', fontsize=7.0, color=sub_text)

    # Connecting Arrows
    arrow_props = dict(arrowstyle='->', lw=1.5, color='#475569')
    # T1 to T2
    ax.annotate('', xy=(4.2, 7.0), xytext=(3.7, 7.0), arrowprops=arrow_props)
    # T2 to T3
    ax.annotate('', xy=(11.9, 7.0), xytext=(11.4, 7.0), arrowprops=arrow_props)
    # T3 to Arb
    ax.annotate('', xy=(13.7, 4.6), xytext=(13.7, 5.0), arrowprops=arrow_props)
    # T2 to Arb
    ax.annotate('', xy=(11.9, 2.5), xytext=(11.4, 2.5), arrowprops=arrow_props)

    plt.tight_layout()
    plt.savefig('overleaf_figures/system_architecture.png', dpi=300, bbox_inches='tight')
    plt.savefig('system_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created system_architecture.png")

# ==============================================================================
# DIAGRAM 2: Content Policy Taxonomy Hierarchy
# ==============================================================================
def create_policy_hierarchy():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(7.0, 7.6, 'SafeAd AI Four-Tier Content Policy Taxonomy & Statutory Alignment',
            ha='center', va='center', fontsize=15, fontweight='bold', color='#0F172A')
    ax.text(7.0, 7.25, 'Decoupled Demographic Delivery Tiers Grounded in Global Advertising Regulations',
            ha='center', va='center', fontsize=10.5, fontstyle='italic', color='#475569')

    tiers = [
        ('1. SAFE_FOR_ALL\n(Universal Audience)',
         'COPPA, FTC Child Guidelines,\nGoogle Ads Family Policy, PEGI 3/7',
         'Benign consumer goods, educational software,\nproduce, apparel, general electronics.',
         'Continuous Risk: S_risk < 25.0\nProhibited: P < 15.0, Adult: Q < 0.10',
         'Unrestricted programmatic delivery\nto all users regardless of age.',
         '#EFF6FF', '#3B82F6', 1.7),

        ('2. SAFE_14_PLUS\n(Adolescent Tier)',
         'UK ASA Rule 15.18, IARC Teen (13+),\nPEGI 12, ASCI Youth Advertising',
         'High-caffeine energy drinks, teen skincare,\naction video games, intense sports gear.',
         'Continuous Risk: 25.0 <= S_risk < 55.0\nProhibited: P < 35.0, Adult: Q < 0.25',
         'Delivered to adolescents (>= 14) and adults;\nstrictly blocked from children (< 14).',
         '#F0FDF4', '#10B981', 5.1),

        ('3. SAFE_18_PLUS\n(Lawful Adult Restricted)',
         'Google Ads Alcohol Policy, Meta 18+,\nIARC Mature (17+/18+), PEGI 18',
         'Commercial alcohol, licensed casino gaming,\nadult dating, swimwear/lingerie.',
         'Continuous Risk: 55.0 <= S_risk < 75.0\nAdult trigger: Q >= 0.25 elevated to 59.5',
         'Mandatory ArcFace biometric age gating;\nstrictly blocked from all minors (< 18).',
         '#FFFBEB', '#F59E0B', 8.5),

        ('4. UNSAFE_FOR_ALL\n(Universally Prohibited)',
         'FTC Deception Act 15 U.S.C. 45, DSA,\nCriminal codes, Counterfeit / CSAM bans',
         'Financial scams, Ponzi schemes, crypto fraud,\nweapons, illicit drugs, severe gore/hate.',
         'Continuous Risk: S_risk >= 75.0\nProhibited trigger: P >= 50.0 elevated to 100',
         'Immediate pre-publication rejection;\npermanent veto across all channels.',
         '#FEF2F2', '#EF4444', 11.9),
    ]

    for title, regs, goods, scores, action, bg, border, x in tiers:
        # Outer Card
        card = patches.FancyBboxPatch((x - 1.5, 0.6), 3.0, 6.2, boxstyle="round,pad=0.12",
                                      facecolor=bg, edgecolor=border, linewidth=2.0)
        ax.add_patch(card)

        # Header Box
        header = patches.FancyBboxPatch((x - 1.4, 5.7), 2.8, 0.9, boxstyle="round,pad=0.08",
                                        facecolor=border, edgecolor=border)
        ax.add_patch(header)
        ax.text(x, 6.15, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#FFFFFF')

        # Sections
        sec_y = [
            ('Statutory Grounding:', regs, 5.1, '#1E293B'),
            ('Eligible Commercial Verticals:', goods, 3.8, '#1E293B'),
            ('Numerical Thresholds (Heuristic):', scores, 2.5, '#78350F' if '18' in title else '#1E293B'),
            ('Enforced Delivery Action:', action, 1.2, '#991B1B' if 'UNSAFE' in title else '#065F46'),
        ]
        for sec_title, sec_desc, y, col in sec_y:
            ax.text(x, y + 0.25, sec_title, ha='center', va='center', fontsize=8, fontweight='bold', color=border)
            ax.text(x, y - 0.15, sec_desc, ha='center', va='center', fontsize=7.2, color=col)

    plt.tight_layout()
    plt.savefig('overleaf_figures/policy_hierarchy.png', dpi=300, bbox_inches='tight')
    plt.savefig('policy_hierarchy.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created policy_hierarchy.png")

# ==============================================================================
# DIAGRAM 3: Strategy D Hierarchical Safety Fusion Protocol Flowchart
# ==============================================================================
def create_fusion_flowchart():
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(7.5, 8.0, 'Strategy D: Hierarchical Multimodal Safety Fusion Protocol',
            ha='center', va='center', fontsize=15, fontweight='bold', color='#0F172A')
    ax.text(7.5, 7.65, 'Formal Arbitration Logic: VLM Semantic Reasoning + Random Forest Tabular Concordance',
            ha='center', va='center', fontsize=10.5, fontstyle='italic', color='#475569')

    # Start Node
    start = patches.FancyBboxPatch((6.0, 6.7), 3.0, 0.6, boxstyle="round,pad=0.08",
                                  facecolor='#38BDF8', edgecolor='#0284C7', linewidth=1.5)
    ax.add_patch(start)
    ax.text(7.5, 7.0, 'Dual Model Inference Input\n(Qwen3-VL Verdict + RF Probabilities)',
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#FFFFFF')

    # Decision Steps
    steps = [
        ('Rule 1: Prohibited Safety Veto\nIs Qwen3-VL = UNSAFE_FOR_ALL and Conf >= 0.70?', 5.4,
         'YES -> Absolute Veto Rejection\nFinal Tier: UNSAFE_FOR_ALL\n(100% Prohibited Recall Maintained)', '#EF4444', 12.5),

        ('Rule 2: Adult Gating Concordance\nIs Qwen3-VL = SAFE_18_PLUS and RF P(S18) >= 0.20?', 4.1,
         'YES -> Mandatory Biometric Gate\nFinal Tier: SAFE_18_PLUS\n(Gated to Verified Adults Only)', '#F59E0B', 12.5),

        ('Rule 3: Benign Concordance\nAre both models predicting benign tiers (SFA / S14)?', 2.8,
         'YES -> Exact Match or Conservative S14\nAdopt Concordant Benign Tier\n(Safe for General/Teen Display)', '#10B981', 12.5),

        ('Rule 4: High-Confidence VLM Override\nIs Qwen3-VL Confidence >= 0.85?', 1.5,
         'YES -> Adopt Qwen3-VL Tier\nHigh-Confidence Semantic Resolution', '#8B5CF6', 12.5),
    ]

    for question, y, action_text, border_color, act_x in steps:
        # Decision Diamond / Hex
        q_box = patches.FancyBboxPatch((4.5, y - 0.35), 6.0, 0.75, boxstyle="round,pad=0.08",
                                      facecolor='#F8FAFC', edgecolor='#334155', linewidth=1.2)
        ax.add_patch(q_box)
        ax.text(7.5, y + 0.02, question, ha='center', va='center', fontsize=8.2, fontweight='bold', color='#1E293B')

        # Action Box on right
        act_box = patches.FancyBboxPatch((act_x - 1.8, y - 0.35), 3.6, 0.75, boxstyle="round,pad=0.08",
                                        facecolor='#FFFFFF', edgecolor=border_color, linewidth=1.5)
        ax.add_patch(act_box)
        ax.text(act_x, y + 0.02, action_text, ha='center', va='center', fontsize=7.5, fontweight='bold', color=border_color)

        # Arrow from question to action
        ax.annotate('', xy=(act_x - 1.8, y), xytext=(10.5, y),
                    arrowprops=dict(arrowstyle='->', lw=1.2, color='#1E293B'))

        # Down arrow to next rule
        if y > 1.5:
            ax.annotate('', xy=(7.5, y - 0.55), xytext=(7.5, y - 0.35),
                        arrowprops=dict(arrowstyle='->', lw=1.2, color='#64748B'))
            ax.text(7.8, y - 0.45, 'NO', fontsize=7.5, fontweight='bold', color='#64748B')

    # Bottom Default Fallback (Rule 5)
    ax.annotate('', xy=(7.5, 0.7), xytext=(7.5, 1.15),
                arrowprops=dict(arrowstyle='->', lw=1.2, color='#64748B'))
    ax.text(7.8, 0.95, 'NO', fontsize=7.5, fontweight='bold', color='#64748B')

    fallback = patches.FancyBboxPatch((4.5, 0.1), 6.0, 0.6, boxstyle="round,pad=0.08",
                                     facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.5)
    ax.add_patch(fallback)
    ax.text(7.5, 0.4, 'Rule 5: Signal Conflict Arbitration -> Route to Human-in-the-Loop Review Queue\nAd Withheld from Publication until Manual Compliance Officer Signoff',
            ha='center', va='center', fontsize=8.0, fontweight='bold', color='#B45309')

    # Down from start
    ax.annotate('', xy=(7.5, 5.8), xytext=(7.5, 6.7),
                arrowprops=dict(arrowstyle='->', lw=1.2, color='#0284C7'))

    plt.tight_layout()
    plt.savefig('overleaf_figures/fusion_pipeline.png', dpi=300, bbox_inches='tight')
    plt.savefig('fusion_pipeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created fusion_pipeline.png")

# ==============================================================================
# DIAGRAM 4: Decoupled DirectShow Concurrency Architecture
# ==============================================================================
def create_concurrency_diagram():
    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(6.5, 7.1, 'Realtime30FPSVisionEngine: Decoupled Thread Architecture',
            ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
    ax.text(6.5, 6.75, 'Prevention of Windows DirectShow STA Thread Collisions and Fatal Native Heap Corruption (0xc0000374)',
            ha='center', va='center', fontsize=9.5, fontstyle='italic', color='#475569')

    # Left Box: Thread 1 Grabber
    t1 = patches.FancyBboxPatch((0.8, 1.8), 3.4, 4.4, boxstyle="round,pad=0.1",
                               facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=1.8)
    ax.add_patch(t1)
    ax.text(2.5, 5.9, 'THREAD 1: HARDWARE GRABBER', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1D4ED8')
    t1_txt = (
        "- OpenCV DirectShow Backend\n"
        "- Non-blocking cap.read() polling\n"
        "- Locked strictly at 30.0 FPS\n"
        "- Never executes heavy AI\n"
        "- Prevents DirectShow STA stalls\n"
        "- Acquires non-blocking mutex\n"
        "- Updates double-buffered frame\n"
        "- Eliminates buffer overruns"
    )
    ax.text(1.1, 3.8, t1_txt, fontsize=8, color='#1E293B', linespacing=1.6)

    # Middle Box: Mutex Protected Buffer
    buf = patches.FancyBboxPatch((4.8, 2.5), 3.4, 3.0, boxstyle="round,pad=0.1",
                                facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1.8)
    ax.add_patch(buf)
    ax.text(6.5, 5.15, 'SHARED MEMORY BUFFER', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#B45309')
    ax.text(6.5, 4.75, 'threading.Lock() Mutex', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#92400E')
    buf_txt = (
        "Double-Buffered Storage:\n"
        "- latest_frame (RGB 1080p)\n"
        "- latest_proxy (640x480)\n"
        "- latest_ai_verdict (PAD, ID)\n"
        "- atomic swap in < 0.2 ms"
    )
    ax.text(5.1, 3.4, buf_txt, fontsize=8, color='#78350F', linespacing=1.5)

    # Right Box: Thread 2 AI Worker
    t2 = patches.FancyBboxPatch((8.8, 1.8), 3.4, 4.4, boxstyle="round,pad=0.1",
                               facecolor='#F0FDF4', edgecolor='#10B981', linewidth=1.8)
    ax.add_patch(t2)
    ax.text(10.5, 5.9, 'THREAD 2: ASYNC AI WORKER', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#047857')
    t2_txt = (
        "- Runs asynchronously downstream\n"
        "- Reads latest proxy frame copy\n"
        "- Dual-Scale MiniFASNet PAD\n"
        "- Probabilistic Hough line bezel\n"
        "- 2D FFT moire spectral check\n"
        "- InsightFace ArcFace (512-D)\n"
        "- ViT Facial Age Classifier\n"
        "- Publishes verdict back to buffer"
    )
    ax.text(9.1, 3.8, t2_txt, fontsize=8, color='#1E293B', linespacing=1.6)

    # Bottom Box: Main UI Display Loop
    ui = patches.FancyBboxPatch((3.5, 0.4), 6.0, 1.0, boxstyle="round,pad=0.08",
                               facecolor='#F8FAFC', edgecolor='#64748B', linewidth=1.5)
    ax.add_patch(ui)
    ax.text(6.5, 1.05, 'MAIN DISPLAY RENDER LOOP (Streamlit / HUD GUI)', ha='center', va='center', fontsize=9.0, fontweight='bold', color='#0F172A')
    ax.text(6.5, 0.65, 'Queries shared buffer every 33.3 ms | Overlays real-time bounding boxes, liveness meters, and ArcFace cosine match at 30 FPS',
            ha='center', va='center', fontsize=7.5, color='#475569')

    # Arrows
    arr_p = dict(arrowstyle='->', lw=1.5, color='#1E293B')
    ax.annotate('', xy=(4.8, 4.0), xytext=(4.2, 4.0), arrowprops=arr_p)
    ax.annotate('', xy=(8.8, 4.0), xytext=(8.2, 4.0), arrowprops=arr_p)
    ax.annotate('', xy=(6.5, 1.4), xytext=(6.5, 2.5), arrowprops=arr_p)

    plt.tight_layout()
    plt.savefig('overleaf_figures/vision_engine_concurrency.png', dpi=300, bbox_inches='tight')
    plt.savefig('vision_engine_concurrency.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created vision_engine_concurrency.png")

# ==============================================================================
# DIAGRAM 5: Phase 10D Independent Test Evaluation Comparison Bar Chart
# ==============================================================================
def create_test_benchmark_chart():
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    strategies = [
        'Strategy A\n(Random Forest Alone)',
        'Strategy B\n(Qwen3-VL Alone)',
        'Strategy C\n(Soft Probability Voting)',
        'Strategy D\n(Hierarchical Safety Fusion)'
    ]

    accuracy = [37.04, 66.67, 51.85, 66.67]
    macro_f1 = [36.21, 65.59, 52.88, 65.59]
    prohibited_recall = [25.00, 100.00, 75.00, 100.00]
    false_acceptance = [75.00, 0.00, 25.00, 0.00]

    x = np.arange(len(strategies))
    width = 0.20

    rects1 = ax.bar(x - 1.5*width, accuracy, width, label='4-Class Accuracy (%)', color='#3B82F6', edgecolor='#1D4ED8')
    rects2 = ax.bar(x - 0.5*width, macro_f1, width, label='Macro-F1 Score (%)', color='#10B981', edgecolor='#047857')
    rects3 = ax.bar(x + 0.5*width, prohibited_recall, width, label='Prohibited Recall (%)', color='#8B5CF6', edgecolor='#6D28D9')
    rects4 = ax.bar(x + 1.5*width, false_acceptance, width, label='Prohibited False Accept (%) [Lower is Better]', color='#EF4444', edgecolor='#B91C1C')

    ax.set_ylabel('Performance Percentage (%)', fontsize=11, fontweight='bold', color='#0F172A')
    ax.set_title('Phase 10D Independent Held-Out Test Evaluation Across Moderation Strategies (N = 27)',
                 fontsize=12, fontweight='bold', color='#0F172A', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(strategies, fontsize=9.5, fontweight='bold', color='#1E293B')
    ax.legend(loc='upper right', framealpha=0.95, fontsize=8.5)
    ax.set_ylim(0, 115)
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#94A3B8')

    # Add values on top of bars
    def autolabel(rects, is_err=False):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=7.2, fontweight='bold',
                        color='#B91C1C' if is_err and height > 0 else '#0F172A')

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    autolabel(rects4, is_err=True)

    # Annotation box highlighting empirical reality
    ax.text(0.5, 0.88, 'Core Scientific Insight: Hierarchical Fusion matches Qwen3-VL (66.7%) and achieves 0% False Acceptance,\npreventing RF collapse (37.0%) on out-of-distribution media via the Rule 1 Safety Veto.',
            transform=ax.transAxes, ha='center', va='top', fontsize=8.2, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FEF3C7', edgecolor='#F59E0B', alpha=0.9))

    plt.tight_layout()
    plt.savefig('overleaf_figures/phase10d_test_comparison.png', dpi=300, bbox_inches='tight')
    plt.savefig('phase10d_test_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created phase10d_test_comparison.png")

# ==============================================================================
# DIAGRAM 6: Multimodal Evidence Feature Extraction & Risk Escalation Pipeline
# ==============================================================================
def create_multimodal_feature_pipeline():
    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('#FFFFFF')

    ax.text(7.0, 6.6, 'Multimodal Evidence Extraction & Non-Linear Risk Escalation Architecture',
            ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
    ax.text(7.0, 6.25, 'Synthesis of Specialized Modality Streams into 33-D Tabular Vector and Piecewise Composite Risk Index',
            ha='center', va='center', fontsize=9.5, fontstyle='italic', color='#475569')

    # Column 1: Raw Inputs
    inputs = [('Visual Keyframes\n(Farnebäck sampled)', 4.8),
              ('OCR On-Screen Text\n(CLAHE + Otsu EasyOCR)', 3.4),
              ('Speech Audio Track\n(16 kHz Whisper PCM)', 2.0)]
    for label, y in inputs:
        b = patches.FancyBboxPatch((0.5, y - 0.45), 2.5, 0.9, boxstyle="round,pad=0.08",
                                   facecolor='#F1F5F9', edgecolor='#94A3B8', linewidth=1.2)
        ax.add_patch(b)
        ax.text(1.75, y, label, ha='center', va='center', fontsize=8, fontweight='bold', color='#1E293B')

    # Column 2: Specialized Feature Heads
    heads = [
        ('ResNet50 / MobileNetV3', 'Visual safety & weapon flags ($V$)', 5.2),
        ('Falcon NSFW ViT Head', 'Adult & suggestive probability ($N$)', 4.2),
        ('RoBERTa / DeBERTa Head', 'Text toxicity & hate speech ($O$)', 3.2),
        ('Whisper + AudioRisk', 'Speech hazard index ($A$)', 2.2),
        ('AdRisk & FTC Regex', 'Deception, scam & lottery index ($M$)', 1.2),
    ]
    for name, desc, y in heads:
        b = patches.FancyBboxPatch((3.7, y - 0.35), 3.0, 0.7, boxstyle="round,pad=0.06",
                                   facecolor='#EFF6FF', edgecolor='#3B82F6', linewidth=1.0)
        ax.add_patch(b)
        ax.text(5.2, y + 0.1, name, ha='center', va='center', fontsize=8, fontweight='bold', color='#1D4ED8')
        ax.text(5.2, y - 0.15, desc, ha='center', va='center', fontsize=6.8, color='#475569')

    # Column 3: 33-D Feature Vector
    vec_box = patches.FancyBboxPatch((7.4, 1.0), 2.6, 4.8, boxstyle="round,pad=0.1",
                                    facecolor='#F0FDF4', edgecolor='#10B981', linewidth=1.5)
    ax.add_patch(vec_box)
    ax.text(8.7, 5.5, '33-D Feature Vector', ha='center', va='center', fontsize=9.0, fontweight='bold', color='#047857')
    vec_text = (
        "z[0:5]: Visual scene\n"
        "z[5:10]: Adult/NSFW\n"
        "z[10:15]: Motion kinetics\n"
        "z[15:20]: OCR text toxicity\n"
        "z[20:25]: Audio speech risk\n"
        "z[25:30]: Deception/AdRisk\n"
        "z[30:33]: Composite stats\n\n"
        "Evaluated via\n"
        "Random Forest\n"
        "(100 Trees, Depth 5)"
    )
    ax.text(7.6, 3.2, vec_text, fontsize=7.2, color='#065F46', linespacing=1.35)

    # Column 4: Piecewise Non-Linear Formulation
    math_box = patches.FancyBboxPatch((10.7, 1.0), 2.8, 4.8, boxstyle="round,pad=0.1",
                                     facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1.5)
    ax.add_patch(math_box)
    ax.text(12.1, 5.5, 'Piecewise Risk Scoring', ha='center', va='center', fontsize=9.0, fontweight='bold', color='#B45309')
    math_text = (
        "Linear Base:\n"
        "Sw = 100 * (0.25V +\n"
        "0.20D + 0.20N + 0.15O +\n"
        "0.10A + 0.10M)\n\n"
        "Escalations:\n"
        "1. Child Safety / Prohibited:\n"
        "If P >= 50: S_risk = max(Sw, P)\n\n"
        "2. Commercial Adult:\n"
        "If Q >= 0.25: S_risk =\n"
        "min(65.0, max(Sw, 70Q))\n\n"
        "3. Benign Ceiling:\n"
        "Else: min(39.9, Sw)"
    )
    ax.text(10.9, 3.2, math_text, fontsize=6.8, color='#78350F', linespacing=1.3)

    # Connections
    for _, y in inputs:
        ax.annotate('', xy=(3.7, y), xytext=(3.0, y), arrowprops=dict(arrowstyle='->', lw=1.0, color='#64748B'))
    ax.annotate('', xy=(7.4, 3.5), xytext=(6.7, 3.5), arrowprops=dict(arrowstyle='->', lw=1.2, color='#10B981'))
    ax.annotate('', xy=(10.7, 3.5), xytext=(10.0, 3.5), arrowprops=dict(arrowstyle='->', lw=1.2, color='#F59E0B'))

    plt.tight_layout()
    plt.savefig('overleaf_figures/multimodal_feature_pipeline.png', dpi=300, bbox_inches='tight')
    plt.savefig('multimodal_feature_pipeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created multimodal_feature_pipeline.png")

if __name__ == '__main__':
    create_system_architecture()
    create_policy_hierarchy()
    create_fusion_flowchart()
    create_concurrency_diagram()
    create_test_benchmark_chart()
    create_multimodal_feature_pipeline()
    print("All professional diagrams successfully generated at 300 DPI!")
