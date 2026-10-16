from pathlib import Path
import json,hashlib,zlib,struct,xml.etree.ElementTree as ET
root=Path('/workspace/sedeppl-ajustada'); out=Path('/workspace/projeto-guarda-popular')
rows=[]
for p in sorted(root.rglob('*')):
 if not p.is_file() or '.git' in p.parts: continue
 d=p.read_bytes(); r={'arquivo':str(p.relative_to(root)),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest(),'tipo':p.suffix}
 if d[:4]==b'RSC7':
  r['cabecalho']=list(struct.unpack('<4I',d[:16]))
  try: raw=zlib.decompress(d[16:],-15); r.update(deflate='OK',bytes_descomprimidos=len(raw))
  except zlib.error as e:r['erro_deflate']=str(e)
  r['interpretacao']='Contêiner descomprimido; malha, materiais, hierarquia e dependências ainda não decodificados.'
 elif p.suffix=='.xml':
  x=ET.fromstring(d); r['raiz']=x.tag; r['geometrias']=[]
  for g in x.findall('.//Geometries/Item'):
   v=[list(map(float,l.split())) for l in g.findtext('VertexBuffer/Data').splitlines() if l.strip()]; ix=list(map(int,g.findtext('IndexBuffer/Data').split()))
   assert len(ix)%3==0 and max(ix)<len(v)
   r['geometrias'].append({'vertices':len(v),'triangulos':len(ix)//3,'shader':g.find('ShaderIndex').get('value'),'min':[min(a[i] for a in v) for i in range(3)],'max':[max(a[i] for a in v) for i in range(3)]})
  r['texturas']=[e.text for e in x.findall('.//TextureDictionary/Item/FileName')]
 elif p.suffix=='.dds':
  assert d[:4]==b'DDS '; r['altura'],r['largura']=struct.unpack_from('<II',d,12); r['fourcc']=d[84:88].decode('ascii')
 rows.append(r)
(out/'inventario.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
print('Arquivos',len(rows),'RSC7',sum('deflate' in r for r in rows),'erros',sum('erro_deflate' in r for r in rows))
print(json.dumps([r for r in rows if r['tipo'] in ['.xml','.dds']],indent=2,ensure_ascii=False))
