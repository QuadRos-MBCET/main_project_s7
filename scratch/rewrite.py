import codecs
with codecs.open("frontend/views/user_workspace.py", "r", "utf-8") as f:
    c = f.read()
c = c.replace("../../face-age", "../../sooraj_face_age_core/face-age")
with codecs.open("frontend/views/user_workspace.py", "w", "utf-8") as f:
    f.write(c)
print("Updated face-age path in user_workspace.py")
