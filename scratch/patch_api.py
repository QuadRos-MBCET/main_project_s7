import sys
content = open("face-age/face_age_api.py").read()

new_endpoints = """
@app.post("/api/verify_id_and_face")
async def verify_id_and_face(
    id_file: UploadFile = File(...),
    live_file: UploadFile = File(...),
    manual_dob: str = Form(None)
):
    try:
        from website.classifier import verify_id_card_and_live_face, process_pdf_id_document
    except ImportError:
        raise HTTPException(status_code=500, detail="Classifier not found")
        
    live_contents = await live_file.read()
    live_image = np.array(Image.open(io.BytesIO(live_contents)).convert("RGB"))
    
    id_contents = await id_file.read()
    import os
    id_ext = os.path.splitext(id_file.filename)[1].lower()
    
    id_image = None
    pdf_text = None
    if id_ext == ".pdf":
        id_image, pdf_text = process_pdf_id_document(id_contents)
    else:
        id_image = np.array(Image.open(io.BytesIO(id_contents)).convert("RGB"))
        
    res = verify_id_card_and_live_face(id_image, live_image, manual_dob, pdf_text)
    
    def convert_types(obj):
        if isinstance(obj, np.generic):
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(i) for i in obj]
        return obj
        
    return convert_types(res)
"""

if "/api/verify_id_and_face" not in content:
    content = content.replace('if __name__ == "__main__":', new_endpoints + '\nif __name__ == "__main__":')
    open("face-age/face_age_api.py", "w").write(content)
    print("Patched face_age_api.py")
else:
    print("Already patched")
