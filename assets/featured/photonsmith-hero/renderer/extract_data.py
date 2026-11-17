#!/usr/bin/env python3
"""Extract only plotted retained data after verifying the original public source."""
import argparse,hashlib,json
from pathlib import Path
REVISION='13912d9d640938acf8ce299a152298666ae61d44'
SOURCE_SHA='bf63ba3ebec2013dde9f10cbd65fa438634d71abd1bbf504577701dbd8a23b1e'
PLOT_SHA='21c935558d8fe79e937e47c959f7d6288dc563c3671fc4440a196269b80055f7'
SOURCE_URL='https://github.com/nazeeh111/PhotonSmith/blob/'+REVISION+'/experiments/designs/interactive-refined-1550nm.json'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('original',type=Path,help='Downloaded original JSON from the pinned public source')
parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'data/plot-data.json')
args=parser.parse_args();raw=args.original.read_bytes()
if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('Refuse changed original source')
d=json.loads(raw)
payload={'source':{'revision':REVISION,'sha256':SOURCE_SHA,'url':SOURCE_URL},'geometry':d['geometry'],'result':{'material_index':d['result']['material_index'],'field':{k:d['result']['field'][k]for k in ['nx','nz','x','z','real','epsilon']},'spectrum':{k:d['result']['spectrum'][k]for k in ['wavelength','efficiency']}}}
b=json.dumps(payload,separators=(',',':'),allow_nan=False).encode()+b'\n'
if hashlib.sha256(b).hexdigest()!=PLOT_SHA:raise ValueError('Unexpected extraction identity')
args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_bytes(b)
print('Exact plotted-data extraction verified:',PLOT_SHA)
