import bpy,sys,math,json,bmesh,addon_utils
from pathlib import Path
from mathutils import Vector,Matrix
sys.path[:0]=['/workspace/tools','/workspace/tools/pydeps'];addon_utils.enable('Sollumz',default_set=True,persistent=True)
P=Path('/workspace/projeto-guarda-popular')
bpy.ops.wm.open_mainfile(filepath=str(P/'vano_implantacao_base.blend'));s=bpy.context.scene;s.name='vano_PROJETO'
with bpy.data.libraries.load(str(P/'vano_biblioteca_originais.blend'),link=False) as (src,dst):dst.scenes=src.scenes
# originals remain in their separate source scene, hidden in source collections
source_scene=next(x for x in bpy.data.scenes if x!=s and x.name.startswith('vano_BIBLIOTECA'))
for cn in ['vano_Fachada','vano_Boteco']:
 c=bpy.data.collections.get(cn)
 if c:
  for ob in list(c.objects):bpy.data.objects.remove(ob,do_unlink=True)
# remove generic gate, retain entrance pillars only
for ob in list(bpy.data.collections['vano_Portao'].objects):
 if 'Pilar entrada' not in ob.name:bpy.data.objects.remove(ob,do_unlink=True)
# retain fixtures but replace generic workshop shell
for ob in list(bpy.data.collections['vano_Oficina'].objects):
 if any(k in ob.name for k in ['Parede oficina']):bpy.data.objects.remove(ob,do_unlink=True)
current=bpy.data.collections['vano_Reuso'];preview={};reused=[]
red=bpy.data.materials['vano_Vermelho GP'];white=bpy.data.materials['vano_Branco quente'];steel=bpy.data.materials['vano_Metal grafite'];roof=bpy.data.materials['vano_Cobertura zincada'];glass=bpy.data.materials['vano_Vidro estudo — shader GTA pendente'];concrete=bpy.data.materials['vano_Concreto'];wood=bpy.data.materials['vano_Madeira']
def preview_material(m,tint=False,asset=None):
 key=m.name+str(tint)+str(asset)
 if key in preview:return preview[key]
 pm=bpy.data.materials.new('vano_visual_'+m.name);pm.use_nodes=True;bs=pm.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.7
 img=next((n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.name=='DiffuseSampler' and n.image),None)
 if img and asset:
  folder=P/'convertidos'/'texturas_por_asset'/(asset+'.ydr')
  candidates=list(folder.glob('*.dds'))
  local=next((p for p in candidates if p.stem==img.name),None)
  if local is None:
   matches=[p for p in candidates if p.stem.lower()==img.name.lower()]
   if len(matches)==1:local=matches[0]
  if local:img=bpy.data.images.load(str(local),check_existing=True)
 if img and img.source=='FILE':
  tex=pm.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img
  if tint:
   mix=pm.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.78;mix.inputs[2].default_value=(.55,.018,.025,1);pm.node_tree.links.new(tex.outputs['Color'],mix.inputs[1]);pm.node_tree.links.new(mix.outputs[0],bs.inputs['Base Color'])
  else:pm.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
  if 'decal' in m.shader_properties.filename:
   pm.node_tree.links.new(tex.outputs['Alpha'],bs.inputs['Alpha'])
 if 'glass' in m.shader_properties.filename:bs.inputs['Roughness'].default_value=.15;bs.inputs['Metallic'].default_value=.5
 pm['vano_shader_origem']=m.shader_properties.filename;preview[key]=pm;return pm

