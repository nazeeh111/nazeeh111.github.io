import hashlib, importlib.util, json, re, shutil, tempfile, unittest, zipfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_site', ROOT/'scripts/build-site.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class BuildTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.files=builder.snapshot(ROOT)
 def test_duplicate_missing_and_hash_refuse_before_output(self):
  for kind in ('duplicate','missing','hash','late','archive'):
   files=dict(self.files);cat=json.loads(files['research/catalog.json']); manifest=json.loads(files['research/manifest.json'])
   if kind=='duplicate':cat[1]['id']=cat[0]['id']
   if kind=='missing':del files['research/papers/'+cat[0]['id']+'.pdf']
   if kind=='hash':manifest['files'][0]['sha256']='0'*64
   if kind=='late':del cat[-1]['article']['limits']
   if kind=='archive':files['research/all-papers.zip']=b'invalid zip'
   files['research/catalog.json']=json.dumps(cat).encode()
   if kind=='hash':files['research/manifest.json']=json.dumps(manifest).encode()
   with self.subTest(kind=kind),self.assertRaises((ValueError,KeyError,zipfile.BadZipFile)):builder.render(files)
 def test_deterministic_and_counts_from_model(self):
  a=builder.render(self.files);b=builder.render(self.files);self.assertEqual(a,b)
  self.assertIn(b'12 studies',a['research/index.html']);self.assertIn(b'14 PDFs + 1 report',a['research/index.html'])
  self.assertEqual(a['research/counterpatch/report.html'],self.files['research/counterpatch/report.html'])
  cat,by_id,formats,projects,archive=builder.prepare(self.files);research=builder.module('reader',self.files['scripts/build-research.py'],ROOT/'scripts/build-research.py')
  smaller=research.render(cat[:-1],by_id,13,1,len(archive))
  self.assertIn(b'11 studies',smaller['research/index.html']);self.assertIn(b'13 PDFs + 1 report',smaller['research/index.html'])
 def test_no_clobber_and_interrupted_output_requires_retry(self):
  rendered=builder.render(self.files)
  with tempfile.TemporaryDirectory() as d:
   old=Path(d)/'old';old.mkdir();(old/'keep').write_bytes(b'keep')
   with self.assertRaises(FileExistsError):builder.publish(old,rendered)
   self.assertEqual((old/'keep').read_bytes(),b'keep')
   failed=Path(d)/'failed';real=Path.open
   def broken(path,*args,**kwargs):
    if path.name=='citation.bib':raise OSError('synthetic late write fault')
    return real(path,*args,**kwargs)
   with patch.object(Path,'open',broken):
    with self.assertRaises(OSError):builder.publish(failed,rendered)
   self.assertFalse((failed/'.build-manifest.json').exists())
   fresh=Path(d)/'fresh';builder.publish(fresh,rendered);self.assertTrue((fresh/'.build-manifest.json').is_file())
   for path,data in rendered.items():self.assertEqual(hashlib.sha256((fresh/path).read_bytes()).digest(),hashlib.sha256(data).digest())

 def test_retained_curation_case_assets_and_generated_work_index(self):
  outputs=builder.render(self.files)
  from html.parser import HTMLParser
  class Catalog(HTMLParser):
   def __init__(self):super().__init__();self.entries=[]
   def handle_starttag(self,tag,attrs):
    a=dict(attrs)
    if tag=='li' and a.get('class')=='project-item':self.entries.append(a)
  page=Catalog();page.feed(outputs['work/index.html'].decode());self.assertEqual(len(page.entries),59)
  projects=json.loads(self.files['projects.json'])['projects'];names={p['url'].rsplit('/',1)[-1]for p in projects}
  self.assertFalse(names & {'AsterScan','AdaCAD','advisory-database','pattern-projector','binaryen.js','meent','fluids'})
  for name in ('QubitGuard','FLUXATLAS'):
   entry=next(e for e in page.entries if name in e['data-search'])
   self.assertEqual(set(entry['data-subjects'].split('|')),{'Physics & quantum','ML & data'})
  cases=json.loads(self.files['cases.json']);self.assertEqual(len(cases),13)
  self.assertEqual({case["slug"] for case in cases},{"solidframe","capsulith","qloom","photonsmith","vibescope","instrumentzero","nstack","solidrift","materialmind","siliconpilot","morphproof","ladderproof","chronal"})
  for case in cases:self.assertIn(case['case_url'].lstrip('/')+'index.html',outputs)
  self.assertIn(b'/assets/featured/materialmind/query-mobile.png',outputs['work/materialmind/index.html'])
  self.assertIn(b'/assets/featured/chronal/review.html',outputs['work/chronal/index.html'])
  payloads = []
  for path in ('report.html', 'review.html'):
   document = outputs['assets/featured/chronal/'+path]
   embedded = re.findall(rb'<script[^>]+type="application/json"[^>]*>(.*?)</script>', document, re.S)
   self.assertEqual(len(embedded), 1)
   payloads.append(embedded[0])
  self.assertEqual(payloads[0], payloads[1])
  self.assertIn(b'Open my GitHub profile',outputs['index.html'])

 def test_only_reviewed_inputs_enter_extracted_archive_build(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);source=root/'source';shutil.copytree(ROOT,source,ignore=shutil.ignore_patterns('.git','__pycache__'))
   (source/'.env').write_bytes(b'SYNTHETIC PRIVATE MARKER')
   (source/'unpublished-note.txt').write_bytes(b'SYNTHETIC DRAFT')
   old=builder.ROOT;builder.ROOT=source
   try:
    out=root/'output';self.assertEqual(builder.main(['--out',str(out)]),0)
    self.assertFalse((out/'.env').exists());self.assertFalse((out/'unpublished-note.txt').exists())
    self.assertTrue((out/'research/counterpatch/report.html').is_file())
    listed=source/'research/papers/counterpatch.md';listed.unlink()
    with self.assertRaisesRegex(ValueError,'Missing regular public input'):builder.snapshot(source)
   finally:builder.ROOT=old

 def test_asset_cache_identity_changes_with_asset_bytes_and_stays_stable_otherwise(self):
  old=builder.render(self.files)
  files=dict(self.files);files['assets/design/portfolio.css']+=b'\n/* SYNTHETIC CACHE REVISION */'
  new=builder.render(files)
  old_css=b'/assets/design/portfolio.css?v='+hashlib.sha256(self.files['assets/design/portfolio.css']).hexdigest()[:16].encode()
  new_css=b'/assets/design/portfolio.css?v='+hashlib.sha256(files['assets/design/portfolio.css']).hexdigest()[:16].encode()
  for page in ['index.html','work/index.html','work/solidframe/index.html','assets/provenance.html','assets/featured/evidence.html']:
   self.assertIn(old_css,old[page]);self.assertIn(new_css,new[page]);self.assertNotIn(old_css,new[page])
  stable_js=b'/assets/portfolio.js?v='+hashlib.sha256(self.files['assets/portfolio.js']).hexdigest()[:16].encode()
  self.assertIn(stable_js,old['index.html']);self.assertIn(stable_js,new['index.html'])
  self.assertEqual(builder.stamp_asset_urls(new),new)
  self.assertNotEqual(files['assets/design/portfolio.css'],self.files['assets/design/portfolio.css'])

  literal=b'<code>src="/assets/work.js"</code>'
  sample=dict(self.files);sample['scripts/portfolio.html']+=literal
  self.assertIn(literal,builder.render(sample)['index.html'])
