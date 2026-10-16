import bpy,sys,math,json,bmesh,os
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.getenv('VANO_TOOLS','/workspace/tools'),os.getenv('VANO_TOOLS','/workspace/tools')+'/pydeps']
import addon_utils
addon_utils.enable('Sollumz',default_set=True,persistent=True)
from Sollumz.sollumz_properties import SollumType,LODLevel,ArchetypeType,LightType
from Sollumz.ydr.shader_materials import create_shader
from Sollumz.ybn.collision_materials import create_collision_material_from_index
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.name='vano_boteco_colorado';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
for y in list(s.ytyps):s.ytyps.remove(0)
C=bpy.data.collections.new('vano_bc_arquitetura');s.collection.children.link(C)
CC=bpy.data.collections.new('vano_bc_colisao');s.collection.children.link(CC)
HC=bpy.data.collections.new('vano_bc_mlo_guias');s.collection.children.link(HC)
HC.hide_render=True
mats={}
for p in sorted((P/'texturas').glob('*.dds')):
 m=create_shader('default.sps');m.name=p.stem;im=bpy.data.images.load(str(p),check_existing=True);m.node_tree.nodes['DiffuseSampler'].image=im;m.node_tree.nodes['DiffuseSampler'].texture_properties.embedded=False;mats[p.stem.removeprefix('vano_bc_')]=m
# Geometry is partitioned into real MLO room entities, not one visible shell called an interior.
G={n:[] for n in ['exterior','salao','circulacao','banheiro','deposito']};COL=[];group='exterior'
roomid={'exterior':0,'salao':1,'circulacao':2,'banheiro':3,'deposito':4}
V=[(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)]
F=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def collision_box(loc,dims,room,material=1):
 verts=[tuple(Vector(loc)+Vector((v[0]*dims[0],v[1]*dims[1],v[2]*dims[2]))) for v in V];COL.append((verts,F,room,material))
def move(ob):
 for c in list(ob.users_collection):c.objects.unlink(ob)
 C.objects.link(ob);G[group].append(ob);return ob
