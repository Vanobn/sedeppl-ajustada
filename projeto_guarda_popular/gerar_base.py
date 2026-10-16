import bpy, math, json
from pathlib import Path
from mathutils import Vector
import xml.etree.ElementTree as ET
O=Path('/workspace/projeto-guarda-popular'); R=Path('/workspace/sedeppl-ajustada/stream/gen8')
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1
collections={}
for n in ['Terreno','Fachada','Boteco','Galpao','Oficina','Muros','Portao','Reuso','Mobiliario','Iluminacao']:
 c=bpy.data.collections.new(n); s.collection.children.link(c); collections[n]=c
current='Terreno'
def move(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 collections[current].objects.link(o); return o
def mat(n,col,metal=0,rough=.5):
 m=bpy.data.materials.new(n); m.diffuse_color=(*col,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*col,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough;return m
red=mat('Vermelho GP',(0.48,.018,.025)); white=mat('Branco quente',(.8,.78,.72)); steel=mat('Metal grafite',(.055,.065,.07),.8); concrete=mat('Concreto',(.28,.29,.28)); roof=mat('Cobertura zincada',(.35,.39,.4),.65); glass=mat('Vidro estudo — shader GTA pendente',(.035,.12,.15),.5,.12); wood=mat('Madeira',(.24,.1,.035)); black=mat('Borracha',(.018,.018,.02))
def box(n,loc,dim,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=move(bpy.context.object);o.name=n;o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bevel: mod=o.modifiers.new('Arestas','BEVEL');mod.width=bevel;mod.segments=2;o.modifiers.new('Normais','WEIGHTED_NORMAL')
 return o
def cyl(n,loc,r,depth,m,vertices=12):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=move(bpy.context.object);o.name=n;o.data.materials.append(m);return o
def beam(n,a,b,width,m):
 a,b=Vector(a),Vector(b);o=box(n,(a+b)/2,(width,width,(b-a).length),m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def text(n,body,loc,size,m):
 bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0));o=move(bpy.context.object);o.name=n;o.data.body=body;o.data.align_x='CENTER';o.data.size=size;o.data.extrude=.008;o.data.materials.append(m);return o
box('Perimetro ocupado 58 x 60', (0,30,-.15),(58,60,.3),concrete)
# Lower two-storey reception, real window openings assembled from piers/spandrels.
current='Fachada'
box('Laje terreo',(-21,15,.12),(13,14,.24),white)
for z in [3.6,7.2]:box('Laje pavimento',(-21,15,z),(13.4,14.4,.22),white)
box('Parede fundos',(-21,21.8,3.6),(13,.25,7.2),red)
for x in [-27.4,-14.6]:box('Parede lateral',(x,15,3.6),(.25,14,7.2),red)
for z in [0.6,3.9,6.9]:box('Faixa fachada',(-21,8.1,z),(13,.3,1.1 if z<6 else .6),red)
for x in [-27.25,-23,-19,-14.75]:box('Pilar fachada',(x,8.1,3.6),(.5,.4,7.2),red)
for x in [-25.2,-21,-16.8]:
 for z in [2.1,5.4]:
  box('Caixilho',(x,8.08,z),(3.4,.16,2.1),steel)
  box('Vidro',(x,7.97,z),(3.15,.04,1.85),glass)
  box('Montante',(x,7.92,z),(.06,.07,1.85),white)
box('Marquise entrada',(-21,6.9,3.3),(7,2.6,.18),steel)
text('Identificacao','GUARDA POPULAR',(-21,7.85,6.6),.65,white)
text('Identificacao 1909','DEZENOVE ZERO NOVE',(-21,7.82,3.8),.43,white)
# stair for access to upper level, conceptual interior
for i in range(20):box('Escada',(-25,19-i*.28,.09+i*.18),(1.4,.29,.18+i*.36),concrete)
current='Boteco'
box('Piso boteco',(-21,37,.12),(13,28,.24),white)
box('Fundo boteco',(-27.25,37,2.1),(.3,28,4.2),red)
box('Cobertura boteco',(-21,37,4.4),(13.5,28,.22),roof)
for y in [24,32,40,50]:box('Pilar boteco',(-14.7,y,2.15),(.22,.22,4.3),red)
box('Balcao base',(-24.5,38,.55),(1.2,15,1.1),red);box('Balcao tampo',(-24.5,38,1.15),(1.5,15,.12),steel)
box('Testeira',(-14.55,37,3.7),(.18,26,.9),red)
text('Boteco placa','BOTECO COLORADO',(-21,23.65,3.6),.65,white)
# main shed low-pitch roof, sparse structural trusses
current='Galpao'
for y in [25,33,41,49,57]:
 for x in [-13.5,26]:box('Pilar metalico',(x,y,4.2),(.3,.3,8.4),red)
 for a,b in [((-13.5,y,8.4),(6.25,y,10)),((6.25,y,10),(26,y,8.4)),((-13.5,y,8.1),(26,y,8.1))]:beam('Banzo trelica',a,b,.17,steel)
 for j in range(8):
  x=-13.5+j*4.9375; z=10-abs(x+2.46875-6.25)*1.6/19.75
  beam('Diagonal trelica',(x,y,8.1),(x+2.46875,y,z),.075,red)
for x in [-13.5,-5,6.25,17.5,26]:beam('Terca',(x,24,10-abs(x-6.25)*1.6/19.75),(x,58,10-abs(x-6.25)*1.6/19.75),.12,steel)
for x1,x2 in [(-14,6.25),(6.25,26.5)]:
 z1=10.1-abs(x1-6.25)*1.6/19.75;z2=10.1-abs(x2-6.25)*1.6/19.75
 o=box('Agua cobertura',((x1+x2)/2,41,(z1+z2)/2),(((x2-x1)**2+(z2-z1)**2)**.5,34,.14),roof);o.rotation_euler[1]=-math.atan2(z2-z1,x2-x1)
box('Fundo galpao',(6,58,4),(40,.22,8),red)
text('Mural tipografico','GUARDA POPULAR',(4,57.83,5.6),1.4,white)
text('Mural subtitulo','POVO • RUA • ARQUIBANCADA',(4,57.82,4),.55,white)
current='Oficina'
box('Piso oficina',(20,45,.15),(11,22,.3),concrete)
box('Parede oficina',(25.8,45,2.5),(.2,22,5),white)
box('Testeira oficina',(20,34,4.8),(11,.25,1.1),red);text('Placa oficina','OFICINA / GARAGEM',(20,33.8,4.6),.55,white)
for x in [16,23]:
 box('Coluna elevador',(x,45,1.6),(.4,.5,3.2),red)
 box('Braco elevador',(x-1 if x>20 else x+1,45,.4),(2,.2,.18),steel)
for y in [49,52,55]:
 box('Bancada oficina',(24.5,y,.95),(1.7,2,.14),steel)
 for z in [.5,1.4]:cyl('Pneu',(24,y,z),.38,.24,black,16)
current='Mobiliario'
for y in [27,32,37,42,47]:
 cyl('Mesa',(-18,y,.8),.65,.1,wood,16)
 for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
  box('Assento',(-18+dx,y+dy,.45),(.44,.44,.08),red)
  for ox in [-.17,.17]:beam('Pe cadeira',(-18+dx+ox,y+dy,.05),(-18+dx+ox,y+dy,.45),.035,steel)
current='Terreno'
for y in [20,26,32]:
 for x in [17,22]:box('Vaga demarcacao',(x,y,.012),(.1,5,.024),white)
 box('Vaga fundo',(19.5,y+2.5,.012),(5,.1,.024),white)
# perimeter low curved front, single 14m gate
current='Muros'
for x in [-28.8,28.8]:box('Muro lateral',(x,30,1.5),(.4,60,3),white)
box('Muro fundos',(0,59.8,1.5),(58,.4,3),white)
for side in [-1,1]:
 pts=[]
 for i in range(25):
  t=i/24;pts.append((side*(7.3+21.4*t),.5+3*(1-t)**2))
 for a,b in zip(pts,pts[1:]):
  # curved masonry segments, joined visual appearance
  o=box('Muro frontal curvo',((a[0]+b[0])/2,(a[1]+b[1])/2,.65),((Vector(a)-Vector(b)).length+.02,.28,1.3),red);o.rotation_euler.z=math.atan2(b[1]-a[1],b[0]-a[0])
  for x,y in [a]:beam('Grade vertical',(x,y,1.3),(x,y,2.15),.035,steel)
 for z in [1.4,2.15]:
  for a,b in zip(pts,pts[1:]):beam('Corrimao grade',(a[0],a[1],z),(b[0],b[1],z),.045,steel)
current='Portao'
for x in [-7.15,7.15]:box('Pilar entrada',(x,3.5,1.45),(.5,.5,2.9),white)
gate=box('Portao deslizante — animacao estudo',(0,3.5,1.2),(13.8,.14,2.4),steel)
# slide two leaves inward sideways; only conceptual not a FiveM controller
for frame,x in [(1,0),(100,14)]:gate.location.x=x;gate.keyframe_insert(data_path='location',frame=frame)
s.frame_set(1)
box('Painel portao',(0,3.39,1.2),(8,.05,1.3),red);text('Placa portao','ALENTO',(0,3.34,.95),.7,white)
# reuse original wall geometry with original UVs and image materials
current='Reuso'
xml=ET.parse(R/'vano_muro1909_ext.model.ydr.xml').getroot()
original=[]
for i,tex in enumerate(['txtvermelha','enferrujadonexus']):
 m=mat('ORIGINAL '+tex,(.5,.1,.1));nodes=m.node_tree.nodes;img=nodes.new('ShaderNodeTexImage');img.image=bpy.data.images.load(str(R/'vano_muro1909_ext.model'/(tex+'.dds')));m.node_tree.links.new(img.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color']);original.append(m)
for g in xml.findall('.//Geometries/Item'):
 rows=[list(map(float,l.split())) for l in g.findtext('VertexBuffer/Data').splitlines() if l.strip()];ix=list(map(int,g.findtext('IndexBuffer/Data').split()));v=[r[:3] for r in rows];faces=[ix[k:k+3] for k in range(0,len(ix),3)]
 mesh=bpy.data.meshes.new('Malha original muro');mesh.from_pydata(v,[],faces);mesh.update();ob=bpy.data.objects.new('REUSO vano muro XML',mesh);collections[current].objects.link(ob);ob.location=(0,86.5,.015);ob.data.materials.append(original[int(g.find('ShaderIndex').get('value'))]);uv=mesh.uv_layers.new()
 for poly in mesh.polygons:
  for li in poly.loop_indices:
   r=rows[mesh.loops[li].vertex_index];uv.data[li].uv=(r[-2],1-r[-1])
 ob['origem']='stream/gen8/vano_muro1909_ext.model.ydr.xml';ob['alteracao']='Translacao apenas, malha e UV preservadas'
current='Iluminacao'
for x in [-5,8,20]:
 for y in [29,41,53]:
  cyl('Pendente',(x,y,7.4),.3,.18,steel,12);beam('Cabo',(x,y,7.5),(x,y,8.2),.025,black)
  ld=bpy.data.lights.new('Luz pendente estudo','POINT');ld.energy=180;ld.color=(1,.68,.4);ob=bpy.data.objects.new('Luz pendente',ld);collections[current].objects.link(ob);ob.location=(x,y,7.1)
# metrics from world-space evaluated geometry, closed gate frame 1
s.frame_set(1);s.view_layers.update() if hasattr(s,'view_layers') and hasattr(s.view_layers,'update') else None
report={};allpoints=[];tri=0
for name,c in collections.items():
 pts=[]
 for o in c.objects:
  if o.type!='MESH':continue
  pts.extend([o.matrix_world@Vector(v) for v in o.bound_box]);tri+=sum(len(p.vertices)-2 for p in o.data.polygons)
 if pts:
  mi=[min(p[i] for p in pts) for i in range(3)];ma=[max(p[i] for p in pts) for i in range(3)];report[name]={'min':mi,'max':ma,'dimensoes':[ma[i]-mi[i] for i in range(3)]};allpoints+=pts
mi=[min(p[i] for p in allpoints) for i in range(3)];ma=[max(p[i] for p in allpoints) for i in range(3)]
area=(ma[0]-mi[0])*(ma[1]-mi[1]);report['total']={'largura':ma[0]-mi[0],'comprimento':ma[1]-mi[1],'area_envelope':area,'altura_acima_piso':ma[2],'margem_area':3500-area,'margem_altura':15-ma[2],'altura_muros':report['Muros']['max'][2],'margem_muros':8.6-report['Muros']['max'][2],'triangulos_base':tri}
assert area<=3500 and ma[2]<=15 and report['Muros']['max'][2]<=8.6
(O/'medidas.json').write_text(json.dumps(report,indent=2))
# prefix and pack source textures
for datablocks in [bpy.data.objects,bpy.data.collections,bpy.data.meshes,bpy.data.materials]:
 for block in datablocks:
  if not block.name.startswith('vano_'):block.name='vano_'+block.name
bpy.ops.file.pack_all()
# presentation
world=s.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.27,.34,.43,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5
ld=bpy.data.lights.new('Sol','SUN');ob=bpy.data.objects.new('Sol',ld);s.collection.objects.link(ob);ob.rotation_euler=(math.radians(28),math.radians(-25),math.radians(-30));ld.energy=3
bpy.ops.object.camera_add(location=(82,-96,76));cam=bpy.context.object;cam.name='Camera perspectiva';cam.rotation_euler=(Vector((0,30,2))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=101;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False;s.render.resolution_x=1500;s.render.resolution_y=1200;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(O/'vano_implantacao_base.blend'))
