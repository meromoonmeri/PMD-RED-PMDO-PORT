"""Rendu Chunsoft sans framebuffer global, cellule par cellule.

Seuls les cycles BPA/BPL réellement référencés par une cellule entrent dans
son cycle local. Ainsi, le PPCM de cycles sans rapport n'est jamais calculé ni
matérialisé.
"""
import math,os
from PIL import Image
import visual_extractor as ve

def _slot_for_tile(bpc,ti):
 start=len(bpc['base_tiles'])
 for i,n in enumerate(bpc['slot_tiles']):
  if start <= ti < start+n:return i,ti-start
  start+=n
 return None,None

def _tile_image(td,palette,hf,vf):
 out=Image.new('RGBA',(8,8),(0,0,0,0));pix=out.load()
 for y in range(8):
  for x in range(4):
   byte=td[y*4+x]
   for k,ci in enumerate((byte&15,byte>>4)):
    if ci:pix[7-(x*2+k) if hf else x*2+k,7-y if vf else y]=palette[ci]
 return out

def _minimal_cycle(images):
 raw=[x.tobytes() for x in images]
 for n in range(1,len(raw)+1):
  if len(raw)%n==0 and all(raw[i]==raw[i%n] for i in range(len(raw))):return images[:n]
 return images

def render_cell_cycles(dep,data_dir,trace=None):
 pal=ve.parse_bpl(os.path.join(data_dir,dep['bpl']+'.bpl'));bpc=ve.parse_bpc(os.path.join(data_dir,dep['bpc']+'.bpc'));bma=ve.decode_bma(os.path.join(data_dir,dep['bma']+'.bma'))
 names=[None]*4
 for name in dep.get('bpa',[]):
  try:i=int(name[-1])-1
  except (ValueError,IndexError):i=next((j for j,x in enumerate(names) if x is None),0)
  if 0<=i<4:names[i]=name
 slots=[ve.parse_bpa(os.path.join(data_dir,n+'.bpa')) if n else None for n in names]
 for i,(need,slot) in enumerate(zip(bpc['slot_tiles'],slots)):
  if need and (not slot or slot['num_tiles']!=need):raise ValueError(f'BPA slot {i}: données invalides')
 W,H=bma['width_tiles'],bma['height_tiles'];cells={};max_frames=0
 for y in range(H):
  for x in range(W):
   cx,cy=x//bpc['chunk_width'],y//bpc['chunk_height'];j=(y%bpc['chunk_height'])*bpc['chunk_width']+(x%bpc['chunk_width']);ents=[];periods=[];durations=[]
   for lay in reversed(bma['layers']):
    cid=lay[cy*64+cx] if cx<bma['width_chunks'] and cy<bma['height_chunks'] else 0
    ent=bpc['chunks'][cid][j] if 0<cid<len(bpc['chunks']) else 0;ents.append(ent)
    ti=ent&0x3ff;pi=(ent>>12)&15;si,_=_slot_for_tile(bpc,ti)
    if si is not None and si<2 and slots[si]:
     ds=[max(1,d) for d in slots[si]['durations']];periods.append(sum(ds));durations+=ds
    if pal['animated'] and pi<len(pal['specs']):
     d,n=pal['specs'][pi]
     if n>0:periods.append(max(1,d)*n);durations.append(max(1,d))
   period=1
   for p in periods:period=math.lcm(period,p)
   quantum=math.gcd(*durations) if durations else 1
   images=[]
   for tick in range(0,period,quantum):
    img=Image.new('RGBA',(8,8),(0,0,0,255));pals=ve._palettes_at_tick(pal,tick)
    for ent in ents:
     ti=ent&0x3ff
     if not ti:continue
     si,rel=_slot_for_tile(bpc,ti)
     if si is None:td=bpc['base_tiles'][ti] if ti<len(bpc['base_tiles']) else None
     else:
      slot=slots[si];td=slot['tiles'][ve._frame_at(slot,tick,si<2)][rel] if slot else None
     if td is None:continue
     pi=(ent>>12)&15;img.alpha_composite(_tile_image(td,pals[pi%len(pals)],(ent>>10)&1,(ent>>11)&1))
    images.append(img)
   images=_minimal_cycle(images);cells[(x,y)]={'frames':images,'frame_length':quantum};max_frames=max(max_frames,len(images))
 if trace is not None:trace.update({'animation_model':'independent_cell_cycles','global_period_ticks':ve._period(pal,slots),'max_cell_frames':max_frames,'framebuffers_materialized':0,'bma_layers_consumed':bma['num_layers'],'bpa_slots_consumed':sum(x is not None for x in slots),'palette_animation_executed':pal['animated'],'source_files':[dep['bpl']+'.bpl',dep['bpc']+'.bpc',dep['bma']+'.bma']+[x+'.bpa' for x in dep.get('bpa',[])]})
 return W,H,cells