def add_source(names,label,center,target,angle=0,scale=(1,1,1),remove=(),trim_front=False,tint=False):
 global current
 root=bpy.data.objects.new('vano_'+label,None);current.objects.link(root);root.location=target;root.rotation_euler.z=angle;root.scale=scale
 root['vano_fontes']=', '.join(names);reused.append({'conjunto':label,'fontes':names,'removidos_materiais':list(remove),'escala':scale,'rotacao_z':angle,'destino':target})
 for name in names:
  c=bpy.data.collections.get('vano_fonte_'+name+'.ydr')
  if not c:raise ValueError(name)
  for src in c.objects:
   if src.type!='MESH':continue
   ob=src.copy();ob.data=src.data.copy();current.objects.link(ob);ob.name='vano_'+label+'_'+src.name;ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.location=Vector(src.location)-Vector(center);ob.rotation_euler=src.rotation_euler;ob.scale=src.scale;ob.hide_render=False;ob.hide_viewport=False
   bm=bmesh.new();bm.from_mesh(ob.data);bad=[]
   for f in bm.faces:
    m=ob.data.materials[f.material_index];mn=m.name.lower()
    if any(k in mn for k in remove) or (trim_front and all(v.co.y < -8.85 for v in f.verts)):bad.append(f)
   bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(ob.data);bm.free()
   # remove unreferenced vertices to measure real retained geometry
   bm=bmesh.new();bm.from_mesh(ob.data);loose=[v for v in bm.verts if not v.link_faces];bmesh.ops.delete(bm,geom=loose,context='VERTS');bm.to_mesh(ob.data);bm.free();ob.data.update()
   for slot in ob.material_slots:
    m=slot.material;slot.material=preview_material(m,tint and any(k in m.name.lower() for k in ['paredelisa','paredebranca','tijoloalento']),asset=name)
   ob['vano_status']='Malha original adaptada; shader Principled apenas para avaliação Blender'
 return root
