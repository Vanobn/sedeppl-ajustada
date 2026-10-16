from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,io,struct,json,shutil
import xml.etree.ElementTree as E
P=Path(__file__).resolve().parents[1];T=P/'texturas';X=P/'xml/ga_texturas';X.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(327);imgs={}
def surface(col,n=512,amp=8):
 a=np.clip(np.array(col)[None,None,:]+rng.normal(0,amp,(n,n,1)),0,255).astype('uint8');return Image.fromarray(a).convert('RGBA')
def brick(col):
 im=surface(col);d=ImageDraw.Draw(im)
 for y in range(0,512,64):
  d.line((0,y,512,y),fill=tuple(int(v*.7) for v in col),width=3)
  off=64 if (y//64)%2 else 0
  for x in range(-128+off,512,128):d.line((x,y,x,y+64),fill=tuple(int(v*.7) for v in col),width=2)
 return im
imgs['tijolo_branco']=brick((191,181,159));imgs['tijolo_vermelho']=brick((133,26,22))
imgs['concreto']=surface((133,129,117),512,12)
d=ImageDraw.Draw(imgs['concreto'])
for x in [0,255,511]:d.line((x,0,x,512),fill=(105,103,96),width=1)
for y in [0,255,511]:d.line((0,y,512,y),fill=(105,103,96),width=1)
imgs['metal_vermelho']=surface((139,29,22),256,7);imgs['metal_preto']=surface((32,33,31),128,4);imgs['telha']=surface((139,132,118),256,6);imgs['piso_vermelho']=surface((125,27,22),256,8);imgs['porta']=surface((132,28,22),256,5);imgs['claraboia']=surface((190,219,229),128,2);imgs['luminaria']=Image.new('RGBA',(64,64),(250,241,212))
font='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
im=surface((144,29,24),1024,4).resize((1024,256));dr=ImageDraw.Draw(im)
def star(cx,cy,r):
 import math
 return [(cx+ (r if i%2==0 else r*.4)*math.sin(i*math.pi/5),cy-(r if i%2==0 else r*.4)*math.cos(i*math.pi/5)) for i in range(10)]
dr.polygon(star(76,128,46),fill=(221,213,191));dr.polygon(star(948,128,46),fill=(221,213,191))
f=ImageFont.truetype(font,89);dr.text((512,128),'GUARDA POPULAR',font=f,anchor='mm',fill=(226,216,192))
imgs['faixa_guarda_popular']=im
mural=T/'ga_murais_fonte.png'
if not mural.exists():raise SystemExit('Falta texturas/ga_murais_fonte.png (atlas de referência reconstruído).')
imgs['murais']=Image.open(mural).convert('RGBA').resize((1024,512),Image.Resampling.LANCZOS)
root=E.Element('TextureDictionary');stats=[]
for n,im in imgs.items():
 name='ga_'+n;im.save(T/(name+'.png'));cur=im;levels=[]
 while True:
  b=io.BytesIO();cur.save(b,format='DDS',pixel_format='DXT5');levels.append(b.getvalue())
  if cur.size==(1,1):break
  cur=cur.resize((max(1,cur.width//2),max(1,cur.height//2)),Image.Resampling.LANCZOS)
 h=bytearray(levels[0][:128]);struct.pack_into('<I',h,8,struct.unpack_from('<I',h,8)[0]|0x20000);struct.pack_into('<I',h,28,len(levels));struct.pack_into('<I',h,108,0x401008);data=h+b''.join(v[128:] for v in levels);(T/(name+'.dds')).write_bytes(data);shutil.copy2(T/(name+'.dds'),X/(name+'.dds'))
 e=E.SubElement(root,'Item');E.SubElement(e,'Name').text=name
 for tag,v in [('Unk32',0),('ExtraFlags',0),('Width',im.width),('Height',im.height),('MipLevels',len(levels))]:E.SubElement(e,tag,value=str(v))
 E.SubElement(e,'Usage').text='DIFFUSE';E.SubElement(e,'UsageFlags');E.SubElement(e,'Format').text='D3DFMT_DXT5';E.SubElement(e,'FileName').text=name+'.dds';stats.append({'nome':name,'resolucao':list(im.size),'mips':len(levels),'bytes_dds':len(data)})
E.indent(root);E.ElementTree(root).write(P/'xml/ga_texturas.ytd.xml',encoding='utf-8',xml_declaration=True);(P/'relatorios/texturas.json').write_text(json.dumps(stats,indent=2));print('TEXTURAS',len(stats),sum(t['bytes_dds'] for t in stats))
