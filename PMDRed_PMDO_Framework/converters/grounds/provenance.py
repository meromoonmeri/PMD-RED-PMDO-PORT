"""Manifeste déterministe de provenance pret/pmd-red."""
from pathlib import Path
import hashlib,json,platform

def sha256(path):
 p=Path(path);h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()

def write_manifest(map_id, inputs, outputs, features, out_path, converter_version='2'):
 ins=[]
 for role,path in sorted(inputs.items()):
  p=Path(path);ins.append({'role':role,'path':str(p),'sha256':sha256(p),'bytes':p.stat().st_size,'authority':'pret/pmd-red'})
 outs=[]
 for role,path in sorted(outputs.items()):
  p=Path(path);outs.append({'role':role,'path':str(p),'sha256':sha256(p),'bytes':p.stat().st_size})
 doc={'schema':1,'map_id':map_id,'converter_version':converter_version,'python':platform.python_version(),'inputs':ins,'outputs':outs,'features':features,'external_graphics_used':False}
 Path(out_path).parent.mkdir(parents=True,exist_ok=True);Path(out_path).write_text(json.dumps(doc,indent=2,sort_keys=True)+'\n')
 return doc
