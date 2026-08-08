#!/usr/bin/env python3
"""Offline, deterministic renderer for native PMDO .rsground + .tile files.

It executes GroundMap tile layers and their local animation timing without
RogueEssence. In --strict mode it refuses unsupported visible decorations or
background animations instead of emitting a misleading validation image.
"""
from __future__ import annotations
from pathlib import Path
import argparse,io,json,struct,sys
from PIL import Image

class TilePackage:
 def __init__(self,path:Path):
  raw=path.read_bytes();self.size,count=struct.unpack_from('<II',raw);self.cells={}
  for i in range(count):
   key,off=struct.unpack_from('<QQ',raw,8+i*16);x,y=key&0xffffffff,key>>32
   if (x,y) in self.cells:continue
   n=struct.unpack_from('<q',raw,off)[0]
   if n<0 or off+8+n>len(raw):raise ValueError(f'{path}: entrée PNG tronquée')
   self.cells[x,y]=Image.open(io.BytesIO(raw[off+8:off+8+n])).convert('RGBA').copy()

def load_json(path):return json.load(open(path,encoding='utf-8-sig'))['Object']
def sheets_of(obj):
 return {f.get('Sheet') for layer in obj.get('Layers',[]) for col in layer.get('Tiles',[]) for cell in col for sub in cell.get('Layers',[]) for f in sub.get('Frames',[]) if f.get('Sheet')}
def render(path:Path,tile_dir:Path,tick:int=0,strict:bool=True):
 o=load_json(path);layers=[x for x in o.get('Layers',[]) if x.get('Visible',True)]
 if not layers:raise ValueError(f'{path}: aucune couche visible')
 warnings=[]
 for deco in o.get('Decorations',[]):
  if deco.get('Visible',True) and deco.get('Anims'):warnings.append(f'décorations visibles non rendues: {deco.get("Name","")}')
 bg=o.get('Background',{});anim=bg.get('BGAnim',{})
 if anim.get('AnimIndex'):warnings.append('Background.BGAnim externe non rendu')
 if strict and warnings:raise ValueError('; '.join(warnings))
 pkgs={}
 for sheet in sheets_of(o):
  p=tile_dir/(sheet+'.tile')
  if not p.exists():raise FileNotFoundError(f'{path.name}: sheet absent {p}')
  pkgs[sheet]=TilePackage(p)
 widths=[len(x.get('Tiles',[])) for x in layers];heights=[len(x['Tiles'][0]) if x.get('Tiles') else 0 for x in layers]
 W,H=max(widths),max(heights);cell_px=8*int(o.get('TexSize',1));canvas=Image.new('RGBA',(W*cell_px,H*cell_px),(0,0,0,255))
 for layer in sorted(layers,key=lambda x:x.get('Layer',0)):
  tiles=layer['Tiles']
  for x,col in enumerate(tiles):
   for y,cell in enumerate(col):
    for sub in cell.get('Layers',[]):
     fs=sub.get('Frames',[])
     if not fs:continue
     fl=max(1,int(sub.get('FrameLength',1)));fr=fs[(tick//fl)%len(fs)];sheet=fr.get('Sheet')
     if not sheet:continue
     loc=fr['TexLoc'];src=pkgs[sheet].cells.get((loc['X'],loc['Y']))
     if src is None:raise KeyError(f'{sheet}: TexLoc absent {loc}')
     if src.size!=(cell_px,cell_px):raise ValueError(f'{sheet}: cellule {src.size}, Ground attend {(cell_px,cell_px)}')
     canvas.alpha_composite(src,(x*cell_px,y*cell_px))
 return canvas,warnings

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ground-dir',required=True);ap.add_argument('--tile-dir',required=True);ap.add_argument('--out',default='debug/render_ground');ap.add_argument('--id',action='append');ap.add_argument('--tick',type=int,default=0);ap.add_argument('--allow-unsupported',action='store_true');a=ap.parse_args()
 gd,td,out=Path(a.ground_dir),Path(a.tile_dir),Path(a.out);paths=[gd/(x+'.rsground') for x in a.id] if a.id else sorted(gd.glob('*.rsground'));ok=[];errors=[]
 for p in paths:
  try:
   im,w=render(p,td,a.tick,not a.allow_unsupported);dest=out/(p.stem+'.png');dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,optimize=True);ok.append({'id':p.stem,'png':str(dest),'width':im.width,'height':im.height,'warnings':w});print('OK',p.stem,im.size)
  except Exception as e:errors.append({'id':p.stem,'error':str(e)});print('ERROR',p.stem,e,file=sys.stderr)
 report={'renderer':'PMDO Ground offline tile-layer renderer','tick':a.tick,'rendered':ok,'errors':errors,'runtime_capture':False,'pixel_comparison':False};out.mkdir(parents=True,exist_ok=True);(out/'render_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'rendered':len(ok),'errors':len(errors)}));raise SystemExit(bool(errors))
if __name__=='__main__':main()
