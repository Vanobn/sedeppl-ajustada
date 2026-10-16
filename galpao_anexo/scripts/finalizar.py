import bpy,os,sys,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];sys.path[:0]=[os.getenv('VANO_TOOLS','/workspace/tools'),os.getenv('VANO_TOOLS','/workspace/tools')+'/pydeps']
import addon_utils;addon_utils.enable('Sollumz',default_set=True,persistent=True)
from Sollumz.sollumz_properties import LODLevel
bpy.ops.wm.open_mainfile(filepath=str(P/'blender/galpao_anexo_master.blend'));s=bpy.context.scene;r=json.loads((P/'relatorios/geometria.json').read_text());lodcounts={}
for name in ['ga_exterior','ga_salao','ga_mezanino']:
 root=bpy.data.objects[name];ob=next(o for o in root.children if o.type=='MESH');lodcounts[name]={'high':sum(len(f.vertices)-2 for f in ob.data.polygons)}
 for level,ratio in [('medium',.50),('low',.25)]:
  temp=ob.copy();temp.data=ob.data.copy();s.collection.objects.link(temp);mod=temp.modifiers.new('LOD_simplificado','DECIMATE');mod.ratio=ratio;mod.use_collapse_triangulate=True
  mesh=bpy.data.meshes.new_from_object(temp.evaluated_get(bpy.context.evaluated_depsgraph_get()));mesh.name=name+'_'+level;getattr(ob.sz_lods,level).mesh=mesh;lodcounts[name][level]=sum(len(f.vertices)-2 for f in mesh.polygons);bpy.data.objects.remove(temp,do_unlink=True)
 ob.sz_lods.active_lod_level=LODLevel.HIGH
 root.drawable_properties.lod_dist_high=65;root.drawable_properties.lod_dist_med=110;root.drawable_properties.lod_dist_low=180
# Explicit GTA collision masks are verified here before each export.
bvh=bpy.data.objects['ga_mlo_bvh']
for prop in ['map_dynamic','map_cover','map_vehicle']:
 assert hasattr(bvh.composite_flags1,prop),prop
 setattr(bvh.composite_flags1,prop,True)
for prop in ['map_weapon','map_dynamic','map_animal','map_cover','map_vehicle','ped','ragdoll','animal','animal_ragdoll','object','plant','projectile','explosion','test_weapon','test_camera','test_ai','test_script','test_vehicle_wheel']:
 assert hasattr(bvh.composite_flags2,prop),prop
 setattr(bvh.composite_flags2,prop,True)
m=next(a for a in s.ytyps[0].archetypes if a.name=='ga_mlo');m.bb_min=r['min'];m.bb_max=r['max'];m.bs_center=[(a+b)/2 for a,b in zip(r['min'],r['max'])];m.bs_radius=math.sqrt(sum((a-b)**2 for a,b in zip(r['max'],m.bs_center)))
m.rooms[0].bb_min=[v-.1 for v in r['min']];m.rooms[0].bb_max=[v+.1 for v in r['max']]
# Reload edited PNG/DDS sources when present, retaining them packed in the master.
for image in bpy.data.images:
 candidate=P/'texturas'/Path(bpy.path.abspath(image.filepath)).name
 if image.source=='FILE' and candidate.is_file():
  image.filepath=str(candidate)
  if image.packed_file:image.unpack(method='REMOVE')
  image.reload();image.pack()
bpy.ops.object.select_all(action='DESELECT')
for coll in ['ga_arquitetura','ga_colisao']:
 for ob in bpy.data.collections[coll].objects:ob.select_set(True)
assert bpy.ops.sollumz.export_assets(directory=str(P/'xml'),direct_export=True,use_custom_settings=True,target_formats={'CWXML'},target_versions={'GEN8'},limit_to_selected=True,export_ytyps=True,export_ytyps_include='ALL',export_ymaps=False,export_ytds=False)=={'FINISHED'}
r['triangulos_por_entidade']={k.removeprefix('ga_'):v['high'] for k,v in lodcounts.items()}
r['lods']=lodcounts;(P/'relatorios/geometria.json').write_text(json.dumps(r,indent=2,ensure_ascii=False))
s.render.resolution_x=1200;s.render.resolution_y=900;s.cycles.samples=24
bpy.ops.wm.save_as_mainfile(filepath=str(P/'blender/galpao_anexo_master.blend'),compress=True)
if os.getenv('GA_SKIP_RENDERS')!='1':
 for name in ['frente','perspectiva','interior','mezanino']:
  s.camera=bpy.data.objects['ga_camera_'+name];s.render.filepath=str(P/'previews'/('ga_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('LODS',lodcounts)
