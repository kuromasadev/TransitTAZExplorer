from pathlib import Path
import zipfile,shutil
r=Path(__file__).resolve().parents[1];dest=r/'output/commuter-explorer';dest.mkdir(parents=True,exist_ok=True)
for name in ['index.html','README.md']:shutil.copy2(r/'explorer'/name,dest/name)
with zipfile.ZipFile(r/'output/commuter-explorer.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in dest.iterdir():z.write(p,'commuter-explorer/'+p.name)
qa=r/'tmp/portable-qa';qa.mkdir(parents=True,exist_ok=True)
copy=(dest/'index.html').read_text(encoding='utf-8')
policy="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; font-src data: blob:; connect-src 'none'; worker-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"
(qa/'index.html').write_text(copy.replace('<meta charset="utf-8">',f'<meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="{policy}">'),encoding='utf-8')
(qa/'sandbox.html').write_text('<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0"><iframe title="Portable explorer in restrictive sandbox" sandbox="allow-scripts" src="index.html" style="border:0;width:100%;height:100vh"></iframe></body></html>',encoding='utf-8')
print('Packaged portable folder and ZIP; copied HTML into isolated restrictive-sandbox QA folder.')
