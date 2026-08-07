#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import tempfile,sys,json,struct
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'PMDRed_PMDO_Framework/converters/grounds'))
from pmdo_ground_writer import write_ground
with tempfile.TemporaryDirectory() as td:
 root=Path(td);p=root/'Data/Ground/test.rsground';a=Image.new('RGBA',(16,16),(255,0,0,255));b=Image.new('RGBA',(16,16),(0,0,255,255));info=write_ground(p,'test','Test_Base',[a,b],[0,1,0,1]);o=json.load(open(p))['Object'];raw=(root/'Content/Tile/Test_Base.tile').read_bytes();size,count=struct.unpack_from('<II',raw)
 assert info=={'width':2,'height':2,'frames':2} and size==8 and count==8 and len(o['Layers'][0]['Tiles'][0][0]['Layers'][0]['Frames'])==2
 print('OK writer PMDO animé',info,'tile entries',count)
