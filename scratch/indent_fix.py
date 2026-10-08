import codecs

with codecs.open("frontend/pages/user_workspace.py", "r", "utf-8") as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "c_id, c_live = st.columns([1, 1]" in line:
        start_idx = i
    if line.strip() == "else:" and "st.markdown" in lines[i+1]:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    for i in range(start_idx, end_idx):
        if len(lines[i].strip()) > 0:
            lines[i] = "    " + lines[i]

with codecs.open("frontend/pages/user_workspace.py", "w", "utf-8") as f:
    f.writelines(lines)
print("Indentation fixed.")
