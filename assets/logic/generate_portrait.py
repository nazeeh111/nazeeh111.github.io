"""Draw all 48 signed stored connections in a 280-unit portrait."""
from collections import Counter
from html import escape
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import sys

repo = Path(sys.argv[1])
archive = repo / "docs/presentation/compiled-example.zip"
digest = "c412cde4a1dec54ef69a2df56bb96e41856c117784327cf60129f79071fcf4ed"
assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest
with ZipFile(archive) as bundle:
    weights = json.loads(bundle.read("direct/weights.json"))["layers"]
    assert weights == json.loads(bundle.read("overlapped/weights.json"))["layers"]
features = json.loads((repo / "models/dataset_manifest.json").read_text())["features"]

svg = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 382" role="img" aria-labelledby="diagram-title diagram-description">
<title id="diagram-title">Banknote classifier from inputs to scores</title>
<desc id="diagram-description">Four inputs connect to eight hidden ReLU units, then to two scores. All 48 stored signed coefficients are shown. Solid cobalt means positive; dashed graphite means negative; dotted gray means zero. This is the logical model, not the hardware layout.</desc>
<metadata>SiliconPilot compiled-example.zip SHA-256: c412cde4a1dec54ef69a2df56bb96e41856c117784327cf60129f79071fcf4ed. Retained source: https://github.com/nazeeh111/SILICONPILOT/tree/fc774a8411f0a008821e95637b810db2a508c962/docs/presentation</metadata>
<style>
text{font-family:Arial,sans-serif;fill:#101820}
.port-id{font-family:ui-monospace,monospace;font-weight:700}
.route{fill:none;stroke-linecap:round}
</style>
<rect width="280" height="382" fill="#fff"/>
<path d="M4 74H276V149H4zM4 210H276V279H4z" fill="#f1f5fa"/>
''']
def label(x, y, text, size=13, weight=500, anchor="start", extra=""):
    assert size >= 12
    svg.append(f'<text x="{x:g}" y="{y:g}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" {extra}>{escape(text)}</text>')

ports = [[36, 105.33, 174.67, 244], [19 + i * 34.57 for i in range(8)], [80, 200]]
edges = []
for stage, layer in enumerate(weights):
    for target, row in enumerate(layer["weights"]):
        for source, weight in enumerate(row):
            x, dest = ports[stage][source], ports[stage + 1][target]
            if stage == 0:
                start_x, end_x = x + (target - 3.5) * 2.05, dest + (source - 1.5) * 2.4
                data = f"M{start_x:.2f} 72 C{start_x:.2f} 100 {end_x:.2f} 119 {end_x:.2f} 151"
            else:
                start_x, end_x = x + (target - .5) * 3.4, dest + (source - 3.5) * 2.5
                data = f"M{start_x:.2f} 207 C{start_x:.2f} 234 {end_x:.2f} 253 {end_x:.2f} 282"
            edges.append((stage, source, target, weight, data))

assert Counter(stage for stage, *_ in edges) == {0: 32, 1: 16}
assert Counter((weight > 0) - (weight < 0) for _, _, _, weight, _ in edges) == {1: 17, 0: 13, -1: 18}

for stage, source, target, weight, data in sorted(edges, key=lambda e: abs(e[3])):
    sign = "positive" if weight > 0 else "negative" if weight < 0 else "zero"
    color, dash, opacity = {
        "positive": ("#234bcf", "", ".90"),
        "negative": ("#26394b", 'stroke-dasharray="4 2.5"', ".88"),
        "zero": ("#72849a", 'stroke-dasharray="1 3.2"', ".85"),
    }[sign]
    line = f'<path class="route" d="{data}" stroke="{color}" stroke-width="{1.35 if weight else 1.2}" opacity="{opacity}" {dash}/>'
    origin_id = ("x", "h")[stage] + str(source)
    target_id = ("h", "s")[stage] + str(target)
    svg.append(f'<g data-layer="{stage}" data-source="{source}" data-target="{target}" data-weight="{weight}" data-sign="{sign}"><title>{origin_id} → {target_id}: {weight:+d}</title>{line}</g>')

label(4, 17, "4 inputs", 14, 750)
for idx, (x, feature) in enumerate(zip(ports[0], features, strict=True)):
    svg.append(f'<rect x="{x-31:.2f}" y="24" width="62" height="46" fill="#fff" stroke="#b9c6d7"/>')
    label(x, 42, "x"+str(idx), 14, 700, "middle", 'class="port-id"')
    label(x, 60, feature, 12, 500, "middle")

svg.append('<rect x="4" y="149" width="272" height="59" fill="#223fb9"/>')
label(140, 171, "8 hidden ReLU units", 14, 720, "middle", 'style="fill:#fff"')
for idx, x in enumerate(ports[1]):
    svg.append(f'<rect x="{x-12:.2f}" y="178" width="24" height="24" fill="#122b90"/>')
    label(x, 195, "h"+str(idx), 13, 700, "middle", 'class="port-id" style="fill:#fff"')

for idx, x in enumerate(ports[2]):
    svg.append(f'<rect x="{x-39:g}" y="281" width="78" height="31" fill="#fff" stroke="#b9c6d7"/>')
    label(x, 301, "s"+str(idx), 14, 700, "middle", 'class="port-id"')
label(140, 331, "2 scores", 14, 750, "middle")

for x, color, dash, name in [(4, "#234bcf", "", "Positive"), (98, "#26394b", 'stroke-dasharray="4 2.5"', "Negative"), (195, "#72849a", 'stroke-dasharray="1 3.2"', "Zero")]:
    svg.append(f'<path class="route" d="M{x} 359h20" stroke="{color}" stroke-width="2" {dash}/>')
    label(x+25, 363, name, 13)

output = Path(__file__).with_name("network-portrait.svg")
output.write_text("\n".join(svg + ["</svg>", ""]), encoding="utf-8")
