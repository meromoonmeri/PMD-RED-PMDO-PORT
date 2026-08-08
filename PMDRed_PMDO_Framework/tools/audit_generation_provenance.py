#!/usr/bin/env python3
"""Interdit toute image externe dans les producteurs d'assets PMDO."""
from pathlib import Path
import ast,re,sys
ROOT=Path(__file__).resolve().parents[2]
FORBIDDEN=('spriters-resource','rtrb','screenshot','capture_emulator','reference.png','reference_png')
producers=[];errors=[]
for p in sorted(ROOT.rglob('*.py')):
 if p.name.startswith('audit_') or any(x in p.parts for x in ('.git','validator','validate')):continue
 s=p.read_text(errors='ignore');low=s.lower()
 produces=any(x in s for x in ('.rsground','.rsmap','.tile')) or 'write_tile' in low or 'make_rsground' in low
 if not produces:continue
 producers.append(p)
 for token in FORBIDDEN:
  if token in low:errors.append(f'{p.relative_to(ROOT)}: référence interdite {token}')
 try:tree=ast.parse(s)
 except SyntaxError as exc:errors.append(f'{p.relative_to(ROOT)}: syntaxe {exc}');continue
 for n in ast.walk(tree):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='open':
   # Image.open(BytesIO(...)) décode un blob produit depuis BPC/BPA : autorisé.
   if isinstance(n.func.value,ast.Name) and n.func.value.id=='Image' and n.args:
    arg=ast.unparse(n.args[0])
    if 'BytesIO' not in arg:errors.append(f'{p.relative_to(ROOT)}: Image.open source fichier interdite: {arg}')
print('AUDIT PROVENANCE GENERATION')
print(f'{len(producers)} producteurs inspectés')
for e in errors:print('ERREUR:',e)
print(f'RESULTAT: {len(errors)} erreur(s)')
raise SystemExit(1 if errors else 0)