def uv_planar(ob,period=1.2):
 mesh=ob.data;uv=mesh.uv_layers.new(name='UVMap 0') if not mesh.uv_layers else mesh.uv_layers[0]
 for face in mesh.polygons:
  axis=max(range(3),key=lambda i:abs(face.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in face.loop_indices:
   co=ob.matrix_world@mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/period,co[axes[1]]/period)
def box(name,loc,dims,mat,collide=False,period=1.2):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=move(bpy.context.object);ob.name='vano_bc_'+name;ob.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(mats[mat]);uv_planar(ob,period)
 if collide:collision_box(loc,dims,roomid[group],1 if mat not in ['metal_oxidado','metal_grafite','chapa_vermelha'] else 55)
 return ob
def beam(name,a,b,width,mat):
 a,b=Vector(a),Vector(b);ob=box(name,(a+b)/2,(width,width,(b-a).length),mat);ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob
def plane(name,verts,mat,period=1.2,uv=None):
 me=bpy.data.meshes.new('vano_bc_'+name);me.from_pydata(verts,[],[(0,1,2,3)]);me.update();ob=bpy.data.objects.new('vano_bc_'+name,me);C.objects.link(ob);G[group].append(ob);me.materials.append(mats[mat]);uv_planar(ob,period)
 if uv:
  for i,co in enumerate(uv):me.uv_layers[0].data[i].uv=co
 return ob
def floor(x0,x1,y0,y1,mat='piso_ceramico'):
 return box('piso_'+group,((x0+x1)/2,(y0+y1)/2,-.09),(x1-x0,y1-y0,.18),mat,True)
def ceiling(x0,x1,y0,y1):
 return box('forro_'+group,((x0+x1)/2,(y0+y1)/2,3.16),(x1-x0,y1-y0,.12),'pintura_branca',True)
def wall_x(name,x,y0,y1,z0=0,z1=3.22,mat='reboco_vermelho',thick=.2):
 return box(name,(x,(y0+y1)/2,(z0+z1)/2),(thick,y1-y0,z1-z0),mat,True)
def wall_y(name,y,x0,x1,z0=0,z1=3.22,mat='reboco_vermelho',thick=.2):
 return box(name,((x0+x1)/2,y,(z0+z1)/2),(x1-x0,thick,z1-z0),mat,True)
def lining_y(y,x0,x1,z0,z1,mat,normal=-1):
 # +X then +Z gives -Y front. Reverse for surfaces looking the other way.
 verts=[(x0,y,z0),(x1,y,z0),(x1,y,z1),(x0,y,z1)]
 if normal>0:verts.reverse()
 return plane('revestimento_'+group,verts,mat)
def lining_x(x,y0,y1,z0,z1,mat,normal=1):
 verts=[(x,y0,z0),(x,y1,z0),(x,y1,z1),(x,y0,z1)]
 if normal<0:verts.reverse()
 return plane('revestimento_'+group,verts,mat)
# Outdoor covered forecourt: permanent open central pedestrian access, no extra entrance.
group='exterior';floor(-6,6,0,2.2)
wall_x('mureta_lateral_esq',-5.9,0,2.2,0,.78);wall_x('mureta_lateral_dir',5.9,0,2.2,0,.78)
for x in [-5.9,5.9]:
 collision_box((x,1.1,1.8),(.06,2.2,2.0),0,55)
 for y in [.12,2.12]:box('montante_lateral',(x,y,1.8),(.09,.09,2.1),'metal_oxidado')
 for z in [.82,2.78]:box('travessa_lateral',(x,1.1,z),(.05,2.1,.05),'metal_oxidado')
 for k in range(11):box('grade_lateral',(x,.15+k*.19,1.8),(.022,.022,1.95),'metal_oxidado')
for x0,x1 in [(-5.92,-1.15),(1.15,5.92)]:
 for z in [.12,2.80]:box('quadro_grade',((x0+x1)/2,.12,z),(x1-x0,.055,.055),'metal_oxidado')
 count=math.ceil((x1-x0)/.18)
 for i in range(count+1):
  x=x0+(x1-x0)*i/count;box('barra_vertical_grade',(x,.12,1.46),(.024,.025,2.7),'metal_oxidado')
 for j in range(1,12):box('barra_horizontal_grade',((x0+x1)/2,.118,j*.235),(x1-x0,.018,.018),'metal_oxidado')
 collision_box(((x0+x1)/2,.12,1.45),(x1-x0,.06,2.8),0,55)
for x in [-5.96,-3.0,-1.15,1.15,3.0,5.96]:box('pilar_grade',(x,.12,1.48),(.065,.065,2.96),'metal_oxidado')
for side in [-1,1]:
 x=side*1.15
 for z in [.12,2.80]:box('folha_aberta_quadro',(x,.7,z),(.055,1.15,.055),'metal_oxidado')
 for k in range(8):box('folha_aberta_barra',(x,.16+k*.155,1.46),(.025,.023,2.7),'metal_oxidado')
 for j in range(1,12):box('folha_aberta_travessa',(x,.7,j*.235),(.02,1.15,.018),'metal_oxidado')
 collision_box((x,.7,1.45),(.06,1.15,2.8),0,55)
# Thin corrugated porch roof, visible soffit and realistic drip edges.
verts=[];faces=[];N=200
for i in range(N+1):
 x=-6.10+12.2*i/N;ripple=.012*math.cos(i*math.pi/2)
 verts.extend([(x,-.18,3.03+ripple),(x,2.3,3.28+ripple)])
for i in range(N):faces.append((2*i,2*i+1,2*i+3,2*i+2))
me=bpy.data.meshes.new('vano_bc_cobertura_varanda');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);C.objects.link(ob);G[group].append(ob);me.materials.append(mats['telhas']);uv_planar(ob);mod=ob.modifiers.new('vano_bc_espessura_chapa','SOLIDIFY');mod.thickness=.035
for z in [2.88,3.00,3.10]:box('testeira_frontal',(0,-.13,z),(12.15,.12,.075),'chapa_vermelha')
for x in [-5.94,5.94]:beam('viga_lateral_varanda',(x,-.1,3.0),(x,2.2,3.23),.075,'chapa_vermelha')
for x in [-5.7,-3,0,3,5.7]:beam('terca_varanda',(x,-.1,3.0),(x,2.2,3.23),.04,'metal_grafite')
# Main front sign, corrugation carries continuous albedo/UVs, no 3D text pretending to be a flat logo.
box('placa_caixa',(0,-.04,3.91),(6.50,.13,1.70),'chapa_vermelha')
verts=[];faces=[];rows=40
for j in range(rows+1):
 z=3.06+1.7*j/rows;y=-.12+.013*math.cos(j*math.pi/2)
 verts.extend([(-3.25,y,z),(3.25,y,z)])
