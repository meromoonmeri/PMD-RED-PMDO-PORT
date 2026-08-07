#!/usr/bin/env python3
"""Audit comportemental: source requise -> exécution observée -> validation oracle."""
from pathlib import Path
import argparse,hashlib,json,sys,tempfile,shutil
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'PMDRed_PMDO_Framework/converters/grounds'))
import visual_extractor as ve
CASES=('MAP_FILE_ID_SQUARE','MAP_FILE_ID_POKEMON_SQUARE','MAP_FILE_ID_PELIPPER_POST_OFFICE','MAP_FILE_ID_TEAM_BASE_PIKACHU_CONSTRUCTION','MAP_FILE_ID_SUMMIT_SUNSET','MAP_FILE_ID_SKY_TOWER_END')

def black_ratio(path):
 im=Image.open(path).convert('RGB');px=list(im.getdata());return sum(max(p)<16 for p in px)/len(px)
def compare(a,b):
 ia=Image.open(a).convert('RGBA');ib=Image.open(b).convert('RGBA')
 if ia.size!=ib.size:return {'validated':False,'reason':'size','generated':ia.size,'oracle':ib.size}
 d=ImageChops.difference(ia,ib);bad=sum(p!=(0,0,0,0) for p in d.getdata());return {'validated':bad==0,'different_pixels':bad,'total_pixels':ia.width*ia.height}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pret',default='/tmp/pmd-red');ap.add_argument('--oracle');ap.add_argument('--out',default='behavioral_audit.json');a=ap.parse_args()
 deps=json.load(open(ROOT/'map_dependencies.json'));data=Path(a.pret)/'data/map_bg';tmp=Path(tempfile.mkdtemp());rows=[]
 try:
  for key in CASES:
   dep=deps[key];base=dep['bpl'];req={'bma_layers':None,'bpa_slots':len(dep['bpa']),'palette_animation':None}
   bma=ve.decode_bma(str(data/(dep['bma']+'.bma')));req['bma_layers']=bma['num_layers']
   raw=(data/(dep['bpl']+'.bpl')).read_bytes();req['palette_animation']=bool(raw[2]) if len(raw)>2 else None
   status={'map_id':key,'source':dep,'requirements':req,'execution':{},'validation':{'validated':False,'reason':'oracle_absent'}}
   try:
    trace={};files=ve.render_map(dep,str(data),str(tmp),trace,max_ticks=16);status['execution']={'ran':True,'frames_emitted':len(files),'files':[Path(x).name for x in files],'black_ratio':[black_ratio(x) for x in files],**trace}
    if a.oracle:
     ref=Path(a.oracle)/(base+'_Frame_0.png')
     if ref.exists():status['validation']=compare(files[0],ref)
   except Exception as exc:status['execution']={'ran':False,'error':repr(exc)}
   rows.append(status)
 finally:shutil.rmtree(tmp)
 report={'schema':1,'cases':rows,'summary':{'executed':sum(x['execution'].get('ran',False) for x in rows),'validated':sum(x['validation'].get('validated',False) for x in rows)}}
 Path(a.out).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['summary']));
 # Échec tant que tous les cas requis ne sont pas exécutés ET validés.
 raise SystemExit(0 if report['summary']=={'executed':len(rows),'validated':len(rows)} else 1)
if __name__=='__main__':main()
