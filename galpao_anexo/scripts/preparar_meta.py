from pathlib import Path
import xml.etree.ElementTree as E,json,math
P=Path(__file__).resolve().parents[1];X=P/'xml';r=json.loads((P/'relatorios/geometria.json').read_text());tree=E.parse(X/'ga_arquetipos.ytyp.xml');m=tree.getroot().find("./archetypes/Item[@type='CMloArchetypeDef']")
lo=r['min'];hi=r['max'];center=[(lo[i]+hi[i])/2 for i in range(3)];radius=math.sqrt(sum((hi[i]-center[i])**2 for i in range(3)))
for tag,vec in [('bbMin',lo),('bbMax',hi),('bsCentre',center)]:
 n=m.find(tag)
 for k,v in zip('xyz',vec):n.set(k,str(v))
m.find('bsRadius').set('value',str(radius));
limbo=m.find('rooms/Item');lomin=[x-.1 for x in lo];lomax=[x+.1 for x in hi]
for tag,vec in [('bbMin',lomin),('bbMax',lomax)]:
 for k,val in zip('xyz',vec):limbo.find(tag).set(k,str(val))
r['salas'][0].update(min=lomin,max=lomax,dimensoes=[lomax[i]-lomin[i] for i in range(3)])
(P/'relatorios/geometria.json').write_text(json.dumps(r,indent=2,ensure_ascii=False))
E.indent(tree);tree.write(X/'ga_arquetipos.ytyp.xml',encoding='utf-8',xml_declaration=True)
# Optional CMloInstanceDef map at origin, outside stream so it cannot appear at an unintended location.
root=E.Element('CMapData');E.SubElement(root,'name').text='ga_implantacao_origem';E.SubElement(root,'parent');E.SubElement(root,'flags',value='0');E.SubElement(root,'contentFlags',value='1')
for tag,vec in [('streamingExtentsMin',[v-200 for v in lo]),('streamingExtentsMax',[v+200 for v in hi]),('entitiesExtentsMin',lo),('entitiesExtentsMax',hi)]:E.SubElement(root,tag,**{k:str(v) for k,v in zip('xyz',vec)})
entities=E.SubElement(root,'entities');e=E.SubElement(entities,'Item',type='CMloInstanceDef');E.SubElement(e,'archetypeName').text='ga_mlo'
for tag,value in [('flags',32),('guid',0)]:E.SubElement(e,tag,value=str(value))
E.SubElement(e,'position',x='0',y='0',z='0');E.SubElement(e,'rotation',x='0',y='0',z='0',w='1')
for tag,value in [('scaleXY',1),('scaleZ',1),('parentIndex',-1),('lodDist',180),('childLodDist',0),('numChildren',0),('ambientOcclusionMultiplier',255),('artificialAmbientOcclusion',255),('tintValue',0),('groupId',0),('floorId',0),('numExitPortals',1),('MLOInstflags',0)]:E.SubElement(e,tag,value=str(value))
E.SubElement(e,'lodLevel').text='LODTYPES_DEPTH_ORPHANHD';E.SubElement(e,'priorityLevel').text='PRI_REQUIRED';E.SubElement(e,'extensions');E.SubElement(e,'defaultEntitySets')
for tag in ['containerLods','boxOccluders','occludeModels','physicsDictionaries','instancedData','timeCycleModifiers','carGenerators','LODLightsSOA','DistantLODLightsSOA']:E.SubElement(root,tag)
block=E.SubElement(root,'block');E.SubElement(block,'version',value='0');E.SubElement(block,'flags',value='0');E.SubElement(block,'name').text='ga_implantacao_origem';E.SubElement(block,'exportedBy').text='vano_boteco_colorado';E.SubElement(block,'owner');E.SubElement(block,'time')
E.indent(root);E.ElementTree(root).write(X/'ga_implantacao_origem.ymap.xml',encoding='utf-8',xml_declaration=True)
print('Bounds MLO calculados da geometria e exemplo CMloInstanceDef preparado.')