# Bar's actual building without the perimeter/terrain packaged with it, facing the single entrance.
add_source(['nexus_bar1909_ext','nexus_bar1909_int'],'fachada_bar_reconstruida',(-10.25,-19.94,0),(-21.4,17.2,.03),-math.pi/2,remove=('concreto1909','txtvermelha','enferrujadonexus'),tint=True)
# Alento is a long side building; turn it to align with the left edge, maintain original scale.
add_source(['nexus_alento_ext','nexus_alento_int'],'alento_convivencia',(-20.25,-11.1,0),(-22.8,41,.03),math.pi/2,remove=('paredenexusfora','enferrujadonexus','texturachaoalentonexus'),tint=True)
# Existing shed shell provides workshop walls/interior. Replace curved roof with main contemporary canopy.
add_source(['nexus_galpao_ext','nexus_galpao_int'],'galpao_oficina',(0,0,0),(20,47,.03),remove=('telhanexusaa',),trim_front=True)
# Existing Alento gate, widened while retaining the original bars, panels and UVs.
gate=add_source(['nexus_portao_alento'],'portao_principal',(0,0,0),(0,0,0))
# normalize using local vertex bounds before dimensioning
pts=[o.matrix_local@v.co for o in gate.children if o.type=='MESH' for v in o.data.vertices];mi=Vector([min(p[i] for p in pts) for i in range(3)]);ma=Vector([max(p[i] for p in pts) for i in range(3)]);cent=(mi+ma)/2
for o in gate.children:o.location-=cent
scale=13.8/(ma.x-mi.x);gate.scale=(scale,1,.78);gate.location=(0,3.75,(ma.z-mi.z)*.78/2+.05)
for f,x in [(1,0),(100,14.1)]:gate.location.x=x;gate.keyframe_insert(data_path='location',frame=f)
s.frame_set(1)
# retain a genuine small wall-mounted identity asset
add_source(['nexus_quadroppl'],'quadro_convivencia',(0,0,0),(-26,32,2))
# helpers for architectural fabrication and joinery
current=bpy.data.collections['vano_Fachada']
def move(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 current.objects.link(o);return o
def box(n,loc,dims,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=move(bpy.context.object);o.name='vano_'+n;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bevel:mod=o.modifiers.new('vano_arestas','BEVEL');mod.width=bevel;mod.segments=2;o.modifiers.new('vano_normais','WEIGHTED_NORMAL')
 return o
def beam(n,a,b,w,m):
 a,b=Vector(a),Vector(b);o=box(n,(a+b)/2,(w,w,(b-a).length),m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def cyl(n,loc,r,depth,m,verts=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);o=move(bpy.context.object);o.name='vano_'+n;o.data.materials.append(m);return o
def text(n,body,loc,size,m,rot=(math.pi/2,0,0)):
 bpy.ops.object.text_add(location=loc,rotation=rot);o=move(bpy.context.object);o.name='vano_'+n;o.data.body=body;o.data.align_x='CENTER';o.data.size=size;o.data.extrude=.008;o.data.materials.append(m);return o
# original building facade now at y~8.7, layer restrained contemporary metal work
box('marquise_visitantes',(-21.4,7.8,3.25),(9.5,2,.14),steel,.035)
for x in [-25.8,-17]:beam('tirante_marquise',(x,7,3.3),(x,8.9,4.2),.035,steel)
text('fachada_nome','GUARDA POPULAR',(-21.4,8.58,7.4),.58,white)
# Original dz909 facade lettering retained without duplicate text.
# New branded red gate insert follows the animated original gate.
current=bpy.data.collections['vano_Portao']
panel=box('painel_portao_alento',(0,3.62,1.35),(7,.06,1.35),red,.02)
sign=text('portao_alento_texto','ALENTO',(0,3.57,1.08),.65,white)
for ob in [panel,sign]:
 world=ob.matrix_world.copy();ob.parent=gate;ob.matrix_world=world
current=bpy.data.collections['vano_Fachada']
# architectural emblem: typographic medallion, no claim to recreate exact trademark artwork
em=cyl('medalhao_GP',(-21.4,8.4,6),1.0,.12,red,48);em.rotation_euler.x=math.pi/2
text('medalhao_tipografia','GP',(-21.4,8.30,5.65),.85,white)
# real window joinery and glass placed within facade openings, no solid box behind the glass
for x in [-24.4,-18.5]:
 box('caixilho_pavimento', (x,8.58,5.6),(2.1,.10,1.65),steel,.015)
 box('vidro_pavimento',(x,8.51,5.6),(1.94,.025,1.48),glass)
 for dx in [-.65,0,.65]:box('montante_vidro',(x+dx,8.47,5.6),(.04,.06,1.5),white)
# boteco terrace beside original Alento. Open social counter and small canopy.
current=bpy.data.collections['vano_Boteco']
box('calcada_boteco',(-17,40,.09),(6.4,29,.18),concrete)
box('balcao_alvenaria',(-20,42,.57),(1,12,1.14),red,.035);box('balcao_pedra',(-20,42,1.18),(1.3,12,.12),steel,.03)
for y in [28,36,44,54]:beam('pilar_varanda',(-15,y,.12),(-15,y,4.1),.12,red)
box('marquise_boteco',(-17.6,40,4.12),(6,29,.12),roof)
box('testeira_boteco',(-14.7,40,3.75),(.12,28,.75),red)
text('boteco_identidade','BOTECO COLORADO',(-17.6,25.4,3.65),.48,white)
# planter troughs and low vegetation without thousands of leaves
current=bpy.data.collections['vano_Mobiliario']
for x,y in [(-14,26),(-14,54),(26,34),(26,56),(-26,6),(25,6)]:
 box('floreira',(x,y,.35),(1.3,2.5,.7),concrete,.06)
 green=bpy.data.materials.get('vano_vegetacao')
 if not green:
  green=bpy.data.materials.new('vano_vegetacao');green.diffuse_color=(.06,.16,.045,1)
 for i in range(3):
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.6,location=(x,y-.7+i*.7,1.0));ob=move(bpy.context.object);ob.name='vano_arbusto';ob.data.materials.append(green)
# chair backs and support columns for the existing table disks
for y in [27,32,37,42,47]:
 beam('pe_mesa',(-18,y,.1),(-18,y,.76),.085,steel)
 for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
  if dy:
   box('encosto_cadeira',(-18+dx,y+dy+dy*.18,.78),(.44,.06,.4),red,.015)
  else:box('encosto_cadeira',(-18+dx+dx*.18,y,.78),(.06,.44,.4),red,.015)
# workshop recognizable tire rack, tool board and motor service bay
current=bpy.data.collections['vano_Oficina']
for y in [50,53]:
 box('painel_ferramentas',(24.6,y,2.05),(.12,2,.95),steel)
 for i in range(4):beam('ferramenta_generica',(24.49,y-.65+i*.4,1.8),(24.49,y-.65+i*.4,2.25),.035,white)
# roof gutters, rainwater downpipes, seams: industrial fabrication instead of thick slabs
current=bpy.data.collections['vano_Galpao']
for x in [-13.8,26.4]:
 box('calha_lateral',(x,41,8.38),(.22,34,.16),steel)
 for y in [25.3,56.7]:beam('descida_pluvial',(x,y,.2),(x,y,8.3),.09,steel)
for x in range(-13,27):
 z=10.2-abs(x-6.25)*1.6/19.75;beam('junta_cobertura',(x,24,z),(x,58,z),.014,roof)
# warm architectural fixture sconces on facade
current=bpy.data.collections['vano_Iluminacao']
for x in [-25.8,-17]:
 for z in [2.7,6.7]:
  box('arandela',(x,8.3,z),(.15,.20,.22),steel,.025)
  ld=bpy.data.lights.new('vano_arandela_luz','POINT');ld.energy=65;ld.color=(1,.63,.32);ob=bpy.data.objects.new('vano_arandela_luz',ld);current.objects.link(ob);ob.location=(x,8,z)
# All reusable assets in source scene retain original shaders, LODs, collisions and transforms.
# Build metrics from evaluated mesh vertices; objects in original library are excluded.
s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();report={};allpts=[];tri=0
for c in s.collection.children:
 pts=[];ct=0
 for ob in c.all_objects:
  if ob.type not in {'MESH','FONT','CURVE'} or ob.hide_render:continue
  ev=ob.evaluated_get(deps);me=ev.to_mesh()
  if not me:continue
  pts.extend([ob.matrix_world@v.co for v in me.vertices]);ct+=sum(len(p.vertices)-2 for p in me.polygons);ev.to_mesh_clear()
 if pts:
  mi=[min(p[i] for p in pts) for i in range(3)];ma=[max(p[i] for p in pts) for i in range(3)];report[c.name]={'min':mi,'max':ma,'dimensoes':[ma[i]-mi[i] for i in range(3)],'triangulos_avaliados':ct};allpts+=pts;tri+=ct
mi=[min(p[i] for p in allpts) for i in range(3)];ma=[max(p[i] for p in allpts) for i in range(3)];area=(ma[0]-mi[0])*(ma[1]-mi[1]);maxwall=report['vano_Muros']['max'][2]
report['total']={'largura':ma[0]-mi[0],'comprimento':ma[1]-mi[1],'area_envelope':area,'altura_acima_piso':ma[2],'altura_muros':maxwall,'margem_area':3500-area,'margem_altura':15-ma[2],'margem_muros':8.6-maxwall,'triangulos_avaliados':tri,'frame_portao':1}
(P/'vano_medidas.json').write_text(json.dumps(report,indent=2));(P/'vano_reaproveitamento.json').write_text(json.dumps(reused,ensure_ascii=False,indent=2));print('MEDIDAS',report['total'])
assert area<=3500 and ma[2]<=15 and maxwall<=8.6
# Default view, complete packed project in meters
s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=False;s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.36,.4,.46,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
cam=s.camera;cam.location=(62,-95,42);cam.rotation_euler=(Vector((0,30,4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=48
# Pack only available images; missing base-game textures remain explicitly listed in the source library.
for image in bpy.data.images:
 if image.source=='FILE' and not image.packed_file and Path(bpy.path.abspath(image.filepath)).is_file():image.pack()
for blocks in [bpy.data.objects,bpy.data.meshes,bpy.data.materials,bpy.data.collections]:
 for ob in blocks:
  if not ob.name.startswith('vano_'):ob.name='vano_'+ob.name
bpy.ops.wm.save_as_mainfile(filepath=str(P/'vano_sede_master.blend'))
s.render.filepath=str(P/'vano_perspectiva.png');bpy.ops.render.render(write_still=True)
cam.location=(4,-48,15);cam.rotation_euler=(Vector((-1,32,4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=34;s.render.filepath=str(P/'vano_frente.png');bpy.ops.render.render(write_still=True)
cam.location=(0,30,110);cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=68;s.render.resolution_x=1400;s.render.resolution_y=1500
for ob in bpy.data.collections['vano_Galpao'].objects:
 if any(k in ob.name for k in ['Agua cobertura','junta_cobertura']):ob.hide_render=True
s.render.filepath=str(P/'vano_planta.png');bpy.ops.render.render(write_still=True)
