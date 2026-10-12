from pathlib import Path
import json,csv,xml.etree.ElementTree as ET,sys
sys.stdout.reconfigure(encoding='utf-8')
from openpyxl import load_workbook
from pypdf import PdfReader
root=Path(__file__).resolve().parents[1]
out=root/'project-review';out.mkdir(exist_ok=True)
inventory=[]
for p in sorted(root.rglob('*')):
 if not p.is_file() or any(x in p.parts for x in ['.git','project-review','tmp']):continue
 d={'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size}
 try:
  if p.suffix=='.pdf':
   d['pages']=[{'page':i+1,'text':page.extract_text()} for i,page in enumerate(PdfReader(p).pages)]
  elif p.suffix=='.xlsx':
   wb=load_workbook(p,read_only=True,data_only=False);d['sheets']=[]
   for s in wb:
    rows=list(s.values); nonempty=[(i+1,r) for i,r in enumerate(rows) if any(v is not None for v in r)]
    d['sheets'].append({'name':s.title,'rows':s.max_row,'columns':s.max_column,'nonempty_rows':len(nonempty),'preview':[{'row':i,'values':r} for i,r in nonempty[:10]],'formula_count':sum(isinstance(v,str) and v.startswith('=') for r in rows for v in r)})
   wb.close()
  elif p.suffix=='.csv':
   enc='utf-16' if p.read_bytes().startswith(b'\xff\xfe') else 'utf-8-sig'
   with p.open(encoding=enc,newline='') as f:rows=list(csv.reader(f,delimiter='\t' if enc=='utf-16' else ','))
   d.update(rows=len(rows)-1,headers=rows[0],preview=rows[1:4])
  elif p.suffix in ['.json','.geojson'] and 'RAW' in p.parts:
   j=json.loads(p.read_text(encoding='utf-8-sig'));fs=j.get('features',[])
   d.update(top_keys=list(j),feature_count=len(fs),fields=j.get('fields'),geometry_type=j.get('geometryType'),spatial_reference=j.get('spatialReference'),sample_properties=[f.get('attributes',f.get('properties')) for f in fs[:2]])
   if fs:
    props=[f.get('attributes',f.get('properties',{})) for f in fs];d['property_keys']=list(props[0]);d['null_counts']={k:sum(x.get(k) is None for x in props) for k in props[0]};d['unique_counts']={k:len(set(str(x.get(k)) for x in props)) for k in props[0]}
  elif p.suffix=='.twb':
   x=ET.parse(p).getroot();d['datasources']=[{'name':s.get('name'),'caption':s.get('caption'),'connections':[c.attrib for c in s.findall('.//connection')],'relations':[r.attrib for r in s.findall('.//relation')],'calculations':[{'name':c.get('caption',c.get('name')),'formula':c.find('calculation').get('formula')} for c in s.findall('.//column') if c.find('calculation') is not None]} for s in x.findall('./datasources/datasource')];d['worksheets']=[s.get('name') for s in x.findall('./worksheets/worksheet')];d['dashboards']=[s.get('name') for s in x.findall('./dashboards/dashboard')];d['actions']=[ET.tostring(a,encoding='unicode') for a in x.findall('./actions/action')]
  elif p.suffix=='.ipynb':
   j=json.loads(p.read_text());d['cells']=[{'type':c['cell_type'],'source':''.join(c['source']),'output_types':[o.get('output_type') for o in c.get('outputs',[])]} for c in j['cells']]
  else:
   # Do not reproduce connection settings or potential credentials.
   d['text']=p.read_text() if '.dbeaver' not in p.parts else 'Connection configuration inspected; details omitted.'
 except Exception as e:d['error']=str(e)
 inventory.append(d)
(out/'inventory.json').write_text(json.dumps(inventory,indent=2,default=str),encoding='utf-8')
lines=['# Project file inventory','','Reviewed October 12, 2026. All original non-Git files; generated review outputs excluded.','','| File | Bytes | Parsed contents |','| --- | ---: | --- |']
for d in inventory:
 if 'sheets' in d: detail='; '.join(f"{s['name']}: {s['rows']} rows x {s['columns']} columns" for s in d['sheets'])
 elif 'feature_count' in d:detail=f"{d['feature_count']} spatial features; {len(d.get('property_keys',[]))} properties"
 elif 'headers' in d:detail=f"{d['rows']} records; "+', '.join(d['headers'])
 elif 'pages' in d:detail=f"{len(d['pages'])} pages, extracted text and separately rendered visual review"
 elif 'cells' in d:detail=f"{len(d['cells'])} notebook cells, source inspected without execution"
 elif 'worksheets' in d:detail=f"{len(d['worksheets'])} worksheets; {len(d['dashboards'])} dashboards; saved connections and actions parsed"
 else:detail='Text/configuration inspected; connection details omitted where applicable'
 lines.append(f"| `{d['path']}` | {d['bytes']:,} | {detail} |")
lines+=['',f"Total: {len(inventory)} files. No parsing errors." if not any('error' in d for d in inventory) else 'Some files reported parsing errors; see inventory.json.']
(out/'FILE_INVENTORY.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
for d in inventory:
 print(d['path'],d.get('error',''), 'features='+str(d.get('feature_count','')), 'sheets='+str([(s['name'],s['rows'],s['columns']) for s in d.get('sheets',[])]))
for d in inventory:
 if 'pages' in d:
  for p in d['pages']:print('\nPAGE',p['page'],p['text'])
