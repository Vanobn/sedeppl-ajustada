from pathlib import Path
import xml.etree.ElementTree as E,json,collections
root=Path('/workspace/projeto-guarda-popular/convertidos');out=[];alltex=set(p.stem.lower() for p in root.glob('*.dds'))
for p in sorted(root.glob('*.xml')):
 x=E.parse(p).getroot();r={'arquivo':p.name,'raiz':x.tag}
 if x.tag=='Drawable':
  vs=[];ts=0;gs=0;shaders=[]
  for g in x.findall('./DrawableModelsHigh/Item/Geometries/Item'):
   pos=[a.tag for a in g.find('VertexBuffer/Layout')];offset=sum({'Position':3,'Normal':3,'Colour0':4,'Colour1':4,'TexCoord0':2,'TexCoord1':2,'TexCoord2':2,'Tangent':4,'BlendWeights':4,'BlendIndices':4}.get(t,0) for t in pos[:pos.index('Position')])
   rows=[list(map(float,l.split())) for l in g.findtext('VertexBuffer/Data').splitlines() if l.strip()];vs.extend([v[offset:offset+3] for v in rows]);ts+=len(g.findtext('IndexBuffer/Data').split())//3;gs+=1
  if vs:r['min']=[min(v[i] for v in vs) for i in range(3)];r['max']=[max(v[i] for v in vs) for i in range(3)];r['dimensoes']=[r['max'][i]-r['min'][i] for i in range(3)]
  r.update(vertices=len(vs),triangulos=ts,geometrias=gs)
  for sh in x.findall('./ShaderGroup/Shaders/Item'):
   textures=[a.findtext('Name') for a in sh.findall('./Parameters/Item') if a.get('type')=='Texture'];shaders.append({'shader':sh.findtext('FileName'),'texturas':textures})
  r['materiais']=shaders;r['texturas_nao_encontradas']=sorted({t for sh in shaders for t in sh['texturas'] if t and t.lower() not in alltex})
 out.append(r)
Path('/workspace/projeto-guarda-popular/analise_modelos.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
for r in out:
 if r['raiz']=='Drawable':print(r['arquivo'],[round(v,2) for v in r.get('dimensoes',[])],r['triangulos'],'tris','missing',r['texturas_nao_encontradas'])
