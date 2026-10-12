from pathlib import Path
p=Path('explorer/source/template.html')
s=p.read_text(encoding='utf-8')
s=s.replace('const pts=focusTs.map(t=>t.xy);','const pts=focusTs.flatMap(t=>[[t.bounds[0],t.bounds[1]],[t.bounds[2],t.bounds[3]]]);')
s=s.replace('for(const sec of DATA.sectors){s+=',"for(const [index,sec] of DATA.sectors.entries()){const shades=['#bfd6ca','#d1ddd2','#b7cdc8','#c5d5e0','#d7ddc0','#c8d7d5'];s+=")
s=s.replace("state.sector===sec.id?'#acd8cd':'#d8e6e0'","state.sector===sec.id?'#acd8cd':shades[index%shades.length]")
p.write_text(s,encoding='utf-8')
