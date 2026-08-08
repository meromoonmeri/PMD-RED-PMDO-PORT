#!/usr/bin/env python3
"""Inventory canonical pmd-sky MAP_BG and exclusive MAP_BG assets from an NDS ROM hack."""
from pathlib import Path
import argparse,hashlib,json
from ndspy.rom import NintendoDSRom
EXT={'.bma','.bpc','.bpl','.bpa'}
def sha(b):return hashlib.sha256(b).hexdigest()
def rom_files(path):
 r=NintendoDSRom.fromFile(str(path));out={}
 def walk(folder,p=''):
  for i,n in enumerate(folder.files):
   full=p+n
   if full.upper().startswith('MAP_BG/') and Path(n).suffix.lower() in EXT:out[full.split('/',1)[1].lower()]=r.files[folder.firstID+i]
  for n,sub in folder.folders:walk(sub,p+n+'/')
 walk(r.filenames);return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pret',required=True);ap.add_argument('--romhack',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();pd=Path(a.pret)/'files/MAP_BG';canon={p.name.lower():p.read_bytes() for p in pd.iterdir() if p.suffix.lower() in EXT};hack=rom_files(a.romhack)
 exclusive=sorted(set(hack)-set(canon));changed=sorted(n for n in set(hack)&set(canon) if sha(hack[n])!=sha(canon[n]));same=sorted(n for n in set(hack)&set(canon) if sha(hack[n])==sha(canon[n]))
 def bases(names):return sorted({Path(n).stem.rstrip('1234') for n in names if n.endswith('.bma')})
 out={'schema':1,'canonical_source':'pret/pmd-sky','romhack_source':str(a.romhack),'counts':{'canonical_files':len(canon),'romhack_files':len(hack),'identical_files':len(same),'changed_files':len(changed),'exclusive_files':len(exclusive),'canonical_bma':sum(n.endswith('.bma') for n in canon),'romhack_bma':sum(n.endswith('.bma') for n in hack),'exclusive_bma':sum(n.endswith('.bma') for n in exclusive)},'exclusive_files':[{'name':n,'bytes':len(hack[n]),'sha256':sha(hack[n])} for n in exclusive],'changed_files':[{'name':n,'canonical_sha256':sha(canon[n]),'romhack_sha256':sha(hack[n])} for n in changed],'exclusive_map_bases':bases(exclusive)}
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['counts']))
if __name__=='__main__':main()
