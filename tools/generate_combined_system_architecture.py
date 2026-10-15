import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_rounded_box(ax, x, y, w, h, bg_color, border_color, border_width=1.5, radius=8):
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad={radius},rounding_size={radius}",
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=border_width
    )
    ax.add_patch(box)
    return box

def draw_arrow(ax, x1, y1, x2, y2, color='#475569', width=2.0, style='->'):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle=style, color=color, lw=width, shrinkA=4, shrinkB=4)
    )

def generate_system_architecture(output_paths):
    # Canvas dimensions: 3200 x 2000
    W, H = 3200, 2000
    fig, ax = plt.subplots(figsize=(W/200, H/200), dpi=200)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis('off')

    # Main canvas background
    ax.add_patch(patches.Rectangle((0, 0), W, H, facecolor='#f8fafc'))

    # ==========================================================================
    # Top Header Banner
    # ==========================================================================
    header = patches.Rectangle((0, H - 110), W, 110, facecolor='#0f172a')
    ax.add_patch(header)
    
    ax.text(60, H - 55, "SafeAd AI: Unified System Architecture Framework", 
            fontsize=26, fontweight='bold', color='#ffffff', va='center')
    ax.text(60, H - 85, "End-to-End Multimodal Video Advertisement Policy Moderation & Biometric Age-Aware Content Delivery", 
            fontsize=13, color='#94a3b8', va='center')
    ax.text(W - 60, H - 65, "B.Tech Major Project | QuadRos-MBCET\nVersion 2.0 Unified Architecture", 
            fontsize=12, color='#38bdf8', ha='right', va='center')

    # ==========================================================================
    # LEFT REGION: AD SAFETY CHECK MODULE (Multimodal Moderation Pipeline)
    # ==========================================================================
    draw_rounded_box(ax, 50, 60, 1480, H - 200, '#ffffff', '#cbd5e1', border_width=2.0, radius=16)
    
    # Section Header
    sec_hdr_1 = patches.FancyBboxPatch((70, H - 190), 1440, 50, boxstyle="round,pad=4", facecolor='#1e3a8a', edgecolor='none')
    ax.add_patch(sec_hdr_1)
    ax.text(790, H - 165, "MODULE 1: MULTIMODAL VIDEO ADVERTISEMENT POLICY CHECK SUBSYSTEM", 
            fontsize=16, fontweight='bold', color='#ffffff', ha='center', va='center')

    # 1.1 Ingestion Box
    draw_rounded_box(ax, 80, H - 360, 1420, 140, '#f1f5f9', '#94a3b8', border_width=1.5)
    ax.text(100, H - 240, "1. Advertisement Creative Ingestion & Preprocessing", fontsize=14, fontweight='bold', color='#1e3a8a')
    ax.text(100, H - 275, "• Media Ingestion: Video Commercials (.mp4, .avi, 720p-1080p) | Static Display Creatives (.png, .jpg)", fontsize=11, color='#334155')
    ax.text(100, H - 305, "• Temporal Frame Sampler: Adaptive Uniform Keyframe Sampling (8-16 Keyframes) with Timestamp Synchronization", fontsize=11, color='#334155')
    ax.text(100, H - 335, "• Audio Stream Extraction: Demuxing Audio Track to 16.0 kHz Single-Channel Linear PCM WAV (Mono)", fontsize=11, color='#334155')

    draw_arrow(ax, 790, H - 360, 790, H - 410, color='#1e3a8a', width=2.5)

    # 1.2 Five Parallel Feature Extraction Analyzers
    draw_rounded_box(ax, 80, H - 980, 1420, 550, '#f8fafc', '#cbd5e1', border_width=1.5)
    ax.text(100, H - 435, "2. Deep Multimodal Feature Extraction & Specialized Detectors", fontsize=14, fontweight='bold', color='#1e3a8a')

    analyzers = [
        ("A. Optical Character Recognition (OCR)", 
         "Model: EasyOCR CRAFT + Tesseract Fallback",
         "• Character Region Awareness for Text Detection (CRAFT)\n• Bounding box overlay localization\n• High-Risk Multi-tier Lexicon Matching\n• Detects '18+', 'T&C Apply', 'Casino', 'Bonus'", 
         "Extracted Text Tokens &\nDisclaimer Bounding Tags",
         '#e0f2fe', '#0284c7', H - 540),
        
        ("B. Audio Speech-to-Text Mining", 
         "Model: OpenAI Whisper (Tiny/Base)",
         "• 16 kHz Log-Mel Spectrogram Transformer\n• Full voiceover audio transcript generation\n• Spoken keyword risk detection\n• Detects financial stakes, gambling invites", 
         "Timestamped Voiceover\nTranscript & Audio Risk",
         '#fef3c7', '#d97706', H - 650),

        ("C. Visual Safety & Hazard Detection", 
         "Model: Llama-Guard-3-11B-Vision + MobileNet",
         "• Evaluates sampled keyframes on MLCommons taxonomy\n• 7 Hazard Categories: S1 (Violent Crimes) to S7 (Drugs)\n• Identifies prohibited products, weapons & assault\n• Computes fine-grained hazard probability", 
         "Visual Safety Classification\n& Threat Probability",
         '#dcfce7', '#16a34a', H - 760),

        ("D. Adult / NSFW ViT Classification", 
         "Model: Falconsai / nsfw_image_detection ViT",
         "• Vision Transformer (ViT-Base, 16x16 patch projection)\n• Softmax distribution across Normal vs Suggestive/NSFW\n• Detects erotic poses, nightlife luxury club imagery\n• Adult suggestive probability thresholding", 
         "Adult Suggestive Prob\nP(NSFW) in [0.0, 1.0]",
         '#fee2e2', '#dc2626', H - 870),

        ("E. VideoMAE Violence & Temporal Motion", 
         "Model: VideoMAE (MCG-NJU) + Consecutive Motion",
         "• 16-frame spatio-temporal attention tubelets\n• Consecutive-frame L1 Motion Difference: ||Frame_{t+1} - Frame_t||\n• Differentiates real assault from fast esports/gaming\n• Kinetic action classification", 
         "Violence Action Score &\nTemporal Motion Vector",
         '#f3e8ff', '#9333ea', H - 980)
    ]

    for title, model, desc, out_text, bg_col, border_col, y_pos in analyzers:
        # Card container
        draw_rounded_box(ax, 100, y_pos, 1380, 95, bg_col, border_col, border_width=1.5)
        ax.text(120, y_pos + 72, title, fontsize=12, fontweight='bold', color=border_col)
        ax.text(500, y_pos + 72, f"[{model}]", fontsize=10.5, fontstyle='italic', color='#475569')
        ax.text(120, y_pos + 18, desc, fontsize=9.5, color='#334155', linespacing=1.25)
        
        # Output box
        draw_rounded_box(ax, 1160, y_pos + 10, 300, 75, '#ffffff', border_col, border_width=1.2)
        ax.text(1310, y_pos + 48, out_text, fontsize=10, fontweight='bold', color=border_col, ha='center', va='center')

    draw_arrow(ax, 790, H - 980, 790, H - 1040, color='#1e3a8a', width=2.5)

    # 1.3 Central SafeAdAssessment & Multimodal Fusion
    draw_rounded_box(ax, 80, H - 1380, 1420, 320, '#eff6ff', '#3b82f6', border_width=2.0)
    ax.text(100, H - 1065, "3. Central SafeAdAssessment Matrix & Multimodal Decision Fusion", fontsize=14, fontweight='bold', color='#1e3a8a')
    
    # Formula Box
    draw_rounded_box(ax, 100, H - 1175, 1380, 85, '#ffffff', '#93c5fd', border_width=1.5)
    ax.text(790, H - 1115, "Composite Risk Score = 100 × [ 0.25·S_nsfw + 0.20·S_ocr + 0.20·S_violence + 0.15·S_visual + 0.10·S_audio + 0.10·S_adrisk ]", 
            fontsize=12, fontweight='bold', color='#1e3a8a', ha='center', va='center')
    ax.text(790, H - 1148, "Deterministic Safety Overrides: Mandatory Adult Warnings ('18+') -> SAFE_18_PLUS | Critical Hazards (S1-S7) -> UNSAFE_FOR_ALL", 
            fontsize=10.5, fontstyle='italic', color='#dc2626', ha='center', va='center')

    # Policy Outcomes Grid
    outcomes = [
        ("SAFE_FOR_ALL", "Risk <= 25.0\nZero Disclaimers\nUniversal Child Safe", '#dcfce7', '#166534', 100),
        ("SAFE_14_PLUS", "25 < Risk <= 50\nMotion 25-45\nEsports / Gaming", '#e0f2fe', '#0369a1', 380),
        ("SAFE_18_PLUS", "50 < Risk <= 85\n18+ Warning / Alcohol\nRestricted to 18+", '#fef3c7', '#92400e', 660),
        ("UNSAFE_FOR_ALL", "Risk > 85.0\nWeapons / Assault\nIMMEDIATE REJECT", '#fee2e2', '#991b1b', 940),
        ("HUMAN_REVIEW", "Confidence < 60%\nCross-Modal Clash\nAdmin HITL Queue", '#f3e8ff', '#6b21a8', 1220)
    ]
    for name, desc, bg, border, x_pos in outcomes:
        draw_rounded_box(ax, x_pos, H - 1350, 260, 140, bg, border, border_width=2.0)
        ax.text(x_pos + 130, H - 1240, name, fontsize=11, fontweight='bold', color=border, ha='center', va='center')
        ax.text(x_pos + 130, H - 1295, desc, fontsize=9.5, color='#334155', ha='center', va='center', linespacing=1.2)

    # 1.4 Ad Storage & Audit Queue
    draw_rounded_box(ax, 80, 80, 1420, 290, '#f8fafc', '#94a3b8', border_width=1.5)
    ax.text(100, 340, "4. Policy Enforcement & Persistence Layer", fontsize=14, fontweight='bold', color='#1e3a8a')
    
    draw_rounded_box(ax, 100, 110, 660, 200, '#ffffff', '#cbd5e1', border_width=1.5)
    ax.text(430, 280, "Approved Ad Repository (Database)", fontsize=12, fontweight='bold', color='#0f172a', ha='center')
    ax.text(120, 240, "• Certified advertisements classified by policy tier", fontsize=10.5, color='#334155')
    ax.text(120, 205, "• Indexed in SQLite/MySQL with metadata and vectors", fontsize=10.5, color='#334155')
    ax.text(120, 170, "• Queried dynamically by the Instakill User Feed", fontsize=10.5, color='#334155')
    ax.text(120, 135, "• Ready for age-aware serving pipeline", fontsize=10.5, color='#16a34a', fontweight='bold')

    draw_rounded_box(ax, 820, 110, 660, 200, '#ffffff', '#cbd5e1', border_width=1.5)
    ax.text(1150, 280, "Admin Governance & HITL Audit Trail", fontsize=12, fontweight='bold', color='#0f172a', ha='center')
    ax.text(840, 240, "• Quarantine buffer for low-confidence creative scans", fontsize=10.5, color='#334155')
    ax.text(840, 205, "• Full XAI (Explainable AI) attribution report", fontsize=10.5, color='#334155')
    ax.text(840, 170, "• Manual Override Controls: 1-Click Approve / Reject", fontsize=10.5, color='#334155')
    ax.text(840, 135, "• Regulatory audit logs (COPPA / GDPR-K / ASCI)", fontsize=10.5, color='#dc2626', fontweight='bold')

    # ==========================================================================
    # RIGHT REGION: FACE DETECTION & BIOMETRIC VERIFICATION MODULE
    # ==========================================================================
    draw_rounded_box(ax, 1670, 60, 1480, H - 200, '#ffffff', '#cbd5e1', border_width=2.0, radius=16)

    # Section Header
    sec_hdr_2 = patches.FancyBboxPatch((1690, H - 190), 1440, 50, boxstyle="round,pad=4", facecolor='#15803d', edgecolor='none')
    ax.add_patch(sec_hdr_2)
    ax.text(2410, H - 165, "MODULE 2: USER KYC, FACE BIOMETRICS & AGE VERIFICATION SUBSYSTEM", 
            fontsize=16, fontweight='bold', color='#ffffff', ha='center', va='center')

    # 2.1 Dual Input: Document & Live Camera
    draw_rounded_box(ax, 1700, H - 490, 690, 270, '#f1f5f9', '#94a3b8', border_width=1.5)
    ax.text(1720, H - 245, "A. Official ID Document Processing", fontsize=13, fontweight='bold', color='#15803d')
    ax.text(1720, H - 280, "• Document Types: College ID, Aadhaar, PAN, DL", fontsize=10.5, color='#334155')
    ax.text(1720, H - 315, "• Multi-Pass Regex OCR: Layout-aware Date of Birth parsing", fontsize=10.5, color='#334155')
    ax.text(1720, H - 350, "• Batch Span Deduction: 'Batch: 2022-2026' -> YOB 2004", fontsize=10.5, color='#334155')
    ax.text(1720, H - 385, "• Chronological Age Computation: A_doc = Current_Year - YOB", fontsize=10.5, color='#15803d', fontweight='bold')
    ax.text(1720, H - 420, "• Document Portrait Face Localization & Normalized Crop", fontsize=10.5, color='#334155')
    ax.text(1720, H - 455, "-> Output: ID Card Face Crop (256x256) & Verified Age", fontsize=10.5, fontweight='bold', color='#0f172a')

    draw_rounded_box(ax, 2430, H - 490, 690, 270, '#f1f5f9', '#94a3b8', border_width=1.5)
    ax.text(2450, H - 245, "B. Live Webcam Capture & Anti-Spoofing", fontsize=13, fontweight='bold', color='#15803d')
    ax.text(2450, H - 280, "• Real-Time Video Stream Capture with interactive freeze", fontsize=10.5, color='#334155')
    ax.text(2450, H - 315, "• 2D FFT High-Frequency Analysis: Detects screen LCD moiré", fontsize=10.5, color='#334155')
    ax.text(2450, H - 350, "• HSV Specular Glare Variance: Detects laminated photo prints", fontsize=10.5, color='#334155')
    ax.text(2450, H - 385, "• Anti-Spoofing Verdict: ISO/IEC 30107-3 PAD Compliant", fontsize=10.5, color='#15803d', fontweight='bold')
    ax.text(2450, H - 420, "• Live Facial Landmark Alignment (Eye/Nose/Mouth)", fontsize=10.5, color='#334155')
    ax.text(2450, H - 455, "-> Output: Genuine Live User Face Crop (256x256)", fontsize=10.5, fontweight='bold', color='#0f172a')

    draw_arrow(ax, 2045, H - 490, 2220, H - 540, color='#15803d', width=2.5)
    draw_arrow(ax, 2775, H - 490, 2600, H - 540, color='#15803d', width=2.5)

    # 2.2 Deep Biometric Cross-Matching & Age Estimation
    draw_rounded_box(ax, 1700, H - 980, 1420, 420, '#f0fdf4', '#86efac', border_width=2.0)
    ax.text(1720, H - 535, "2. Deep ArcFace Biometric Cross-Matching & ViT Age Estimation", fontsize=14, fontweight='bold', color='#15803d')

    # Left: ArcFace Engine
    draw_rounded_box(ax, 1720, H - 950, 680, 380, '#ffffff', '#cbd5e1', border_width=1.5)
    ax.text(1740, H - 575, "ArcFace Deep Feature Representation", fontsize=12.5, fontweight='bold', color='#0f172a')
    ax.text(1740, H - 610, "• Architecture: ResNet-50 with Additive Angular Margin Loss", fontsize=10.5, color='#334155')
    ax.text(1740, H - 645, "• Vector Embedding: 512-Dimensional Identity Vector", fontsize=10.5, color='#334155')
    ax.text(1740, H - 685, "• ID Embedding: E_id  |  Live Webcam Embedding: E_live", fontsize=11, fontweight='bold', color='#15803d')
    ax.text(1740, H - 730, "Cosine Similarity Formula:\n   S(E_id, E_live) = (E_id • E_live) / ( ||E_id|| * ||E_live|| )", fontsize=11, fontweight='bold', color='#1e3a8a')
    ax.text(1740, H - 790, "• Decision Threshold: θ = 0.650 (Empirical EER = 2.1%)", fontsize=10.5, color='#334155')
    ax.text(1740, H - 830, "• IF S >= 0.65 -> BIOMETRIC MATCH CONFIRMED (Same Person)", fontsize=11, fontweight='bold', color='#16a34a')
    ax.text(1740, H - 865, "• IF S < 0.65  -> ACCESS DENIED (Identity Impersonation)", fontsize=11, fontweight='bold', color='#dc2626')

    # Right: ViT Age Classifier & Cross-Check
    draw_rounded_box(ax, 2420, H - 950, 680, 380, '#ffffff', '#cbd5e1', border_width=1.5)
    ax.text(2440, H - 575, "ViT Facial Age Classifier & Cross-Validation", fontsize=12.5, fontweight='bold', color='#0f172a')
    ax.text(2440, H - 610, "• Architecture: Vision Transformer trained on age cohorts", fontsize=10.5, color='#334155')
    ax.text(2440, H - 645, "• Cohort Classes: Under-14 (<14) | Youth (14-17) | Adult (18+)", fontsize=10.5, color='#334155')
    ax.text(2440, H - 685, "• Estimated Biological Age: A_face (Mean ± Std)", fontsize=11, fontweight='bold', color='#15803d')
    ax.text(2440, H - 730, "Dual-Modality Cross-Validation:\n   Discrepancy: ΔA = |A_doc - A_face| <= 3.0 Years", fontsize=11, fontweight='bold', color='#1e3a8a')
    ax.text(2440, H - 790, "• Resolves Document Tampering & Fake ID Scenarios", fontsize=10.5, color='#334155')
    ax.text(2440, H - 830, "• Certifies Verified Age Category for Session Authentication", fontsize=10.5, color='#334155')
    ax.text(2440, H - 865, "-> Certified Output: [UNDER_14] or [YOUTH_14_17] or [ADULT_18_PLUS]", fontsize=10.5, fontweight='bold', color='#16a34a')

    draw_arrow(ax, 2410, H - 980, 2410, H - 1040, color='#15803d', width=2.5)

    # 2.3 User Authentication & Instakill Session
    draw_rounded_box(ax, 1700, H - 1380, 1420, 320, '#eff6ff', '#3b82f6', border_width=2.0)
    ax.text(1720, H - 1065, "3. Secure Direct User Authentication & Instakill Session Generator", fontsize=14, fontweight='bold', color='#1e3a8a')

    # Auth details
    draw_rounded_box(ax, 1720, H - 1350, 680, 250, '#ffffff', '#cbd5e1', border_width=1.5)
    ax.text(1740, H - 1105, "Credential Binding & Token Issuance", fontsize=12.5, fontweight='bold', color='#0f172a')
    ax.text(1740, H - 1145, "• Upon biometric pass, prompts for Username & Password", fontsize=10.5, color='#334155')
    ax.text(1740, H - 1180, "• Cryptographic SHA-256 password hashing & verification", fontsize=10.5, color='#334155')
    ax.text(1740, H - 1215, "• Establishes Authenticated Session in Streamlit state", fontsize=10.5, color='#334155')
    ax.text(1740, H - 1250, "• Session binds: user_id, verified_dob, certified_age_group", fontsize=10.5, color='#15803d', fontweight='bold')
    ax.text(1740, H - 1285, "• Prevents multi-account circumvention by minors", fontsize=10.5, color='#475569')

    # Feed Gating Logic
    draw_rounded_box(ax, 2420, H - 1350, 680, 250, '#ffffff', '#cbd5e1', border_width=1.5)
    ax.text(2440, H - 1105, "Dynamic Age-Gating Policy Rules", fontsize=12.5, fontweight='bold', color='#0f172a')
    ax.text(2440, H - 1145, "• IF Verified Age < 14:\n   -> ALLOW: SAFE_FOR_ALL\n   -> BLOCK: SAFE_14_PLUS, SAFE_18_PLUS, UNSAFE", fontsize=10, color='#991b1b', fontweight='bold')
    ax.text(2440, H - 1215, "• IF Verified Age 14 - 17:\n   -> ALLOW: SAFE_FOR_ALL, SAFE_14_PLUS\n   -> BLOCK: SAFE_18_PLUS, UNSAFE", fontsize=10, color='#0369a1', fontweight='bold')
    ax.text(2440, H - 1275, "• IF Verified Age >= 18:\n   -> ALLOW: Full Clearance to 18+, 14+, All Audiences", fontsize=10, color='#166534', fontweight='bold')

    # 2.4 User Instakill Feed Delivery
    draw_rounded_box(ax, 1700, 80, 1420, 290, '#f8fafc', '#94a3b8', border_width=1.5)
    ax.text(1720, 340, "4. Instakill Age-Aware Social Feed (End-User Interface)", fontsize=14, fontweight='bold', color='#1e3a8a')

    # Feed Mock Cards
    feed_cards = [
        ("Child Feed (<14 User)", "Strict COPPA Mode", "• Filtered FMCG Ads\n• Educational Apps\n• Toy Commercials\n• 100% Adult Ad Block", '#fef2f2', '#ef4444', 1720),
        ("Teen Feed (14-17 User)", "Youth Protected Mode", "• Esports Tournaments\n• Sneaker Launches\n• Dynamic Gaming Ads\n• Alcohol / Casino Block", '#f0f9ff', '#0284c7', 2180),
        ("Adult Feed (18+ User)", "Full Access Mode", "• Unrestricted Feed\n• Lawful 18+ Casino\n• Spirits & Finance\n• Verified Adult Content", '#f0fdf4', '#16a34a', 2640)
    ]
    for title, mode, details, bg, border, x_pos in feed_cards:
        draw_rounded_box(ax, x_pos, 110, 440, 200, bg, border, border_width=1.5)
        ax.text(x_pos + 220, 280, title, fontsize=11.5, fontweight='bold', color=border, ha='center')
        ax.text(x_pos + 220, 255, f"[{mode}]", fontsize=10, color='#475569', ha='center')
        ax.text(x_pos + 40, 180, details, fontsize=10, color='#334155', linespacing=1.35)

    # ==========================================================================
    # CENTRAL CONNECTOR: AD FLOW TO FEED DELIVERY
    # ==========================================================================
    # Draw large stylized connector between approved ad database (left) and age-gated feed (right)
    draw_arrow(ax, 760, 210, 1720, 210, color='#2563eb', width=4.0)
    ax.text(1600, 240, "Dynamic Real-Time Ad Query\nFiltered by Certified Age Group", 
            fontsize=11.5, fontweight='bold', color='#1e3a8a', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffffff', edgecolor='#3b82f6', lw=1.5))

    # Save to all requested paths
    for p in output_paths:
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        plt.savefig(p, dpi=200, bbox_inches='tight')
        print(f"Generated Combined System Architecture: {p}")
        
    plt.close()

if __name__ == "__main__":
    targets = [
        r"c:\Users\hello\Videos\sourav\system_architecture.png",
        r"c:\Users\hello\Videos\sourav\results\system_architecture.png"
    ]
    generate_system_architecture(targets)
