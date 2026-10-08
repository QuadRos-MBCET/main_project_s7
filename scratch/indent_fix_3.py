import codecs

with codecs.open("frontend/pages/user_workspace.py", "r", "utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    # Just fix the specific else block that causes the problem
    if line.strip() == "else:" and "border:2px dashed" in lines[i+2]:
        # It's line 121
        # The else needs to match 'if cam_active:'
        lines[i] = "                else:\n"
        # The next 8 lines belong to it!
        for j in range(i+1, i+9):
            if lines[j].strip():
                # Add 4 spaces
                lines[j] = "    " + lines[j]
        break

with codecs.open("frontend/pages/user_workspace.py", "w", "utf-8") as f:
    f.writelines(lines)
print("Indentation fixed.")
