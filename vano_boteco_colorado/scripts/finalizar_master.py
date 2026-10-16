import bpy,json,sys,os,math,bmesh
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];sys.path[:0]=[os.getenv('VANO_TOOLS','/workspace/tools'),os.getenv('VANO_TOOLS','/workspace/tools')+'/pydeps']
import addon_utils;addon_utils.enable('Sollumz',default_set=True,persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(P/'blender/vano_boteco_colorado_master.blend'));s=bpy.context.scene;r=json.loads((P/'relatorios/geometria.json').read_text());m=next(a for a in s.ytyps[0].archetypes if a.name=='vano_bc_mlo');m.bb_min=r['min'];m.bb_max=r['max'];m.bs_center=[(r['min'][i]+r['max'][i])/2 for i in range(3)];m.bs_radius=math.sqrt(sum((r['max'][i]-m.bs_center[i])**2 for i in range(3)));m.rooms[0].bb_min=r['salas'][0]['min'];m.rooms[0].bb_max=r['salas'][0]['max']
# Top camera remains available in master; cutaway is presentation-only after saving.
d=bpy.data.cameras.new('vano_bc_camera_planta');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);cam.location=(0,4.5,20);cam.rotation_euler=(0,0,0);d.type='ORTHO';d.ortho_scale=14
s.camera=bpy.data.objects['vano_bc_camera_frente'];bpy.ops.wm.save_as_mainfile(filepath=str(P/'blender/vano_boteco_colorado_master.blend'),compress=True)
s.render.resolution_x=1300;s.render.resolution_y=900;s.cycles.samples=64;s.camera=bpy.data.objects['vano_bc_camera_interior'];s.render.filepath=str(P/'previews/vano_bc_interior.png');bpy.ops.render.render(write_still=True)
# Cut geometry above 1.8m to display actual partitions and door openings from above.
for ob in list(bpy.data.collections['vano_bc_arquitetura'].objects):
 if ob.type!='MESH':continue
 ob.data=ob.data.copy();bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=(0,0,1.8),plane_no=(0,0,1),clear_outer=True,clear_inner=False);bm.to_mesh(ob.data);bm.free();ob.data.update()
s.camera=cam;s.render.resolution_x=1300;s.render.resolution_y=1100;s.cycles.samples=32;s.render.filepath=str(P/'previews/vano_bc_planta_corte.png');bpy.ops.render.render(write_still=True)
