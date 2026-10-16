import bpy,json,sys,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];sys.path[:0]=[os.getenv('VANO_TOOLS','/workspace/tools'),os.getenv('VANO_TOOLS','/workspace/tools')+'/pydeps']
import addon_utils;addon_utils.enable('Sollumz',default_set=True,persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(P/'blender/vano_boteco_colorado_master.blend'))
col=bpy.data.objects['vano_bc_colisao_malha'];me=col.data;me.calc_loop_triangles();verts=[col.matrix_world@v.co for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles];bvh=BVHTree.FromPolygons(verts,tris,all_triangles=True)
checks=[]
def cast(name,a,b,expect_hit):
 direction=Vector(b)-Vector(a);hit=bvh.ray_cast(Vector(a),direction.normalized(),direction.length)[0];ok=(hit is not None)==expect_hit;checks.append({'nome':name,'passou':ok,'atingiu_colisao':hit is not None,'ponto':list(hit) if hit else None});assert ok,name
for x in [-.4,0,.4]:cast('acesso_grade_aberto_'+str(x),(x,-.5,1),(x,1.7,1),False)
for x in [-3,0,3]:cast('entrada_salao_livre_'+str(x),(x,1.7,1),(x,3,1),False)
for y in [7.45,7.65,7.9]:cast('porta_wc_livre_'+str(y),(-2, y,1),(-4,y,1),False)
for y in [7.45,7.8,8.15]:cast('porta_deposito_livre_'+str(y),(1.5,y,1),(4,y,1),False)
cast('grade_esquerda_bloqueia',(-3,-.5,1),(-3,.5,1),True);cast('grade_direita_bloqueia',(3,-.5,1),(3,.5,1),True)
cast('parede_lateral_bloqueia',(5,4,1),(6.5,4,1),True);cast('parede_fundos_bloqueia',(0,8.5,1),(0,10,1),True)
cast('parede_frontal_wc_bloqueia',(-4.4,6,1),(-4.4,7.2,1),True)
for name,x,y in [('varanda',0,1),('entrada_soleira',0,2.25),('salao',0,4),('circulacao',0,8),('wc_soleira',-2.9,7.65),('deposito_soleira',2.5,7.8),('wc',-4.4,8),('deposito',4.2,8)]:
 hit=bvh.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),2)[0];ok=hit is not None and abs(hit.z)<.001;checks.append({'nome':'piso_continuo_'+name,'passou':ok,'altura':hit.z if hit else None});assert ok,name
s=bpy.context.scene;archetype=next(a for a in s.ytyps[0].archetypes if a.name=='vano_bc_mlo');assert len(archetype.rooms)==5 and len(archetype.portals)==4 and len(archetype.entities)==5
assert {m.collision_properties.room_id for m in me.materials}==set(range(5))
images=[]
for img in bpy.data.images:
 if img.source=='FILE':images.append({'nome':img.name,'empacotada':img.packed_file is not None,'dimensoes':list(img.size)});assert img.packed_file and img.size[0]>0
report={'cheques_de_colisao':checks,'passaram':sum(c['passou'] for c in checks),'salas':len(archetype.rooms),'portais':len(archetype.portals),'entidades':len(archetype.entities),'ids_de_sala_colisao':sorted({m.collision_properties.room_id for m in me.materials}),'texturas':images,'limite_validacao':'Raios em BVH e dados de arquivo; não é teste do motor GTA/FiveM.'}
(P/'relatorios/validacao_blender.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print('PASS',report['passaram'],'checagens físicas; 5 salas; 4 portais; 5 entidades; texturas empacotadas.')
