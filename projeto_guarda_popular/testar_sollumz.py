import sys,bpy,addon_utils
sys.path[:0]=['/workspace/tools','/workspace/tools/pydeps']
addon_utils.enable('Sollumz',default_set=True,persistent=True)
print('REGISTERED',hasattr(bpy.ops.sollumz,'import_assets'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
result=bpy.ops.sollumz.import_assets(directory='/workspace/projeto-guarda-popular/convertidos',files=[{'name':'nexus_galpao_ext.ydr.xml'}])
print('RESULT',result,'OBJECTS',len(bpy.data.objects))
bpy.ops.wm.save_as_mainfile(filepath='/workspace/projeto-guarda-popular/teste_importacao.blend')
