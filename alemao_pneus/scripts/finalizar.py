import bpy,os,sys,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];sys.path[:0]=[os.getenv('VANO_TOOLS','/workspace/tools'),os.getenv('VANO_TOOLS','/workspace/tools')+'/pydeps']
import addon_utils;addon_utils.enable('Sollumz',default_set=True,persistent=True)
from Sollumz.sollumz_properties import LODLevel
bpy.ops.wm.open_mainfile(filepath=str(P/'blender/alemao_pneus_master.blend'));s=bpy.context.scene;r=json.loads((P/'relatorios/geometria.json').read_text());lodcounts={}
# Make pavement continuous across the entrance threshold; source, visual and BVH agree.
for collname in ['ap_arquitetura','ap_colisao','EDITAVEIS_pecas_individuais']:
 for ob in bpy.data.collections[collname].objects:
  if ob.type!='MESH':continue
  inverse=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   world=ob.matrix_world@v.co
   if abs(world.y)<.00001 and world.z<.00001:
    world.y=.42;v.co=inverse@world
  ob.data.update()
# Close the rear gable below the pitched roof; retain an independent editable source.
ex=bpy.data.objects['ap_exterior'];model=next(o for o in ex.children if o.type=='MESH')
if not model.get('empena_fechada'):
 vs=[(-3.63,y,5.34) for y in [17.91,18.09]]+[(3.63,y,5.34) for y in [17.91,18.09]]+[(0,y,6.37) for y in [17.91,18.09]]
 fs=[(0,2,4),(1,5,3),(0,1,3,2),(2,3,5,4),(4,5,1,0)]
 me=bpy.data.meshes.new('ap_fechamento_empena_fundos');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['ap_branco']);me.update();uv=me.uv_layers.new(name='UVMap 0')
 for face in me.polygons:
  for li in face.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/2,v.z/2)
 for cname in ['Color 1','Color 2']:
  attr=me.color_attributes.new(name=cname,type='BYTE_COLOR',domain='CORNER')
  for item in attr.data:item.color_srgb=(1,1,1,1)
 obj=bpy.data.objects.new(me.name,me);bpy.data.collections['ap_arquitetura'].objects.link(obj)
 src=obj.copy();src.data=me.copy();bpy.data.collections['EDITAVEIS_pecas_individuais'].objects.link(src);src.name='ap_fechamento_empena_fundos_editavel'
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);model.select_set(True);bpy.context.view_layer.objects.active=model;bpy.ops.object.join();model['empena_fechada']=True
for name in ['ap_exterior','ap_oficina']:
 root=bpy.data.objects[name];ob=next(o for o in root.children if o.type=='MESH');lodcounts[name]={'high':sum(len(f.vertices)-2 for f in ob.data.polygons)}
 for level,ratio in [('medium',.50),('low',.25)]:
  temp=ob.copy();temp.data=ob.data.copy();s.collection.objects.link(temp);mod=temp.modifiers.new('LOD_simplificado','DECIMATE');mod.ratio=ratio;mod.use_collapse_triangulate=True
  mesh=bpy.data.meshes.new_from_object(temp.evaluated_get(bpy.context.evaluated_depsgraph_get()));mesh.name=name+'_'+level;getattr(ob.sz_lods,level).mesh=mesh;lodcounts[name][level]=sum(len(f.vertices)-2 for f in mesh.polygons);bpy.data.objects.remove(temp,do_unlink=True)
 ob.sz_lods.active_lod_level=LODLevel.HIGH
 root.drawable_properties.lod_dist_high=65;root.drawable_properties.lod_dist_med=110;root.drawable_properties.lod_dist_low=180
m=next(a for a in s.ytyps[0].archetypes if a.name=='ap_mlo');m.bb_min=r['min'];m.bb_max=r['max'];m.bs_center=[(a+b)/2 for a,b in zip(r['min'],r['max'])];m.bs_radius=math.sqrt(sum((a-b)**2 for a,b in zip(r['max'],m.bs_center)))
m.rooms[0].bb_min=[v-.1 for v in r['min']];m.rooms[0].bb_max=[v+.1 for v in r['max']]
bpy.ops.object.select_all(action='DESELECT')
for coll in ['ap_arquitetura','ap_colisao']:
 for ob in bpy.data.collections[coll].objects:ob.select_set(True)
assert bpy.ops.sollumz.export_assets(directory=str(P/'xml'),direct_export=True,use_custom_settings=True,target_formats={'CWXML'},target_versions={'GEN8'},limit_to_selected=True,export_ytyps=True,export_ytyps_include='ALL',export_ymaps=False,export_ytds=False)=={'FINISHED'}
r['triangulos_por_entidade']={k.removeprefix('ap_'):v['high'] for k,v in lodcounts.items()}
r['lods']=lodcounts;(P/'relatorios/geometria.json').write_text(json.dumps(r,indent=2,ensure_ascii=False))
s.render.resolution_x=1200;s.render.resolution_y=900;s.cycles.samples=24
bpy.ops.wm.save_as_mainfile(filepath=str(P/'blender/alemao_pneus_master.blend'),compress=True)
if os.getenv('AP_SKIP_RENDERS')!='1':
 for name in ['frente','perspectiva','interior']:
  s.camera=bpy.data.objects['ap_camera_'+name];s.render.filepath=str(P/'previews'/('ap_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('LODS',lodcounts)
