"""Renderer Ground GBA alimenté exclusivement par pret/pmd-red.

Implémente BMA/BPC/BPL et les quatre slots BPA selon ground_bg.c. Les slots
0-1 sont animés; 2-3 chargent leur première frame statiquement, comme Chunsoft.
"""
import os,struct,math
from PIL import Image

def parse_bpl(path):
 d=open(path,'rb').read();num=int.from_bytes(d[0:2],'little');animated=bool(int.from_bytes(d[2:4],'little'));off=4;pals=[]
 for _ in range(num):
  cols=[(0,0,0,0)]
  for _ in range(15):cols.append((d[off],d[off+1],d[off+2],255));off+=4
  pals.append(cols)
 specs=[];anim=[]
 if animated:
  for i in range(num):
   dur,nf=struct.unpack_from('<hh',d,off+i*4);specs.append((dur,nf))
  off+=num*4
  for dur,nf in specs:
   frames=[]
   for _ in range(max(0,nf)):
    cols=[(0,0,0,0)]
    for _ in range(15):cols.append((d[off],d[off+1],d[off+2],255));off+=4
    frames.append(cols)
   anim.append(frames)
 return {'base':pals,'animated':animated,'specs':specs,'frames':anim}

def parse_bpc(path):
 d=open(path,'rb').read();cw,ch,nt,*rest=struct.unpack_from('<8H',d,0);slots=rest[:4];nc=rest[4]
 tiles=[bytes(32)]+[d[16+i*32:16+(i+1)*32] for i in range(nt-1)];off=16+(nt-1)*32;n=cw*ch;chunks=[[0]*n]
 for _ in range(nc-1):chunks.append(list(struct.unpack_from(f'<{n}H',d,off)));off+=n*2
 return {'chunk_width':cw,'chunk_height':ch,'base_tiles':tiles,'slot_tiles':slots,'chunks':chunks}

def parse_bpa(path):
 if not path or not os.path.exists(path):return None
 d=open(path,'rb').read();num=d[0];frames=struct.unpack_from('<h',d,2)[0]
 if num<=0 or frames<=0:return None
 durations=list(struct.unpack_from(f'<{frames}i',d,4));off=4+frames*4;data=[]
 for _ in range(frames):
  data.append([d[off+i*32:off+(i+1)*32] for i in range(num)]);off+=num*32
 if off>len(d):raise ValueError(f'BPA tronqué: {path}')
 return {'num_tiles':num,'num_frames':frames,'durations':durations,'tiles':data}

def decode_bma(path):
 d=open(path,'rb').read();Wt,Ht,tw,th,Wc,Hc=d[:6];nL,hD,hC=struct.unpack_from('<HhH',d,6);src=12;layers=[]
 for _ in range(nL):
  dst=[]
  for y in range(Hc):
   row=[];prev=dst[(y-1)*64:y*64] if y else [0]*64;k=0
   while k<Wc:
    cmd=d[src];src+=1
    if cmd>=0xC0:
     count=cmd-0xC0+1
     for _ in range(count):
      v=d[src]|d[src+1]<<8|d[src+2]<<16;src+=3;a,b=v&0xFFF,(v>>12)&0xFFF
      if y:a^=prev[len(row)];b^=prev[len(row)+1]
      row += [a,b]
     k+=count*2
    elif cmd>=0x80:
     count=cmd-0x80+1;v=d[src]|d[src+1]<<8|d[src+2]<<16;src+=3
     for _ in range(count):
      a,b=v&0xFFF,(v>>12)&0xFFF
      if y:a^=prev[len(row)];b^=prev[len(row)+1]
      row += [a,b]
     k+=count*2
    else:
     count=cmd+1
     for _ in range(count):row += [prev[len(row)],prev[len(row)+1]] if y else [0,0]
     k+=count*2
   dst += (row[:64]+[0]*64)[:64]
  layers.append(dst)
 return {'width_tiles':Wt,'height_tiles':Ht,'width_chunks':Wc,'height_chunks':Hc,'num_layers':nL,'has_data':hD,'collision_layers':hC,'layers':layers}

def _frame_at(slot,tick,animated):
 if not slot:return 0
 if not animated:return 0
 cycle=sum(max(1,x) for x in slot['durations']);pos=tick%cycle;acc=0
 for i,d in enumerate(slot['durations']):
  acc+=max(1,d)
  if pos<acc:return i
 return 0

