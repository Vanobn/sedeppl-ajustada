from pathlib import Path
import zipfile,json,hashlib,argparse
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--saida',type=Path,default=P.parents[1]/'entregas');a=a.parse_args();D=a.saida;D.mkdir(parents=True,exist_ok=True)
def include(p):
 rel=p.relative_to(P)
 return p.is_file() and not any(x in ['bin','obj','__pycache__'] for x in rel.parts) and p.suffix!='.blend1' and p.name not in ['blender.log','previews_finais.log','manifesto_arquivos.json']
files=sorted(p for p in P.rglob('*') if include(p))
manifest={str(p.relative_to(P)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
(P/'relatorios/manifesto_arquivos.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));files.append(P/'relatorios/manifesto_arquivos.json')
for nome,items in [('completo',files),('recurso',sorted((P/'stream').iterdir())+[P/'fxmanifest.lua',P/'INSTALACAO.md']+list((P/'exemplos').iterdir()))]:
 target=D/('vano_boteco_colorado_'+nome+'.zip')
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in items:
   if p.is_file():z.write(p,'vano_boteco_colorado/'+str(p.relative_to(P)))
 with zipfile.ZipFile(target) as z:assert z.testzip() is None
 print(target,round(target.stat().st_size/1024**2,2),'MiB, CRC OK')
