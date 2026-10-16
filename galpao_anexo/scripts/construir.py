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
s=bpy.context.scene;s.name='galpao_anexo';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
for y in list(s.ytyps):s.ytyps.remove(0)
C=bpy.data.collections.new('ga_arquitetura');s.collection.children.link(C)
CC=bpy.data.collections.new('ga_colisao');s.collection.children.link(CC)
HC=bpy.data.collections.new('ga_mlo_guias');s.collection.children.link(HC)
HC.hide_render=True
mats={}
for p in sorted((P/'texturas').glob('*.dds')):
 m=create_shader('default.sps');m.name=p.stem;im=bpy.data.images.load(str(p),check_existing=True);m.node_tree.nodes['DiffuseSampler'].image=im;m.node_tree.nodes['DiffuseSampler'].texture_properties.embedded=False;mats[p.stem.removeprefix('ga_')]=m
# Geometry is partitioned into real MLO room entities, not one visible shell called an interior.
G={n:[] for n in ['exterior','salao','mezanino']};COL=[];group='exterior'
roomid={'exterior':0,'salao':1,'mezanino':1}
V=[(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)]
F=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def collision_box(loc,dims,room,material=1):
 verts=[tuple(Vector(loc)+Vector((v[0]*dims[0],v[1]*dims[1],v[2]*dims[2]))) for v in V];COL.append((verts,F,room,material))
def move(ob):
 for c in list(ob.users_collection):c.objects.unlink(ob)
 C.objects.link(ob);G[group].append(ob);return ob
