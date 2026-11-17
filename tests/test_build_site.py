import hashlib, importlib.util, json, shutil, tempfile, unittest, zipfile
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

 def test_retained_catalog_and_cross_discipline_membership(self):
  output=builder.render(self.files)['index.html'].decode()
  from html.parser import HTMLParser
  class Catalog(HTMLParser):
   def __init__(self):super().__init__();self.entries=[]
   def handle_starttag(self,tag,attrs):
    data=dict(attrs)
    if tag=='li' and data.get('class')=='project-item':self.entries.append(data)
  page=Catalog();page.feed(output);self.assertEqual(len(page.entries),59)
  projects=json.loads(self.files['projects.json'])['projects']
  names={p['url'].rstrip('/').rsplit('/',1)[-1] for p in projects}
  self.assertFalse(names & {'AsterScan','AdaCAD','advisory-database','pattern-projector','binaryen.js','meent','fluids'})
  for name in ('QubitGuard','FLUXATLAS'):
   entry=next(e for e in page.entries if e['data-search'].startswith(name.lower()+' '))
   self.assertEqual(set(entry['data-subjects'].split('|')),{'Physics & quantum','ML & data'})

 def test_invalid_memberships_refuse_without_generation(self):
  for invalid in ([],['Physics & quantum','Physics & quantum'],['Unknown'],"ML & data",['ML & data']):
   files=dict(self.files);projects=json.loads(files['projects.json']);projects['projects'][0]['subjects']=invalid
   files['projects.json']=json.dumps(projects).encode()
   with self.subTest(invalid=invalid),self.assertRaisesRegex(ValueError,'discipline memberships'):builder.render(files)

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
