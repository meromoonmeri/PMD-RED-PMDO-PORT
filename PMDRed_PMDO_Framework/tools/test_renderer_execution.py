#!/usr/bin/env python3
"""Tests d'exécution réels sur les données pret/pmd-red."""
from pathlib import Path
import json,sys,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'PMDRed_PMDO_Framework/converters/grounds'))
import visual_extractor as ve
pret=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/pmd-red');deps=json.load(open(ROOT/'map_dependencies.json'));tmp=Path(tempfile.mkdtemp())
try:
 cases={
  'MAP_FILE_ID_PELIPPER_POST_OFFICE':lambda t:t['bma_layers_consumed']==2,
  'MAP_FILE_ID_TEAM_BASE_PIKACHU_CONSTRUCTION':lambda t:t['bpa_slots_required']==2 and t['bpa_slots_consumed']==2,
  'MAP_FILE_ID_POKEMON_SQUARE':lambda t:t['palette_animation_executed'] and t['bpa_slots_consumed']==1,
 }
 for key,check in cases.items():
  trace={};files=ve.render_map(deps[key],str(pret/'data/map_bg'),str(tmp),trace,max_ticks=2)
  assert files and check(trace),(key,trace)
  print('OK',key,trace)
finally:shutil.rmtree(tmp)
