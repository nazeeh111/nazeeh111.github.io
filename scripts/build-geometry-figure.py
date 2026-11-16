"""Recompose preserved, recorded mesh projections. No new geometry is solved."""

from pathlib import Path
import xml.etree.ElementTree as ET
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def element(parent, tag, attributes, text=None):
    result = ET.SubElement(parent, f"{{{NS}}}{tag}", attributes)
    result.text = text
    return result


source = ET.parse(ROOT / "assets/sources/solidrift-profile.svg").getroot()
panels = source.findall(f"{{{NS}}}svg")
assert len(panels) == 2
for index, name in enumerate(["input", "union"]):
    panel = deepcopy(panels[index])
    panel.attrib.pop("x", None)
    panel.attrib.pop("y", None)
    panel.attrib.update(width="500", height="300", role="img")
    ET.ElementTree(panel).write(ROOT / f"assets/solidrift-{name}.svg", encoding="unicode", xml_declaration=False)

mobile = ET.Element(f"{{{NS}}}svg", {"width": "640", "height": "820", "viewBox": "0 0 640 820", "role": "img", "aria-labelledby": "mobile-title"})
element(mobile, "title", {"id": "mobile-title"}, "Two input solids and Blender's recorded union: original 132-triangle stage")
element(mobile, "rect", {"width": "640", "height": "820", "fill": "#132a48"})
for index, (panel, label) in enumerate(zip(panels, ["Two input solids", "Blender returned one"])):
    projected = deepcopy(panel)
    projected.attrib.update(x="24", y=str(index * 410 + 75), width="592", height="300")
    mobile.append(projected)
    element(mobile, "text", {"x": "28", "y": str(index * 410 + 48), "font-family": "sans-serif", "font-size": "34", "font-weight": "600", "fill": "#ffffff"}, label)
ET.ElementTree(mobile).write(ROOT / "assets/solidrift-comparison-mobile.svg", encoding="unicode", xml_declaration=False)

figure = ET.Element(f"{{{NS}}}svg", {"width": "1000", "height": "520", "viewBox": "0 0 1000 520", "role": "img", "aria-labelledby": "title desc"})
element(figure, "title", {"id": "title"}, "The missing solid: original recorded Blender union")
element(figure, "desc", {"id": "desc"}, "Both panels depict the original 132-triangle stage, not the reduced witness. Two input solids on the left; one body missing from the recorded FLOAT union on the right.")
element(figure, "rect", {"width": "1000", "height": "520", "fill": "#132a48"})
for index, (panel, label) in enumerate(zip(panels, ["Two input solids", "Blender returned one"])):
    panel.attrib.update(x=str(index * 500), y="90", width="500", height="380")
    figure.append(panel)
    element(figure, "text", {"x": str(index * 500 + 22), "y": "48", "font-family": "sans-serif", "font-size": "24", "font-weight": "600", "fill": "#ffffff"}, label)
element(figure, "text", {"x": "22", "y": "506", "font-family": "sans-serif", "font-size": "16", "fill": "#d2def0"}, "Original 132-triangle case · recorded FLOAT union")
ET.ElementTree(figure).write(ROOT / "assets/solidrift-comparison.svg", encoding="unicode", xml_declaration=False)
