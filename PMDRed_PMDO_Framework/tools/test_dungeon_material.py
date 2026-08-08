#!/usr/bin/env python3
from pathlib import Path
import sys,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'PMDRed_PMDO_Framework/converters/grounds'))
from dungeon_material import decompress_at,DungeonArchive,DungeonArchiveMissing
# Mode AT non compressé: preuve comportementale minimale du lecteur.
payload=b'pipeline-chunsoft';src=b'AT4PN'+bytes((len(payload)&255,len(payload)>>8))+payload
assert decompress_at(src)==payload
try:DungeonArchive('/definitely/missing').read('b00fon')
except DungeonArchiveMissing:pass
else:raise AssertionError('archive manquante non détectée')
print('OK décompression AT-N et refus archive absente')
