#!/usr/bin/env python3
"""Conversion réelle des cartes standards pret/pmd-red vers PMDO."""
from pathlib import Path
import argparse,json,sys,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'PMDRed_PMDO_Framework/converters/grounds'),str(ROOT/'PMDRed_PMDO_Framework/tools/convert')]
import visual_extractor as ve
from pmdo_ground_writer import write_ground
from provenance import write_manifest
from convert_pmdred_batch import parse_station,mk_marker
DUNGEON_BACKED={'D01P02','D02P02','D03P02','D04P02','D05P02','D06P02','D06P03','D09P02','D09P03','D10P02','D10P03','D11P02','D11P03','D12P02','D12P04','D13P02','D13P03','D14P01','D15P01','D16P01','D17P01','D18P01','D19P01','D20P01','D21P01','D23P01','D25P01'}
def collision(path):
 from skytemple_files.common.types.file_types import FileType
 b=FileType.BMA.deserialize(Path(path).read_bytes());c=b.collision
 if not c:return [False]*(b.map_width_camera*b.map_height_camera)
 return list(collision for collision in c)
def entities(src):
 try:lives,effs=parse_station(src)
 except Exception:return [mk_marker('Main_Entrance_Marker',0,0,4)],[]
 marks=[];sp=[];mate=1
 for kind,x,y in lives:
  x,y=x*8,y*8
  if kind==0:marks.append(mk_marker('Main_Entrance_Marker',x,y,4))
  elif kind in (4,10,11,34):marks.append(mk_marker(f'TEAMMATE_{mate}_Marker',x,y,4));mate+=1
  elif kind>=80:marks.append(mk_marker('Boss_Marker' if not any(m['EntName']=='Boss_Marker' for m in marks) else f'PNJ_Marker_{kind}',x,y,4))
 for i,(x,y) in enumerate(effs):marks.append(mk_marker('Cutscene_Marker' if i==0 else f'Cutscene_Marker_{i+1}',x*8,y*8,4))
 if not any(x['EntName']=='Main_Entrance_Marker' for x in marks):marks.append(mk_marker('Main_Entrance_Marker',0,0,4))
 return marks,sp
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pret',default='/tmp/pmd-red');ap.add_argument('--out',required=True);ap.add_argument('--map-id',action='append');ap.add_argument('--max-period',type=int,default=4096);ap.add_argument('--limit',type=int);a=ap.parse_args();pret=Path(a.pret);data=pret/'data/map_bg';deps=json.load(open(ROOT/'map_dependencies.json'));keys=a.map_id or list(deps);done=[];blocked=[]
 for key in keys:
  if a.limit and len(done)>=a.limit:break
  dep=deps[key]
  if dep['bpl'].upper() in DUNGEON_BACKED:blocked.append((key,'dungeon_blobs'));continue
  root=Path(a.out);asset=dep['bpl'].lower();gp=root/'Data/Ground'/f'{asset}.rsground'
  if gp.exists() and (root/'Manifests'/(asset+'.json')).exists():done.append(key);print('SKIP',key);continue
  timeline=ve.inspect_timeline(dep,str(data))
  if timeline['period_ticks']>a.max_period:blocked.append((key,f'period_{timeline["period_ticks"]}'));print('BLOCK',key,blocked[-1][1]);continue
  tmp=Path(tempfile.mkdtemp())
  try:
   trace={};files=ve.render_map(dep,str(data),str(tmp),trace,max_ticks=a.max_period)
   from PIL import Image
   frames=[Image.open(x).convert('RGBA').copy() for x in files];col=collision(data/(dep['bma']+'.bma'));marks,sp=entities(dep['bpl']);asset=dep['bpl'].lower();root=Path(a.out);gp=root/'Data/Ground'/f'{asset}.rsground';info=write_ground(gp,asset,asset+'_Base',frames,col,marks,sp)
   inputs={'bpl':data/(dep['bpl']+'.bpl'),'bpc':data/(dep['bpc']+'.bpc'),'bma':data/(dep['bma']+'.bma')}
   for i,n in enumerate(dep['bpa']):inputs[f'bpa_{i}']=data/(n+'.bpa')
   outputs={'ground':gp,'tile':root/'Content/Tile'/(asset+'_Base.tile')};write_manifest(key,inputs,outputs,{**trace,**info},root/'Manifests'/(asset+'.json'));done.append(key);print('OK',key,info)
  finally:shutil.rmtree(tmp)
 summary={'converted':done,'blocked':blocked};Path(a.out,'conversion_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({'converted':len(done),'blocked':len(blocked)}))
if __name__=='__main__':main()
