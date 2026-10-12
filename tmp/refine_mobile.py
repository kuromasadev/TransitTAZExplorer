from pathlib import Path
p=Path('explorer/source/template.html');s=p.read_text(encoding='utf-8')
s=s.replace('.quiet{background:', '.quiet{white-space:nowrap;background:')
s=s.replace("const labels=['Region sector','Freeway corridor','Origin neighborhood','Nearest facility','Where you can go'];", "const labels=['Region sector','Freeway corridor','Origin neighborhood','Nearest facility','Where you can go'];\nconst shortLabels=['Sector','Corridor','Neighborhood','Facility','Destinations'];")
s=s.replace('<b>${esc(l)}</b>','<b>${esc(shortLabels[i])}</b>')
p.write_text(s,encoding='utf-8')
