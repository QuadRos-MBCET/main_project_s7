import re
import glob

def clean_figures_in_text(text):
    # Regex to find \IfFileExists blocks and ensure proper filenames and clean fallback boxes
    # Pattern: \IfFileExists{...}{...}{...}
    
    # Let's map known figure names to their clean fallback label
    figure_labels = {
        "system_architecture.png": "SafeAd AI Three-Tier End-to-End System Architecture",
        "results/system_architecture.png": "SafeAd AI Three-Tier End-to-End System Architecture",
        "joseph_safead_core/backend2jb/system diagrams/dfd_level_0.jpg": "SafeAd AI Level 0 Context Data Flow Diagram",
        "dfd_level_0.jpg": "SafeAd AI Level 0 Context Data Flow Diagram",
        "joseph_safead_core/backend2jb/system diagrams/dfd_level_1.jpg": "SafeAd AI Level 1 Subsystem Process Decomposition Diagram",
        "dfd_level_1 (1).png": "SafeAd AI Level 1 Subsystem Process Decomposition Diagram",
        "dfd_level_1.jpg": "SafeAd AI Level 1 Subsystem Process Decomposition Diagram",
        "joseph_safead_core/backend2jb/system diagrams/class_diagram.jpg": "SafeAd AI Unified Object-Oriented Architecture Class Diagram",
        "class_diagram.jpg": "SafeAd AI Unified Object-Oriented Architecture Class Diagram",
        "joseph_safead_core/backend2jb/system diagrams/use_case_diagram.jpg": "SafeAd AI Platform Actor UML Use Case Diagram",
        "use_case_diagram.jpg": "SafeAd AI Platform Actor UML Use Case Diagram",
        "safead_use_case_diagram.png": "SafeAd AI Platform Actor UML Use Case Diagram",
        "results/visual_safety_result.png": "Visual Hazard and Safety Guardrail Detection Telemetry",
        "results/nsfw_result.png": "Falcon NSFW ViT Suggestive and Adult Content Classification Output",
        "results/video_analysis_result.png": "Farneback Optical Motion Dynamics and Keyframe Energy Timeline",
        "results/ocr_result.png": "CLAHE and Otsu Enhanced EasyOCR Text Extraction Bounding Overlays",
        "results/audio_transcription_result.png": "OpenAI Whisper Speech Transcription and Audio Risk Analysis Output",
        "results/policy_confusion_matrix.png": "Random Forest 5-Fold Cross-Validation Confusion Matrix (N=194)",
        "results/facenet_matching_result.png": "ArcFace Live Biometric Cross-Matching Telemetry HUD",
        "results/facenet_similarity_distribution.png": "Cosine Similarity Density Distributions: Genuine vs Impostor Pairs",
        "liveness_result.png": "Dual-Scale MiniFASNet Live Verification Diagnostic HUD",
        "results/liveness_result.png": "Dual-Scale MiniFASNet Live Verification Diagnostic HUD",
        "spoof.png": "Presentation Attack Interception HUD: Screen Replay Detected",
        "results/spoof.png": "Presentation Attack Interception HUD: Screen Replay Detected",
        "results/id_ocr_result.png": "Credential Document Ingestion and Date-of-Birth OCR Telemetry",
        "results/age_confusion_matrix.png": "Vision Transformer Age Estimation Confusion Matrix",
        "results/age_aware_feed_result.png": "Age-Aware Programmatic Delivery Filtering Dashboard Interface",
        "results/admin_review_result.png": "Compliance Officer Human-in-the-Loop Audit Portal Interface",
        "results/xai_explanation_result.png": "Explainable AI (XAI) Multimodal Diagnostic Attribution Dashboard",
        "sample_ad_media/apples_ad.jpg": "Apples Commercial Ad (SAFE-FOR-ALL)",
        "apples_ad.jpg": "Apples Commercial Ad (SAFE-FOR-ALL)",
        "joseph_safead_core/backend2jb/datasets/samples/safe_python_ad.jpg": "Python Educational Ad (SAFE-FOR-ALL)",
        "safe_python_ad.jpg": "Python Educational Ad (SAFE-FOR-ALL)",
        "joseph_safead_core/backend2jb/datasets/samples/violence_combat_ad.jpg": "Action Combat and Gaming Ad (SAFE-14-PLUS)",
        "violence_combat_ad.jpg": "Action Combat and Gaming Ad (SAFE-14-PLUS)",
        "sample_ad_media/beer_pub.jpg": "Commercial Brewery and Pub Ad (SAFE-18-PLUS)",
        "beer_pub.jpg": "Commercial Brewery and Pub Ad (SAFE-18-PLUS)",
        "sample_ad_media/adult_dating.jpg": "Adult Matchmaking Service Ad (SAFE-18-PLUS)",
        "adult_dating.jpg": "Adult Matchmaking Service Ad (SAFE-18-PLUS)",
        "sample_ad_media/lucky_draw.jpg": "Predatory Lottery Scam Ad (UNSAFE-FOR-ALL)",
        "lucky_draw.jpg": "Predatory Lottery Scam Ad (UNSAFE-FOR-ALL)",
        "joseph_safead_core/backend2jb/datasets/samples/scam_paisa_double_ad.jpg": "Paisa Double Ponzi Scam Ad (UNSAFE-FOR-ALL)",
        "scam_paisa_double_ad.jpg": "Paisa Double Ponzi Scam Ad (UNSAFE-FOR-ALL)"
    }

    # First clean any mangled [SafeAd ...] inside \IfFileExists or \includegraphics
    # Replace back to canonical relative paths
    reverse_map = {
        r"[Random Forest 5-Fold Cross-Validation Confusion Matrix on 194 Samples]": "results/policy_confusion_matrix.png",
        r"[SafeAd AI Three-Tier End-to-End System Architecture Blueprint]": "system_architecture.png",
        r"[SafeAd AI Level 0 Context Data Flow Diagram]": "joseph_safead_core/backend2jb/system diagrams/dfd_level_0.jpg",
        r"[SafeAd AI Level 1 Subsystem Process Decomposition Diagram]": "joseph_safead_core/backend2jb/system diagrams/dfd_level_1.jpg",
        r"[SafeAd AI Unified Object-Oriented Architecture Class Diagram]": "joseph_safead_core/backend2jb/system diagrams/class_diagram.jpg",
        r"[SafeAd AI Platform Actor UML Use Case Diagram]": "joseph_safead_core/backend2jb/system diagrams/use_case_diagram.jpg",
        r"[SafeAd AI Comprehensive Platform Actor UML Use Case Diagram]": "joseph_safead_core/backend2jb/system diagrams/use_case_diagram.jpg",
        r"[SafeAd AI UML Use Case Functional Interaction Diagram]": "safead_use_case_diagram.png",
        r"[Visual Hazard and Safety Guardrail Detection Telemetry]": "results/visual_safety_result.png",
        r"[Falcon NSFW ViT Suggestive and Adult Content Classification Output]": "results/nsfw_result.png",
        r"[Farneb\"{a}ck Optical Motion Dynamics and Keyframe Energy Timeline]": "results/video_analysis_result.png",
        r"[Farneb\"{\a}ck Optical Motion Dynamics and Keyframe Energy Timeline]": "results/video_analysis_result.png",
        r"[CLAHE and Otsu Enhanced EasyOCR Text Extraction Bounding Overlays]": "results/ocr_result.png",
        r"[OpenAI Whisper Speech Transcription and Audio Risk Analysis Output]": "results/audio_transcription_result.png",
        r"[ArcFace Live Biometric Cross-Matching Telemetry HUD]": "results/facenet_matching_result.png",
        r"[Cosine Similarity Density Distributions: Genuine vs Impostor Pairs]": "results/facenet_similarity_distribution.png",
        r"[Dual-Scale MiniFASNet Live Verification Diagnostic HUD]": "results/liveness_result.png",
        r"[Presentation Attack Interception HUD: Screen Replay Detected]": "results/spoof.png",
        r"[Credential Document Ingestion and Date-of-Birth OCR Telemetry]": "results/id_ocr_result.png",
        r"[Vision Transformer Age Estimation Confusion Matrix]": "results/age_confusion_matrix.png",
        r"[Age-Aware Programmatic Delivery Filtering Dashboard Interface]": "results/age_aware_feed_result.png",
        r"[Compliance Officer Human-in-the-Loop Audit Portal Interface]": "results/admin_review_result.png",
        r"[Explainable AI (XAI) Multimodal Diagnostic Attribution Dashboard]": "results/xai_explanation_result.png",
    }
    for bad, good in reverse_map.items():
        text = text.replace(bad, good)

    # Also handle partial Farneb matches
    text = re.sub(r'\[Farneb[^{]*\{a\}\s*ck[^\]]*\]', 'results/video_analysis_result.png', text)

    return text

def run():
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    for f in glob.glob("tools/report_modules/*.py"):
        with open(f, "r", encoding="utf-8") as fp:
            c = fp.read()
        cleaned = clean_figures_in_text(c)
        with open(f, "w", encoding="utf-8") as fp:
            fp.write(cleaned)
        print(f"Cleaned {f}")

    from tools.assemble_report import assemble
    assemble()

    tex_path = "SAFE_VISION_Final_Project_Report.tex"
    with open(tex_path, "r", encoding="utf-8") as fp:
        c = fp.read()
    c = clean_figures_in_text(c)
    with open(tex_path, "w", encoding="utf-8") as fp:
        fp.write(c)
    print("Report file re-cleaned successfully!")

if __name__ == "__main__":
    run()
