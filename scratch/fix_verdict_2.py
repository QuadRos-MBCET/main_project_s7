import codecs

with codecs.open("frontend/views/user_workspace.py", "r", "utf-8") as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if line.strip() == 'st.markdown("---")' and 'ID vs Live Face' in lines[i+1]:
        start_idx = i
    if line.strip() == "else:" and "st.markdown" in lines[i+1] and "<style>" in lines[i+2]:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    print(f"Indenting from {start_idx} to {end_idx}")
    for i in range(start_idx, end_idx):
        if len(lines[i].strip()) > 0:
            lines[i] = "    " + lines[i]
else:
    print(f"Failed to find indices. start: {start_idx}, end: {end_idx}")

with codecs.open("frontend/views/user_workspace.py", "w", "utf-8") as f:
    f.writelines(lines)
