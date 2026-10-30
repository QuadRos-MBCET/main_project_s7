with open('SAFE_VISION_Final_Project_Report.tex', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\u2014', '---')
text = text.replace('\u2013', '--')
text = text.replace('\u2018', "'")
text = text.replace('\u2019', "'")
text = text.replace('\u201c', '``')
text = text.replace('\u201d', "''")

with open('SAFE_VISION_Final_Project_Report.tex', 'w', encoding='utf-8') as f:
    f.write(text)

non_ascii = [c for c in text if ord(c) > 127]
print(f'Remaining non-ASCII characters: {len(non_ascii)}')
