from pathlib import Path
from PIL import Image
import io,struct,json,shutil
import xml.etree.ElementTree as E
P=Path(__file__).resolve().parents[1];T=P/'texturas';X=P/'xml/ap_texturas';X.mkdir(parents=True,exist_ok=True)
imgs={p.stem.removeprefix('ap_'):Image.open(p).convert('RGBA') for p in sorted(T.glob('ap_*.png'))}
assert len(imgs)==12
for name,im in imgs.items():
 w,h=im.size
 assert w>0 and h>0 and not w&(w-1) and not h&(h-1),name
# DDS DXT5, complete mip chains; small repeat textures and one 1024x256 sign.
root=E.Element('TextureDictionary');stats=[]
for name,im in imgs.items():
 name='ap_'+name;im.save(T/(name+'.png'));levels=[];cur=im
 while True:
  b=io.BytesIO();cur.save(b,format='DDS',pixel_format='DXT5');levels.append(b.getvalue())
  if cur.size==(1,1):break
  cur=cur.resize((max(1,cur.width//2),max(1,cur.height//2)),Image.Resampling.LANCZOS)
 header=bytearray(levels[0][:128]);struct.pack_into('<I',header,8,struct.unpack_from('<I',header,8)[0]|0x20000);struct.pack_into('<I',header,28,len(levels));struct.pack_into('<I',header,108,0x401008)
 data=header+b''.join(v[128:] for v in levels);(T/(name+'.dds')).write_bytes(data);shutil.copy2(T/(name+'.dds'),X/(name+'.dds'))
 item=E.SubElement(root,'Item');E.SubElement(item,'Name').text=name
 for tag,v in [('Unk32',0),('ExtraFlags',0),('Width',im.width),('Height',im.height),('MipLevels',len(levels))]:E.SubElement(item,tag,value=str(v))
 E.SubElement(item,'Usage').text='DIFFUSE';E.SubElement(item,'UsageFlags');E.SubElement(item,'Format').text='D3DFMT_DXT5';E.SubElement(item,'FileName').text=name+'.dds';stats.append({'nome':name,'resolucao':list(im.size),'mips':len(levels),'dds_bytes':len(data)})
E.indent(root);E.ElementTree(root).write(P/'xml/ap_texturas.ytd.xml',encoding='utf-8',xml_declaration=True);(P/'relatorios/texturas.json').write_text(json.dumps(stats,indent=2));print('TEXTURAS',len(stats),sum(x['dds_bytes'] for x in stats),'bytes DDS')