for j in range(rows):faces.append((2*j,2*j+1,2*j+3,2*j+2))
me=bpy.data.meshes.new('vano_bc_placa_face');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);C.objects.link(ob);G[group].append(ob);me.materials.append(mats['placa']);uv=me.uv_layers.new(name='UVMap 0')
for poly in me.polygons:
 for li in poly.loop_indices:
  co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((co.x+3.25)/6.5,(co.z-3.06)/1.7)
# Three projecting gooseneck sign fixtures, as in the reference.
for x in [-2.45,0,2.45]:
 beam('suporte_letreiro',(x,-.02,4.68),(x,-.70,4.94),.035,'metal_grafite')
 lamp=box('refletor_letreiro',(x,-.70,4.9),(.26,.18,.09),'metal_grafite');lamp.rotation_euler.x=.35
# Envelope: only the ground-floor bar, no building on top.
wall_x('parede_externa_esquerda',-5.9,2.2,9.5);wall_x('parede_externa_direita',5.9,2.2,9.5)
wall_y('parede_externa_fundos',9.4,-5.8,5.8)
wall_y('frente_jamba_esquerda',2.2,-6,-4.8);wall_y('frente_jamba_direita',2.2,4.8,6)
wall_y('verga_entrada',2.2,-4.8,4.8,2.78,3.22)
for x in [-4.83,4.83]:box('caixilho_entrada',(x,2.15,1.38),(.06,.09,2.76),'metal_oxidado')
box('caixilho_verga',(0,2.15,2.77),(9.72,.09,.06),'metal_oxidado')
mainroof=box('cobertura_principal',(0,5.8,3.34),(12.18,7.65,.12),'telhas',True);mainroof.rotation_euler.x=.016
for x in [-6.02,6.02]:box('rufo_lateral',(x,5.78,3.36),(.06,7.7,.16),'chapa_vermelha')
box('calha_fundos',(0,9.55,3.36),(12.15,.16,.12),'metal_grafite')
# Physical interior room floors, ceilings and linings; no furnishings or sanitary props.
group='salao';floor(-5.8,5.8,2.3,6.6);box('soleira_entrada',(0,2.25,-.09),(9.6,.1,.18),'piso_ceramico',True);ceiling(-5.8,5.8,2.3,6.6)
for x,normal in [(-5.794,1),(5.794,-1)]:
 lining_x(x,2.3,6.6,0,1.25,'azulejo_creme',normal);lining_x(x,2.3,6.6,1.25,3.10,'reboco_vermelho',normal)
# Front faces of the service rooms, opening in the center to the rear circulation.
wall_y('parede_frente_wc',6.7,-5.8,-2.8,mat='pintura_branca');wall_y('parede_frente_deposito',6.7,2.4,5.8,mat='pintura_branca')
for a,b in [(-5.8,-2.8),(2.4,5.8)]:
 lining_y(6.594,a,b,0,1.25,'azulejo_creme');lining_y(6.594,a,b,1.25,3.10,'reboco_vermelho')
group='circulacao';floor(-2.8,2.4,6.6,9.3);box('soleira_wc',(-2.9,7.65,-.09),(.2,.9,.18),'azulejo_wc',True);box('soleira_deposito',(2.5,7.8,-.09),(.2,1.2,.18),'concreto',True);ceiling(-2.8,2.4,6.6,9.3)
lining_y(9.294,-2.8,2.4,0,1.25,'azulejo_creme');lining_y(9.294,-2.8,2.4,1.25,3.10,'reboco_vermelho')
# Bathroom: 2.8 x 2.6 envelope, side doorway 0.9m; stockroom: 3.4 x 2.6, side doorway 1.2m.
for side,x,door_end,g in [('wc',-2.9,8.1,'banheiro'),('deposito',2.5,8.4,'deposito')]:
 group=g
 wall_x('divisoria_'+side+'_trecho1',x,6.6,7.2,mat='pintura_branca');wall_x('divisoria_'+side+'_trecho2',x,door_end,9.4,mat='pintura_branca');wall_x('divisoria_'+side+'_verga',x,7.2,door_end,2.15,3.22,mat='pintura_branca')
 for y in [7.2,door_end]:box('batente_'+side,(x,y,1.08),(.24,.06,2.16),'chapa_vermelha')
 box('batente_verga_'+side,(x,(7.2+door_end)/2,2.15),(.24,door_end-7.2+.06,.06),'chapa_vermelha')
