"""Ressources de décor utilisées par GroundMap_SelectDungeon/sub_80A3440.

Ces scènes ne doivent jamais être rendues depuis leur BMA seule. Chunsoft
remplace les tuiles/palettes par bXXfon, bXXpal, bXXcel, bXXcex et bXXcanm.
"""
from pathlib import Path

class DungeonArchiveMissing(RuntimeError):pass

def decompress_at(src:bytes,expected_size=0)->bytes:
 if src[:4] not in (b'AT4P',b'AT3P'):raise ValueError('signature AT inconnue')
 compressed=src[5]|src[6]<<8
 if src[4]==ord('N'):return src[7:7+compressed]
 start=0x12 if src[:4]==b'AT4P' else 0x10
 if src[:4]==b'AT4P' and expected_size and (src[0x10]|src[0x11]<<8)!=expected_size:raise ValueError('taille AT4P inattendue')
 flags=[src[7+i]+3 for i in range(9)];out=bytearray();i=start;bits=8;cmd=0
 while i<compressed:
  if expected_size and len(out)>=expected_size:break
  if bits==8:cmd=src[i];i+=1;bits=0
  if cmd&0x80:out.append(src[i]);i+=1
  else:
   first=src[i];length=(first>>4)+3;back=((first&15)<<8);i+=1
   if length in flags:
    code=flags.index(length);c=src[i]&15;i+=1
    patterns=(((c,c),(c,c)),((c,c+1),(c+1,c+1)),((c,c-1),(c,c)),((c,c),(c-1,c)),((c,c),(c,c-1)),((c,c-1),(c-1,c-1)),((c,c+1),(c,c)),((c,c),(c+1,c)),((c,c),(c,c+1)))
    for a,b in patterns[code]:out.append(((a&15)<<4)|(b&15))
   else:
    back+=src[i];i+=1;pos=len(out)-0x1000+back
    for _ in range(length):out.append(out[pos]);pos+=1
  bits+=1;cmd=(cmd<<1)&255
 return bytes(out)

class DungeonArchive:
 def __init__(self,root):self.root=Path(root)
 def read(self,name):
  for p in (self.root/name,self.root/(name+'.bin')):
   if p.exists():return p.read_bytes()
  raise DungeonArchiveMissing(f'ressource dungeon absente: {name}')
 def load_tileset(self,tileset,variant=0):
  """Charge les cinq familles exactes demandées par sub_80ADD9C."""
  names={'font':f'b{tileset:02d}fon','palette':f'b{tileset:02d}pal','cells':f'b{tileset:02d}cel','extra':f'b{tileset:02d}cex','animation':f'b{tileset:02d}canm'}
  raw={k:self.read(v) for k,v in names.items()}
  return {'names':names,'font':decompress_at(raw['font']),'palette':raw['palette'],'cells':decompress_at(raw['cells'],0x1194),'extra':decompress_at(raw['extra'],0x930) if raw['extra'][:4] in (b'AT3P',b'AT4P') else raw['extra'],'animation':raw['animation']}
