import codecs

with codecs.open("frontend/pages/user_workspace.py", "r", "utf-8") as f:
    lines = f.readlines()

# 1. Add 'souravrd' to default user_db
for i, line in enumerate(lines):
    if '"demo": {"password": "demo"' in line:
        lines[i] = '            "demo": {"password": "demo", "category": "18 to 24", "norm": "AGE_18_PLUS"},\n            "souravrd": {"password": "loyola", "category": "18 to 24", "norm": "AGE_18_PLUS"}\n'
        break

# 2. Fix the indentation of the verdict block
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    # Find the separator right after camera block
    if line == '        st.markdown("---")\n' and 'ID vs Live Face' in lines[i+1]:
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
print("Indentation fixed and user added.")