def uv_planar(ob,period=1.2):
 mesh=ob.data;uv=mesh.uv_layers.new(name='UVMap 0') if not mesh.uv_layers else mesh.uv_layers[0]
 uv.name='UVMap 0'
 for face in mesh.polygons:
  axis=max(range(3),key=lambda i:abs(face.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in face.loop_indices:
   co=ob.matrix_world@mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/period,co[axes[1]]/period)
def box(name,loc,dims,mat,collide=False,period=1.2):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=move(bpy.context.object);ob.name='ga_'+name;ob.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(mats[mat]);uv_planar(ob,period)
 if collide:collision_box(loc,dims,roomid[group],1 if mat not in ['metal_vermelho','metal_preto'] else 55)
 return ob
def beam(name,a,b,width,mat):
 a,b=Vector(a),Vector(b);ob=box(name,(a+b)/2,(width,width,(b-a).length),mat);ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob
def plane(name,verts,mat,period=1.2,uv=None):
 me=bpy.data.meshes.new('ga_'+name);me.from_pydata(verts,[],[(0,1,2,3)]);me.update();ob=bpy.data.objects.new('ga_'+name,me);C.objects.link(ob);G[group].append(ob);me.materials.append(mats[mat]);uv_planar(ob,period)
 if uv:
  for i,co in enumerate(uv):me.uv_layers[0].data[i].uv=co
 return ob
def floor(x0,x1,y0,y1,mat='concreto'):
 return box('piso_'+group,((x0+x1)/2,(y0+y1)/2,-.09),(x1-x0,y1-y0,.18),mat,True)
def ceiling(x0,x1,y0,y1):
 return box('forro_'+group,((x0+x1)/2,(y0+y1)/2,3.16),(x1-x0,y1-y0,.12),'tijolo_branco',True)
def wall_x(name,x,y0,y1,z0=0,z1=3.22,mat='tijolo_vermelho',thick=.2):
 return box(name,(x,(y0+y1)/2,(z0+z1)/2),(thick,y1-y0,z1-z0),mat,True)
def wall_y(name,y,x0,x1,z0=0,z1=3.22,mat='tijolo_vermelho',thick=.2):
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


# Dimensions estimated from one interior reference; exterior and unseen front are inferred.
WIDTH=24.0;DEPTH=32.0;EAVE=9.0;RIDGE=12.0;MEZZ=3.5
# Mesh helpers avoid texture-heavy props; each component stays independent in the source.
def cyl(name,loc,r,depth,mat,segments=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=r,depth=depth,location=loc);ob=move(bpy.context.object);ob.name='ga_'+name;ob.data.materials.append(mats[mat]);uv_planar(ob);return ob
def mesh(name,verts,faces,mat):
 me=bpy.data.meshes.new('ga_'+name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);C.objects.link(ob);G[group].append(ob);me.materials.append(mats[mat]);uv_planar(ob);return ob
def coll_mesh(ob,material=1):
 bpy.context.view_layer.update();COL.append(([tuple(ob.matrix_world@v.co) for v in ob.data.vertices],[tuple(f.vertices) for f in ob.data.polygons],roomid[group],material))
def deco(name,verts,mat,uv=None):
 return plane(name,verts,mat,uv=uv or [(0,0),(1,0),(1,1),(0,1)])
def door_right(y,width=1.05,z=0,height=2.25):
 box('porta_painel_fechado',(11.825,y,z+height/2),(.055,width,height),'porta')
 for yy in [y-width/2-.04,y+width/2+.04]:box('batente_porta',(11.78,yy,z+height/2),(.075,.075,height+.1),'metal_vermelho')
 box('verga_porta',(11.78,y,z+height+.04),(.08,width+.16,.08),'metal_vermelho')
 box('macaneta',(11.73,y-.30,z+1.02),(.07,.15,.035),'metal_preto')
# Outside: compact industrial envelope, no fabricated neighbouring buildings.
group='exterior';floor(-12.4,12.4,-3,0)
for x in [-12,12]:
 wall_x('parede_lateral_base',x,0,32,0,1.65,'tijolo_vermelho',.24)
 wall_x('parede_lateral_alta',x,0,32,1.65,9.0,'tijolo_branco',.24)
wall_y('parede_fundos_base',32,-12,12,0,1.65,'tijolo_vermelho',.24)
wall_y('parede_fundos_alta',32,-12,12,1.65,9,'tijolo_branco',.24)
# Front has a deliberate open entrance on the unseen side; no dynamic gate script is claimed.
for a,b in [(-12,-3.5),(3.5,12)]:
 wall_y('frente_alvenaria',0,a,b,0,1.65,'tijolo_vermelho',.24);wall_y('frente_alvenaria_alta',0,a,b,1.65,9,'tijolo_branco',.24)
wall_y('verga_acesso',0,-3.5,3.5,5.6,9,'tijolo_branco',.24)
for x in [-3.55,3.55]:box('montante_portao_acesso',(x,-.16,2.8),(.10,.12,5.6),'metal_vermelho',True)
# Solid gable prisms front and rear close the envelope under the pitched roof.
for y in [0,32]:
 vs=[(-12,y-.12,9),(12,y-.12,9),(0,y-.12,12),(-12,y+.12,9),(12,y+.12,9),(0,y+.12,12)]
 ob=mesh('empena',vs,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'telha');coll_mesh(ob)
# Roof is panelled in strips. Two translucent strips match the industrial reference.
for side in [-1,1]:
 for i in range(48):
  xx=(i+.5)*12.35/48;x=side*xx;z=12-xx*.25+.06
  mat='claraboia' if 6.9<xx<8.2 else 'telha'
  ob=box('claraboia' if mat=='claraboia' else 'telha_corrugada',(x,16,z),(12.35/48+.012,32.65,.055),mat);ob.rotation_euler.y=side*math.atan(.25)
 # Roof slab collision follows the actual pitch, rather than an invisible flat ceiling.
 ob=box('suporte_cobertura',(side*6.10,16,10.48),(12.60,32.5,.08),'metal_preto');ob.rotation_euler.y=side*math.atan(.25);coll_mesh(ob);G[group].remove(ob);bpy.data.objects.remove(ob,do_unlink=True)
box('cumeeira',(0,16,12.12),(.22,32.7,.08),'metal_vermelho')
for x in [-12.25,12.25]:box('calha',(x,16,8.95),(.16,32.6,.18),'metal_vermelho')
for x in [-12.18,12.18]:cyl('condutor_pluvial',(x,31.6,4.4),.065,8.8,'metal_vermelho',12)
# Interior main hall: empty open concrete floor with red/white perimeter markings.
group='salao';floor(-11.88,11.88,0,31.88)
for x in [-11.3,11.3]:box('faixa_piso_vermelha',(x,16,.003),(1.08,31.7,.006),'piso_vermelho')
for y in [.58,31.3]:box('faixa_piso_vermelha',(0,y,.004),(22.6,1.08,.008),'piso_vermelho')
for x in [-10.70,10.70]:box('linha_branca_piso',(x,16,.009),(.11,30.7,.01),'luminaria')
for y in [1.2,30.7]:box('linha_branca_piso',(0,y,.01),(21.5,.11,.01),'luminaria')
# Separate inward-facing wall and roof surfaces belong to the interior room.
# This avoids relying on limbo visibility to draw the hall envelope from inside.
for x,norm in [(-11.874,1),(11.874,-1)]:
 lining_x(x,0,31.88,0,1.65,'tijolo_vermelho',norm)
 lining_x(x,0,31.88,1.65,9,'tijolo_branco',norm)
lining_y(31.874,-11.88,11.88,0,1.65,'tijolo_vermelho',normal=-1)
lining_y(31.874,-11.88,11.88,1.65,9,'tijolo_branco',normal=-1)
for lo,hi in [(-11.88,-3.5),(3.5,11.88)]:
 lining_y(.126,lo,hi,0,1.65,'tijolo_vermelho',normal=1)
 lining_y(.126,lo,hi,1.65,9,'tijolo_branco',normal=1)
lining_y(.126,-3.5,3.5,5.6,9,'tijolo_branco',normal=1)
for i in range(96):
 x0=-12+i*.25;x1=x0+.25;mid=(x0+x1)/2
 z0=12-abs(x0)*.25-.02;z1=12-abs(x1)*.25-.02
 mat='claraboia' if 6.9<abs(mid)<8.2 else 'telha'
 plane('revestimento_interno_cobertura',[(x0,.13,z0),(x0,31.87,z0),(x1,31.87,z1),(x1,.13,z1)],mat)
for y in [.126,31.874]:
 v=[(-11.88,y,9),(11.88,y,9),(0,y,11.98)]
 if y<1:v.reverse()
 mesh('empena_interna',v,[(0,1,2)],'telha')
# Red structural bands and tall concrete piers, as photographed.
for x in [-11.84,11.84]:
 box('faixa_parede',(x,16,4.0),(.025,31.8,.35),'tijolo_vermelho')
 for y in ([.3,8,16,24,31.7] if x<0 else [.3,4,12.5,31.7]):
  box('pilar_concreto',(x,y,4.5),(.38,.48,9),'tijolo_branco',True)
  box('pilar_faixa_vermelha',(x-.01 if x>0 else x+.01,y,3.8),(.4,.5,.42),'tijolo_vermelho')
for x in [-11.65,-3.5,4.2,11.65]:
 box('pilar_fundos',(x,31.74,4.5),(.45,.4,9),'tijolo_branco',True)
 box('pilar_fundos_faixa',(x,31.52,3.8),(.48,.025,.42),'tijolo_vermelho')
# Large corrugated red door on the photographed end wall, intentionally closed.
box('portao_fundos_fechado',(.2,31.82,2.9),(6.8,.12,5.8),'porta')
for i in range(46):box('nervura_portao',(-3.12+i*.146,31.742,2.9),(.028,.025,5.8),'metal_vermelho')
for x in [-3.25,.2,3.65]:box('perfil_portao',(x,31.68,2.9),(.065,.06,5.8),'metal_preto')
for x in [-.02,.45]:box('puxador_portao',(x,31.61,1.6),(.04,.08,.3),'metal_preto')
# Upper metal cladding and gridded clerestory windows above that door.
box('painel_chapa_fundos',(.2,31.79,7.3),(6.8,.09,2.8),'telha')
for i in range(45):box('friso_chapa_fundos',(-3.12+i*.15,31.72,7.3),(.017,.025,2.8),'metal_preto')
box('janela_fundos',(.2,31.64,7.1),(6.7,.035,.60),'claraboia')
for z in [6.80,7.1,7.40]:box('caixilho_janela_fundos',(.2,31.60,z),(6.75,.035,.025),'metal_preto')
for x in [-3.12+i*.30 for i in range(23)]:box('caixilho_janela_fundos',(x,31.60,7.1),(.022,.035,.60),'metal_preto')
# Rear-left circular supporter mural, reconstructed from the reference.
deco('mural_guarda_popular',[(-11.3,31.59,1.9),(-4.55,31.59,1.9),(-4.55,31.59,8.55),(-11.3,31.59,8.55)],'murais',[(0,0),(.5,0),(.5,1),(0,1)])
# Right wall: red lettering band and tall SCI mural near the staircase.
deco('faixa_guarda_popular',[(11.735,29.7,6.15),(11.735,14.0,6.15),(11.735,14.0,8.5),(11.735,29.7,8.5)],'faixa_guarda_popular')
deco('mural_sci',[(11.72,10.8,3.8),(11.72,5.8,3.8),(11.72,5.8,8.75),(11.72,10.8,8.75)],'murais',[(.5,0),(1,0),(1,1),(.5,1)])
# Closed door panels reflect only visible openings; no invented offices/bathrooms behind them.
for y in [12.4,17.4,22.5,27.8]:door_right(y)
for y in [14.0,19.3,24.5,29.2]:door_right(y,z=3.5,height=2.15)
for y in [17.5,24.0,29.4]:
 box('janela_alta_lateral',(11.765,y,5.75),(.035,1.6,.38),'claraboia')
 for yy in [y-.80,y,y+.80]:box('caixilho_janela_lateral',(11.73,yy,5.75),(.04,.025,.42),'metal_vermelho')
 for z in [5.56,5.75,5.94]:box('caixilho_janela_lateral',(11.73,y,z),(.04,1.65,.02),'metal_vermelho')
# Real steel roof trusses, diagonals and secondary purlins, no suspended false ceiling.
for y in [.45,6.5,12.8,19.1,25.4,31.55]:
 for side in [-1,1]:
  beam('banzo_superior',(0,y,11.8),(side*11.8,y,8.86),.085,'metal_preto')
  beam('banzo_inferior',(0,y,11.0),(side*11.8,y,8.1),.075,'metal_vermelho')
  for k in range(8):
   x0=side*k*11.8/8;x1=side*(k+1)*11.8/8
   za=11.8-abs(x0)*.25;zb=11.0-abs(x1)*.25
   beam('diagonal_trelica',(x0,y,za),(x1,y,zb),.045,'metal_preto')
   beam('vertical_trelica',(x0,y,za),(x0,y,za-.8),.04,'metal_preto')
for side in [-1,1]:
 for xx in [1.2,3.3,5.4,7.5,9.6,11.7]:beam('terca',(side*xx,.0,11.95-xx*.25),(side*xx,32,11.95-xx*.25),.055,'metal_preto')
# Suspended bell fixtures at alternating truss positions, without heavy bulb meshes.
for x,y,z in [(-6,6.5,9.1),(5.5,6.5,9.25),(-6,16,9.1),(5.5,16,9.25),(-6,25.4,9.1),(5.5,25.4,9.25)]:
 beam('pendente_luminaria',(x,y,z+.75),(x,y,z+.12),.025,'metal_preto')
 bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.30,radius2=.12,depth=.38,location=(x,y,z));ob=move(bpy.context.object);ob.name='ga_campanula';ob.data.materials.append(mats['metal_preto']);uv_planar(ob)
 cyl('difusor_luminaria',(x,y,z-.195),.276,.015,'luminaria')