group='banheiro';floor(-5.8,-3.0,6.8,9.3,'azulejo_wc');ceiling(-5.8,-3.0,6.8,9.3)
lining_x(-5.794,6.8,9.3,0,3.1,'azulejo_wc');lining_y(9.294,-5.8,-3,0,3.1,'azulejo_wc');lining_y(6.806,-5.8,-3,0,3.1,'azulejo_wc',normal=1)
for a,b in [(6.8,7.2),(8.1,9.3)]:lining_x(-3.006,a,b,0,3.1,'azulejo_wc',normal=-1)
lining_x(-3.006,7.2,8.1,2.15,3.1,'azulejo_wc',normal=-1)
group='deposito';floor(2.6,5.8,6.8,9.3,'concreto');ceiling(2.6,5.8,6.8,9.3)
lining_x(5.794,6.8,9.3,0,3.1,'pintura_branca',normal=-1);lining_y(9.294,2.6,5.8,0,3.1,'pintura_branca');lining_y(6.806,2.6,5.8,0,3.1,'pintura_branca',normal=1)
# Small red/brown base trim and ceramic top band, sized as actual joinery.
for g,x0,x1,y0,y1 in [('salao',-5.8,5.8,2.3,6.6),('circulacao',-2.8,2.4,6.6,9.3),('banheiro',-5.8,-3,6.8,9.3),('deposito',2.6,5.8,6.8,9.3)]:
 group=g
 for side,x in enumerate([x0+.012,x1-.012]):
  door=None
  if (g=='circulacao' and side==0) or (g=='banheiro' and side==1):door=(7.2,8.1)
  if (g=='circulacao' and side==1) or (g=='deposito' and side==0):door=(7.2,8.4)
  spans=[(y0,y1)] if door is None else [(y0,door[0]),(door[1],y1)]
  for lo,hi in spans:
   if hi>lo:box('rodape',(x,(lo+hi)/2,.06),(.022,hi-lo,.12),'chapa_vermelha')
# Apply physical modifiers, join per drawable/room, initialize real Sollumz models with vertex channels.
roots={};counts={}
for g,obs in G.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 for ob in obs:
  bpy.context.view_layer.objects.active=ob
  for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='vano_bc_'+g+'.model';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 root=bpy.data.objects.new('vano_bc_'+g,None);root.sollum_type=SollumType.DRAWABLE;C.objects.link(root);ob.parent=root;ob.sollum_type=SollumType.DRAWABLE_MODEL;ob.sz_lods.high.mesh=ob.data;ob.sz_lods.active_lod_level=LODLevel.HIGH
 for name in ['Color 1','Color 2']:
  attr=ob.data.color_attributes.new(name=name,type='BYTE_COLOR',domain='CORNER')
  for d in attr.data:d.color_srgb=(1,1,1,1)
 root.drawable_properties.lod_dist_high=180;root.drawable_properties.lod_dist_med=220;root.drawable_properties.lod_dist_low=260;root.drawable_properties.lod_dist_vlow=300;roots[g]=root;counts[g]=sum(len(p.vertices)-2 for p in ob.data.polygons)
# Genuine BVH collision with room-coded materials, simplified cage panels and clear door openings.
colroot=bpy.data.objects.new('vano_bc_mlo',None);colroot.sollum_type=SollumType.BOUND_COMPOSITE;CC.objects.link(colroot)
bvh=bpy.data.objects.new('vano_bc_mlo_bvh',None);bvh.sollum_type=SollumType.BOUND_GEOMETRYBVH;CC.objects.link(bvh);bvh.parent=colroot
for prop in ['map_dynamic','map_cover','map_vehicle']:setattr(bvh.composite_flags1,prop,True)
for prop in ['map_weapon','map_dynamic','map_animal','map_cover','map_vehicle','ped','ragdoll','animal','animal_ragdoll','object','plant','projectile','explosion','test_weapon','test_camera','test_ai','test_script','test_vehicle_wheel']:setattr(bvh.composite_flags2,prop,True)
verts=[];faces=[];inds=[];cmats={}
for v,f,r,material in COL:
 key=(r,material)
 if key not in cmats:
  cm=create_collision_material_from_index(material);cm.name=f'vano_bc_col_room_{r}_mat_{material}';cm.collision_properties.room_id=r
  if material==55:cm.collision_flags.see_through=True;cm.collision_flags.shoot_through=True
  cmats[key]=cm
 off=len(verts);verts.extend(v);faces.extend([tuple(i+off for i in face) for face in f]);inds.extend([list(cmats).index(key)]*len(f))
