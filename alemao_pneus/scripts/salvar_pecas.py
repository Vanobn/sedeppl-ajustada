import bpy,sys,os
from pathlib import Path
sys.path[:0]=[os.getenv('VANO_TOOLS','/workspace/tools'),os.getenv('VANO_TOOLS','/workspace/tools')+'/pydeps']
import addon_utils;addon_utils.enable('Sollumz',default_set=True,persistent=True)
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'blender/alemao_pneus_master.blend'))
for name in ['ap_arquitetura','ap_colisao','ap_mlo_guias']:
 c=bpy.data.collections[name];c.hide_viewport=True;c.hide_render=True
c=bpy.data.collections['EDITAVEIS_pecas_individuais'];c.hide_viewport=False;c.hide_render=False
for ob in c.objects:
 ob.hide_set(False)
 if ob.type=='MESH' and not ob.data.color_attributes:
  for name in ['Color 1','Color 2']:
   a=ob.data.color_attributes.new(name=name,type='BYTE_COLOR',domain='CORNER')
   for v in a.data:v.color_srgb=(1,1,1,1)
bpy.context.scene['instrucoes']='Peças independentes para edição. A exportação GTA está no master; esta cópia não sincroniza automaticamente com ela.'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'blender/alemao_pneus_pecas_editaveis.blend'),compress=True)
print('PECAS_EDITAVEIS',sum(o.type=='MESH' for o in c.objects))