# Mezzanine is an open walkway inside the same physical hall; no false culling partition.
group='mezanino'
box('laje_mezanino',(10.35,21.1,3.36),(3.05,21.4,.28),'tijolo_branco',True)
box('longarina_mezanino',(8.78,21.1,3.35),(.18,21.5,.30),'metal_vermelho',True)
for y in [11.0,16.2,21.4,26.6,31.5]:
 box('pilar_mezanino',(8.85,y,1.65),(.25,.25,3.3),'tijolo_branco',True)
 box('viga_mezanino',(10.35,y,3.22),(3.1,.16,.22),'metal_preto')
# Waist-high red guardrail, collidable as a simple thin screen; the aisle stays clear.
for y in [10.5+i*1.52 for i in range(15)]:box('poste_guarda_corpo',(8.80,y,4.02),(.045,.045,1.04),'metal_vermelho')
for z in [3.72,4.0,4.28,4.55]:box('travessa_guarda_corpo',(8.80,21.1,z),(.035,21.3,.035),'metal_vermelho')
collision_box((8.80,21.1,4.02),(.045,21.3,1.05),1,55)
# 21 stairs, each a separate mesh and collision step, rise 3.5m over 6.3m.
for i in range(21):
 z=(i+1)*3.5/21;y=4.1+(i+.5)*.30
 box('degrau_%02d'%(i+1),(10.30,y,z-.055),(1.80,.30,.11),'metal_vermelho',True)
