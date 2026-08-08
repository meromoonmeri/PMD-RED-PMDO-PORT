#!/usr/bin/env python3
from pathlib import Path
import tempfile,struct,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'PMDRed_PMDO_Framework/extractors'))
from dungeon_archive_extractor import extract,find_archive_in_rom,ROM_BASE
with tempfile.TemporaryDirectory() as td:
 rom=bytearray(0x400);a=0x100;entries=0x120
 rom[a:a+8]=b'PksDir0\0';struct.pack_into('<II',rom,a+8,2,ROM_BASE+entries)
 rom[0x180:0x189]=b'mapparam\0';rom[0x190:0x197]=b'b00fon\0'
 rom[0x200:0x220]=b'AT4PN\x04\x00DATA'+bytes(21);rom[0x240:0x250]=b'AT4PN\x03\x00XYZ'+bytes(6)
 struct.pack_into('<II',rom,entries,ROM_BASE+0x190,ROM_BASE+0x240)
 struct.pack_into('<II',rom,entries+8,ROM_BASE+0x180,ROM_BASE+0x200)
 rp=Path(td)/'rom.gba';rp.write_bytes(rom);assert find_archive_in_rom(rp)==ROM_BASE+a;rows=extract(rp,ROM_BASE+a,Path(td)/'out')
 assert len(rows)==2 and (Path(td)/'out/mapparam').exists() and (Path(td)/'out/b00fon').exists()
 print('OK archive FileArchive extraite',[(x['name'],x['bytes']) for x in rows])
