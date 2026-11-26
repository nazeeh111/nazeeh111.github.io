"""Generate the three narrow SiliconPilot figures from the pinned case checkout."""
import csv
import hashlib
import json
import sys
from html import escape
from pathlib import Path
from zipfile import ZipFile

out = Path(__file__).resolve().parent
src = Path(sys.argv[1]) / "docs/presentation"
archive = src / "compiled-example.zip"
digest = "c412cde4a1dec54ef69a2df56bb96e41856c117784327cf60129f79071fcf4ed"
assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest
source = "https://github.com/nazeeh111/SILICONPILOT/tree/fc774a8411f0a008821e95637b810db2a508c962/docs/presentation"
ink, cobalt, gray = "#101820", "#234bcf", "#47596a"
with ZipFile(archive) as z:
    layers = json.loads(z.read("direct/weights.json"))["layers"]
    assert layers == json.loads(z.read("overlapped/weights.json"))["layers"]
    raw = z.read("direct/expected.hex")
    assert raw == z.read("overlapped/expected.hex")
    for variant in ("direct", "overlapped"):
        assert "PASS samples=78 " in z.read(variant + "/core.log").decode()
record = json.loads((src / "execution.json").read_text())
assert hashlib.sha256(raw).hexdigest() == record["expectedOutputsSHA256"]
schedules = list(csv.DictReader((src / "schedule.csv").open()))

def start(name, desc, height):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 {height}" role="img" aria-labelledby="t d"><title id="t">{escape(name)}</title><desc id="d">{escape(desc)}</desc><metadata>{source}</metadata><style>text{{font-family:Arial,Helvetica,sans-serif;fill:{ink}}}.mono{{font-family:Menlo,monospace}}</style>']

def label(x,y,value,size=14,color=ink,weight=400,anchor="start",mono=False):
    assert size >= 13
    a.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" style="fill:{color}" class="{"mono" if mono else ""}">{escape(str(value))}</text>')

def rect(x,y,w,h,c):
    a.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{c}"/>')

def line(x,y,X,Y,c,w=1):
    a.append(f'<path d="M{x:.2f} {y:.2f}L{X:.2f} {Y:.2f}" stroke="{c}" stroke-width="{w}"/>')

def finish(name):
    (out / (name+"-mobile.svg")).write_text("\n".join(a+["</svg>"])+"\n")

a=start("All 48 compiled weights","Four input columns and two score columns share eight hidden-unit rows. Each cell contains its exact signed quantized coefficient. Blue means positive, slate negative, and pale gray zero.",365)
label(2,21,"4 inputs → 8 hidden → 2 scores",16,ink,700)
label(2,48,"Hidden",13,gray,600)
label(104,48,"Input weights",14,gray,600,"middle")
label(230,48,"Score weights",14,gray,600,"middle")
xs=[52,84,116,148,209,244]
for x,h in zip(xs,["x0","x1","x2","x3","s0","s1"]):
    label(x,72,h,14,ink,600,"middle",True)
for h in range(8):
    y=80+24*h
    label(4,y+16,"h"+str(h),14,ink,700,mono=True)
    vals=layers[0]["weights"][h]+[v[h] for v in layers[1]["weights"]]
    for col,(x,v) in enumerate(zip(xs,vals)):
        color=cobalt if v>0 else "#374b5b" if v<0 else "#e5eaf0"
        source_idx,target_idx,layer=(col,h,0) if col<4 else (h,col-4,1)
        a.append(f'<g data-layer="{layer}" data-source="{source_idx}" data-target="{target_idx}" data-weight="{v}">')
        rect(x-15,y,30,22,color)
        label(x,y+15,v,13,"white" if v else gray,600,"middle",True)
        a.append("</g>")
line(179,57,179,272,"#aebccb")
label(2,296,"x0  variance",14);label(142,296,"x1  skewness",14)
label(2,317,"x2  curtosis",14);label(142,317,"x3  entropy",14)
label(2,348,"Each row follows one hidden unit.",14,gray)
finish("network")

a=start("First result on a shared clock scale","The direct-product core takes 32 clocks, one clock to hand off, then 16 clocks. The two-lane registered-product core needs 17, one, and nine. The bars share one clock scale.",289)
label(2,23,"Core clocks to first output",20,ink,700)
for i,r in enumerate(schedules):
    y=56+110*i
    label(2,y,["1 lane · direct products","2 lanes · registered products"][i],16,ink,700)
    count=0
    for k,c in zip(("stage0","handoff","stage1"),(cobalt,"#93610a","#344b5f")):
        for _ in range(int(r[k])):
            a.append(f'<g data-schedule="{r["schedule"]}" data-stage="{k}" data-clock="{count}">')
            rect(3+count*5.42,y+14,4.86,23,c);a.append("</g>");count+=1
    line(3+count*5.42,y+10,3+count*5.42,y+43,ink)
    label(2,y+62,f'{r["stage0"]} + 1 + {r["stage1"]} =',17,gray,500,mono=True)
    label(157,y+62,f'{r["latency"]} clocks',22,cobalt,700)
    limits=record['cases'][r['schedule']]['scheduleLog']
    assert f'latency={count} interval={r["interval"]}' in limits and count==int(r["latency"])
line(2,243,277,243,"#b9c6d2")
for x,t,c in [(2,"Layer 1",cobalt),(95,"Handoff","#93610a"),(191,"Layer 2","#344b5f")]:
    rect(x,258,10,10,c);label(x+16,268,t,14,ink)
finish("schedule")

words=[int(x,16) for x in raw.split()]
assert len(words)==78
a=start("78 reference score words","Three strips of 26 consecutively indexed test vectors show the signed high and low score bytes from the independent reference, with the same vertical scale in each strip. Both RTL cores passed all 78 comparisons.",430)
label(2,22,"Reference scores",21,ink,700)
label(2,48,"●",15,cobalt);label(20,48,"High byte",14)
line(120,44,132,44,ink,2.8);label(139,48,"Low byte",14)
for group in range(3):
    top=88+100*group
    label(2,top-12,f"Vectors {group*26:02d}–{group*26+25:02d}",14,ink,700)
    for val in (127,0,-128):
        y=top+(127-val)*.237
        label(36,y+4,str(val).replace("-","−"),13,gray,400,"end",True)
        line(42,y,277,y,"#bcc8d2" if val==0 else "#e1e7ee")
    for j in range(26):
        idx=group*26+j;word=words[idx];x=46+j*9.05
        scores=[(((word>>shift)&255)^128)-128 for shift in (8,0)]
        a.append(f'<g data-vector="{idx}" data-high="{scores[0]}" data-low="{scores[1]}">')
        high_y,low_y=(top+(127-val)*.237 for val in scores)
        line(x-2.8,low_y,x+2.8,low_y,ink,2.5)
        a.append(f'<circle cx="{x:.2f}" cy="{high_y:.2f}" r="2.2" stroke="#fff" stroke-width=".55" fill="{cobalt}"/></g>')
line(2,371,278,371,"#b9c6d2")
label(2,396,"78/78 passed in both cores",17,ink,700)
label(2,419,"14 directed · 64 random · seed 1729",14,gray)
finish("verification")
