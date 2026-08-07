#!/usr/bin/env python3
"""Validation statique 245/245 sans ROM ni runtime PMDO."""
from pathlib import Path
import argparse,hashlib,json,re,sys,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'PMDRed_PMDO_Framework/converters/grounds'))
import visual_extractor as ve
DUNGEON_BACKED={'D01P02','D02P02','D03P02','D04P02','D05P02','D06P02','D06P03','D09P02','D09P03','D10P02','D10P03','D11P02','D11P03','D12P02','D12P04','D13P02','D13P03','D14P01','D15P01','D16P01','D17P01','D18P01','D19P01','D20P01','D21P01','D23P01','D25P01'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pret',default='/tmp/pmd-red');ap.add_argument('--out',default='static_readiness.json');a=ap.parse_args();pret=Path(a.pret);data=pret/'data/map_bg';deps=json.load(open(ROOT/'map_dependencies.json'));rows=[];errors=[]
 for key,dep in deps.items():
  files={k:data/(v+'.'+k) for k,v in [('bpl',dep['bpl']),('bpc',dep['bpc']),('bma',dep['bma'])]};bpas=[data/(x+'.bpa') for x in dep['bpa']]
  missing=[str(p) for p in [*files.values(),*bpas] if not p.exists()]
  row={'map_id':key,'resources':dep,'missing':missing,'hashes':{},'static':{},'status':'error' if missing else 'ready_standard'}
  if not missing:
   try:
    pal=ve.parse_bpl(str(files['bpl']));bpc=ve.parse_bpc(str(files['bpc']));bma=ve.decode_bma(str(files['bma']));slots={int(p.stem[-1])-1:ve.parse_bpa(str(p)) for p in bpas}
    slot_errors=[]
    for i,n in enumerate(bpc['slot_tiles']):
     s=slots.get(i)
     if n and (not s or s['num_tiles']!=n):slot_errors.append({'slot':i,'expected':n,'actual':None if not s else s['num_tiles']})
    row['hashes']={p.name:sha(p) for p in [*files.values(),*bpas]};row['static']={'size_tiles':[bma['width_tiles'],bma['height_tiles']],'layers':bma['num_layers'],'collision_layers':bma['collision_layers'],'has_data_layer':bma['has_data'],'base_tiles':len(bpc['base_tiles']),'chunks':len(bpc['chunks']),'bpa_slot_tiles':bpc['slot_tiles'],'bpa_slot_errors':slot_errors,'palette_animation':pal['animated'],'palette_count':len(pal['base']),'markers_source_present':(pret/'src/data/ground'/f'ground_data_{dep["bpl"].lower()}_station.h').exists()}
    if slot_errors:row['status']='error';errors.append(f'{key}: BPA slots {slot_errors}')
    if dep['bpl'].upper() in DUNGEON_BACKED:row['status']='waiting_rom_dungeon_blobs'
   except Exception as exc:row['status']='error';row['error']=repr(exc);errors.append(f'{key}: {exc!r}')
  else:errors.append(f'{key}: fichiers absents')
  rows.append(row)
 summary={'maps':len(rows),'ready_standard':sum(r['status']=='ready_standard' for r in rows),'waiting_rom_dungeon_blobs':sum(r['status']=='waiting_rom_dungeon_blobs' for r in rows),'errors':sum(r['status']=='error' for r in rows),'runtime_capture':'deferred','pixel_comparison':'deferred','pmdo_runtime':'deferred'}
 Path(a.out).write_text(json.dumps({'schema':1,'source':'pret/pmd-red','external_graphics_used':False,'summary':summary,'maps':rows},indent=2)+'\n');print(json.dumps(summary));
 raise SystemExit(1 if errors else 0)
if __name__=='__main__':main()
