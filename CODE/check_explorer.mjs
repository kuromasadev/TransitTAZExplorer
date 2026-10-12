import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const html=fs.readFileSync(new URL('../explorer/index.html',import.meta.url),'utf8');
const payload=html.match(/<script id="explorer-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const data=JSON.parse(payload);
assert.equal(data.taz.length,1239);assert.equal(new Set(data.taz.map(t=>t.id)).size,1239);
assert.equal(new Set(data.taz.map(t=>t.name)).size,113);
assert.equal(data.routes.length,26);assert.equal(data.facilities.length,22);
assert.ok(Buffer.byteLength(html)<1024*1024,'Keep portable HTML under 1 MB');
assert.ok(!/<(?:script[^>]+src|link[^>]+href|img[^>]+src=["']https)/i.test(html),'No external assets');
assert.ok(!/\b(?:fetch|XMLHttpRequest|localStorage|sessionStorage|indexedDB)\s*\(/.test(html),'No runtime network or storage dependency');
const runtime=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
const nodes=new Map();const node=id=>{if(!nodes.has(id))nodes.set(id,{textContent:id==='explorer-data'?payload:'',innerHTML:'',addEventListener(){},focus(){},querySelector(){return {setAttribute(){}};}});return nodes.get(id);};
const context=vm.createContext({document:{getElementById:node,addEventListener(){}},console});
vm.runInContext(runtime.replace(/render\(\);\s*$/,''),context);
const evalJS=code=>vm.runInContext(code,context);
assert.ok(Math.abs(evalJS('miles([-95.3698,29.7604],[-95.3698,30.7604])')-69.0934)<.01,'Distance uses geographic miles');
const seen=new Set();let paths=0;
for(const sec of data.sectors){
 evalJS(`Object.assign(state,{sector:${JSON.stringify(sec.id)},corridor:null,neighborhood:null,taz:null,facility:null,step:1})`);
 const corridors=evalJS('availableCorridors().map(c=>c.id)');assert.ok(corridors.length);
 for(const cor of corridors){
  evalJS(`state.corridor=${JSON.stringify(cor)}`);
  const neighborhoods=evalJS('neighborhoods()');assert.ok(neighborhoods.length);
  for(const name of neighborhoods){
   evalJS(`state.neighborhood=${JSON.stringify(name)};state.taz=null`);
   const origin=evalJS('originPoint()');assert.ok(origin.every(Number.isFinite));
   const ranks=evalJS('rankings()');assert.equal(ranks.length,data.facilities.length);
   for(let i=1;i<ranks.length;i++)assert.ok(ranks[i].distance>=ranks[i-1].distance);
   const ts=evalJS('origins().map(t=>t.id)');ts.forEach(id=>seen.add(id));assert.ok(ts.length);paths++;
   for(const id of ts){evalJS(`state.taz=${JSON.stringify(id)}`);assert.equal(evalJS('origins().length'),1);assert.ok(evalJS('rankings()[0].distance')>=0);}
  }
  evalJS('state.neighborhood=null;state.taz=null');
 }
}
assert.equal(seen.size,1239,'Every original TAZ is reachable through the sector/corridor/neighborhood flow');
for(const f of data.facilities){assert.ok(f.routes.length);for(const id of f.routes){const route=data.routes.find(r=>r.id===id);assert.ok(route.facilities.includes(f.id));assert.ok(route.stops.length);assert.ok(route.url.startsWith('https://webapps.ridemetro.org/schedules/schedule.aspx?q='));}}
const f=id=>data.facilities.find(f=>f.id===id);
assert.deepEqual(f(4).routes,[222,229]);assert.deepEqual(f(12).routes,[228,229,298]);
assert.deepEqual(f(11).routes,[292],'Do not retain obsolete Westwood downtown service');
assert.deepEqual(f(29).routes,[255,259],'Include currently listed Kingwood routes');
evalJS("Object.assign(state,{sector:'20',corridor:'west',neighborhood:'Katy',taz:'1',facility:4});clearAfter(0)");
assert.equal(evalJS('state.corridor'),null);assert.equal(evalJS('state.neighborhood'),null);assert.equal(evalJS('state.taz'),null);assert.equal(evalJS('state.facility'),null);
assert.equal(evalJS('canGo(4)'),false,'Downstream steps cannot retain stale selections');
const report={result:'passed',tazReachable:seen.size,originPaths:paths,sectors:data.sectors.length,corridors:data.corridors.length,facilities:data.facilities.length,routes:data.routes.length,htmlBytes:Buffer.byteLength(html),checks:['offline assets','geographic distance','all origin paths','global facility ranking','route/facility consistency','current service regressions','selection reset']};
fs.writeFileSync(new URL('../explorer/source/verification.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