def _palettes_at_tick(pal,tick):
 out=list(pal['base'])
 if not pal['animated']:return out
 for i,(dur,nf) in enumerate(pal['specs']):
  if nf>0 and pal['frames'][i]:out[i]=pal['frames'][i][(tick//max(1,dur))%nf]
 return out

def _period(pal,slots):
 periods=[1]
 for dur,nf in pal.get('specs',[]):
  if nf>0:periods.append(max(1,dur)*nf)
 for i,s in enumerate(slots[:2]):
  if s:periods.append(sum(max(1,x) for x in s['durations']))
 p=1
 for x in periods:p=math.lcm(p,x)
 return p

def render_map(dep,data_dir,output_dir,trace=None,max_ticks=None):
 pal=parse_bpl(os.path.join(data_dir,dep['bpl']+'.bpl'));bpc=parse_bpc(os.path.join(data_dir,dep['bpc']+'.bpc'));bma=decode_bma(os.path.join(data_dir,dep['bma']+'.bma'))
 names=[None]*4
 for name in dep.get('bpa',[]):
  # La convention Chunsoft suffixe les BPA par leur slot 1..4.
  try:idx=int(name[-1])-1
  except (ValueError,IndexError):idx=next((i for i,x in enumerate(names) if x is None),0)
  if 0<=idx<4:names[idx]=name
 slots=[parse_bpa(os.path.join(data_dir,n+'.bpa')) if n else None for n in names]
 for i,(need,slot) in enumerate(zip(bpc['slot_tiles'],slots)):
  if need and (not slot or slot['num_tiles']!=need):raise ValueError(f'BPA slot {i}: {need} tuiles attendues, {None if not slot else slot["num_tiles"]}')
 period=_period(pal,slots);ticks=range(period if max_ticks is None else min(period,max_ticks));files=[]
 os.makedirs(output_dir,exist_ok=True)
 for tick in ticks:
  tiles=list(bpc['base_tiles'])
  for i,need in enumerate(bpc['slot_tiles']):
   s=slots[i]
   if need:tiles.extend(s['tiles'][_frame_at(s,tick,i<2)])
  pals=_palettes_at_tick(pal,tick);img=Image.new('RGBA',(bma['width_tiles']*8,bma['height_tiles']*8),(0,0,0,255))
  for lay in reversed(bma['layers']):
   for cy in range(bma['height_chunks']):
    for cx in range(bma['width_chunks']):
     cid=lay[cy*64+cx]
     if cid<=0 or cid>=len(bpc['chunks']):continue
     for j,ent in enumerate(bpc['chunks'][cid]):
      ti=ent&0x3FF;hf=(ent>>10)&1;vf=(ent>>11)&1;pi=(ent>>12)&0xF
      if ti==0 or ti>=len(tiles):continue
      td=tiles[ti];palette=pals[pi%len(pals)];tx,ty=cx*bpc['chunk_width']+j%bpc['chunk_width'],cy*bpc['chunk_height']+j//bpc['chunk_width']
      for y in range(8):
       for x in range(4):
        byte=td[y*4+x]
        for k,ci in enumerate((byte&15,byte>>4)):
         if not ci:continue
         xx=7-(x*2+k) if hf else x*2+k;yy=7-y if vf else y;px,py=tx*8+xx,ty*8+yy
         if 0<=px<img.width and 0<=py<img.height:img.putpixel((px,py),palette[ci])
  out=os.path.join(output_dir,f'{dep["bpl"]}_Tick_{tick}.png');img.save(out);files.append(out)
 if trace is not None:trace.update({'bma_layers_consumed':bma['num_layers'],'bpa_slots_required':sum(x>0 for x in bpc['slot_tiles']),'bpa_slots_consumed':sum(x is not None for x in slots),'palette_animation_executed':pal['animated'],'period_ticks':period,'ticks_emitted':len(files),'source_files':[dep['bpl']+'.bpl',dep['bpc']+'.bpc',dep['bma']+'.bma']+[x+'.bpa' for x in dep.get('bpa',[])]})
 return files
# Compatibilité temporaire des anciens appelants.
def render_gba_map(base_name,pmdred_dir,output_dir):
 dep={'bpl':base_name,'bpc':base_name+'c','bma':base_name+'m','bpa':[base_name+'1'] if os.path.exists(os.path.join(pmdred_dir,base_name+'1.bpa')) else []}
 return render_map(dep,pmdred_dir,output_dir,max_ticks=512)
