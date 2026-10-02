import os
import cv2
from PIL import Image

def extract_ocr_from_image(image_input) -> str:
    """
    Extracts text from an image (PIL Image, numpy array, or file path).
    Tries PyTesseract first; falls back gracefully to filename/metadata analysis if missing.
    """
    # Normalize input to PIL Image
    pil_img = None
    file_path = ""
    
    if isinstance(image_input, str):
        file_path = image_input
        if os.path.exists(file_path):
            try:
                pil_img = Image.open(file_path).convert("RGB")
            except Exception:
                pass
    elif isinstance(image_input, Image.Image):
        pil_img = image_input
    elif hasattr(image_input, "dtype"):  # numpy array
        pil_img = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
        
    extracted_text = ""
    
    # 1. Attempt PyTesseract
    try:
        import pytesseract
        if pil_img:
            extracted_text = pytesseract.image_to_string(pil_img).strip()
    except Exception:
        extracted_text = ""
        
    # 2. Fallback heuristic parsing if OCR text is empty
    if not extracted_text and file_path:
        base_name = os.path.basename(file_path).lower().replace("_", " ").replace("-", " ")
        # Extract meaningful tokens from path
        tokens = [w for w in base_name.split() if w not in ["jpg", "png", "jpeg", "mp4", "ad", "image", "file"]]
        extracted_text = " ".join(tokens)
        
    return extracted_text if extracted_text else "No text detected in creative overlay."

def extract_video_ocr(sampled_frames: list) -> str:
    """
    Extracts text from representative sampled video frames,
    combines results, and removes duplicate lines/phrases.
    """
    if not sampled_frames:
        return "No text detected in creative overlay."

    seen_lines = set()
    combined_lines = []

    for frame in sampled_frames:
        txt = extract_ocr_from_image(frame)
        if txt and txt != "No text detected in creative overlay.":
            for line in txt.splitlines():
                line_clean = line.strip()
                if line_clean and line_clean.lower() not in seen_lines:
                    seen_lines.add(line_clean.lower())
                    combined_lines.append(line_clean)

    if combined_lines:
        return " ".join(combined_lines)
    return "No text detected in creative overlay."

