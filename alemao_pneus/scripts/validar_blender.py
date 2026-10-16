import bpy,json,sys,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];sys.path[:0]=[os.getenv('VANO_TOOLS','/workspace/tools'),os.getenv('VANO_TOOLS','/workspace/tools')+'/pydeps']
import addon_utils;addon_utils.enable('Sollumz',default_set=True,persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(P/'blender/alemao_pneus_master.blend'))
compiled='--colisao-compilada' in sys.argv
col=bpy.data.objects['ap_colisao_malha']
if compiled:
 before=set(bpy.data.objects)
 result=bpy.ops.sollumz.import_assets(directory=str(P/'relatorios/roundtrip'),files=[{'name':'ap_mlo.ybn.xml'}])
 assert result=={'FINISHED'}
 meshes=[o for o in set(bpy.data.objects)-before if o.type=='MESH']
 assert len(meshes)==1
 col=meshes[0]
 bpy.context.view_layer.update()
me=col.data;me.calc_loop_triangles();verts=[col.matrix_world@v.co for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles];bvh=BVHTree.FromPolygons(verts,tris,all_triangles=True)
checks=[]
def cast(name,a,b,expect_hit):
 direction=Vector(b)-Vector(a);hit=bvh.ray_cast(Vector(a),direction.normalized(),direction.length)[0];ok=(hit is not None)==expect_hit;checks.append({'nome':name,'passou':ok,'atingiu_colisao':hit is not None,'ponto':list(hit) if hit else None});assert ok,name
# Open vehicle access, left display and side walls; floors at grade.
for x in [-2,-1,0,1,2]:cast('entrada_veiculo_'+str(x),(x,-2,1),(x,3,1),False)
for x in [-1,0,1]:cast('circulacao_longitudinal_'+str(x),(x,1,1),(x,16,1),False)
for y in [3,6,10,16]:
 cast('parede_esquerda_'+str(y),(-3,y,1),(-4,y,1),True)
 cast('parede_direita_'+str(y),(3,y,1),(4,y,1),True)
cast('fundos',(0,17,1),(0,19,1),True)
cast('portao_expositor',(-4.2,-.1,1),(-4.2,-2.0,1),True)
for x in [-2,0,2]:
 for y in [-1,.1,.3,1,5,10,16]:
  hit=bvh.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),2)[0];ok=hit is not None and abs(hit.z)<.001;checks.append({'nome':f'piso_{x}_{y}','passou':ok,'altura':hit.z if hit else None});assert ok,(x,y)
s=bpy.context.scene;archetype=next(a for a in s.ytyps[0].archetypes if a.name=='ap_mlo');assert len(archetype.rooms)==2 and len(archetype.portals)==1 and len(archetype.entities)==2
assert {m.collision_properties.room_id for m in me.materials}==set(range(2))
images=[]
for img in bpy.data.images:
 if img.source=='FILE':images.append({'nome':img.name,'empacotada':img.packed_file is not None,'dimensoes':list(img.size)});assert img.packed_file and img.size[0]>0
report={'cheques_de_colisao':checks,'passaram':sum(c['passou'] for c in checks),'salas':len(archetype.rooms),'portais':len(archetype.portals),'entidades':len(archetype.entities),'ids_de_sala_colisao':sorted({m.collision_properties.room_id for m in me.materials}),'texturas':images,'limite_validacao':'Raios em BVH e dados de arquivo; não é teste do motor GTA/FiveM.'}
report['origem_colisao']='YBN compilado e relido pelo CodeWalker.Core, reimportado pelo Sollumz' if compiled else 'Master Blender fonte'
(P/('relatorios/validacao_colisao_compilada.json' if compiled else 'relatorios/validacao_blender.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False));print('PASS',report['passaram'],'checagens físicas; 2 salas; 1 portal; 2 entidades; texturas empacotadas.')
