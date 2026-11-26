"""Generate a logical port drawing from SiliconPilot's frozen two-circuit case."""
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile

source = Path(sys.argv[1])
out = Path(__file__).resolve().parent
bundle = source/'docs/presentation/compiled-example.zip'
assert hashlib.sha256(bundle.read_bytes()).hexdigest() == 'c412cde4a1dec54ef69a2df56bb96e41856c117784327cf60129f79071fcf4ed'
with ZipFile(bundle) as zipfile:
    layers = json.loads(zipfile.read('direct/weights.json'))['layers']
    assert layers == json.loads(zipfile.read('overlapped/weights.json'))['layers']
features = json.loads((source/'models/dataset_manifest.json').read_text())['features']
s = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 500" role="img" aria-labelledby="title desc">
<title id="title">Banknote classifier, exploded logical network</title>
<desc id="desc">Four standardized features connect to eight hidden ReLU units and two output scores. Each path is one compiled coefficient. Positive weights are cobalt, negative weights are slate and zero coefficients are dotted. Path width scales with magnitude.</desc>
<defs>
<linearGradient id="skin" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox"><stop stop-color="#dae3ee"/><stop offset=".12" stop-color="#f6f9fc"/><stop offset=".63" stop-color="#fff"/><stop offset="1" stop-color="#e4eaf4"/></linearGradient>
<linearGradient id="core"><stop stop-color="#163396"/><stop offset=".5" stop-color="#325de2"/><stop offset="1" stop-color="#163285"/></linearGradient>
<filter id="shadow" x="-.4" y="-.35" width="1.8" height="1.8"><feGaussianBlur stdDeviation="4"/></filter>
</defs>
<style>text{font-family:Arial,Helvetica,sans-serif;fill:#101820}.id{font-family:Menlo,monospace}.trace{fill:none;stroke-linecap:round}</style>''']

def path(d, attrs):
    s.append(f'<path d="{d}" {attrs}/>')
def text(x,y,label,size=13,attrs=''):
    s.append(f'<text x="{x}" y="{y}" font-size="{size}" {attrs}>{label}</text>')
def polygon(points,fill,stroke='none',attrs=''):
    coords=' '.join(f'{x:.1f},{y:.1f}' for x,y in points)
    s.append(f'<polygon points="{coords}" fill="{fill}" stroke="{stroke}" {attrs}/>')
def coord(origin,i):
    return origin[0]-i*6,origin[1]+i*38
origins=[(154,206),(400,95),(634,156)]
counts=[4,8,2]

# The plates lie on parallel skew axes. Their thickness has no circuit meaning.
for stage,(origin,count) in enumerate(zip(origins,counts)):
    x,y=origin
    u,v=coord(origin,count-1)
    half=27 if stage==1 else 25
    points=[(x-half+5,y-23),(x+half+5,y-23),(u+half-5,v+23),(u-half-5,v+23)]
    drop=[(a+9,b+10) for a,b in points]
    polygon(drop,'#74859f',attrs='opacity=".22" filter="url(#shadow)"')
    polygon([points[1],(points[1][0]+5,points[1][1]+5),(points[2][0]+5,points[2][1]+5),points[2]],'#8699b5')
    polygon([points[2],(points[2][0]+5,points[2][1]+5),(points[3][0]+5,points[3][1]+5),points[3]],'#aab9cb')
    polygon(points,'url(#core)' if stage==1 else 'url(#skin)','#304bb0' if stage==1 else '#9aaec3')
    for i in range(count):
        xx,yy=coord(origin,i)
        polygon([(xx-half+5,yy+4),(xx+half-4,yy+4),(xx+half-6,yy+12),(xx-half+3,yy+12)],'#173695' if stage==1 else '#cbd6e1')
        path(f'M{xx-half+4} {yy+12}h{2*half-10}', 'stroke="#ffffff" stroke-opacity=".65"')
    for end_i,offset in [(0,-16),(count-1,17)]:
        xx,yy=coord(origin,end_i)
        for dx in [-17,17]:
            path(f'M{xx+dx} {yy+offset}h4','stroke="#8fa1b9" stroke-width="1.4"')

connections=[]
for layer_index,layer in enumerate(layers):
    for dest,row in enumerate(layer['weights']):
        for src,w in enumerate(row):
            x,y=coord(origins[layer_index],src)
            X,Y=coord(origins[layer_index+1],dest)
            sign='zero' if w==0 else 'positive' if w>0 else 'negative'
            connections.append((abs(w),w,layer_index,src,dest,x+22,y,X-22,Y,sign))
assert len(connections)==48
for magnitude,w,layer,src,dest,x,y,X,Y,sign in sorted(connections):
    c={'zero':'#8d9eb4','positive':'#234edf','negative':'#344759'}[sign]
    width=.82 if not w else 1.12+3.25*(magnitude/80)**.65
    alpha=.64 if not w else .75+ .23*magnitude/80
    d=f'M{x} {y} C{x+65} {y-14} {X-59} {Y+13} {X} {Y}'
    if w:
        path(d,f'class="trace" stroke="#f6f8fb" stroke-width="{width+1.9:.2f}" opacity=".89"')
    dash='stroke-dasharray="1 4"' if not w else ''
    s.append(f'<g data-layer="{layer}" data-source="{src}" data-target="{dest}" data-weight="{w}"><title>{src} → {dest}, weight {w}</title>')
    path(d,f'class="trace" stroke="{c}" stroke-width="{width:.2f}" opacity="{alpha:.2f}" {dash}')
    s.append('</g>')

for stage,(origin,count) in enumerate(zip(origins,counts)):
    for i in range(count):
        x,y=coord(origin,i)
        for dx in ([22] if stage==0 else [-22] if stage==2 else [-22,22]):
            s.append(f'<ellipse cx="{x+dx}" cy="{y}" rx="4" ry="3.1" fill="#f6f8fb" stroke="#263954" stroke-width="1.5"/>')
        text(x,y+3,['x','h','s'][stage]+str(i),12,'text-anchor="middle" class="id" font-weight="700" style="fill:white"' if stage==1 else 'text-anchor="middle" class="id" font-weight="700"')
        if stage==0:
            text(x-37,y+4,features[i],14,'text-anchor="end"')
for x,y,num,name in [(42,110,'4','inputs'),(309,35,'8','hidden'),(575,86,'2','scores')]:
    text(x,y,num,31,'font-weight="750"')
    text(x+25,y,name,17,'font-weight="650"')
path('M68 122H113l26 45M333 48h45l18 18M602 99h22l8 27','fill="none" stroke="#8798ab" stroke-width="1"')
text(46,426,'Logical connections',15,'font-weight="700"')
for x,c,title,dash in [(46,'#234edf','Positive',''),(199,'#344759','Negative',''),(357,'#8d9eb4','Zero','stroke-dasharray="1 4"')]:
    path(f'M{x} 463h32',f'class="trace" stroke="{c}" stroke-width="2.6" {dash}')
    text(x+42,468,title,14)
text(487,468,'Width = weight magnitude',14,'style="fill:#516176"')
(out/'network.svg').write_text('\n'.join(s+['</svg>'])+'\n')