mesh=bpy.data.meshes.new('vano_bc_colisao_malha');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(mesh.name,mesh);CC.objects.link(ob);ob.parent=bvh;ob.sollum_type=SollumType.BOUND_POLY_TRIANGLE
for m in cmats.values():mesh.materials.append(m)
for f,idx in zip(mesh.polygons,inds):f.material_index=idx
ob.hide_render=True;ob.display_type='WIRE';bvh.hide_render=True;colroot.hide_render=True
# MLO rooms and portals registered in Blender's actual Sollumz YTYP data.
ytyp=s.ytyps.add();ytyp.name='vano_bc_arquetipos';s.ytyp_index=0
for g,root in roots.items():
 a=ytyp.new_archetype(ArchetypeType.BASE);a.asset=root;a.name=root.name;a.texture_dictionary='vano_bc_texturas';a.flags.total='32';a.lod_dist=180
mlo=ytyp.new_archetype(ArchetypeType.MLO);mlo.asset=colroot;mlo.name='vano_bc_mlo';mlo.asset_name='vano_bc_mlo';mlo.lod_dist=180;mlo.flags.total='0';mlo.mlo_flags.total='0'
roomdefs=[('limbo',(-6.2,-.9,-.3),(6.2,9.8,5.1)),('salao',(-5.8,2.3,0),(5.8,6.6,3.1)),('circulacao',(-2.8,6.6,0),(2.4,9.3,3.1)),('banheiro',(-5.8,6.8,0),(-3,9.3,3.1)),('deposito',(2.6,6.8,0),(5.8,9.3,3.1))]
rooms=[]
for name,mi,ma in roomdefs:
 r=mlo.new_room();r.name=name;r.bb_min=mi;r.bb_max=ma;r.timecycle='';r.secondary_timecycle='';r.floor_id=0;r.exterior_visibility_depth=3;r.flags.total='0';rooms.append(r)
# Portal normals point from source room to destination room.
portals=[(0,1,[(-4.8,2.2,0),(-4.8,2.2,2.78),(4.8,2.2,2.78),(4.8,2.2,0)]),(1,2,[(-2.8,6.65,0),(-2.8,6.65,3.1),(2.4,6.65,3.1),(2.4,6.65,0)]),(2,3,[(-2.9,7.2,0),(-2.9,8.1,0),(-2.9,8.1,2.15),(-2.9,7.2,2.15)]),(2,4,[(2.5,7.2,0),(2.5,7.2,2.15),(2.5,8.4,2.15),(2.5,8.4,0)])]
# Snapshot after collection growth: Blender invalidates earlier PropertyGroup references.
rooms=list(mlo.rooms)
# Correct winding via room centers; no inverted portal corners.
for rf,rt,corners in portals:
 n=(Vector(corners[1])-Vector(corners[0])).cross(Vector(corners[2])-Vector(corners[0]));dest=(Vector(roomdefs[rt][1])+Vector(roomdefs[rt][2]))/2
 if rf==0:direction=Vector((0,1,0))
 else:direction=dest-sum((Vector(c) for c in corners),Vector())/4
 if n.dot(direction)<0:corners.reverse()
 p=mlo.new_portal();p.room_from_id=str(rooms[rf].id);p.room_to_id=str(rooms[rt].id);p.flags.total='0';p.opacity=0;p.audio_occlusion='0'
 for i,co in enumerate(corners):setattr(p,'corner'+str(i+1),co)
 # Non-exported helpers are editable visual references for portal bounds.
 me=bpy.data.meshes.new('vano_bc_portal');me.from_pydata(corners,[],[(0,1,2,3)]);helper=bpy.data.objects.new(f'vano_bc_portal_{rf}_{rt}',me);HC.objects.link(helper);helper.display_type='WIRE';helper.hide_render=True
