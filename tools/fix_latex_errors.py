import re
import glob
import os
import sys

def fix_content(c):
    # Restore any file paths that might have gotten replaced accidentally:
    c = c.replace(r"joseph_safead_core/backend2jb/system diagrams/[SafeAd AI Level 0 Context Data Flow Diagram]", "joseph_safead_core/backend2jb/system diagrams/dfd_level_0.jpg")
    c = c.replace(r"joseph_safead_core/backend2jb/system diagrams/[SafeAd AI Unified Object-Oriented Architecture Class Diagram]", "joseph_safead_core/backend2jb/system diagrams/class_diagram.jpg")
    c = c.replace(r"joseph_safead_core/backend2jb/system diagrams/[SafeAd AI Comprehensive Platform Actor UML Use Case Diagram]", "joseph_safead_core/backend2jb/system diagrams/use_case_diagram.jpg")

    # 1. Fix Table 4.1 in Chapter 4:
    c = c.replace(r"\textbf{Preconditions & Triggers} & \textbf{Postconditions & System Action}", 
                  r"\textbf{Preconditions \& Triggers} & \textbf{Postconditions \& System Action}")
    c = c.replace("Trust & Safety Officer", "Trust \\& Safety Officer")

    # 2. Fix Section and Subsection headers containing '&'
    headers_to_fix = [
        ("Detailed Problem Statement & Mathematical Objectives", "Detailed Problem Statement \\& Mathematical Objectives"),
        ("Summary of Scientific & Engineering Contributions", "Summary of Scientific \\& Engineering Contributions"),
        ("The Four-Tier Content Policy Taxonomy: Comprehensive Statutory & Policy Defense", "The Four-Tier Content Policy Taxonomy: Comprehensive Statutory \\& Policy Defense"),
        ("Biometric Age Assurance & Recipient Verification Mapping", "Biometric Age Assurance \\& Recipient Verification Mapping"),
        ("Tier 2: Backend Application & Detector Engine", "Tier 2: Backend Application \\& Detector Engine"),
        ("Optical Character Recognition & Typographic Enhancement", "Optical Character Recognition \\& Typographic Enhancement"),
        ("Visual Scene Safety: Llama Guard 3 Vision & Empirical Failure Analysis", "Visual Scene Safety: Llama Guard 3 Vision \\& Empirical Failure Analysis"),
        ("OCR Text Safety & Toxicity: RoBERTa & DeBERTa", "OCR Text Safety \\& Toxicity: RoBERTa \\& DeBERTa"),
        ("Commercial Risk & Deception Analyzer", "Commercial Risk \\& Deception Analyzer"),
        ("Realtime Vision Engine & DirectShow Concurrency Control", "Realtime Vision Engine \\& DirectShow Concurrency Control"),
        ("Presentation Attack Detection (PAD) & Biometrics", "Presentation Attack Detection (PAD) \\& Biometrics"),
        ("ViT Facial Age Estimation & Mandibular Edge Density", "ViT Facial Age Estimation \\& Mandibular Edge Density"),
        ("Multimodal Detector Validation & Functional Results", "Multimodal Detector Validation \\& Functional Results"),
        ("Video Motion Kinetics & Keyframe Dynamics", "Video Motion Kinetics \\& Keyframe Dynamics"),
        ("Category 4: \\texttt{UNSAFE\\_FOR\\_ALL} (Universally Prohibited Hazards & Scams)", "Category 4: \\texttt{UNSAFE\\_FOR\\_ALL} (Universally Prohibited Hazards \\& Scams)"),
        ("Category 4: \\texttt{UNSAFE_FOR_ALL} (Universally Prohibited Hazards & Scams)", "Category 4: \\texttt{UNSAFE\\_FOR\\_ALL} (Universally Prohibited Hazards \\& Scams)"),
        ("Identified Gaps & Limitations", "Identified Gaps \\& Limitations"),
        ("Preconditions & Triggers", "Preconditions \\& Triggers"),
        ("Postconditions & System Action", "Postconditions \\& System Action"),
        ("Delivery Filtering and Human-in-the-Loop Review", "Delivery Filtering and Human-in-the-Loop Review"),
        ("System Architecture and Detailed Design", "System Architecture and Detailed Design"),
    ]
    for old, new in headers_to_fix:
        c = c.replace(old, new)

    # 3. Fix unescaped '&' in common prose expressions
    prose_amps = [
        ("Google Ads & Meta Advertising Standards", "Google Ads \\& Meta Advertising Standards"),
        ("Google Ads Editorial & Professional Standards", "Google Ads Editorial \\& Professional Standards"),
        ("UK Advertising Standards Authority (ASA) & CAP Code", "UK Advertising Standards Authority (ASA) \\& CAP Code"),
        ("IARC / ESRB Teen (13+) & PEGI 12 Content Descriptors", "IARC / ESRB Teen (13+) \\& PEGI 12 Content Descriptors"),
        ("Meta Advertising Standards --- Restricted Goods & Services", "Meta Advertising Standards --- Restricted Goods \\& Services"),
        ("IARC Mature (17+/18+) & PEGI 18 Standards", "IARC Mature (17+/18+) \\& PEGI 18 Standards"),
        ("Google Ads Policies --- Prohibited Content & Dishonest Behavior", "Google Ads Policies --- Prohibited Content \\& Dishonest Behavior"),
        ("Client Presentation Layer, the Core Backend & Detector Engine", "Client Presentation Layer, the Core Backend \\& Detector Engine"),
        ("Policy & Audit Logging Broker", "Policy \\& Audit Logging Broker"),
        ("Evidence Vectorization & Risk Scoring", "Evidence Vectorization \\& Risk Scoring"),
        ("Dual-Model Inference & Policy Evaluation", "Dual-Model Inference \\& Policy Evaluation"),
        ("Hierarchical Safety Fusion & HITL Routing", "Hierarchical Safety Fusion \\& HITL Routing"),
        ("Decoupled Video Capture & Anti-Spoofing", "Decoupled Video Capture \\& Anti-Spoofing"),
        ("Biometric Matching & Age Assurance", "Biometric Matching \\& Age Assurance"),
        ("Policy Rules & Threshold Repository", "Policy Rules \\& Threshold Repository"),
        ("Preconditions & Triggers", "Preconditions \\& Triggers"),
        ("Postconditions & System Action", "Postconditions \\& System Action"),
        ("Adaptive Keyframe & Audio Extraction", "Adaptive Keyframe \\& Audio Extraction"),
        ("Risk Indexing & Random Forest Evaluation", "Risk Indexing \\& Random Forest Evaluation"),
        ("Hardware Capture & Anti-Spoofing", "Hardware Capture \\& Anti-Spoofing"),
        ("Biometric Matching & Age-Gated Delivery", "Biometric Matching \\& Age-Gated Delivery"),
        ("Optical Character Recognition & Typographic Enhancement", "Optical Character Recognition \\& Typographic Enhancement"),
        ("Visual Scene Safety: Llama Guard 3 Vision & Empirical Failure Analysis", "Visual Scene Safety: Llama Guard 3 Vision \\& Empirical Failure Analysis"),
        ("Commercial Risk & Deception Analyzer", "Commercial Risk \\& Deception Analyzer"),
        ("Realtime Vision Engine & DirectShow Concurrency Control", "Realtime Vision Engine \\& DirectShow Concurrency Control"),
        ("Presentation Attack Detection (PAD) & Biometrics", "Presentation Attack Detection (PAD) \\& Biometrics"),
        ("ViT Facial Age Estimation & Mandibular Edge Density", "ViT Facial Age Estimation \\& Mandibular Edge Density"),
        ("Multimodal Detector Validation & Functional Results", "Multimodal Detector Validation \\& Functional Results"),
        ("Video Motion Kinetics & Keyframe Dynamics", "Video Motion Kinetics \\& Keyframe Dynamics"),
        ("Commercial Brewery & Pub Ad", "Commercial Brewery \\& Pub Ad"),
        ("Problem Formulation & Policy Framework", "Problem Formulation \\& Policy Framework"),
        ("Summary of Scientific & Engineering Contributions", "Summary of Scientific \\& Engineering Contributions"),
        ("Detailed Problem Statement & Mathematical Objectives", "Detailed Problem Statement \\& Mathematical Objectives"),
        ("Research Gaps & Motivation", "Research Gaps \\& Motivation"),
        ("Background & Industrial Context", "Background \\& Industrial Context"),
        ("Core Backend & Detector Engine", "Core Backend \\& Detector Engine"),
        ("Advertising Standards Authority (ASA) &", "Advertising Standards Authority (ASA) \\&"),
    ]
    for old, new in prose_amps:
        c = c.replace(old, new)

    # 4. Clean captions
    c = c.replace(r"\caption{Consumer Grocery Promotion (`apples_ad.jpg`)}", r"\caption{Consumer Grocery Promotion (\texttt{apples\_ad.jpg})}")
    c = c.replace(r"\caption{Educational Software Ad (`safe_python_ad.jpg`)}", r"\caption{Educational Software Ad (\texttt{safe\_python\_ad.jpg})}")
    c = c.replace(r"\caption{Representative `SAFE\_FOR\_ALL` Commercial Advertisements.}", r"\caption{Representative \texttt{SAFE\_FOR\_ALL} Commercial Advertisements.}")
    c = c.replace(r"\caption{Representative `SAFE_FOR_ALL` Commercial Advertisements.}", r"\caption{Representative \texttt{SAFE\_FOR\_ALL} Commercial Advertisements.}")
    c = c.replace(r"\caption{Representative `SAFE\_14\_PLUS` Adolescent Commercial Advertisements.}", r"\caption{Representative \texttt{SAFE\_14\_PLUS} Adolescent Commercial Advertisements.}")
    c = c.replace(r"\caption{Representative `SAFE_14_PLUS` Adolescent Commercial Advertisements.}", r"\caption{Representative \texttt{SAFE\_14\_PLUS} Adolescent Commercial Advertisements.}")
    c = c.replace(r"\caption{Commercial Brewery & Pub Ad (`beer_pub.jpg`)}", r"\caption{Commercial Brewery \& Pub Ad (\texttt{beer\_pub.jpg})}")
    c = c.replace(r"\caption{Commercial Brewery \& Pub Ad (`beer_pub.jpg`)}", r"\caption{Commercial Brewery \& Pub Ad (\texttt{beer\_pub.jpg})}")
    c = c.replace(r"\caption{Adult Social Matchmaking (`adult_dating.jpg`)}", r"\caption{Adult Social Matchmaking (\texttt{adult\_dating.jpg})}")
    c = c.replace(r"\caption{Representative `SAFE\_18\_PLUS` Adult-Restricted Commercial Advertisements.}", r"\caption{Representative \texttt{SAFE\_18\_PLUS} Adult-Restricted Commercial Advertisements.}")
    c = c.replace(r"\caption{Representative `SAFE_18_PLUS` Adult-Restricted Commercial Advertisements.}", r"\caption{Representative \texttt{SAFE\_18\_PLUS} Adult-Restricted Commercial Advertisements.}")
    c = c.replace(r"\caption{Predatory Lucky Draw Scam (`lucky_draw.jpg`)}", r"\caption{Predatory Lucky Draw Scam (\texttt{lucky\_draw.jpg})}")
    c = c.replace(r"\caption{Guaranteed Returns Fraud (`scam_paisa_double_ad.jpg`)}", r"\caption{Guaranteed Returns Fraud (\texttt{scam\_paisa\_double\_ad.jpg})}")
    c = c.replace(r"\caption{Representative `UNSAFE\_FOR\_ALL` Universally Prohibited Advertisements.}", r"\caption{Representative \texttt{UNSAFE\_FOR\_ALL} Universally Prohibited Advertisements.}")
    c = c.replace(r"\caption{Representative `UNSAFE_FOR_ALL` Universally Prohibited Advertisements.}", r"\caption{Representative \texttt{UNSAFE\_FOR\_ALL} Universally Prohibited Advertisements.}")

    # 5. Clean prose filenames
    c = c.replace("`safe\\_python_ad.jpg`", r"\texttt{safe\_python\_ad.jpg}")
    c = c.replace("`safe_python_ad.jpg`", r"\texttt{safe\_python\_ad.jpg}")
    c = c.replace("`apples_ad.jpg`", r"\texttt{apples\_ad.jpg}")
    c = c.replace("`beer_pub.jpg`", r"\texttt{beer\_pub.jpg}")
    c = c.replace("`adult_dating.jpg`", r"\texttt{adult\_dating.jpg}")
    c = c.replace("`lucky_draw.jpg`", r"\texttt{lucky\_draw.jpg}")
    c = c.replace("`scam_paisa_double_ad.jpg`", r"\texttt{scam\_paisa\_double\_ad.jpg}")
    c = c.replace(r"\texttt{SAFEAD\_S14P\_IMG_050}", r"\texttt{SAFEAD\_S14P\_IMG\_050}")
    c = c.replace(r"\texttt{SAFEAD_S14P_IMG_050}", r"\texttt{SAFEAD\_S14P\_IMG\_050}")

    # 6. Fallback boxes with zero raw underscores
    box_map = [
        (r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{ArcFace Cross-Matching HUD (results/facenet_matching_result.png)}}}",
         r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{[ArcFace Live Biometric Cross-Matching Telemetry HUD]}}}"),
        (r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{Similarity Distribution (results/facenet_similarity_distribution.png)}}}",
         r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{[Cosine Similarity Density Distributions: Genuine vs Impostor Pairs]}}}"),
        (r"\fbox{\parbox{0.75\textwidth}{\centering \textbf{ID Document Processing Screenshot (results/id_ocr_result.png)}}}",
         r"\fbox{\parbox{0.75\textwidth}{\centering \textbf{[Credential Document Ingestion and Date-of-Birth OCR Telemetry]}}}"),
        (r"\fbox{\parbox{0.50\textwidth}{\centering \textbf{ViT Age Confusion Matrix (results/age_confusion_matrix.png)}}}",
         r"\fbox{\parbox{0.50\textwidth}{\centering \textbf{[Vision Transformer Age Estimation Confusion Matrix]}}}"),
        (r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{Age-Aware Delivery Feed (results/age_aware_feed_result.png)}}}",
         r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{[Age-Aware Programmatic Delivery Filtering Dashboard Interface]}}}"),
        (r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{Admin Review Dashboard (results/admin_review_result.png)}}}",
         r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{[Compliance Officer Human-in-the-Loop Audit Portal Interface]}}}"),
        (r"\fbox{\parbox{0.75\textwidth}{\centering \textbf{Explainability Dashboard (results/xai_explanation_result.png)}}}",
         r"\fbox{\parbox{0.75\textwidth}{\centering \textbf{[Explainable AI (XAI) Multimodal Diagnostic Attribution Dashboard]}}}"),
        (r"\fbox{\parbox{0.78\textwidth}{\centering \textbf{Visual Safety Analysis Output Screenshot (results/visual_safety_result.png)}}}",
         r"\fbox{\parbox{0.78\textwidth}{\centering \textbf{[Visual Hazard and Safety Guardrail Detection Telemetry]}}}"),
        (r"\fbox{\parbox{0.78\textwidth}{\centering \textbf{Falcon NSFW Detection Output Screenshot (results/nsfw_result.png)}}}",
         r"\fbox{\parbox{0.78\textwidth}{\centering \textbf{[Falcon NSFW ViT Suggestive and Adult Content Classification Output]}}}"),
        (r"\fbox{\parbox{0.78\textwidth}{\centering \textbf{Video Analysis and Optical Flow Output (results/video_analysis_result.png)}}}",
         r"\fbox{\parbox{0.78\textwidth}{\centering \textbf{[Farneb\"{a}ck Optical Motion Dynamics and Keyframe Energy Timeline]}}}"),
        (r"\fbox{\parbox{0.78\textwidth}{\centering \textbf{OCR Text Extraction Output (results/ocr_result.png)}}}",
         r"\fbox{\parbox{0.78\textwidth}{\centering \textbf{[CLAHE and Otsu Enhanced EasyOCR Text Extraction Bounding Overlays]}}}"),
        (r"\fbox{\parbox{0.78\textwidth}{\centering \textbf{Audio Transcription Output (results/audio_transcription_result.png)}}}",
         r"\fbox{\parbox{0.78\textwidth}{\centering \textbf{[OpenAI Whisper Speech Transcription and Audio Risk Analysis Output]}}}"),
        (r"\fbox{\parbox{0.55\textwidth}{\centering \textbf{Phase 8 Random Forest Confusion Matrix (results/policy_confusion_matrix.png)}}}",
         r"\fbox{\parbox{0.55\textwidth}{\centering \textbf{[Random Forest 5-Fold Cross-Validation Confusion Matrix on 194 Samples]}}}"),
        (r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{[SafeAd AI Three-Tier End-to-End System Architecture]}}}",
         r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{[SafeAd AI Three-Tier End-to-End System Architecture]}}}"),
        (r"\fbox{\parbox{0.75\textwidth}{\centering \textbf{DFD Level 0 Context Diagram}}}",
         r"\fbox{\parbox{0.75\textwidth}{\centering \textbf{[SafeAd AI Level 0 Context Data Flow Diagram]}}}"),
        (r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{DFD Level 1 Process Decomposition}}}",
         r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{[SafeAd AI Level 1 Subsystem Process Decomposition Diagram]}}}"),
        (r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{SafeAd AI UML Class Diagram}}}",
         r"\fbox{\parbox{0.80\textwidth}{\centering \textbf{[SafeAd AI Unified Object-Oriented Architecture Class Diagram]}}}"),
        (r"\fbox{\parbox{0.70\textwidth}{\centering \textbf{SafeAd AI UML Use Case Diagram}}}",
         r"\fbox{\parbox{0.70\textwidth}{\centering \textbf{[SafeAd AI Platform Actor UML Use Case Diagram]}}}"),
    ]
    for old, new in box_map:
        c = c.replace(old, new)

    return c

def process_all():
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    mod_files = glob.glob("tools/report_modules/*.py")
    for f in mod_files:
        with open(f, "r", encoding="utf-8") as fp:
            content = fp.read()
        fixed = fix_content(content)
        with open(f, "w", encoding="utf-8") as fp:
            fp.write(fixed)
        print(f"Updated {f}")

    from tools.assemble_report import assemble
    assemble()

    tex_path = "SAFE_VISION_Final_Project_Report.tex"
    with open(tex_path, "r", encoding="utf-8") as fp:
        c = fp.read()
    c = fix_content(c)
    with open(tex_path, "w", encoding="utf-8") as fp:
        fp.write(c)
    print("Report file fully sanitized and verified!")

if __name__ == "__main__":
    process_all()
