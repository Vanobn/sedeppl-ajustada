from pathlib import Path
import hashlib,json,zipfile
P=Path(__file__).resolve().parents[1]
def included(p):
 rel=p.relative_to(P)
 return p.is_file() and not any(n in {'bin','obj','__pycache__','.git'} for n in rel.parts) and p.suffix!='.blend1' and p.name!='manifesto.json'
files=sorted(p for p in P.rglob('*') if included(p))
manifest=[{'arquivo':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
m=P/'relatorios/manifesto.json';m.write_text(json.dumps(manifest,ensure_ascii=False,indent=2));files.append(m)
archive=P.parent/'alemao_pneus_entrega.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('alemao_pneus')/p.relative_to(P))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(archive,archive.stat().st_size,'bytes;',len(files),'arquivos; ZIP verificado')
