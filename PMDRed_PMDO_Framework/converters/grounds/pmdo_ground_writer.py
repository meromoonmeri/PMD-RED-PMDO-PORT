"""Écrit les framebuffers Chunsoft en formats natifs PMDO."""
from pathlib import Path
import io,json,struct

def png(tile):
 b=io.BytesIO();tile.save(b,'PNG',optimize=True);return b.getvalue()
def write_tile(path,frames,cell=8):
 w,h=frames[0].size;W,H=w//cell,h//cell;entries=[];mapping={};encoded={}
 for y in range(H):
  for x in range(W):
   seq=[]
   for im in frames:
    tile=im.crop((x*cell,y*cell,(x+1)*cell,(y+1)*cell));raw=tile.tobytes()
    blob=encoded.get(raw)
    if blob is None:blob=png(tile);encoded[raw]=blob
    seq.append(blob)
   if all(v==seq[0] for v in seq):seq=seq[:1]
   keys=[]
   for fi,blob in enumerate(seq):
    key=(x+fi*W,y);entries.append((key,blob));keys.append(key)
   mapping[(x,y)]=keys
 uniq={};order=[]
 for _,b in entries:
  if b not in uniq:uniq[b]=None;order.append(b)
 pos=8+16*len(entries)
 for b in order:uniq[b]=pos;pos+=8+len(b)
 out=bytearray(struct.pack('<II',cell,len(entries)))
 for (x,y),b in entries:out+=struct.pack('<QQ',x|(y<<32),uniq[b])
 for b in order:out+=struct.pack('<q',len(b))+b
 Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_bytes(out)
 return W,H,len(entries),len(order),mapping
def write_ground(path,asset,sheet,frames,collision=None,markers=None,spawners=None,objects=None,music=''):
 tile_path=Path(path).parents[2]/'Content/Tile'/f'{sheet}.tile';W,H,entry_count,unique_count,mapping=write_tile(tile_path,frames)
 def cell(x,y):
  keys=mapping[(x,y)];return {'AutoTileset':'','Associates':[],'Layers':[{'Frames':[{'Sheet':sheet,'TexLoc':{'X':kx,'Y':ky}} for kx,ky in keys],'FrameLength':1}],'NeighborCode':-1}
 obs=[]
 for x in range(W):
  col=[]
  for y in range(H):
   blocked=bool(collision[y*W+x]) if collision is not None else False;col.append({'Bounds':{'X':x*8,'Y':y*8,'Width':8,'Height':8},'Tags':1 if blocked else 0})
  obs.append(col)
 obj={'$type':'RogueEssence.Ground.GroundMap, RogueEssence','TexSize':1,'Name':{'DefaultText':asset,'LocalTexts':{}},'Released':False,'Comment':'Generated exclusively from pret/pmd-red framebuffer pipeline.','obstacles':obs,'Status':{},'Background':{'$type':'RogueEssence.Dungeon.MapBG, RogueEssence','MapLoc':{'X':0,'Y':0},'BGAnim':{'AnimIndex':'','FrameTime':1,'StartFrame':-1,'EndFrame':-1,'AnimDir':-1,'Alpha':255,'AnimFlip':0},'BGMovement':{'X':0,'Y':0},'RepeatX':False,'RepeatY':False},'BlankBG':{'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1},'Layers':[{'Name':'Chunsoft Final Framebuffer','Layer':0,'Visible':True,'Tiles':[[cell(x,y) for y in range(H)] for x in range(W)]}],'AssetName':asset,'Music':music,'EdgeView':1,'NoSwitching':False,'ViewCenter':None,'ViewOffset':{'X':0,'Y':0},'Decorations':[{'Name':'New Deco','Layer':0,'Visible':True,'Anims':[]}],'Entities':[{'Name':'New EntLayer','Visible':True,'MapChars':[],'GroundObjects':objects or [],'Spawners':spawners or [],'Markers':markers or []}]}
 Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(json.dumps({'Version':'0.8.9.0','Object':obj},separators=(',',':'))+'\n')
 return {'width':W,'height':H,'frames':len(frames),'tile_entries':entry_count,'unique_tiles':unique_count}