for x in [9.37,11.23]:
 ob=beam('longarina_escada',(x,4.1,.02),(x,10.4,3.50),.13,'metal_preto');coll_mesh(ob,55)
 for offset in [.45,.80,1.05]:
  ob=beam('corrimao_escada',(x,4.1,offset),(x,10.4,3.5+offset),.035,'metal_vermelho')
  if offset==1.05:
   # Thin sloping rail proxy; matches slope and does not fill the walking volume.
   bpy.context.view_layer.update();a=Vector((x,4.1,.15));b=Vector((x,10.4,3.65));v=[tuple(q) for q in [a+Vector((-.025,0,0)),a+Vector((.025,0,0)),b+Vector((.025,0,0)),b+Vector((-.025,0,0)),a+Vector((-.025,0,.95)),a+Vector((.025,0,.95)),b+Vector((.025,0,.95)),b+Vector((-.025,0,.95))]];COL.append((v,F,1,55))
 for i in range(8):
  y=4.1+i*.9;z=(y-4.1)*3.5/6.3;box('poste_escada',(x,y,z+.55),(.04,.04,1.1),'metal_vermelho')
# Small safety cabinet/extinguisher at the foot of the photographed staircase.
group='salao';box('caixa_incendio',(11.72,5.1,.9),(.12,.65,1.2),'metal_vermelho');cyl('extintor',(11.45,5.15,.62),.10,.55,'porta',12)
# Independent editable pieces retain an explicit export group for later synchronization.
editable=bpy.data.collections.new('EDITAVEIS_pecas_individuais');s.collection.children.link(editable)
for g,obs in G.items():
 for ob in obs:
  dup=ob.copy();dup.data=ob.data.copy();dup.name=ob.name+'_editavel';dup['grupo_exportacao']=g;editable.objects.link(dup)
