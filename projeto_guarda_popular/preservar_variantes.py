import bpy,sys,addon_utils
from pathlib import Path
sys.path[:0]=['/workspace/tools','/workspace/tools/pydeps'];addon_utils.enable('Sollumz',default_set=True,persistent=True)
P=Path('/workspace/projeto-guarda-popular');bpy.ops.wm.open_mainfile(filepath=str(P/'vano_sede_master.blend'));source=bpy.data.scenes['vano_BIBLIOTECA_ORIGINAIS'];count=0
for ob in source.objects:
 if ob.type!='MESH' or 'vano_fonte' not in ob:continue
 name=ob['vano_fonte'].removesuffix('.xml');dirs=[P/'convertidos/texturas_por_asset'/name,P/'convertidos/texturas_por_asset'/name.replace('.yft','.ytd')]
 for slot in ob.material_slots:
  m=slot.material
  if not m or not m.use_nodes:continue
  changes=[]
  for n in m.node_tree.nodes:
   if n.type!='TEX_IMAGE' or not n.image:continue
   imgname=n.image.name
   for folder in dirs:
    candidates=list(folder.glob('*.dds'));f=next((p for p in candidates if p.stem==imgname),None)
    if f is None:
     matches=[p for p in candidates if p.stem.lower()==imgname.lower()]
     if len(matches)==1:f=matches[0]
    if f:
     changes.append((n.name,f));break
  if changes:
   cp=m.copy();cp.name='vano_fonte_material_'+name+'_'+m.name.removeprefix('vano_');slot.material=cp
   for node,path in changes:
    im=bpy.data.images.load(str(path),check_existing=True);cp.node_tree.nodes[node].image=im
    if not im.packed_file:im.pack()
    count+=1
bpy.context.window.scene=bpy.data.scenes['vano_PROJETO'];bpy.ops.wm.save_as_mainfile(filepath=str(P/'vano_sede_master.blend'));print('SOURCE_TEXTURE_BINDINGS',count)
