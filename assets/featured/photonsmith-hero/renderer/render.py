#!/usr/bin/env python3
"""Render exact retained PhotonSmith samples; no solver/import of application code.

Requires existing NumPy and Matplotlib. Registers a bundled OFL font in process
only. SVG glyph paths are standalone, with no font/network/runtime dependency.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

SOURCE_SHA='21c935558d8fe79e937e47c959f7d6288dc563c3671fc4440a196269b80055f7'
ORIGINAL_SOURCE_SHA='bf63ba3ebec2013dde9f10cbd65fa438634d71abd1bbf504577701dbd8a23b1e'
ORIGINAL_SOURCE_URL='https://github.com/nazeeh111/PhotonSmith/blob/13912d9d640938acf8ce299a152298666ae61d44/experiments/designs/interactive-refined-1550nm.json'
FONT_SHA='3b031aa4216174205bd8471f88a49b91f093169e9e87bd5262242bc5967fe2e3'
ROOT=Path(__file__).resolve().parents[1]
SOURCE_REV='13912d9d640938acf8ce299a152298666ae61d44'

def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(a):return json.dumps(a,separators=(',',':'),allow_nan=False).encode()
def checked(path,expected):
 b=path.read_bytes()
 if sha(b)!=expected:raise ValueError('Refuse changed input: '+str(path))
 return b

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--source',type=Path,default=ROOT/'data/plot-data.json')
 parser.add_argument('--font',type=Path,default=ROOT/'fonts/IBMPlexSans.ttf')
 parser.add_argument('--out',type=Path,default=ROOT/'assets')
 args=parser.parse_args()
 raw=checked(args.source,SOURCE_SHA);font_raw=checked(args.font,FONT_SHA)
 data=json.loads(raw)
 assert data['source']=={'revision':SOURCE_REV,'sha256':ORIGINAL_SOURCE_SHA,'url':ORIGINAL_SOURCE_URL},'Original source identity mismatch'
 r=data['result'];f=r['field'];s=r['spectrum'];geometry=data['geometry']
 # Configure before importing Matplotlib; do not modify user caches/fonts.
 with tempfile.TemporaryDirectory(prefix='photonsmith-figure-cache-') as cache:
  os.environ['MPLCONFIGDIR']=cache;os.environ['MPLBACKEND']='Agg'
  import numpy as np
  import matplotlib as mpl
  mpl.use('Agg')
  import matplotlib.pyplot as plt
  from matplotlib import font_manager,patheffects
  from matplotlib.patches import Rectangle
  font_manager.fontManager.addfont(str(args.font))
  family=font_manager.FontProperties(fname=str(args.font)).get_name()
  assert Path(font_manager.findfont(font_manager.FontProperties(family=family))).resolve()==args.font.resolve(),'Unexpected font substitution'
  xx=np.asarray(f['x'],dtype=float);zz=np.asarray(f['z'],dtype=float)
  values=np.asarray(f['real'],dtype=float);eps=np.asarray(f['epsilon'],dtype=float)
  wavelength=np.asarray(s['wavelength'],dtype=float)*1000
  efficiency=np.asarray(s['efficiency'],dtype=float)*100
  assert values.shape==(97,96) and eps.shape==values.shape
  assert len(wavelength)==len(efficiency)==21
  assert all(np.isfinite(a).all()for a in [xx,zz,values,eps,wavelength,efficiency])
  assert np.all(np.diff(xx)>0) and np.all(np.diff(zz)>0)
  assert values.min()>-2 and values.max()<2 and efficiency.min()>=0 and efficiency.max()<=100
  # Exact geometry construction from recorded fractional bar widths/centres.
  # Verify it reproduces ALL stored binary epsilon samples, with no solve.
  model=np.ones_like(eps)
  period=geometry['period_um'];lh=geometry['layer_height_um']
  for iz,z in enumerate(zz):
   if 0<=z<=3*lh:
    j=min(int(z/lh),2)
    distance=(xx/period-geometry['shifts'][j]+.5)%1-.5
    model[iz,abs(distance)<geometry['widths'][j]/2]=r['material_index']**2
  assert np.array_equal(model,eps),'Recorded geometry and epsilon disagree'
  def edges(a):return np.r_[a[0]-(a[1]-a[0])/2,(a[:-1]+a[1:])/2,a[-1]+(a[-1]-a[-2])/2]
  xe,ze=edges(xx),edges(zz)
  # Voronoi display cells retain every original point. Extension by half a
  # sampling interval is display support, not additional field computation.
  arrays={k:sha(canonical(v)) for k,v in {'x_um':f['x'],'z_um':f['z'],'field_real':f['real'],'epsilon':f['epsilon'],'geometry':geometry,'spectrum_wavelength_um':s['wavelength'],'spectrum_efficiency_fraction':s['efficiency']}.items()}
  args.out.mkdir(parents=True,exist_ok=True)
  records=[]
  def export(fig,ax,stem,kind,layout):
   fig.canvas.draw()
   box=ax.get_window_extent();perunit_x=box.width/abs(np.diff(ax.get_xlim())[0]);perunit_y=box.height/abs(np.diff(ax.get_ylim())[0])
   if kind=='field':assert abs(perunit_x-perunit_y)<1e-7,'Unequal spatial scale'
   else:
    expected=ax.transData.transform(np.column_stack([wavelength,efficiency]));expected[:,1]=fig.bbox.height-expected[:,1];expected*=72/fig.dpi
   paths=[]
   for ext in ['svg','png']:
    dst=args.out/(stem+'.'+ext)
    meta={'Date':None,'Creator':'Retained-data renderer'} if ext=='svg' else {'Software':'Retained-data renderer'}
    fig.savefig(dst,format=ext,dpi=100,facecolor='#fbfaf7',transparent=False,metadata=meta)
    paths.append({'file':dst.name,'sha256':sha(dst.read_bytes()),'bytes':dst.stat().st_size})
   svg=args.out/(stem+'.svg')
   desc=('All 9312 stored real electric-field samples, with exact saved bar geometry and equal micrometre scales. Color is Re(Ey) relative to unit incident amplitude; it is not intensity. A legacy M9 numerical model, not a measurement.' if kind=='field' else 'All 21 stored wavelength solves, shown as circles with straight connecting segments. Wavelength is nanometres; target-order efficiency is percent of incident power. Zero percent baseline; no new fit or solve.')
   text=svg.read_text();text=re.sub(r'(<svg\b[^>]*>)',lambda m:m[0]+'\n<title>'+xml_escape(stem.replace('-',' '))+'</title><desc>'+xml_escape(desc)+'</desc>',text,count=1);svg.write_text(text)
   paths[0].update(sha256=sha(svg.read_bytes()),bytes=svg.stat().st_size)
   if layout=='mobile':
    # Direct numeric rerasterization at the intended 390px display size, not a
    # resize or edit of the delivered 320px PNG.
    review=args.out/(stem+'-review390.png')
    fig.savefig(review,dpi=100*390/320,facecolor='#fbfaf7',transparent=False,metadata={'Software':'Retained-data renderer'})
    paths.append({'file':review.name,'sha256':sha(review.read_bytes()),'bytes':review.stat().st_size,'purpose':'Direct plot render for 390px review'})
   tree=ET.parse(svg);ns={'s':'http://www.w3.org/2000/svg'}
   assert not tree.findall('.//s:image',ns),'Unexpected embedded raster'
   assert not tree.findall('.//s:text',ns),'Unoutlined font'
   assert not tree.findall('.//s:script',ns),'Unexpected script'
   if kind=='field':
    group=tree.find('.//s:g[@id="retained-field"]',ns);n=len(group.findall('s:path',ns));assert n==values.size
    audit={'unique_source_samples':values.size,'svg_data_cells':n,'pixels_per_um_x':float(perunit_x),'pixels_per_um_z':float(perunit_y),'equal_scale_error':float(abs(perunit_x-perunit_y))}
   else:
    group=tree.find('.//s:g[@id="retained-spectrum"]',ns);d=group.find('s:path',ns).attrib['d']
    points=np.array([[float(a),float(b)]for a,b in re.findall(r'[ML]\s*([-+\deE.]+)\s+([-+\deE.]+)',d)])
    assert points.shape==(21,2);error=float(abs(points-expected).max());assert error<1e-5
    marker_group=tree.find('.//s:g[@id="retained-samples"]',ns)
    uses=marker_group.findall('.//s:use',ns);assert len(uses)==21
    audit={'source_points':21,'svg_line_vertices':len(points),'svg_sample_markers':len(uses),'max_svg_coordinate_error_pt':error,'y_limits_percent':list(ax.get_ylim())}
   # Bounds audit of labels/ticks at actual export size, not only save success.
   text_boxes=[]
   for label in fig.findobj(mpl.text.Text):
    if label.get_visible() and label.get_text():
     bb=label.get_window_extent(fig.canvas.get_renderer())
     if bb.width and bb.height:
      assert bb.x0>=-1 and bb.y0>=-1 and bb.x1<=fig.bbox.width+1 and bb.y1<=fig.bbox.height+1,(stem,label.get_text(),bb)
      text_boxes.append({'text':label.get_text(),'font_px_at_native_width':label.get_fontsize()*100/72})
   records.append({'name':stem,'kind':kind,'layout':layout,'width_px':round(fig.bbox.width),'height_px':round(fig.bbox.height),'outputs':paths,'audit':audit,'text':text_boxes})
   plt.close(fig)
  common={'font.family':family,'font.size':10,'axes.labelcolor':'#182126','text.color':'#182126','xtick.color':'#182126','ytick.color':'#182126','axes.edgecolor':'#182126','axes.linewidth':.8,'svg.fonttype':'path','svg.hashsalt':'photonsmith-retained-v3','path.simplify':False,'savefig.bbox':None}
  with mpl.rc_context(common):
   for layout,width in [('desktop',640),('mobile',320)]:
    mobile=layout=='mobile';height=width if mobile else round(width*.90)
    fig=plt.figure(figsize=(width/100,height/100),dpi=100)
    ax=fig.add_axes([.23,.37,.72,.59]if mobile else [.12,.30,.83,.66])
    font=9.5 if mobile else 12
    ax.tick_params(labelsize=font,length=3,pad=4)
    ax.set_xlabel('x (µm)',fontsize=font+1,labelpad=5);ax.set_ylabel('z (µm)',fontsize=font+1,labelpad=5)
    mesh=ax.pcolormesh(xe,ze,values,shading='flat',cmap='RdBu_r',vmin=-2,vmax=2,edgecolors='none',antialiased=False)
    mesh.set_gid('retained-field')
    ax.set_xlim(xe[0],xe[-1]);ax.set_ylim(ze[-1],ze[0]);ax.set_aspect('equal',adjustable='box')
    ax.set_xticks([0,.6,1.2,1.8]);ax.set_yticks([-.45,0,.45,.9,1.35]);ax.set_yticklabels(['−0.45','0','0.45','0.90','1.35'])
    for j,(w,c)in enumerate(zip(geometry['widths'],geometry['shifts'])):
     left=(c-w/2)*period;barwidth=w*period
     for shift in [-period,0,period]:
      a,b=max(xe[0],left+shift),min(xe[-1],left+barwidth+shift)
      if a<b:
       outline=Rectangle((a,j*lh),b-a,lh,fill=False,edgecolor='#182126',linewidth=.9 if mobile else 1.15)
       outline.set_path_effects([patheffects.Stroke(linewidth=2.2 if mobile else 2.7,foreground='#fffdf8'),patheffects.Normal()]);ax.add_patch(outline)
    cax=fig.add_axes([.25,.17,.65,.035] if mobile else [.20,.135,.66,.045])
    bar=fig.colorbar(mesh,cax=cax,orientation='horizontal',ticks=[-2,0,2]);bar.solids.set_rasterized(False);bar.ax.tick_params(labelsize=font,length=3,pad=2)
    bar.set_label('Re(Ey) / Einc',fontsize=font+1,labelpad=3)
    export(fig,ax,'field-'+layout,'field',layout)
    height=round(width*.76)
    fig=plt.figure(figsize=(width/100,height/100),dpi=100);ax=fig.add_axes([.20,.24,.75,.70] if mobile else [.14,.20,.81,.74])
    ax.tick_params(labelsize=font,length=3,pad=4);ax.set_xlabel('Wavelength (nm)',fontsize=font+1,labelpad=6);ax.set_ylabel('Efficiency (%)',fontsize=font+1,labelpad=6)
    ax.set_xlim(1300,1700);ax.set_ylim(0,100);ax.set_xticks([1300,1400,1500,1600,1700]);ax.set_yticks([0,25,50,75,100]);ax.grid(axis='y',color='#d5d6d2',linewidth=.7);ax.set_axisbelow(True)
    ax.spines[['top','right']].set_visible(False)
    line,=ax.plot(wavelength,efficiency,color='#a33624',linewidth=1.6 if mobile else 2.0);line.set_gid('retained-spectrum')
    samples,=ax.plot(wavelength,efficiency,linestyle='none',marker='o',markersize=3.4 if mobile else 4.5,markerfacecolor='#fbfaf7',markeredgewidth=1.1,color='#a33624');samples.set_gid('retained-samples')
    export(fig,ax,'spectrum-'+layout,'spectrum',layout)
  # Accessible exact-values alternatives, not resampled presentation arrays.
  csv_path=args.out/'spectrum.csv'
  with csv_path.open('w',newline='')as out:
   writer=csv.writer(out);writer.writerow(['wavelength_um','efficiency_fraction','wavelength_nm','efficiency_percent'])
   for a,b,c,d in zip(s['wavelength'],s['efficiency'],wavelength,efficiency):writer.writerow([repr(a),repr(b),repr(float(c)),repr(float(d))])
  field_csv=args.out/'field.csv'
  with field_csv.open('w',newline='')as out:
   writer=csv.writer(out);writer.writerow(['x_um','z_um','real_Ey_per_unit_incident','relative_permittivity'])
   for iz,z in enumerate(f['z']):
    for ix,x in enumerate(f['x']):writer.writerow([repr(x),repr(z),repr(f['real'][iz][ix]),repr(f['epsilon'][iz][ix])])
  manifest={'source_revision':SOURCE_REV,'plot_data_sha256':SOURCE_SHA,'original_source_sha256':ORIGINAL_SOURCE_SHA,'original_source_url':ORIGINAL_SOURCE_URL,'font_sha256':sha(font_raw),'source_array_hash_format':'SHA256 of compact JSON arrays, original parsed values, allow_nan=False','arrays':arrays,'field_shape':list(values.shape),'field_minmax':[float(values.min()),float(values.max())],'field_color_limits':[-2,2],'display_cell_edges_um':{'x':[float(xe[0]),float(xe[-1])],'z':[float(ze[0]),float(ze[-1])]},'geometry_matches_all_stored_epsilon_samples':True,'runtime':{'python':sys.version,'numpy':np.__version__,'matplotlib':mpl.__version__,'font':family},'figures':records,'renderer_sha256':sha(Path(__file__).read_bytes()),'csv_sha256':sha(csv_path.read_bytes())}
  manifest['field_csv_sha256']=sha(field_csv.read_bytes())
  manifest['transformations']=['No solver, model inference, fit, interpolation, smoothing, filtering, masking, or omission.','Field values unchanged. Display cells use midpoints of stored coordinates and half-interval edge support.','Geometry rectangles reconstructed exactly from saved fractional widths/centres and layer heights; all stored epsilon values match.','Field axes use equal physical scale, z increasing downwards. Diverging linear color mapping is fixed at [-2,2] with no clipped source values.','Wavelength micrometres multiplied by 1000 to nanometres; efficiency fraction multiplied by 100 to percent of incident power.','All 21 sample circles retained. Straight segments only connect actual stored samples; no intermediate solve or estimated curve.','Plex font registered only for this process and SVG glyphs outlined; no global font installation.']
  (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  print(json.dumps({'status':'PASS','figures':len(records),'field_samples':values.size,'spectrum_samples':len(wavelength),'output':str(args.out)}))
if __name__=='__main__':main()