editable.hide_render=True;editable.hide_viewport=True
# Apply physical modifiers, join per drawable/room, initialize real Sollumz models with vertex channels.
roots={};counts={}
for g,obs in G.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 for ob in obs:
  bpy.context.view_layer.objects.active=ob
  for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='ga_'+g+'.model';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 root=bpy.data.objects.new('ga_'+g,None);root.sollum_type=SollumType.DRAWABLE;C.objects.link(root);ob.parent=root;ob.sollum_type=SollumType.DRAWABLE_MODEL;ob.sz_lods.high.mesh=ob.data;ob.sz_lods.active_lod_level=LODLevel.HIGH
 for name in ['Color 1','Color 2']:
  attr=ob.data.color_attributes.new(name=name,type='BYTE_COLOR',domain='CORNER')
  for d in attr.data:d.color_srgb=(1,1,1,1)
 root.drawable_properties.lod_dist_high=180;root.drawable_properties.lod_dist_med=220;root.drawable_properties.lod_dist_low=260;root.drawable_properties.lod_dist_vlow=300;roots[g]=root;counts[g]=sum(len(p.vertices)-2 for p in ob.data.polygons)
# Genuine BVH collision with room-coded materials, simplified cage panels and clear door openings.
colroot=bpy.data.objects.new('ga_mlo',None);colroot.sollum_type=SollumType.BOUND_COMPOSITE;CC.objects.link(colroot)
bvh=bpy.data.objects.new('ga_mlo_bvh',None);bvh.sollum_type=SollumType.BOUND_GEOMETRYBVH;CC.objects.link(bvh);bvh.parent=colroot
for prop in ['map_dynamic','map_cover','map_vehicle']:setattr(bvh.composite_flags1,prop,True)
for prop in ['map_weapon','map_dynamic','map_animal','map_cover','map_vehicle','ped','ragdoll','animal','animal_ragdoll','object','plant','projectile','explosion','test_weapon','test_camera','test_ai','test_script','test_vehicle_wheel']:setattr(bvh.composite_flags2,prop,True)
verts=[];faces=[];inds=[];cmats={}
for v,f,r,material in COL:
 key=(r,material)
 if key not in cmats:
  cm=create_collision_material_from_index(material);cm.name=f'ga_col_room_{r}_mat_{material}';cm.collision_properties.room_id=r
  if material==55:cm.collision_flags.see_through=True
  cmats[key]=cm
 off=len(verts);verts.extend(v);faces.extend([tuple(i+off for i in face) for face in f]);inds.extend([list(cmats).index(key)]*len(f))
