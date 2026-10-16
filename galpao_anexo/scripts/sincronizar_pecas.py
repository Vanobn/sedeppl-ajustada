"""Load edited independent pieces and update High meshes in the GTA master.
Run with Blender --python this_script, not by running Python outside Blender.
Collision/room edits must be made explicitly in the same editable .blend.
"""
import bpy,sys,os,json
from pathlib import Path
sys.path[:0]=[os.getenv('VANO_TOOLS','/workspace/tools'),os.getenv('VANO_TOOLS','/workspace/tools')+'/pydeps']
import addon_utils;addon_utils.enable('Sollumz',default_set=True,persistent=True)
from Sollumz.sollumz_properties import LODLevel
P=Path(__file__).resolve().parents[1];source=P/'blender/galpao_anexo_pecas_editaveis.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;coll=bpy.data.collections['ga_arquitetura'];coll.hide_viewport=False;coll.hide_render=False
editable=bpy.data.collections['EDITAVEIS_pecas_individuais'];editable.hide_viewport=True;editable.hide_render=True
for group in ['exterior','salao','mezanino']:
 parts=[o for o in editable.objects if o.type=='MESH' and o.get('grupo_exportacao')==group];assert parts,group
 clones=[]
 for part in parts:
  ob=part.copy();ob.data=part.data.copy();ob.parent=None;coll.objects.link(ob);ob.matrix_world=part.matrix_world.copy();ob.hide_set(False);clones.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in clones:ob.select_set(True)
 bpy.context.view_layer.objects.active=clones[0]
 for ob in clones:
  bpy.context.view_layer.objects.active=ob
  for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.context.view_layer.objects.active=clones[0];bpy.ops.object.join();joined=bpy.context.object;s.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 for name in ['Color 1','Color 2']:
  if not joined.data.color_attributes.get(name):
   attr=joined.data.color_attributes.new(name=name,type='BYTE_COLOR',domain='CORNER')
   for item in attr.data:item.color_srgb=(1,1,1,1)
 root=bpy.data.objects['ga_'+group];model=next(o for o in root.children if o.type=='MESH');model.sz_lods.active_lod_level=LODLevel.HIGH;model.sz_lods.high.mesh=joined.data;bpy.data.objects.remove(joined,do_unlink=True)
# Measured bounds and counts describe the edited geometry, not the initial template.
pts=[o.matrix_world@v.co for g in ['exterior','salao','mezanino'] for o in bpy.data.objects['ga_'+g].children if o.type=='MESH' for v in o.data.vertices]
lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
r=json.loads((P/'relatorios/geometria.json').read_text());r.update(min=lo,max=hi,dimensoes=[hi[i]-lo[i] for i in range(3)],area_envelope=(hi[0]-lo[0])*(hi[1]-lo[1]))
co=bpy.data.objects['ga_colisao_malha'].data;co.calc_loop_triangles();r['triangulos_colisao']=len(co.loop_triangles);(P/'relatorios/geometria.json').write_text(json.dumps(r,indent=2,ensure_ascii=False))
for name in ['ga_colisao','ga_mlo_guias']:bpy.data.collections[name].hide_viewport=False;bpy.data.collections[name].hide_render=True
for image in bpy.data.images:
 if image.source=='FILE':image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'blender/galpao_anexo_master.blend'),compress=True)
print('SINCRONIZADO: peças → meshes High. Regere LODs, bounds e binários antes de instalar. Colisão não é recriada automaticamente.')
