"""Regenerate the three evidence views: python3 generate.py PATH_TO_SILICONPILOT."""
import csv
import hashlib
import json
import sys
import zipfile
from pathlib import Path

out = Path(__file__).resolve().parent
src = Path(sys.argv[1]) / 'docs/presentation'
record = json.loads((src/'execution.json').read_text())
bundle = (src/'compiled-example.zip').read_bytes()
assert hashlib.sha256(bundle).hexdigest() == record['bundleSHA256']
z = zipfile.ZipFile(src/'compiled-example.zip')
weights = json.loads(z.read('direct/weights.json'))['layers']
assert weights == json.loads(z.read('overlapped/weights.json'))['layers']
schedule = list(csv.DictReader((src/'schedule.csv').open()))
blue, ink, paper = '#244fe2', '#101820', '#f6f8fb'

def start(title, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 590" role="img" aria-labelledby="t d"><title id="t">{title}</title><desc id="d">{desc}</desc><style>text{{font-family:Arial,Helvetica,sans-serif;fill:{ink}}}.mono{{font-family:ui-monospace,Menlo,monospace}}</style><rect width="760" height="590" fill="{paper}"/>']

def label(x,y,value,size=16,color=ink,weight=500,mono=False):
    a.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" style="fill:{color}" class="{("mono" if mono else "")}">{value}</text>')

def line(x,y,X,Y,c,w=1,dash=''):
    a.append(f'<path d="M{x:.2f} {y:.2f}L{X:.2f} {Y:.2f}" fill="none" stroke="{c}" stroke-width="{w}" stroke-dasharray="{dash}"/>')

def poly(points,fill,edge=paper):
    coords=' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
    a.append(f'<polygon points="{coords}" fill="{fill}" stroke="{edge}" stroke-width="1.1" stroke-linejoin="round"/>')

def prism(x,y,dx,dy,depth,h,top,front,side):
    p=[(x,y),(x+dx,y+dy),(x+dx-depth,y+dy+depth*.48),(x-depth,y+depth*.48)]
    q=[(u,v-h) for u,v in p]
    poly([p[2],p[3],q[3],q[2]],front)
    poly([p[1],p[2],q[2],q[1]],side)
    poly(q,top)

def footer(title,caption):
    line(36,506,724,506,'#a9b8ca')
    label(36,544,title,29,ink,700);label(36,574,caption,17,'#405269')
def save(name):
    (out/f'{name}.svg').write_text('\n'.join(a+['</svg>'])+'\n')

a=start('Classifier weight matrices','The 32 hidden and 16 output weights in the compiled classifier. Column heights show absolute quantized weight. Blue columns are positive, ink negative and flat white tiles zero.')
label(36,48,'Quantized weights',29,ink,700)
label(36,80,'4 inputs  /  8 hidden units  /  2 scores',18,'#405269',500,True)
# Back-to-front matrix rows and columns. Shared height scale for both layers.
for idx,(ox,oy,sx,sy,dep) in enumerate([(219,185,46,21,21),(560,269,21,10,20)]):
    matrix=weights[idx]['weights']
    for r,row in enumerate(matrix):
        for c,val in enumerate(row):
            x,y=ox+c*sx-r*dep,oy+c*sy+r*dep*.48
            colors=('#779bff',blue,'#1436ab') if val>0 else ('#6d8196','#354b60',ink) if val<0 else ('#ffffff','#d6dfeb','#bdcbda')
            prism(x,y,sx,sy,dep,max(2,abs(val)*1.42),*colors)
label(43,409,'4 × 8',48,ink,700)
label(45,438,'Input → hidden',19)
label(490,423,'8 × 2',43,ink,700)
label(490,453,'Hidden → scores',19)
line(46,380,115,339,'#8495a8',1.5)
line(497,382,540,338,'#8495a8',1.5)
footer('48 learned weights','Height = absolute weight.  Blue = positive.  Slate = negative.  Flat white = zero.')
save('model')

a=start('Two schedules for one classifier','First core output after 49 clocks with one direct lane versus 27 clocks with two registered-product lanes. Each tile is one clock. The handoff takes one clock in both circuits.')
label(36,48,'Core schedule',29,ink,700)
label(36,80,'One tile per clock, both rows on the same time scale.',18,'#405269')
for i,row in enumerate(schedule):
    y=184+i*177
    label(40,y-32,['1 lane · direct products','2 lanes · registered products'][i],23,ink,700)
    count=0
    for group,key in enumerate(['stage0','handoff','stage1']):
        for j in range(int(row[key])):
            palette=[('#6387ff','#2346bc','#182d72'),('#f6c453','#8c6800','#725305'),('#69869d','#34495b','#101820')][group]
            prism(59+count*13.05,y+count*1.07,13.05,1.07,17,13,*palette)
            count+=1
    label(40,y+76,f"{row['stage0']} + 1 + {row['stage1']}",18,'#405269',500,True)
    label(536,y+95,f"{row['latency']} clocks",34,blue,700)
footer('First core output','Blue = first dense layer.  Gold = handoff.  Slate = second dense layer.')
save('schedule')

a=start('Independent reference check','Two signed score bytes from each of the 78 reference vectors. Both generated RTL cores passed every comparison. The first 14 test cases are directed and the next 64 are seeded random.')
label(36,48,'Output words',29,ink,700);label(36,80,'Independent integer reference · signed 8-bit scores',18,'#405269')
raw=z.read('direct/expected.hex')
assert raw==z.read('overlapped/expected.hex')
assert hashlib.sha256(raw).hexdigest()==record['expectedOutputsSHA256']
words=[int(x,16) for x in raw.split()]
assert len(words)==78
for variant in ('direct', 'overlapped'):
    log = z.read(f'{variant}/core.log').decode()
    assert 'PASS samples=78 ' in log
for idx,(shift,base,c) in enumerate([(8,214,blue),(0,365,ink)]):
    label(36,base-88,['High byte','Low byte'][idx],21,c,700)
    line(48,base,716,base,'#bac7d5')
    for j,w in enumerate(words):
        b=(w>>shift)&255
        signed=(b^128)-128
        x=53+j*8.52
        line(x,base,x,base-signed*.53,c,5)
line(168,140,168,435,'#7d8fa3',1,'3 5')
label(43,466,'14 directed',17);label(195,466,'64 seeded random',17)
footer('78 / 78 vectors passed per core','Both generated circuits matched the reference.  Random seed = 1729.')
save('verification')