mesh=bpy.data.meshes.new('ga_colisao_malha');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(mesh.name,mesh);CC.objects.link(ob);ob.parent=bvh;ob.sollum_type=SollumType.BOUND_POLY_TRIANGLE
for m in cmats.values():mesh.materials.append(m)
for f,idx in zip(mesh.polygons,inds):f.material_index=idx
ob.hide_render=True;ob.display_type='WIRE';bvh.hide_render=True;colroot.hide_render=True
# MLO rooms and portals registered in Blender's actual Sollumz YTYP data.
ytyp=s.ytyps.add();ytyp.name='ga_arquetipos';s.ytyp_index=0
for g,root in roots.items():
 a=ytyp.new_archetype(ArchetypeType.BASE);a.asset=root;a.name=root.name;a.texture_dictionary='ga_texturas';a.flags.total='32';a.lod_dist=180
mlo=ytyp.new_archetype(ArchetypeType.MLO);mlo.asset=colroot;mlo.name='ga_mlo';mlo.asset_name='ga_mlo';mlo.lod_dist=180;mlo.flags.total='0';mlo.mlo_flags.total='0'
roomdefs=[('limbo',(-12.6,-3.2,-.3),(12.6,32.6,12.4)),('salao',(-11.88,0,0),(11.88,31.88,12.20))]
rooms=[]
for name,mi,ma in roomdefs:
 r=mlo.new_room();r.name=name;r.bb_min=mi;r.bb_max=ma;r.timecycle='';r.secondary_timecycle='';r.floor_id=0;r.exterior_visibility_depth=3;r.flags.total='0';rooms.append(r)
# Portal normals point from source room to destination room.
portals=[(0,1,[(-3.45,0,0),(-3.45,0,5.55),(3.45,0,5.55),(3.45,0,0)])]
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
 me=bpy.data.meshes.new('ga_portal');me.from_pydata(corners,[],[(0,1,2,3)]);helper=bpy.data.objects.new(f'ga_portal_{rf}_{rt}',me);HC.objects.link(helper);helper.display_type='WIRE';helper.hide_render=True
for g,root in roots.items():
 ent=mlo.new_entity();ent.archetype_name=root.name;ent.linked_object=root;ent.attached_room_id=str(rooms[roomid[g]].id);ent.flags.total='32';ent.lod_dist=180
