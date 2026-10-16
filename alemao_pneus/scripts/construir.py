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
s=bpy.context.scene;s.name='alemao_pneus';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
for y in list(s.ytyps):s.ytyps.remove(0)
C=bpy.data.collections.new('ap_arquitetura');s.collection.children.link(C)
CC=bpy.data.collections.new('ap_colisao');s.collection.children.link(CC)
HC=bpy.data.collections.new('ap_mlo_guias');s.collection.children.link(HC)
HC.hide_render=True
mats={}
for p in sorted((P/'texturas').glob('*.dds')):
 m=create_shader('default.sps');m.name=p.stem;im=bpy.data.images.load(str(p),check_existing=True);m.node_tree.nodes['DiffuseSampler'].image=im;m.node_tree.nodes['DiffuseSampler'].texture_properties.embedded=False;mats[p.stem.removeprefix('ap_')]=m
# Geometry is partitioned into real MLO room entities, not one visible shell called an interior.
G={n:[] for n in ['exterior','oficina']};COL=[];group='exterior'
roomid={'exterior':0,'oficina':1}
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
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=move(bpy.context.object);ob.name='ap_'+name;ob.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(mats[mat]);uv_planar(ob,period)
 if collide:collision_box(loc,dims,roomid[group],1 if mat not in ['metal','cromado'] else 55)
 return ob
def beam(name,a,b,width,mat):
 a,b=Vector(a),Vector(b);ob=box(name,(a+b)/2,(width,width,(b-a).length),mat);ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob
def plane(name,verts,mat,period=1.2,uv=None):
 me=bpy.data.meshes.new('ap_'+name);me.from_pydata(verts,[],[(0,1,2,3)]);me.update();ob=bpy.data.objects.new('ap_'+name,me);C.objects.link(ob);G[group].append(ob);me.materials.append(mats[mat]);uv_planar(ob,period)
 if uv:
  for i,co in enumerate(uv):me.uv_layers[0].data[i].uv=co
 return ob
def floor(x0,x1,y0,y1,mat='concreto'):
 return box('piso_'+group,((x0+x1)/2,(y0+y1)/2,-.09),(x1-x0,y1-y0,.18),mat,True)
def ceiling(x0,x1,y0,y1):
 return box('forro_'+group,((x0+x1)/2,(y0+y1)/2,3.16),(x1-x0,y1-y0,.12),'branco',True)
def wall_x(name,x,y0,y1,z0=0,z1=3.22,mat='vermelho',thick=.2):
 return box(name,(x,(y0+y1)/2,(z0+z1)/2),(thick,y1-y0,z1-z0),mat,True)
def wall_y(name,y,x0,x1,z0=0,z1=3.22,mat='vermelho',thick=.2):
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

