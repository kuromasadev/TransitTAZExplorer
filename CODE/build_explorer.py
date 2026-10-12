"""Produce one offline HTML file from local geography and checked service evidence."""
from pathlib import Path
import json,math,re,html,collections
from openpyxl import load_workbook
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'explorer';SRC=OUT/'source'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def hav(a,b):
 lat1,lat2=math.radians(a[1]),math.radians(b[1]);dl=math.radians(b[0]-a[0]);dt=lat2-lat1
 return 3958.7613*2*math.asin(min(1,math.sqrt(math.sin(dt/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dl/2)**2)))
def center(ring):
 a=sx=sy=0
 for p,q in zip(ring,ring[1:]):
  cross=p[0]*q[1]-q[0]*p[1];a+=cross;sx+=(p[0]+q[0])*cross;sy+=(p[1]+q[1])*cross
 if abs(a)<1e-12:return [sum(p[0] for p in ring)/len(ring),sum(p[1] for p in ring)/len(ring)],0
 return [sx/(3*a),sy/(3*a)],abs(a/2)
def simple(pts,tol=.00022):
 if len(pts)<3:return pts
 a,b=pts[0],pts[-1];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
 def dist(p):
  t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
  return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
 idx=max(range(1,len(pts)-1),key=lambda i:dist(pts[i]))
 return simple(pts[:idx+1],tol)[:-1]+simple(pts[idx:],tol) if dist(pts[idx])>tol else [a,b]
def xy(p):return [round((p[0]+96.05)*710,2),round((30.35-p[1])*815,2)]
def path(rings):
 return ''.join('M'+'L'.join(','.join(map(str,xy(p))) for p in simple(ring))+'Z' for ring in rings)
corridors=read(SRC/'corridors.json');official=read(SRC/'official-routes.json')
assert len(official['routes'])==26,'Run refresh_routes.py before building'
routecorr={n:c['id'] for c in corridors for n in c['routes']}
route_names={202:'Kuykendahl',204:'Spring',209:'Spring / Kuykendahl',212:'Seton Lake',216:'West Little York / Northwest Station',217:'Cypress',219:'Cypress / Northwest Station / West Little York',221:'Kingsland',222:'Grand Parkway',228:'Addicks',229:'Grand Parkway / Kingsland / Addicks',236:'Maxey',237:'Baytown',244:'Monroe / El Dorado',247:'Fuqua / Bay Area',249:'Bay Area / El Dorado / Fuqua / Monroe',255:'Kingwood',256:'Eastex',257:'Townsen',259:'Kingwood / Townsen / Eastex',265:'West Bellfort',269:'West Bellfort',270:'Missouri City',292:'Southwest Freeway / TMC',297:'Gulf Freeway / TMC',298:'Katy Freeway / TMC'}
aliases={12:['ADDICKS'],3:['TOWNSEN'],9:['MISSOURI CITY PARK & RIDE'],10:['WEST BELLFORT'],11:['WESTWOOD'],13:['KINGSLAND'],18:['WEST LITTLE YORK'],20:['MAXEY ROAD'],22:['FUQUA'],23:['MONROE'],24:['BAY AREA'],26:['KUYKENDAHL'],27:['SPRING'],28:['EASTEX'],29:['KINGWOOD'],17:['NORTHWEST STATION'],1:['CYPRESS'],2:['BAYTOWN'],4:['GRAND PARKWAY'],33:['EL DORADO PR'],93:['SOUTH POINT'],94:['SETON LAKE']}
routes=[]
for d in official['routes']:
 stops=[html.unescape(re.sub('<[^>]+>','',s)).strip() for s in d['options'] if re.search(r' - \d+$',s)]
 routes.append({'id':d['route'],'name':route_names[d['route']],'corridor':routecorr[d['route']],'destination':'Texas Medical Center' if d['route'] in [270,292,297,298] else 'Downtown Houston','url':d['url'],'stops':stops,'facilities':[k for k,v in aliases.items() if any(s.rsplit(' - ',1)[0].upper() in v for s in stops)]})
facilities=[]
display={10:'West Bellfort',18:'West Little York',20:'Maxey Road',94:'Seton Lake'}
for f in read(ROOT/'RAW/pnr_esrigj/METRO_PnR_pt.geojson')['features']:
 p=f['properties'];k=p['PRKNRD_ID'];rr=[r['id'] for r in routes if k in r['facilities']]
 if not rr:continue
 facilities.append({'id':k,'name':display.get(k,p['NAME1']),'address':p['ADDRESS'].title(),'point':f['geometry']['coordinates'],'xy':xy(f['geometry']['coordinates']),'corridor':next(c['id'] for c in corridors if k in c['facilities']),'routes':rr})
wb=load_workbook(ROOT/'RAW/pnr_esrigc/TAZ DATA.xlsx',read_only=True,data_only=True)
sectors={str(row[2]):str(int(float(row[3]))) for row in list(wb['SECT'].values)[1:]}
taz=[]
for f in read(ROOT/'RAW/pnr_esrigj/METRO_Pln_TAZ48d00.json')['features']:
 p=f['properties'];k=str(int(p['TAZ']));g=f['geometry'];polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
 centers=[center(poly[0]) for poly in polys];area=sum(a for _,a in centers);point=[sum(pt[i]*a for pt,a in centers)/area for i in [0,1]]
 nearest=min(facilities,key=lambda f:hav(point,f['point']))
 coords=[xy(p) for poly in polys for ring in poly for p in ring]
 bounds=[min(p[0] for p in coords),min(p[1] for p in coords),max(p[0] for p in coords),max(p[1] for p in coords)]
 taz.append({'id':k,'name':p['ODAREA'].title(),'sector':sectors[k],'point':point,'area':area,'xy':xy(point),'bounds':bounds,'path':path([ring for poly in polys for ring in poly]),'corridor':nearest['corridor']})
groups=collections.defaultdict(list)
for t in taz:groups[t['sector']].append(t)
sector_data=[]
for k,ts in sorted(groups.items(),key=lambda kv:int(kv[0])):
 cnt=collections.Counter(t['name'] for t in ts);examples=', '.join(n for n,_ in cnt.most_common(3));point=[sum(t['point'][i]*t['area'] for t in ts)/sum(t['area'] for t in ts) for i in [0,1]]
 sector_data.append({'id':k,'name':f'Sector {k}','examples':examples,'xy':xy(point),'count':len(ts)})
data={'checked':official['checked'],'corridors':corridors,'sectors':sector_data,'taz':taz,'facilities':facilities,'routes':routes,'method':'straight-line','metroSource':official['source']}
payload=json.dumps(data,separators=(',',':'),ensure_ascii=False).replace('<','\\u003c')
template=(SRC/'template.html').read_text(encoding='utf-8');assert '__EXPLORER_DATA__' in template
(OUT/'index.html').write_text(template.replace('__EXPLORER_DATA__',payload),encoding='utf-8')
(SRC/'data.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(f"Built {len(taz)} TAZs, {len(sector_data)} sectors, {len(facilities)} facilities, {len(routes)} routes; {(OUT/'index.html').stat().st_size:,} bytes")