# Real light instances inside room drawables, not just preview-only illumination.
for g,loc,energy in [('salao',(x,y,8.7),320) for x in [-6,5.5] for y in [6.5,16,25.4]]+[('mezanino',(10.2,y,2.9),70) for y in [13,20,27]]:
 d=bpy.data.lights.new('ga_luz_'+g,'POINT');d.sollum_type=LightType.POINT;d.energy=energy;d.color=(1,.86,.70);d.shadow_soft_size=.12;d.time_flags.total=str((1<<24)-1);d.light_properties.falloff=6 if g in ['banheiro','deposito'] else 14;d.light_flags.cast_shadows=True
 if g=='exterior':d.light_flags.exterior_only=True
 else:d.light_flags.interior_only=True
 light=bpy.data.objects.new(d.name,d);C.objects.link(light);light.parent=roots[g];light.location=loc
# Measured dimensions from actual vertices; floor and door clearances are recorded separately.
bpy.context.view_layer.update();pts=[o.matrix_world@v.co for root in roots.values() for o in root.children if o.type=='MESH' for v in o.data.vertices];mi=[min(p[i] for p in pts) for i in range(3)];ma=[max(p[i] for p in pts) for i in range(3)]
report={'min':mi,'max':ma,'dimensoes':[ma[i]-mi[i] for i in range(3)],'area_envelope':(ma[0]-mi[0])*(ma[1]-mi[1]),'dimensoes_estimadas':True,'largura_nominal':24,'profundidade_nominal':32,'altura_beiral':9,'altura_cumeeira':12.12,'mezanino_altura':3.5,'degraus':21,'triangulos_por_entidade':counts,'triangulos_colisao':sum(len(f)-2 for f in faces),'salas':[{'nome':n,'min':lo,'max':hi,'dimensoes':[hi[i]-lo[i] for i in range(3)]} for n,lo,hi in roomdefs],'portais':len(portals),'mobiliario':'Sem mobiliário inventado; gabinete de incêndio e extintor simplificados','limites':'Exterior e face oposta estimados; portas laterais fechadas sem salas inventadas; murais reconstruídos da referência.'}
(P/'relatorios/geometria.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
# Save/export using real GTA materials and room data, before adding preview-only sun/camera.
for image in bpy.data.images:
 if image.source=='FILE':image.pack()
CC.hide_render=True;HC.hide_render=True
bpy.ops.object.select_all(action='DESELECT')
for ob in list(C.objects)+list(CC.objects):ob.select_set(True)
res=bpy.ops.sollumz.export_assets(directory=str(P/'xml'),direct_export=True,use_custom_settings=True,target_formats={'CWXML'},target_versions={'GEN8'},limit_to_selected=True,export_ytyps=True,export_ytyps_include='ALL',export_ymaps=False,export_ytds=False)
print('EXPORT_RESULT',res);assert res=={'FINISHED'}
# World and cameras; source geometry/material properties remain exportable.
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.61,.68,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
ld=bpy.data.lights.new('ga_sol_preview','SUN');ld.energy=2.6;sun=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(sun);sun.rotation_euler=(.55,-.3,-.4)
for name,loc,target,lens in [('frente',(27,-36,18),(0,13,5),40),('perspectiva',(-34,-30,25),(0,15,5),40),('interior',(-9,1.5,1.7),(7.5,23,4.7),17),('mezanino',(10.1,13,5.1),(-4,23,4.2),24)]:
 d=bpy.data.cameras.new('ga_camera_'+name);cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
s.camera=bpy.data.objects['ga_camera_interior'];s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=960;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(P/'blender/galpao_anexo_master.blend'),compress=True)
for name in ([] if os.getenv('VANO_SKIP_RENDERS')=='1' else ['frente','perspectiva','interior','mezanino']):
 s.camera=bpy.data.objects['ga_camera_'+name];s.render.filepath=str(P/'previews'/('ga_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('GEOMETRIA',json.dumps(report))
