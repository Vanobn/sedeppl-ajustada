import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path('/workspace/projeto-guarda-popular');bpy.ops.wm.open_mainfile(filepath=str(P/'vano_sede_master.blend'));s=bpy.data.scenes['vano_PROJETO'];bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
r={'cenas':[sc.name for sc in bpy.data.scenes],'escala_metros':s.unit_settings.scale_length,'componentes':{}}
for root in s.objects:
 if root.type!='EMPTY' or 'vano_fontes' not in root:continue
 pts=[ob.matrix_world@v.co for ob in root.children_recursive if ob.type=='MESH' for v in ob.data.vertices]
 if not pts:continue
 mi=[min(p[i] for p in pts) for i in range(3)];ma=[max(p[i] for p in pts) for i in range(3)];r['componentes'][root.name]={'min':mi,'max':ma,'dimensoes':[ma[i]-mi[i] for i in range(3)],'fontes':root['vano_fontes']}
# Audit source files against baseline, not just git status.
base=json.loads((P/'inventario.json').read_text());changed=[]
for row in base:
 p=Path('/workspace/sedeppl-ajustada')/row['arquivo']
 if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:changed.append(row['arquivo'])
r['originais_alterados']=changed;assert not changed
# Check all active-project assets have packed textures (source library may retain base-game placeholders).
missing=[]
for ob in s.objects:
 if ob.type!='MESH':continue
 for m in ob.data.materials:
  if not m or not m.use_nodes:continue
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image and (n.image.size[0]==0 or (n.image.source=='FILE' and not n.image.packed_file and not Path(bpy.path.abspath(n.image.filepath)).exists())):missing.append((ob.name,n.image.name))
r['texturas_projeto_ausentes']=missing;assert not missing,missing
# Gate travel stays within staff perimeter; geometry clearance/collision remains a game integration task.
for frame in [1,100]:
 s.frame_set(frame);bpy.context.view_layer.update();gate=next(o for o in s.objects if o.type=='EMPTY' and o.name.startswith('vano_portao_principal'))
 pts=[o.matrix_world@v.co for o in gate.children_recursive if o.type=='MESH' for v in o.data.vertices]
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];r['portao_frame_'+str(frame)]={'min':lo,'max':hi}
 assert lo[0]>=-29 and hi[0]<=29 and lo[1]>=0 and hi[1]<=60
s.frame_set(1)
(P/'vano_validacao.json').write_text(json.dumps(r,indent=2,ensure_ascii=False));print(json.dumps(r,indent=2,ensure_ascii=False))
