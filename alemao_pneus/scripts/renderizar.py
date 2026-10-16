import bpy,sys,os
sys.path[:0]=[os.getenv("VANO_TOOLS","/workspace/tools"),os.getenv("VANO_TOOLS","/workspace/tools")+"/pydeps"]
import addon_utils;addon_utils.enable("Sollumz",default_set=True,persistent=True)
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'blender/alemao_pneus_master.blend'));s=bpy.context.scene;s.render.resolution_x=1200;s.render.resolution_y=900;s.cycles.samples=24;s.cycles.use_denoising=False
for name in ['frente','perspectiva','interior']:
 s.camera=bpy.data.objects['ap_camera_'+name];s.render.filepath=str(P/'previews'/('ap_'+name+'.png'));bpy.ops.render.render(write_still=True)
