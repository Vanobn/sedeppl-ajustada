from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,io,struct,json,shutil,math
import xml.etree.ElementTree as E
P=Path(__file__).resolve().parents[1];T=P/'texturas';X=P/'xml/ap_texturas';X.mkdir(parents=True,exist_ok=True);T.mkdir(exist_ok=True)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def f(n):return ImageFont.truetype(font,n)
rng=np.random.default_rng(420)
imgs={}
for name,col,noise,size in [('vermelho',(153,55,39),9,256),('branco',(172,171,155),6,256),('metal',(74,68,50),10,256),('borracha',(28,29,27),4,128),('cromado',(168,176,181),3,128),('concreto',(118,112,93),9,512),('telha',(139,143,132),8,256),('preto',(38,40,36),4,128),('vidro',(69,86,82),3,128)]:
 a=np.clip(np.array(col)[None,None,:]+rng.normal(0,noise,(size,size,1)),0,255).astype('uint8');imgs[name]=Image.fromarray(a).convert('RGBA')
# All lettering is newly drawn; neither sign contains a phone number.
im=Image.new('RGBA',(1024,256),(191,55,57));dr=ImageDraw.Draw(im)
for y in range(256):dr.line((0,y,1024,y),fill=(int(193-20*y/256),int(63-15*y/256),int(66-17*y/256)))
for j,t in enumerate(['BALANCEAMENTO','GEOMETRIA','SUSPENSÃO','MECÂNICA','FREIOS']):dr.text((22,14+j*39),t,font=f(28),fill=(244,238,219))
dr.ellipse((680,6,839,245),outline=(40,34,30),width=12)
dr.ellipse((706,17,822,235),outline=(40,34,30),width=6)
for j in range(10):
 y=20+j*23;dr.line((815,y,841,y+12),fill=(40,34,30),width=6)
dr.line((485,106,998,86),fill='white',width=5);dr.line((485,193,998,179),fill='white',width=5)
dr.text((489,104),'ALEMÃO',font=f(91),stroke_width=1,fill=(248,245,225));dr.text((668,195),'PNEUS',font=f(38),fill=(248,245,225))
imgs['placa_sem_telefone']=im
im=Image.new('RGBA',(256,256),(22,104,54));dr=ImageDraw.Draw(im);dr.polygon([(128,23),(238,128),(128,233),(18,128)],fill=(232,196,35));dr.ellipse((79,79,177,177),fill=(22,51,109));dr.arc((66,112,190,170),190,340,fill='white',width=6);imgs['bandeira_brasil']=im
im=Image.new('RGBA',(256,256),(193,159,38));dr=ImageDraw.Draw(im);dr.polygon([(0,0),(256,0),(0,256)],fill=(123,25,28));dr.ellipse((79,78,177,178),fill=(211,204,169),outline=(55,58,41),width=5);dr.ellipse((103,100,152,154),fill=(44,94,55));imgs['bandeira_rs_estudo']=im
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
