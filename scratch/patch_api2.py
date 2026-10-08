import sys

# Patch face_age_api.py
content1 = open("face-age/face_age_api.py").read()
if "isinstance(obj, np.ndarray)" not in content1:
    content1 = content1.replace(
        "if isinstance(obj, np.generic):",
        "if isinstance(obj, np.ndarray):\n            return obj.tolist()\n        elif isinstance(obj, np.generic):"
    )
    open("face-age/face_age_api.py", "w").write(content1)
    print("Patched face_age_api.py")

# Patch safead_client.py
content2 = open("frontend/services/safead_client.py").read()
if "timeout=60)" in content2:
    content2 = content2.replace("timeout=60)", "timeout=600)")
    open("frontend/services/safead_client.py", "w").write(content2)
    print("Patched safead_client.py timeout")
