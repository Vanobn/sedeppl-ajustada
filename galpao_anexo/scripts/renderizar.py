import bpy,sys,os
from pathlib import Path
from mathutils import Vector
sys.path[:0]=[os.getenv('VANO_TOOLS','/workspace/tools'),os.getenv('VANO_TOOLS','/workspace/tools')+'/pydeps']
import addon_utils;addon_utils.enable('Sollumz',default_set=True,persistent=True)
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'blender/galpao_anexo_master.blend'));s=bpy.context.scene
s.render.resolution_x=1400;s.render.resolution_y=960;s.cycles.samples=int(os.getenv("GA_SAMPLES","32"));s.cycles.use_denoising=os.getenv("GA_DENOISE","0")=="1";s.render.resolution_percentage=int(os.getenv("GA_RESOLUTION_PERCENT","100"))
# Actual render lights supplement the exported point lights only for presentation.
for x in [-6,6]:
 for y in [8,23]:
  d=bpy.data.lights.new('preview_area','AREA');d.energy=1600;d.shape='DISK';d.size=6;ob=bpy.data.objects.new(d.name,d);s.collection.objects.link(ob);ob.location=(x,y,9)
for name in os.getenv('GA_VIEWS','interior,mezanino,frente,perspectiva').split(','):
 s.camera=bpy.data.objects['ga_camera_'+name];s.render.filepath=str(P/'previews'/('ga_'+name+'.png'));bpy.ops.render.render(write_still=True)