for g,root in roots.items():
 ent=mlo.new_entity();ent.archetype_name=root.name;ent.linked_object=root;ent.attached_room_id=str(rooms[roomid[g]].id);ent.flags.total='32';ent.lod_dist=180
# Real light instances inside room drawables, not just preview-only illumination.
for g,loc,energy in [('exterior',(-2.45,-.70,4.84),35),('exterior',(0,-.70,4.84),35),('exterior',(2.45,-.70,4.84),35),('salao',(-3,4.4,2.95),90),('salao',(3,4.4,2.95),90),('circulacao',(0,8.1,2.95),45),('banheiro',(-4.4,8.0,2.95),35),('deposito',(4.2,8.0,2.95),35)]:
 d=bpy.data.lights.new('vano_bc_luz_'+g,'POINT');d.sollum_type=LightType.POINT;d.energy=energy;d.color=(1,.86,.70);d.shadow_soft_size=.12;d.time_flags.total=str((1<<24)-1);d.light_properties.falloff=6 if g in ['banheiro','deposito'] else 8;d.light_flags.cast_shadows=True
 if g=='exterior':d.light_flags.exterior_only=True
 else:d.light_flags.interior_only=True
 light=bpy.data.objects.new(d.name,d);C.objects.link(light);light.parent=roots[g];light.location=loc
# Measured dimensions from actual vertices; floor and door clearances are recorded separately.
bpy.context.view_layer.update();pts=[o.matrix_world@v.co for root in roots.values() for o in root.children if o.type=='MESH' for v in o.data.vertices];mi=[min(p[i] for p in pts) for i in range(3)];ma=[max(p[i] for p in pts) for i in range(3)]
report={'min':mi,'max':ma,'dimensoes':[ma[i]-mi[i] for i in range(3)],'area_envelope':(ma[0]-mi[0])*(ma[1]-mi[1]),'pe_direito':3.1,'triangulos_por_entidade':counts,'triangulos_colisao':sum(len(f)-2 for f in faces),'salas':[{'nome':n,'min':lo,'max':hi,'dimensoes':[hi[i]-lo[i] for i in range(3)]} for n,lo,hi in roomdefs],'portais':len(portals),'mobiliario':False,'portao':'Aberto permanentemente, sem folha no vão de passagem','textura_placa':'Reconstrução visual gerada a partir da fotografia; não reprodução pixel a pixel.'}
(P/'relatorios/geometria.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
# Save/export using real GTA materials and room data, before adding preview-only sun/camera.
for image in bpy.data.images:
 if image.source=='FILE':image.pack()
CC.hide_render=True;HC.hide_render=True
res=bpy.ops.sollumz.export_assets(directory=str(P/'xml'),direct_export=True,use_custom_settings=True,target_formats={'CWXML'},target_versions={'GEN8'},limit_to_selected=False,export_ytyps=True,export_ytyps_include='ALL',export_ymaps=False,export_ytds=False)
print('EXPORT_RESULT',res);assert res=={'FINISHED'}
# World and cameras; source geometry/material properties remain exportable.
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.61,.68,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
ld=bpy.data.lights.new('vano_bc_sol_preview','SUN');ld.energy=2.6;sun=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(sun);sun.rotation_euler=(.55,-.3,-.4)
for name,loc,target,lens in [('frente',(1,-19,5.8),(0,3,1.7),43),('perspectiva',(14,-17,10),(0,4.2,1.7),43),('interior',(0,2.65,1.7),(0,8,1.55),19)]:
 d=bpy.data.cameras.new('vano_bc_camera_'+name);cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
s.camera=bpy.data.objects['vano_bc_camera_frente'];s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False;s.render.resolution_x=1500;s.render.resolution_y=1050;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(P/'blender/vano_boteco_colorado_master.blend'),compress=True)
for name in ([] if os.getenv('VANO_SKIP_RENDERS')=='1' else ['frente','perspectiva','interior']):
 s.camera=bpy.data.objects['vano_bc_camera_'+name];s.render.filepath=str(P/'previews'/('vano_bc_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('GEOMETRIA',json.dumps(report))
