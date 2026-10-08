import codecs

with codecs.open("frontend/pages/user_workspace.py", "r", "utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip() == "else:" and "st.markdown" in lines[i+1] and "border:2px dashed" in lines[i+2]:
        lines[i] = "                else:\n"
        print("Fixed else on line", i)

with codecs.open("frontend/pages/user_workspace.py", "w", "utf-8") as f:
    f.writelines(lines)
print("Syntax fixed")
