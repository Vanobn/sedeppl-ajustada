import bpy,sys,addon_utils
from pathlib import Path
from mathutils import Vector
sys.path[:0]=['/workspace/tools','/workspace/tools/pydeps'];addon_utils.enable('Sollumz',default_set=True,persistent=True)
P=Path('/workspace/projeto-guarda-popular');bpy.ops.wm.open_mainfile(filepath=str(P/'vano_sede_master.blend'));s=bpy.context.scene
s.camera.name='vano_camera_perspectiva'
for n,loc,target,lens in [('frente',(4,-48,15),(-1,32,4),34),('patio',(3,15,3),(0,46,3.9),22),('planta',(0,30,110),(0,30,0),35)]:
 d=bpy.data.cameras.new('vano_camera_'+n);o=bpy.data.objects.new('vano_camera_'+n,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
 if n=='planta':d.type='ORTHO';d.ortho_scale=68
bpy.ops.wm.save_as_mainfile(filepath=str(P/'vano_sede_master.blend'))
s.camera=bpy.data.objects['vano_camera_patio'];s.render.resolution_x=1500;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=96;s.render.filepath=str(P/'vano_patio.png');bpy.ops.render.render(write_still=True)
