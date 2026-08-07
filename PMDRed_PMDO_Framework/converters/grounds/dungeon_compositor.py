"""Chunsoft SelectDungeon compositor for bXX dungeon materials."""
from pathlib import Path
import struct
from PIL import Image
try: from skytemple_files.common.types.file_types import FileType
except ImportError: FileType=None
REMAP=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,16,23,24,25,20,23,28,29,30,31,32,33,28,35,36,37,30,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,45,45,59,60,48,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79]
def decomp(data):
 if data[:4] not in (b'AT4P',b'AT3P'):return data
 if FileType is None:raise RuntimeError('skytemple-files requis')
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
def materials(root,tileset):
 root=Path(root);mapped=REMAP[tileset];font=decomp((root/f'b{mapped:02d}fon').read_bytes());cel=decomp((root/f'b{mapped:02d}cel').read_bytes());palraw=(root/f'b{tileset:02d}pal').read_bytes()
 if len(cel)!=0x1194:raise ValueError(len(cel))
 tiles=[font[i:i+32] for i in range(0,len(font),32)];pals=[[tuple(palraw[(p*16+c)*4:(p*16+c)*4+4]) for c in range(16)] for p in range(12)]
 return tiles,pals,cel
def compose(chunks,w,h,tiles,pals,cel):
 img=Image.new('RGBA',(w*24,h*24),(0,0,0,255));cache={}
 for cy in range(h):
  for cx in range(w):
   cid=chunks[cy*w+cx]
   for j in range(9):
    ent=struct.unpack_from('<H',cel,(cid*9+j)*2)[0];ti=ent&1023;pi=(ent>>12)&15
    if ti>=len(tiles):continue
    im=cache.get(ent)
    if im is None:im=tile(tiles[ti],pals[pi%len(pals)],(ent>>10)&1,(ent>>11)&1);cache[ent]=im
    img.alpha_composite(im,((cx*3+j%3)*8,(cy*3+j//3)*8))
 return img
def render_special(archive,tileset,variant,width_chunks,height_chunks):
 tiles,pals,cel=materials(archive,tileset);emap=decomp((Path(archive)/f'b{tileset:02d}emap{variant}').read_bytes())
 if len(emap)!=0x240:raise ValueError(len(emap))
 return compose([emap[y*24+x] for y in range(height_chunks) for x in range(width_chunks)],width_chunks,height_chunks,tiles,pals,cel)
def _at(grid,x,y,w,h,default=0):return grid[y*64+x] if 0<=x<w and 0<=y<h else default
def render_regular(archive,tileset,terrain,width_chunks,height_chunks,default=0):
 tiles,pals,cel=materials(archive,tileset);cex=decomp((Path(archive)/f'b{REMAP[tileset]:02d}cex').read_bytes())
 chunks=[]
 for y in range(height_chunks):
  for x in range(width_chunks):
   base=_at(terrain,x,y,width_chunks,height_chunks,default);off=[_at(terrain,x+dx,y+dy,width_chunks,height_chunks,default) for dx,dy in ((0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1))]
   if base==1:
    mask=0xff
    for i,v in enumerate(off):
     if v==0:mask&=~(1<<i)
    mask|=0x200
   elif base in (2,3):
    mask=0xff
    for i,v in enumerate(off):
     if v!=base:mask&=~(1<<i)
    mask|=0x100
   else:
    mask=0
    for i,v in enumerate(off):
     if v==0:mask|=1<<i
   chunks.append(cex[mask*3])
 return compose(chunks,width_chunks,height_chunks,tiles,pals,cel)
