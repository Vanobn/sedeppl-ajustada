"""Gera XML de implantação; nenhum local de jogo é escolhido sem coordenadas explícitas."""
from pathlib import Path
import argparse,xml.etree.ElementTree as E,math,itertools
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--x',type=float,required=True);a.add_argument('--y',type=float,required=True);a.add_argument('--z',type=float,required=True);a.add_argument('--rotacao-z',type=float,default=0,help='Rotação CodeWalker em graus no eixo Z');a.add_argument('--saida',type=Path,default=P/'xml/ap_posicionado.ymap.xml');a=a.parse_args()
tree=E.parse(P/'xml/ap_implantacao_origem.ymap.xml');root=tree.getroot();name=a.saida.name.removesuffix('.ymap.xml');root.find('name').text=name;root.find('block/name').text=name;inst=root.find("entities/Item[@type='CMloInstanceDef']")
for k,v in zip('xyz',(a.x,a.y,a.z)):inst.find('position').set(k,str(v))
angle=math.radians(a.rotacao_z);q=inst.find('rotation');q.set('z',str(math.sin(angle/2)));q.set('w',str(math.cos(angle/2)))
lo=[float(root.find('entitiesExtentsMin').get(k)) for k in 'xyz'];hi=[float(root.find('entitiesExtentsMax').get(k)) for k in 'xyz'];co=math.cos(angle);si=math.sin(angle);pts=[(a.x+co*x-si*y,a.y+si*x+co*y,a.z+z) for x,y,z in itertools.product(*zip(lo,hi))]
newlo=[min(p[i] for p in pts) for i in range(3)];newhi=[max(p[i] for p in pts) for i in range(3)]
for tag,values in [('entitiesExtentsMin',newlo),('entitiesExtentsMax',newhi),('streamingExtentsMin',[x-200 for x in newlo]),('streamingExtentsMax',[x+200 for x in newhi])]:
 for k,v in zip('xyz',values):root.find(tag).set(k,str(v))
a.saida.parent.mkdir(parents=True,exist_ok=True);E.indent(tree);tree.write(a.saida,encoding='utf-8',xml_declaration=True);print(a.saida)
