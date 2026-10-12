"""Refresh official METRO route evidence for the static explorer (build time only)."""
from pathlib import Path
import re,json,urllib.request,concurrent.futures,argparse,datetime
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--checked',required=True,help='Actual verification date in YYYY-MM-DD format')
args=parser.parse_args();datetime.date.fromisoformat(args.checked)
BASE='https://www.ridemetro.org'
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.parts.append(d.strip())
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
 return urllib.request.urlopen(req,timeout=30).read().decode('utf-8')
main=get(BASE+'/riding-metro/transit-services/park-and-ride-bus/')
numbers=[202,204,209,212,216,217,219,221,222,228,229,236,237,244,247,249,255,256,257,259,265,269,270,292,297,298]
paths=[f'https://webapps.ridemetro.org/schedules/schedule.aspx?q={n}' for n in numbers]
def read(path):
 s=get(path);p=Text();p.feed(s);text='\n'.join(p.parts)
 return {'url':path,'route':int(path.split('q=')[1]),'text':text,'options':re.findall(r'<option[^>]*>(.*?)</option>',s,re.S)}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for d in pool.map(read,paths):results.append(d);print(d['route'],len(d['text']))
dest=ROOT/'explorer/source';dest.mkdir(parents=True,exist_ok=True)
(dest/'official-routes.json').write_text(json.dumps({'checked':args.checked,'source':BASE+'/riding-metro/transit-services/park-and-ride-bus/','routes':results},indent=2),encoding='utf-8')
print('Saved',len(results),'routes')
