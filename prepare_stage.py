"""Prepare an isolated stage from a caller-supplied ok-script source snapshot."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--framework-source', type=Path, required=True, help='Path to the ok/ Python package')
parser.add_argument('--framework-license', type=Path, required=True)
parser.add_argument('--font', type=Path, required=True, help='A Chinese TrueType Collection (.ttc) font')
parser.add_argument('--font-license', type=Path, required=True)
parser.add_argument('--stage', type=Path, default=root/'stage')
args = parser.parse_args()
expected = json.loads((root/'framework-source-sha256.json').read_text())
for name, digest in expected.items():
    path = args.framework_source/name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        parser.error('Framework snapshot mismatch: '+name+'; use the recorded version or review the patch first.')
for path in (args.framework_license, args.font, args.font_license):
    if not path.is_file():
        parser.error('Missing input: '+str(path))
if args.font.suffix.lower() != '.ttc':
    parser.error('The offline fixture currently requires a .ttc Chinese font')
stage = args.stage.resolve()
if stage.exists():
    parser.error('Stage already exists; choose a fresh directory')
stage.mkdir(parents=True)
shutil.copytree(root/'code',stage/'code',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in expected:
    target = stage/'vendor/ok'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(args.framework_source/name,target)
shutil.copy2(args.framework_license,stage/'vendor/LICENSE-ok-script.txt')
fonts=stage/'fonts/usr/share/fonts/truetype'
fonts.mkdir(parents=True)
shutil.copy2(args.font,fonts/args.font.name)
shutil.copy2(args.font_license,stage/'fonts/LICENSE-font.txt')
manifest={p.relative_to(stage).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
          for p in stage.rglob('*.py')}
(stage/'source-manifest.json').write_text(json.dumps({'files':manifest},indent=2))
subprocess.run([sys.executable,str(stage/'code/linux/patch_framework.py'),str(stage)],check=True)
print('Prepared:',stage)
