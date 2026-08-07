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
def find_archive_in_rom(rom_path):
 """Locate the unique pksdir0 FileArchive header in retail/rebuilt ROMs."""
 rom=Path(rom_path).read_bytes();low=rom.lower();hits=[];start=0
 while True:
  pos=low.find(b'pksdir0\0',start)
  if pos<0:break
  if pos+16<=len(rom):
   count,entries=struct.unpack_from('<II',rom,pos+8)
   eo=entries-ROM_BASE if entries>=ROM_BASE else entries
   if 0<count<2000 and 0<=eo<=len(rom)-count*8:
    valid=0
    for i in range(min(count,16)):
     np=struct.unpack_from('<I',rom,eo+i*8)[0];no=np-ROM_BASE if np>=ROM_BASE else np
     if 0<=no<len(rom):
      end=rom.find(b'\0',no,min(len(rom),no+32));name=rom[no:end] if end>=0 else b''
      if name and all(32<=c<127 for c in name):valid+=1
    if valid==min(count,16):hits.append((count,pos))
  start=pos+1
 if not hits:raise ValueError('archive pksdir0 valide absent')
 best=max(hits)
 if sum(x[0]==best[0] for x in hits)!=1:raise ValueError(f'archive pksdir0 ambigu: {hits}')
 return ROM_BASE+best[1]
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
  # mapparam contient des pointeurs relocalisés vers des tables situées avant
  # son pointeur principal SIR0. Écrire seulement `data` les tronquerait.
  # Conserver aussi le blob archive complet et son adresse ROM.
  if row['name']=='mapparam':
   (out/'mapparam.archive_blob').write_bytes(blob)
  path=out/row['name'];path.write_bytes(data);manifest.append({'name':row['name'],'rom_start':start,'rom_end':end,'archive_bytes':len(blob),'bytes':len(data),'data_offset':len(blob)-len(data),'sha256':hashlib.sha256(data).hexdigest(),'archive_sha256':hashlib.sha256(blob).hexdigest()})
 (out/'archive_manifest.json').write_text(json.dumps({'magic':magic.decode('ascii','replace'),'count':count,'archive_address':hex(archive_address),'files':manifest},indent=2)+'\n')
 return manifest
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('out');ap.add_argument('--address',type=parse_symbol);ap.add_argument('--map');a=ap.parse_args();addr=a.address or (find_symbol(a.map) if a.map else find_archive_in_rom(a.rom));rows=extract(a.rom,addr,a.out);print(f'{len(rows)} ressources extraites depuis {addr:#x}')
