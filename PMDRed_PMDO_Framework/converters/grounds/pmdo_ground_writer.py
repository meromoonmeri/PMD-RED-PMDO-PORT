"""Écrit des cellules Chunsoft indépendamment animées en formats PMDO natifs.

Le writer n'impose aucun cycle global : chaque cellule possède ses propres
frames et son propre FrameLength. Les cellules statiques ne sont encodées
qu'une fois.
"""
from pathlib import Path
import io,json,struct

def png(tile):
 b=io.BytesIO();tile.save(b,'PNG',optimize=True);return b.getvalue()

def write_tile_cells(path,width,height,cells,cell=8):
 """cells[(x,y)] = {'frames': [PIL.Image], 'frame_length': int}."""
 entries=[];mapping={};encoded={}
 for y in range(height):
  for x in range(width):
   spec=cells[(x,y)];keys=[]
   for fi,tile in enumerate(spec['frames']):
    raw=tile.tobytes();blob=encoded.get(raw)
    if blob is None:blob=png(tile);encoded[raw]=blob
    key=(x+fi*width,y);entries.append((key,blob));keys.append(key)
   mapping[(x,y)]={'keys':keys,'frame_length':max(1,int(spec.get('frame_length',1)))}
 uniq={};order=[]
 for _,b in entries:
  if b not in uniq:uniq[b]=None;order.append(b)
 pos=8+16*len(entries)
 for b in order:uniq[b]=pos;pos+=8+len(b)
 out=bytearray(struct.pack('<II',cell,len(entries)))
 for (x,y),b in entries:out+=struct.pack('<QQ',x|(y<<32),uniq[b])
 for b in order:out+=struct.pack('<q',len(b))+b
 Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_bytes(out)
 return len(entries),len(order),mapping

def _ground(path,asset,sheet,W,H,mapping,collision,markers,spawners,objects,music,comment):
 def cell(x,y):
  spec=mapping[(x,y)]
  return {'AutoTileset':'','Associates':[],'Layers':[{'Frames':[{'Sheet':sheet,'TexLoc':{'X':kx,'Y':ky}} for kx,ky in spec['keys']],'FrameLength':spec['frame_length']}],'NeighborCode':-1}
 obs=[]
 for x in range(W):
  col=[]
  for y in range(H):
   blocked=bool(collision[y*W+x]) if collision is not None else False;col.append({'Bounds':{'X':x*8,'Y':y*8,'Width':8,'Height':8},'Tags':1 if blocked else 0})
  obs.append(col)
 obj={'$type':'RogueEssence.Ground.GroundMap, RogueEssence','TexSize':1,'Name':{'DefaultText':asset,'LocalTexts':{}},'Released':False,'Comment':comment,'obstacles':obs,'Status':{},'Background':{'$type':'RogueEssence.Dungeon.MapBG, RogueEssence','MapLoc':{'X':0,'Y':0},'BGAnim':{'AnimIndex':'','FrameTime':1,'StartFrame':-1,'EndFrame':-1,'AnimDir':-1,'Alpha':255,'AnimFlip':0},'BGMovement':{'X':0,'Y':0},'RepeatX':False,'RepeatY':False},'BlankBG':{'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1},'Layers':[{'Name':'Chunsoft framebuffer (cell-local cycles)','Layer':0,'Visible':True,'Tiles':[[cell(x,y) for y in range(H)] for x in range(W)]}],'AssetName':asset,'Music':music,'EdgeView':1,'NoSwitching':False,'ViewCenter':None,'ViewOffset':{'X':0,'Y':0},'Decorations':[{'Name':'New Deco','Layer':0,'Visible':True,'Anims':[]}],'Entities':[{'Name':'New EntLayer','Visible':True,'MapChars':[],'GroundObjects':objects or [],'Spawners':spawners or [],'Markers':markers or []}]}
 Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(json.dumps({'Version':'0.8.9.0','Object':obj},separators=(',',':'))+'\n')

def write_ground_cells(path,asset,sheet,width,height,cells,collision=None,markers=None,spawners=None,objects=None,music=''):
 p=Path(path);tile_path=(p.parent.parent/'Tiles'/f'{sheet}.tile') if p.parent.name=='Grounds' else (p.parents[2]/'Content/Tile'/f'{sheet}.tile');ec,uc,mapping=write_tile_cells(tile_path,width,height,cells)
 _ground(path,asset,sheet,width,height,mapping,collision,markers,spawners,objects,music,'Generated exclusively from pret/pmd-red; independent cell-local animation cycles.')
 return {'width':width,'height':height,'frames':'independent','tile_entries':ec,'unique_tiles':uc,'max_cell_frames':max(len(v['frames']) for v in cells.values())}

def write_ground(path,asset,sheet,frames,collision=None,markers=None,spawners=None,objects=None,music=''):
 """Compatibility API for short, already materialised frame sequences."""
 W,H=frames[0].width//8,frames[0].height//8;cells={}
 for y in range(H):
  for x in range(W):
   seq=[im.crop((x*8,y*8,x*8+8,y*8+8)) for im in frames]
   if all(im.tobytes()==seq[0].tobytes() for im in seq):seq=seq[:1]
   cells[(x,y)]={'frames':seq,'frame_length':1}
 info=write_ground_cells(path,asset,sheet,W,H,cells,collision,markers,spawners,objects,music);info['frames']=len(frames);return info
