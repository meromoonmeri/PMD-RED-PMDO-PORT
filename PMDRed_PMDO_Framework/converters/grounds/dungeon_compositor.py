"""Chunsoft SelectDungeon compositor for bXX dungeon materials."""
from pathlib import Path
import struct
from PIL import Image
try:
 from skytemple_files.common.types.file_types import FileType
except ImportError: FileType=None

def decomp(data):
 if data[:4] not in (b'AT4P',b'AT3P'):return data
 if FileType is None:raise RuntimeError('skytemple-files requis pour AT3PX/AT4PX')
 if data[:4]==b'AT3P':return FileType.AT3PX.deserialize(data).decompress()
 return (FileType.AT4PN if data[:5]==b'AT4PN' else FileType.AT4PX).deserialize(data).decompress()

def tile(td,pal,hf,vf):
 im=Image.new('RGBA',(8,8),(0,0,0,0));px=im.load()
 for y in range(8):
  for x in range(4):
   b=td[y*4+x]
   for k,c in enumerate((b&15,b>>4)):
    if c:px[7-(x*2+k) if hf else x*2+k,7-y if vf else y]=pal[c]
 return im

def render_special(archive,tileset,variant,width_chunks,height_chunks):
 """Render r8>=64 emap rooms exactly as sub_80ADD9C."""
 root=Path(archive);font=decomp((root/f'b{tileset:02d}fon').read_bytes());cel=decomp((root/f'b{tileset:02d}cel').read_bytes());emap=decomp((root/f'b{tileset:02d}emap{variant}').read_bytes());palraw=(root/f'b{tileset:02d}pal').read_bytes()
 if len(cel)!=0x1194 or len(emap)!=0x240:raise ValueError((len(cel),len(emap)))
 tiles=[font[i:i+32] for i in range(0,len(font),32)];pals=[]
 for p in range(12):pals.append([tuple(palraw[(p*16+c)*4:(p*16+c)*4+4]) for c in range(16)])
 img=Image.new('RGBA',(width_chunks*24,height_chunks*24),(0,0,0,255));cache={}
 for cy in range(height_chunks):
  for cx in range(width_chunks):
   cid=emap[cy*24+cx]
   for j in range(9):
    ent=struct.unpack_from('<H',cel,(cid*9+j)*2)[0];ti=ent&1023;pi=(ent>>12)&15
    if ti>=len(tiles):continue
    key=ent
    im=cache.get(key)
    if im is None:im=tile(tiles[ti],pals[pi%len(pals)],(ent>>10)&1,(ent>>11)&1);cache[key]=im
    img.alpha_composite(im,((cx*3+j%3)*8,(cy*3+j//3)*8))
 return img
