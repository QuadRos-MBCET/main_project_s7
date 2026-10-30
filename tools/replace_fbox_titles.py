import glob

def replace_in_file(path):
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    subs = [
        (r"\textbf{joseph_safead_core/backend2jb/system diagrams/dfd_level_0.jpg}", r"\textbf{SafeAd AI Level 0 Context Data Flow Diagram}"),
        (r"\textbf{joseph_safead_core/backend2jb/system diagrams/dfd_level_1.jpg}", r"\textbf{SafeAd AI Level 1 Process Decomposition Diagram}"),
        (r"\textbf{joseph_safead_core/backend2jb/system diagrams/class_diagram.jpg}", r"\textbf{SafeAd AI Unified Object-Oriented Architecture Class Diagram}"),
        (r"\textbf{joseph_safead_core/backend2jb/system diagrams/use_case_diagram.jpg}", r"\textbf{SafeAd AI Platform Actor UML Use Case Diagram}"),
        (r"\textbf{Visual Safety Analysis Output Screenshot (results/visual_safety_result.png)}", r"\textbf{Visual Hazard and Safety Guardrail Detection Telemetry}"),
        (r"\textbf{Falcon NSFW Detection Output Screenshot (results/nsfw_result.png)}", r"\textbf{Falcon NSFW Suggestive and Adult Content Classification Output}"),
        (r"\textbf{Video Analysis and Optical Flow Output (results/video_analysis_result.png)}", r"\textbf{Farneb\"{a}ck Optical Motion Dynamics and Keyframe Energy Timeline}"),
        (r"\textbf{OCR Text Extraction Output (results/ocr_result.png)}", r"\textbf{CLAHE and Otsu Enhanced EasyOCR Text Extraction Bounding Overlays}"),
        (r"\textbf{Audio Transcription Output (results/audio_transcription_result.png)}", r"\textbf{OpenAI Whisper Speech Transcription and Audio Risk Analysis Output}"),
        (r"\textbf{Phase 8 Random Forest Confusion Matrix (results/policy_confusion_matrix.png)}", r"\textbf{Random Forest 5-Fold Cross-Validation Confusion Matrix}"),
        (r"\textbf{ArcFace Cross-Matching HUD (results/facenet_matching_result.png)}", r"\textbf{ArcFace Live Biometric Cross-Matching Telemetry HUD}"),
        (r"\textbf{Similarity Distribution (results/facenet_similarity_distribution.png)}", r"\textbf{Cosine Similarity Density Distributions: Genuine vs Impostor Pairs}"),
        (r"\textbf{ID Document Processing Screenshot (results/id_ocr_result.png)}", r"\textbf{Credential Document Ingestion and Date-of-Birth OCR Telemetry}"),
        (r"\textbf{ViT Age Confusion Matrix (results/age_confusion_matrix.png)}", r"\textbf{Vision Transformer Age Estimation Confusion Matrix}"),
        (r"\textbf{Age-Aware Delivery Feed (results/age_aware_feed_result.png)}", r"\textbf{Age-Aware Programmatic Delivery Filtering Dashboard Interface}"),
        (r"\textbf{Admin Review Dashboard (results/admin_review_result.png)}", r"\textbf{Compliance Officer Human-in-the-Loop Audit Portal Interface}"),
        (r"\textbf{Explainability Dashboard (results/xai_explanation_result.png)}", r"\textbf{Explainable AI Multimodal Diagnostic Attribution Dashboard}"),
        (r"\textbf{dfd_level_0.jpg}", r"\textbf{SafeAd AI Level 0 Context Data Flow Diagram}"),
        (r"\textbf{dfd_level_1 (1).png}", r"\textbf{SafeAd AI Level 1 Process Decomposition Diagram}"),
        (r"\textbf{class_diagram.jpg}", r"\textbf{SafeAd AI Unified Object-Oriented Architecture Class Diagram}"),
        (r"\textbf{use_case_diagram.jpg}", r"\textbf{SafeAd AI Platform Actor UML Use Case Diagram}"),
        (r"\textbf{safead_use_case_diagram.png}", r"\textbf{SafeAd AI Platform Actor UML Use Case Diagram}"),
    ]

    for old, new in subs:
        c = c.replace(old, new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

for f in glob.glob("tools/report_modules/*.py"):
    replace_in_file(f)

replace_in_file("SAFE_VISION_Final_Project_Report.tex")
print("Fallback titles cleanly replaced!")
