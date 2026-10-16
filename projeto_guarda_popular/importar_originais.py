import bpy,sys,addon_utils,json,math
from pathlib import Path
from mathutils import Vector
sys.path[:0]=['/workspace/tools','/workspace/tools/pydeps'];addon_utils.enable('Sollumz',default_set=True,persistent=True)
P=Path('/workspace/projeto-guarda-popular');D=P/'convertidos'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Cache all extracted DDS at asset-relative paths expected by CodeWalker XML.
import xml.etree.ElementTree as E
for p in D.glob('*.xml'):
 for tag in E.parse(p).getroot().findall('.//TextureDictionary/Item/FileName'):
  src=D/tag.text;dest=D/p.name.removesuffix('.xml')/tag.text
  if src.exists():
   dest.parent.mkdir(exist_ok=True)
   if not dest.exists():dest.symlink_to(src)
assets={};results=[]
for p in sorted(D.glob('*.xml')):
 if not p.name.endswith(('.ydr.xml','.yft.xml','.ybn.xml')):continue
 before=set(bpy.data.objects)
 try:
  result=bpy.ops.sollumz.import_assets(directory=str(D),files=[{'name':p.name}]);obs=set(bpy.data.objects)-before
  c=bpy.data.collections.new('vano_fonte_'+p.name.removesuffix('.xml'));bpy.context.scene.collection.children.link(c)
  for o in obs:
   for co in list(o.users_collection):co.objects.unlink(o)
   c.objects.link(o);o['vano_fonte']=p.name;o.name='vano_original_'+o.name
  c.hide_render=True;c.hide_viewport=True;assets[p.name]=c
  results.append({'arquivo':p.name,'resultado':str(result),'objetos':len(obs)})
 except Exception as e:results.append({'arquivo':p.name,'erro':str(e)})
# keep sources separate scene, original coordinates unchanged
bpy.context.scene.name='vano_BIBLIOTECA_ORIGINAIS'
for image in bpy.data.images:
 key=(Path(image.filepath).stem if image.filepath else image.name).lower()
 f=next((p for p in D.glob('*.dds') if p.stem.lower()==key),None)
 if f:
  image.source='FILE';image.filepath=str(f);image.reload()
loaded=[{'nome':i.name,'size':list(i.size),'filepath':i.filepath} for i in bpy.data.images]
(P/'importacao_sollumz.json').write_text(json.dumps({'assets':results,'imagens':loaded},indent=2))

for image in bpy.data.images:
 if image.source=='FILE' and Path(bpy.path.abspath(image.filepath)).is_file():image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'vano_biblioteca_originais.blend'))
print('IMPORTED',len(results),'ERRORS',sum('erro' in r for r in results),'IMAGES',len(loaded))
# Principled preview copies: retain unmodified GTA shaders in the saved source library.
preview_mats={}
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 for slot in ob.material_slots:
  m=slot.material
  if not m:continue
  if m.name not in preview_mats:
   images=[n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.name=='DiffuseSampler' and n.image]
   pm=bpy.data.materials.new('vano_preview_'+m.name);pm.use_nodes=True;p=pm.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.7
   if images:
    t=pm.node_tree.nodes.new('ShaderNodeTexImage');t.image=images[0];pm.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
   preview_mats[m.name]=pm
  slot.material=preview_mats[m.name]
# inspect architecture assemblies in genuine rendered previews
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=1100;s.render.resolution_y=850;s.render.resolution_percentage=100
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
ld=bpy.data.lights.new('vano_sol','SUN');ob=bpy.data.objects.new('vano_sol',ld);s.collection.objects.link(ob);ld.energy=3;ob.rotation_euler=(.5,-.3,-.5)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO'
for name,files in [('galpao',['nexus_galpao_ext.ydr.xml','nexus_galpao_int.ydr.xml']),('bar',['nexus_bar1909_ext.ydr.xml','nexus_bar1909_int.ydr.xml']),('alento',['nexus_alento_ext.ydr.xml','nexus_alento_int.ydr.xml'])]:
 pts=[]
 for f in files:
  c=assets[f];c.hide_render=False;c.hide_viewport=False
  for o in c.objects:
   if o.type=='MESH':pts.extend([o.matrix_world@Vector(v) for v in o.bound_box])
 mi=Vector(tuple(min(p[i] for p in pts) for i in range(3)));ma=Vector(tuple(max(p[i] for p in pts) for i in range(3)));center=(mi+ma)/2;size=max(ma-mi)
 cam.location=center+Vector((size*.7,-size*1.3,size*.65));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*1.4;s.render.filepath=str(P/('vano_original_'+name+'.png'));bpy.ops.render.render(write_still=True)
 for f in files:assets[f].hide_render=True;assets[f].hide_viewport=True
