import bpy,json,sys,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];sys.path[:0]=[os.getenv('VANO_TOOLS','/workspace/tools'),os.getenv('VANO_TOOLS','/workspace/tools')+'/pydeps']
import addon_utils;addon_utils.enable('Sollumz',default_set=True,persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(P/'blender/galpao_anexo_master.blend'))
compiled='--colisao-compilada' in sys.argv
col=bpy.data.objects['ga_colisao_malha']
if compiled:
 before=set(bpy.data.objects)
 result=bpy.ops.sollumz.import_assets(directory=str(P/'relatorios/roundtrip'),files=[{'name':'ga_mlo.ybn.xml'}])
 assert result=={'FINISHED'}
 meshes=[o for o in set(bpy.data.objects)-before if o.type=='MESH']
 assert len(meshes)==1
 col=meshes[0]
 bpy.context.view_layer.update()
me=col.data;me.calc_loop_triangles();verts=[col.matrix_world@v.co for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles];bvh=BVHTree.FromPolygons(verts,tris,all_triangles=True)
checks=[]
def cast(name,a,b,expect_hit):
 direction=Vector(b)-Vector(a);hit=bvh.ray_cast(Vector(a),direction.normalized(),direction.length)[0];ok=(hit is not None)==expect_hit;checks.append({'nome':name,'passou':ok,'atingiu_colisao':hit is not None,'ponto':list(hit) if hit else None});assert ok,name
# Ground floor, entry and boundary walls.
for x in [-2,0,2]:cast('entrada_livre_'+str(x),(x,-2,1),(x,3,1),False)
for x in [-6,0,6]:cast('circulacao_salao_'+str(x),(x,1,1),(x,30,1),False)
for y in [4,12,20,30]:
 cast('parede_esquerda_'+str(y),(-11,y,1),(-13,y,1),True)
 cast('parede_direita_'+str(y),(11,y,1),(13,y,1),True)
for x in [-8,0,8]:cast('fundos_fechados_'+str(x),(x,31,1),(x,33,1),True)
for x in [-6,6]:cast('frente_fechada_'+str(x),(x,1,1),(x,-1,1),True)
def floorcheck(name,x,y,height):
 hit=bvh.ray_cast(Vector((x,y,height+.45)),Vector((0,0,-1)),.70)[0];ok=hit is not None and abs(hit.z-height)<.012;checks.append({'nome':name,'passou':ok,'altura':hit.z if hit else None,'esperado':height});assert ok,(name,hit)
for x in [-10,-5,0,5,10]:
 for y in [-1,.1,1,8,16,24,30]:floorcheck(f'piso_{x}_{y}',x,y,0)
# Stair treads and player head clearance tested at every step, not just endpoints.
for i in range(21):
 y=4.1+(i+.5)*.30;z=(i+1)*3.5/21
 floorcheck(f'degrau_{i+1}',10.30,y,z)
 cast(f'pe_direito_escada_{i+1}',(10.30,y,z+.15),(10.30,y,z+2.15),False)
for y in [10.41,11,16,22,30]:
 for x in [9.4,10.3,11.3]:floorcheck(f'mezanino_{x}_{y}',x,y,3.5)
for y in [12,20,29]:cast(f'guarda_corpo_{y}',(9.2,y,4),(8.4,y,4),True)
for y in [6.0,8.5]:
 z=(y-4.1)*3.5/6.3+.6
 cast(f'corrimao_esq_{y}',(9.6,y,z),(9.1,y,z),True)
 cast(f'corrimao_dir_{y}',(11.0,y,z),(11.5,y,z),True)
# Roof collisions follow both pitches; no invisible ceiling in the playable hall.
for x in [-8,0,8]:cast('cobertura_'+str(x),(x,15,8),(x,15,14),True)
s=bpy.context.scene;archetype=next(a for a in s.ytyps[0].archetypes if a.name=='ga_mlo');assert len(archetype.rooms)==2 and len(archetype.portals)==1 and len(archetype.entities)==3
assert {m.collision_properties.room_id for m in me.materials}==set(range(2))
source=bpy.data.collections['EDITAVEIS_pecas_individuais'];assert len(source.objects)>100
assert {'exterior','salao','mezanino'}=={o.get('grupo_exportacao') for o in source.objects}
images=[]
for img in bpy.data.images:
 if img.source=='FILE':images.append({'nome':img.name,'empacotada':img.packed_file is not None,'dimensoes':list(img.size)});assert img.packed_file and img.size[0]>0
report={'cheques_de_colisao':checks,'passaram':sum(c['passou'] for c in checks),'salas':len(archetype.rooms),'portais':len(archetype.portals),'entidades':len(archetype.entities),'ids_de_sala_colisao':sorted({m.collision_properties.room_id for m in me.materials}),'texturas':images,'limite_validacao':'Raios em BVH e dados de arquivo; não é teste do motor GTA/FiveM.'}
report['origem_colisao']='YBN compilado e relido pelo CodeWalker.Core, reimportado pelo Sollumz' if compiled else 'Master Blender fonte'
(P/('relatorios/validacao_colisao_compilada.json' if compiled else 'relatorios/validacao_blender.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False));print('PASS',report['passaram'],'checagens físicas; 2 salas; 1 portal; 3 entidades; texturas empacotadas.')