# Editable dimensions in metres, estimated from the three reference views.
WIDTH=7.2;DEPTH=18.0;EAVE=5.4
# Repeated objects use 12/16 radial segments; stock rims have open spokes.
def cylinder(name,loc,radius,depth,mat,axis='Y',segments=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=radius,depth=depth,location=loc,rotation=(math.pi/2,0,0) if axis=='Y' else (0,math.pi/2,0) if axis=='X' else (0,0,0));ob=move(bpy.context.object);ob.name='ap_'+name;ob.data.materials.append(mats[mat]);uv_planar(ob);return ob
def ring(name,loc,outer,inner,depth,mat,segments=16):
 vs=[];fs=[]
 for y,r in [(-depth/2,outer),(depth/2,outer),(-depth/2,inner),(depth/2,inner)]:
  for i in range(segments):
   a=i*2*math.pi/segments;vs.append((loc[0]+r*math.cos(a),loc[1]+y,loc[2]+r*math.sin(a)))
 for i in range(segments):
  j=(i+1)%segments
  fs.extend([(i,j,segments+j,segments+i),(2*segments+j,2*segments+i,3*segments+i,3*segments+j),(i,2*segments+i,2*segments+j,j),(segments+j,3*segments+j,3*segments+i,segments+i)])
 me=bpy.data.meshes.new('ap_'+name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(me.name,me);C.objects.link(ob);G[group].append(ob);me.materials.append(mats[mat]);uv_planar(ob);return ob
def rim(loc,r=.29,style=0):
 ring('aro_expositor',loc,r,r*.79,.14,'cromado',12)
 cylinder('cubo_roda',loc,r*.18,.16,'cromado',segments=8)
 n=[5,6,8][style%3]
 for k in range(n):
  a=k*2*math.pi/n;beam('raio_roda',Vector(loc)+Vector((r*.12*math.cos(a),-.005,r*.12*math.sin(a))),Vector(loc)+Vector((r*.82*math.cos(a),-.005,r*.82*math.sin(a))),.027,'cromado')
def decal(name,verts,mat):return plane(name,verts,mat,uv=[(0,0),(1,0),(1,1),(0,1)])
# Main footprint, driveway and exposed red portal frame.
group='exterior'
floor(-8.8,3.9,-3.2,.42)
for x in [-3.6,3.6]:box('pilar_fachada',(x,.22,2.75),(.25,.5,5.5),'vermelho',True)
box('viga_vermelha_fachada',(0,.22,4.65),(7.25,.45,.23),'vermelho',True)
box('verga_portao',(0,.22,4.05),(7.05,.40,.20),'metal',True)
box('base_pilar_direito',(3.62,.10,.45),(.4,.6,.9),'preto',True)
# Shallow entrance canopy and rusty tracks.
for y in [-.48,.3]:box('perfil_marq',(0,y,4.12),(7.4,.10,.10),'metal')
box('marquise',(0,-.07,4.20),(7.4,.9,.06),'telha')
for x in [-3.6,3.6]:beam('mao_francesa',(x,.35,3.75),(x,-.5,4.14),.06,'metal')
# Upper grille runs across front; central red sign hides part of it.
for z in [4.55,5.65]:box('grade_superior_trilho',(0,.28,z),(7.2,.05,.05),'metal')
for i in range(49):box('grade_superior_barra',(-3.56+i*7.12/48,.28,5.1),(.022,.035,1.1),'metal')
box('placa_principal_fundo',(0,.12,5.52),(4.7,.10,1.30),'vermelho')
decal('placa_principal_sem_telefone',[(-2.35,.061,4.87),(2.35,.061,4.87),(2.35,.061,6.17),(-2.35,.061,6.17)],'placa_sem_telefone')
# Left gate: open leaf with rim display and second advertising board.
A=Vector((-3.6,-.05,0));B=Vector((-5.05,-2.60,0));u=(B-A).normalized();normal=Vector((u.y,-u.x,0));length=(B-A).length
for z in [.1,2.6,3.0,4.25]:beam('portao_expositor_trilho',A+Vector((0,0,z)),B+Vector((0,0,z)),.06,'vermelho')
for t in [0,1]:beam('portao_expositor_montante',A.lerp(B,t),A.lerp(B,t)+Vector((0,0,4.3)),.075,'vermelho')
# Independent rims retain physically open spokes; faces point toward sidewalk.
for row in range(4):
 for col in range(4):
  pos=A.lerp(B,(col+.5)/4)+normal*.11+Vector((0,0,.42+row*.62))
  before=set(G[group]);rim(pos,.275,row+col)
  # Rotate the wheel assemblies around their center to align with the leaf.
  ang=math.atan2(-u.y,-u.x)
  for ob in set(G[group])-before:
   R=Matrix.Rotation(ang,4,'Z');ob.matrix_world=Matrix.Translation(pos)@R@Matrix.Translation(-pos)@ob.matrix_world
corners=[A+normal*.06+Vector((0,0,3.0)),B+normal*.06+Vector((0,0,3.0)),B+normal*.06+Vector((0,0,4.2)),A+normal*.06+Vector((0,0,4.2))]
corners=[corners[1],corners[0],corners[3],corners[2]]
decal('placa_portao_sem_telefone',corners,'placa_sem_telefone')
# Collision proxy follows the open leaf, never covers the entrance.
# Axis-aligned small sections approximate the slanted display with cheap boxes.
for i in range(12):
 q=A.lerp(B,(i+.5)/12);collision_box((q.x,q.y,1.3),(.20,.25,2.6),0,55)
# Right pavement stack and low wheel rack, evident in both close reference views.
for z in [.16,.46,.76,1.06]:
 ob=ring('pneu_empilhado',(3.95,-.15,z),.38,.20,.28,'borracha',16);center=Vector((3.95,-.15,z));ob.matrix_world=Matrix.Translation(center)@Matrix.Rotation(math.pi/2,4,'X')@Matrix.Translation(-center)@ob.matrix_world
box('expositor_direito_base',(4.12,-.40,.10),(.75,.5,.12),'metal',True)
for x in [3.83,4.40]:box('expositor_direito_montante',(x,-.22,.68),(.035,.04,1.3),'metal')
rim((4.10,-.48,.84),.31,0)
# Side parking enclosure and long corrugated side wall, without neighbours/cars/utility wires.
box('muro_patio_esquerdo',(-8.75,4.0,.55),(.15,8,1.1),'branco',True)
box('mureta_portao_patio',(-6.20,.15,.40),(4.9,.15,.8),'branco',True)
for x in [-8.65,-3.88]:box('pilar_cerca_patio',(x,.12,1.25),(.16,.16,2.5),'branco',True)
for z in [.85,2.35]:box('cerca_patio_travessa',(-6.25,.13,z),(4.6,.035,.035),'metal')
for i in range(30):box('cerca_patio_barra',(-8.5+i*.155,.13,1.6),(.018,.018,1.5),'metal')
collision_box((-6.25,.13,1.6),(4.6,.05,1.5),0,55)
floor(-8.7,-3.73,.25,8)
# Exterior shell; interior stays a single confirmed open workshop, no invented rooms.
wall_x('parede_lateral_esquerda',-3.63,.4,18,0,5.35,'branco',.18)
wall_x('parede_lateral_direita',3.63,.4,18,0,5.35,'preto',.18)
wall_y('fundos_estimados',18,-3.63,3.63,0,5.35,'branco',.18)
for i in range(90):box('nervura_chapa_lateral',(-3.735,.45+i*.195,3.65),(.035,.028,3.3),'telha')
# Shallow pitched corrugated roof, estimated from side view.
for side in [-1,1]:
 for i in range(24):
  x=side*(i+.5)*3.85/24;z=5.52+(3.85-abs(x))*.22
  ob=box('telha_cobertura',(x,9.4,z),(3.85/24+.005,17.9,.055),'telha');ob.rotation_euler.y=side*.216
box('cumeeira',(0,9.4,6.39),(.17,18.0,.07),'telha')
collision_box((0,9.1,5.60),(7.7,18.5,.10),0,1)
# Workshop interior and visible fixtures.
group='oficina';floor(-3.53,3.53,.42,17.9)
for x in [-3.526,3.526]:
 lining_x(x,.45,17.9,0,2.15,'branco',1 if x<0 else -1);lining_x(x,.45,17.9,2.15,5.25,'preto',1 if x<0 else -1)
for y in [1.0,4.5,8.0,11.5,15.0,17.7]:
 beam('tesoura_horizontal',(-3.5,y,5.22),(3.5,y,5.22),.055,'metal')
 beam('tesoura_agua_esq',(-3.5,y,5.22),(0,y,6.18),.055,'metal');beam('tesoura_agua_dir',(0,y,6.18),(3.5,y,5.22),.055,'metal')
 for x in [-2.0,0,2.0]:box('luminaria_regua',(x,y,5.12),(1.20,.12,.05),'branco')
# Wall-mounted stock: only along the left edge, leaving vehicle circulation clear.
for y in [1.5,3,4.5,6,7.5]:
 for z in [2.7,3.45,4.2]:
  pos=Vector((-3.30,y,z));before=set(G[group]);rim(pos,.28,int(y+z)%3)
  for ob in set(G[group])-before:ob.matrix_world=Matrix.Translation(pos)@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation(-pos)@ob.matrix_world
for y in [1.3,4.2,7.3]:box('suporte_rodas_parede',(-3.40,y,3.5),(.05,.05,2.2),'metal')
# Lean ladder, red equipment and dark service counter visible behind the entrance.
for y in [2.0,2.52]:beam('escada_longarina',(-2.95,y,0),(-3.15,y,3.4),.045,'cromado')
for j in range(12):beam('escada_degrau',(-2.95-.20*j/11,2.0,j*3.4/11),(-2.95-.20*j/11,2.52,j*3.4/11),.035,'cromado')
box('maquina_balanceadora',(-2.75,5.4,.56),(1.05,.75,1.12),'vermelho',True)
box('painel_balanceadora',(-2.75,5.65,1.30),(.60,.10,.35),'preto')
box('bancada_servico',(-2.78,8,.55),(1.10,2,.96),'vermelho',True);box('tampo_bancada',(-2.78,8,1.08),(1.20,2.1,.10),'metal')
for z in [.25,.48,.71]:box('gaveta_bancada',(-2.17,8,z),(.02,1.8,.16),'preto')
cylinder('reservatorio_compressor',(-2.65,3.50,.65),.24,1.28,'vermelho','Z',12)
# Rear lift (partly visible silhouette); no invented bathroom/office or unverified vehicle.
for x in [-1.45,1.45]:
 box('coluna_elevador',(x,13,1.8),(.28,.35,3.6),'vermelho',True)
 box('base_elevador',(x,13,.04),(.65,.70,.08),'metal',True)
 beam('braco_elevador',(x,13,1.6),(x*.3,12.4,1.6),.10,'metal')
# Two cloth references hanging just behind the entrance.
for x,mat in [(-.85,'bandeira_brasil'),(.90,'bandeira_rs_estudo')]:
 decal('bandeira_'+mat,[(x-.65,2.7,3.25),(x+.65,2.7,3.25),(x+.65,2.7,4.6),(x-.65,2.7,4.6)],mat)
 beam('haste_bandeira',(x-.7,2.73,4.62),(x+.7,2.73,4.62),.02,'metal')
# Preserve all components individually in a dedicated source collection before export joins.
editable=bpy.data.collections.new('EDITAVEIS_pecas_individuais');s.collection.children.link(editable)
for obs in G.values():
 for ob in obs:
  dup=ob.copy();dup.data=ob.data.copy();editable.objects.link(dup);dup.name=ob.name+'_editavel';dup['origem']='Componente fonte independente; alterar e regenerar exportações pelo script.'
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
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='ap_'+g+'.model';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 root=bpy.data.objects.new('ap_'+g,None);root.sollum_type=SollumType.DRAWABLE;C.objects.link(root);ob.parent=root;ob.sollum_type=SollumType.DRAWABLE_MODEL;ob.sz_lods.high.mesh=ob.data;ob.sz_lods.active_lod_level=LODLevel.HIGH
 for name in ['Color 1','Color 2']:
  attr=ob.data.color_attributes.new(name=name,type='BYTE_COLOR',domain='CORNER')
  for d in attr.data:d.color_srgb=(1,1,1,1)
 root.drawable_properties.lod_dist_high=180;root.drawable_properties.lod_dist_med=220;root.drawable_properties.lod_dist_low=260;root.drawable_properties.lod_dist_vlow=300;roots[g]=root;counts[g]=sum(len(p.vertices)-2 for p in ob.data.polygons)
# Genuine BVH collision with room-coded materials, simplified cage panels and clear door openings.
colroot=bpy.data.objects.new('ap_mlo',None);colroot.sollum_type=SollumType.BOUND_COMPOSITE;CC.objects.link(colroot)
bvh=bpy.data.objects.new('ap_mlo_bvh',None);bvh.sollum_type=SollumType.BOUND_GEOMETRYBVH;CC.objects.link(bvh);bvh.parent=colroot
for prop in ['map_dynamic','map_cover','map_vehicle']:setattr(bvh.composite_flags1,prop,True)
for prop in ['map_weapon','map_dynamic','map_animal','map_cover','map_vehicle','ped','ragdoll','animal','animal_ragdoll','object','plant','projectile','explosion','test_weapon','test_camera','test_ai','test_script','test_vehicle_wheel']:setattr(bvh.composite_flags2,prop,True)
verts=[];faces=[];inds=[];cmats={}
for v,f,r,material in COL:
 key=(r,material)
 if key not in cmats:
  cm=create_collision_material_from_index(material);cm.name=f'ap_col_room_{r}_mat_{material}';cm.collision_properties.room_id=r
  if material==55:cm.collision_flags.see_through=True;cm.collision_flags.shoot_through=True
  cmats[key]=cm
 off=len(verts);verts.extend(v);faces.extend([tuple(i+off for i in face) for face in f]);inds.extend([list(cmats).index(key)]*len(f))
mesh=bpy.data.meshes.new('ap_colisao_malha');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(mesh.name,mesh);CC.objects.link(ob);ob.parent=bvh;ob.sollum_type=SollumType.BOUND_POLY_TRIANGLE
for m in cmats.values():mesh.materials.append(m)
for f,idx in zip(mesh.polygons,inds):f.material_index=idx
ob.hide_render=True;ob.display_type='WIRE';bvh.hide_render=True;colroot.hide_render=True
# MLO rooms and portals registered in Blender's actual Sollumz YTYP data.
ytyp=s.ytyps.add();ytyp.name='ap_arquetipos';s.ytyp_index=0
for g,root in roots.items():
 a=ytyp.new_archetype(ArchetypeType.BASE);a.asset=root;a.name=root.name;a.texture_dictionary='ap_texturas';a.flags.total='32';a.lod_dist=180
mlo=ytyp.new_archetype(ArchetypeType.MLO);mlo.asset=colroot;mlo.name='ap_mlo';mlo.asset_name='ap_mlo';mlo.lod_dist=180;mlo.flags.total='0';mlo.mlo_flags.total='0'
roomdefs=[('limbo',(-9,-3.4,-.3),(4.6,18.6,6.7)),('oficina',(-3.53,.42,0),(3.53,17.9,6.4))]
rooms=[]
for name,mi,ma in roomdefs:
 r=mlo.new_room();r.name=name;r.bb_min=mi;r.bb_max=ma;r.timecycle='';r.secondary_timecycle='';r.floor_id=0;r.exterior_visibility_depth=3;r.flags.total='0';rooms.append(r)
# Portal normals point from source room to destination room.
portals=[(0,1,[(-3.45,.42,0),(-3.45,.42,3.94),(3.45,.42,3.94),(3.45,.42,0)])]
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
 me=bpy.data.meshes.new('ap_portal');me.from_pydata(corners,[],[(0,1,2,3)]);helper=bpy.data.objects.new(f'ap_portal_{rf}_{rt}',me);HC.objects.link(helper);helper.display_type='WIRE';helper.hide_render=True
for g,root in roots.items():
 ent=mlo.new_entity();ent.archetype_name=root.name;ent.linked_object=root;ent.attached_room_id=str(rooms[roomid[g]].id);ent.flags.total='32';ent.lod_dist=180
# Real light instances inside room drawables, not just preview-only illumination.
for g,loc,energy in [('oficina',(x,y,4.9),80) for x in [-1.8,1.8] for y in [3,8,13,16.5]]:
 d=bpy.data.lights.new('ap_luz_'+g,'POINT');d.sollum_type=LightType.POINT;d.energy=energy;d.color=(1,.86,.70);d.shadow_soft_size=.12;d.time_flags.total=str((1<<24)-1);d.light_properties.falloff=6 if g in ['banheiro','deposito'] else 8;d.light_flags.cast_shadows=True
 if g=='exterior':d.light_flags.exterior_only=True
 else:d.light_flags.interior_only=True
 light=bpy.data.objects.new(d.name,d);C.objects.link(light);light.parent=roots[g];light.location=loc
# Measured dimensions from actual vertices; floor and door clearances are recorded separately.
bpy.context.view_layer.update();pts=[o.matrix_world@v.co for root in roots.values() for o in root.children if o.type=='MESH' for v in o.data.vertices];mi=[min(p[i] for p in pts) for i in range(3)];ma=[max(p[i] for p in pts) for i in range(3)]
report={'min':mi,'max':ma,'dimensoes':[ma[i]-mi[i] for i in range(3)],'area_envelope':(ma[0]-mi[0])*(ma[1]-mi[1]),'pe_direito':5.35,'triangulos_por_entidade':counts,'triangulos_colisao':sum(len(f)-2 for f in faces),'salas':[{'nome':n,'min':lo,'max':hi,'dimensoes':[hi[i]-lo[i] for i in range(3)]} for n,lo,hi in roomdefs],'portais':len(portals),'mobiliario':'Expositores, rodas, pneus, escada, bancada e equipamentos aproximados das fotos','portao':'Folha expositora esquerda aberta; passagem de veículos livre','textura_placa':'Redesenho vetorial aproximado das fotos; nenhum telefone.'}
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
ld=bpy.data.lights.new('ap_sol_preview','SUN');ld.energy=2.6;sun=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(sun);sun.rotation_euler=(.55,-.3,-.4)
for name,loc,target,lens in [('frente',(0,-19,6.2),(-.6,3,2.7),39),('perspectiva',(-17,-20,11),(-1.6,6,2.8),42),('interior',(1,1.0,1.75),(-.4,10,2.4),20)]:
 d=bpy.data.cameras.new('ap_camera_'+name);cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens
s.camera=bpy.data.objects['ap_camera_frente'];s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(P/'blender/alemao_pneus_master.blend'),compress=True)
for name in ([] if os.getenv('VANO_SKIP_RENDERS')=='1' else ['frente','perspectiva','interior']):
 s.camera=bpy.data.objects['ap_camera_'+name];s.render.filepath=str(P/'previews'/('ap_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('GEOMETRIA',json.dumps(report))
