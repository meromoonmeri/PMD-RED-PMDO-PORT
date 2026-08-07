"""Extraction de gDungeonFileArchive depuis une ROM reconstruite pret/pmd-red."""
from pathlib import Path
import argparse,json,re,struct,hashlib
ROM_BASE=0x08000000

def off(ptr,size):
 x=ptr-ROM_BASE if ptr>=ROM_BASE else ptr
 if not 0<=x<=size:raise ValueError(f'pointeur hors ROM: {ptr:#x}')
 return x
def cstr(rom,pos):
 end=rom.index(0,pos);return rom[pos:end].decode('ascii')
def parse_symbol(value):return int(value,0)
def find_symbol(map_path,name='gDungeonFileArchive'):
 text=Path(map_path).read_text(errors='ignore')
 pats=(rf'\b{name}\b\s*=\s*(0x[0-9a-fA-F]+)',rf'^(0x[0-9a-fA-F]+)\s+{name}\b',rf'^\s*(0x[0-9a-fA-F]+)\s+\S*{name}\b')
 for pat in pats:
  m=re.search(pat,text,re.M)
  if m:return int(m.group(1),16)
 raise KeyError(f'symbole absent: {name}')
def siro_data(blob,rom_start):
 if blob[:4] not in (b'SIR0',b'SIRO'):return blob
 ptr=struct.unpack_from('<I',blob,4)[0]
 # Le pointeur peut viser la ROM ou être relatif au début du fichier.
 rel=(ptr-ROM_BASE-rom_start) if ptr>=ROM_BASE else ptr
 if 0<=rel<len(blob):return blob[rel:]
 raise ValueError('pointeur SIRO invalide')
def extract(rom_path,archive_address,out_dir):
 rom=Path(rom_path).read_bytes();a=off(archive_address,len(rom));magic=rom[a:a+8];count,entries=struct.unpack_from('<II',rom,a+8);eoff=off(entries,len(rom));rows=[]
 for i in range(count):
  np,dp=struct.unpack_from('<II',rom,eoff+i*8);rows.append({'name':cstr(rom,off(np,len(rom))),'data_ptr':dp})
 rows.sort(key=lambda x:x['data_ptr']);out=Path(out_dir);out.mkdir(parents=True,exist_ok=True);manifest=[]
 pointers=sorted(set(x['data_ptr'] for x in rows)|{ROM_BASE+len(rom)})
 for row in rows:
  start=off(row['data_ptr'],len(rom));nextp=min(p for p in pointers if p>row['data_ptr']);end=off(nextp,len(rom));blob=rom[start:end];data=siro_data(blob,start)
  # Pour une ressource SIR, la longueur exacte sera déterminée par son format;
  # conserver le blob jusqu'à la ressource suivante garantit zéro perte.
  path=out/row['name'];path.write_bytes(data);manifest.append({'name':row['name'],'rom_start':start,'rom_end':end,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 (out/'archive_manifest.json').write_text(json.dumps({'magic':magic.decode('ascii','replace'),'count':count,'archive_address':hex(archive_address),'files':manifest},indent=2)+'\n')
 return manifest
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('out');ap.add_argument('--address',type=parse_symbol);ap.add_argument('--map');a=ap.parse_args();addr=a.address or find_symbol(a.map);rows=extract(a.rom,addr,a.out);print(f'{len(rows)} ressources extraites')
