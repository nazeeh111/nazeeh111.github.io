"""Render the portfolio's spectrum probe from the recorded PhotonSmith solutions."""
import csv
import io
import math


def render(template, spectrum_csv):
    rows = csv.DictReader(io.StringIO(spectrum_csv.decode("utf-8")))
    samples = [(float(row["wavelength_nm"]), float(row["efficiency_percent"])) for row in rows]
    if len(samples) < 2 or any(not math.isfinite(nm) or not 0 <= efficiency <= 100 for nm, efficiency in samples):
        raise ValueError("Spectrum needs at least two finite wavelengths and valid efficiencies")
    if any(left[0] >= right[0] for left, right in zip(samples, samples[1:])):
        raise ValueError("Spectrum wavelengths must increase")

    first, last = samples[0][0], samples[-1][0]
    points = []
    marks = []
    peak = max(range(len(samples)), key=lambda index: samples[index][1])
    for index, (nm, efficiency) in enumerate(samples):
        x = 34 + 298 * (nm - first) / (last - first)
        y = 8 + 70 * (1 - efficiency / 100)
        points.append(f"{x:.3f},{y:.3f}")
        selected = ' class="peak"' if index == peak else ''
        marks.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="2.6" data-nm="{nm:g}" '
                     f'data-percent="{efficiency:.2f}"{selected}/>')
    chart = f'''<figure class="spectrum-probe" aria-label="Saved efficiency spectrum">
<figcaption>Efficiency into order +1</figcaption>
<svg viewBox="0 0 346 104" role="img" aria-label="Target-order efficiency across {len(samples)} stored wavelength solves. The highest sample is {samples[peak][1]:.2f} percent at {samples[peak][0]:g} nanometres.">
<g class="axes"><path d="M34 8H332M34 78H332"/></g>
<g class="scale"><text x="0" y="12">100%</text><text x="11" y="82">0%</text><text x="34" y="99">{first:g} nm</text><text x="332" y="99" text-anchor="end">{last:g} nm</text></g>
<polyline class="curve" points="{' '.join(points)}"/><g class="samples">{''.join(marks)}</g></svg>
<label class="probe-control" hidden><span>Wavelength</span><input type="range" min="0" max="{len(samples)-1}" step="1" value="{peak}" aria-label="Inspect a saved wavelength"></label>
<output>{samples[peak][0]:g} nm · {samples[peak][1]:.2f}% into order +1</output>
</figure>'''
    return template.replace("{{SPECTRUM}}", chart).encode("utf-8")
