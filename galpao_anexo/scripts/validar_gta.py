from pathlib import Path
import xml.etree.ElementTree as E,json,struct,zlib,hashlib,math
import numpy as np
P=Path(__file__).resolve().parents[1];R=P/'relatorios/roundtrip';report={}
files=sorted((P/'stream').glob('*'))+sorted((P/'exemplos').glob('*.ymap'))
for p in files:
 d=p.read_bytes();assert d[:4]==b'RSC7' and len(d)>16;raw=zlib.decompress(d[16:],-15);assert raw;report[p.name]={'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest(),'descomprimido':len(raw),'versao':struct.unpack_from('<I',d,4)[0]}
assert len(files)==7
x=E.parse(R/'ga_arquetipos.ytyp.xml').getroot();archetypes=x.findall('./archetypes/Item');a=next(a for a in archetypes if a.get('type')=='CMloArchetypeDef');assert a.findtext('assetName')=='ga_mlo' and a.findtext('assetType')=='ASSET_TYPE_ASSETLESS';rooms=a.findall('rooms/Item');ports=a.findall('portals/Item');entities=a.findall('entities/Item');assert len(rooms)==2 and len(ports)==1 and len(entities)==3
pairs=[];attached=[]
for i,r in enumerate(rooms):
 lo=np.array([float(r.find('bbMin').get(k)) for k in 'xyz']);hi=np.array([float(r.find('bbMax').get(k)) for k in 'xyz']);assert np.all(hi>lo)
 objects=list(map(int,(r.findtext('attachedObjects') or '').split()));attached.extend(objects);assert objects==([[0],[1,2]][i])
 pairs.append((r.findtext('name'),lo,hi))
assert sorted(attached)==list(range(3))
links=[]
for p in ports:
 fr=int(p.find('roomFrom').get('value'));to=int(p.find('roomTo').get('value'));assert 0<=fr<2 and 0<=to<2 and fr!=to;links.append((fr,to))
 corners=[np.array([float(v.strip()) for v in (e.text or '').split(',')[:3]]) for e in p.findall('corners/Item')];assert len(corners)==4
 n=np.cross(corners[1]-corners[0],corners[2]-corners[0]);assert np.linalg.norm(n)>1e-6 and abs(np.dot(n,corners[3]-corners[0]))<1e-5
 direction=np.array((0,1,0)) if fr==0 else (pairs[to][1]+pairs[to][2])/2-sum(corners)/4;assert np.dot(n,direction)>0
for i,r in enumerate(rooms):assert int(r.find('portalCount').get('value'))==sum(i in l for l in links)
seen={0}
while True:
 next_seen=seen|{b for a,b in links if a in seen}|{a for a,b in links if b in seen}
 if next_seen==seen:break
 seen=next_seen
assert seen==set(range(2))
textures=E.parse(R/'ga_texturas.ytd.xml').getroot();texnames={t.findtext('Name') for t in textures};assert len(texnames)==12
for t in textures:
 w=int(t.find('Width').get('value'));h=int(t.find('Height').get('value'));m=int(t.find('MipLevels').get('value'));assert w&(w-1)==0 and h&(h-1)==0 and m==int(math.log2(max(w,h)))+1;assert t.findtext('Format')=='D3DFMT_DXT5'
assert {f.name for f in R.glob('*.ydr.xml')}=={'ga_exterior.ydr.xml','ga_salao.ydr.xml','ga_mezanino.ydr.xml'}
tris={};light_count=0
for f in sorted(R.glob('*.ydr.xml')):
 d=E.parse(f).getroot();idx=0
 for g in d.findall('./DrawableModelsHigh/Item/Geometries/Item'):
  v=[l for l in g.findtext('VertexBuffer/Data').splitlines() if l.strip()];ix=list(map(int,g.findtext('IndexBuffer/Data').split()));assert v and len(ix)%3==0 and min(ix)>=0 and max(ix)<len(v);idx+=len(ix)//3
  layout=[e.tag for e in g.findall('VertexBuffer/Layout/*')];assert 'Position' in layout and 'Normal' in layout and 'TexCoord0' in layout
 refs={t.findtext('Name') for t in d.findall("./ShaderGroup/Shaders/Item/Parameters/Item[@type='Texture']")};assert refs<=texnames,(f.name,refs-texnames)
 assert idx>0;tris[f.name]=idx
 for level in ['DrawableModelsMedium','DrawableModelsLow']:
  models=d.findall('./'+level+'/Item/Geometries/Item');assert models,(f.name,level)
  count=sum(len(g.findtext('IndexBuffer/Data').split())//3 for g in models);assert 0<count<idx,(f.name,level,count,idx)
 for light in d.findall('Lights/Item'):
  assert int(light.find('TimeFlags').get('value'))==16777215;assert float(light.find('Falloff').get('value'))>0;assert int(light.find('Flags').get('value'))&64;light_count+=1
assert light_count==9
col=E.parse(R/'ga_mlo.ybn.xml').getroot();assert col.find('Bounds').get('type')=='Composite';bvh=col.find(".//Children/Item[@type='GeometryBVH']");assert bvh is not None;assert {int(m.find('RoomID').get('value')) for m in bvh.findall('Materials/Item')}==set(range(2));assert len(bvh.findall('Polygons/Triangle'))==json.loads((P/'relatorios/geometria.json').read_text())['triangulos_colisao']
flags1={v.strip() for v in bvh.findtext('CompositeFlags1').split(',')};flags2={v.strip() for v in bvh.findtext('CompositeFlags2').split(',')}
assert {'MAP_DYNAMIC','MAP_COVER','MAP_VEHICLE'}<=flags1
assert {'MAP_WEAPON','MAP_DYNAMIC','MAP_VEHICLE','PED','TEST_VEHICLE_WHEEL','TEST_CAMERA'}<=flags2
ymap=E.parse(R/'ga_implantacao_origem.ymap.xml').getroot();inst=ymap.find("entities/Item[@type='CMloInstanceDef']");assert inst is not None and inst.findtext('archetypeName')=='ga_mlo'
report['MLO']={'salas':[p[0] for p in pairs],'portais':links,'entidades':len(entities),'conectividade':'todas as salas acessíveis a partir do exterior','texturas':len(texnames),'luzes_com_horario_e_sombra':light_count,'triangulos':tris,'triangulos_colisao':len(bvh.findall('Polygons/Triangle')),'compilados':len(files),'instancia_exemplo':'CMloInstanceDef','teste_no_jogo':False}
(P/'relatorios/validacao_gta.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print('PASS: 7 binários RSC7, MLO conectado, 12 DDS/mips, 9 luzes, referências e colisão BVH.')
