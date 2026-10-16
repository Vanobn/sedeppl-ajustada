from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,struct,json,shutil,xml.etree.ElementTree as E
P=Path(__file__).resolve().parents[1];T=P/'texturas';T.mkdir(exist_ok=True);X=P/'xml/vano_bc_texturas';X.mkdir(exist_ok=True)
rng=np.random.default_rng(1909)
def noise(base,amp=3,size=512):
 a=np.clip(np.array(base)[None,None,:]+rng.normal(0,amp,(size,size,1)),0,255).astype('uint8');return Image.fromarray(a,'RGB').convert('RGBA')
def dds_mips(im,path):
 im=im.convert('RGBA');levels=[];w,h=im.size
 while True:
  import io
  b=io.BytesIO();im.save(b,format='DDS',pixel_format='DXT5');levels.append(b.getvalue())
  if im.size==(1,1):break
  im=im.resize((max(1,im.width//2),max(1,im.height//2)),Image.Resampling.LANCZOS)
 header=bytearray(levels[0][:128]);flags=struct.unpack_from('<I',header,8)[0]|0x20000;struct.pack_into('<I',header,8,flags);struct.pack_into('<I',header,28,len(levels));struct.pack_into('<I',header,108,0x401008)
 path.write_bytes(header+b''.join(b[128:] for b in levels));return len(levels)
imgs={}
imgs['vano_bc_reboco_vermelho']=noise((167,19,20),5)
imgs['vano_bc_pintura_branca']=noise((223,218,204),2)
imgs['vano_bc_chapa_vermelha']=noise((181,16,20),3)
imgs['vano_bc_metal_oxidado']=noise((96,69,42),8,256)
imgs['vano_bc_metal_grafite']=noise((39,40,37),3,256)
imgs['vano_bc_telhas']=noise((118,121,114),4)
imgs['vano_bc_concreto']=noise((151,146,135),4)
floor=noise((132,104,83),3);draw=ImageDraw.Draw(floor)
for i in range(0,512,128):draw.line([(i,0),(i,511)],fill=(65,56,48),width=3);draw.line([(0,i),(511,i)],fill=(65,56,48),width=3)
imgs['vano_bc_piso_ceramico']=floor
wall=noise((208,197,172),2);draw=ImageDraw.Draw(wall)
for i in range(0,512,128):draw.line([(i,0),(i,511)],fill=(157,151,139),width=2);draw.line([(0,i),(511,i)],fill=(157,151,139),width=2)
imgs['vano_bc_azulejo_creme']=wall
bath=noise((226,227,219),2);draw=ImageDraw.Draw(bath)
for i in range(0,512,128):draw.line([(i,0),(i,511)],fill=(157,163,157),width=2);draw.line([(0,i),(511,i)],fill=(157,163,157),width=2)
imgs['vano_bc_azulejo_wc']=bath
source=Path('/workspace/generated_images/exec-0d7a2976-0f59-459b-af76-b29878d0a66a.png')
if source.exists() and not (T/'vano_bc_placa_reconstrucao_original.png').exists():shutil.copy2(source,T/'vano_bc_placa_reconstrucao_original.png')
source=T/'vano_bc_placa_reconstrucao_original.png'
imgs['vano_bc_placa']=Image.open(source).convert('RGBA').resize((2048,512),Image.Resampling.LANCZOS)
root=E.Element('TextureDictionary');stats=[]
for name,im in imgs.items():
 im.save(T/(name+'.png'));mips=dds_mips(im,T/(name+'.dds'));shutil.copy2(T/(name+'.dds'),X/(name+'.dds'))
 e=E.SubElement(root,'Item');E.SubElement(e,'Name').text=name
 for tag,value in [('Unk32',0),('ExtraFlags',0),('Width',im.width),('Height',im.height),('MipLevels',mips)]:E.SubElement(e,tag,value=str(value))
 E.SubElement(e,'Usage').text='DIFFUSE';E.SubElement(e,'UsageFlags').text='';E.SubElement(e,'Format').text='D3DFMT_DXT5';E.SubElement(e,'FileName').text=name+'.dds'
 stats.append({'nome':name,'dimensoes':im.size,'mipmaps':mips,'dds_bytes':(T/(name+'.dds')).stat().st_size})
E.indent(root);E.ElementTree(root).write(P/'xml/vano_bc_texturas.ytd.xml',encoding='utf-8',xml_declaration=True)
(P/'relatorios/texturas.json').write_text(json.dumps(stats,indent=2));print('Texturas DDS DXT5 com mips:',len(stats))
