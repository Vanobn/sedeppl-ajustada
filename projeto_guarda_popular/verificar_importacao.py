import bpy
bpy.ops.wm.open_mainfile(filepath='/workspace/projeto-guarda-popular/vano_biblioteca_originais.blend')
c=bpy.data.collections['vano_fonte_nexus_galpao_ext.ydr']
for o in c.objects:
 print('OBJ',o.name,o.type)
 if o.type=='MESH':
  print('MATS',[(m.name,m.shader_properties.filename) for m in o.data.materials]);print('UV',[(u.name) for u in o.data.uv_layers]);print('ATTR',[(a.name,a.data_type) for a in o.data.attributes])
  for m in o.data.materials:
   print('MAT',m.name,'IMAGES',[(n.name,n.image.name if n.image else None) for n in m.node_tree.nodes if n.type=='TEX_IMAGE'])
