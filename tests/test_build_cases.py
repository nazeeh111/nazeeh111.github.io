import copy
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('case_builder',ROOT/'scripts/build-cases.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class CaseBuilderTests(unittest.TestCase):
    def setUp(self):
        self.case={'slug':'tool','name':'Tool','repository_url':'https://github.com/owner/tool','source_revision':None,'case_url':'/work/tool/','lead':'An inspectable tool.','action':{'label':'Open tool','url':'https://example.org/tool/'},'secondary_action':{'label':'Read source','url':'https://github.com/owner/tool'},'problem':'A concrete problem.','mechanism':'A concrete mechanism.','observed_result':'A bounded result.','scope_note':'A recorded example.','foundations':'Retained upstream notices.','evidence_url':'/assets/evidence.html#tool','media':[{'src':'/assets/tool.png','alt':'The recorded tool.','caption':'Recorded output.'}],'technical_details':['A real technical detail.']}
        self.files={'assets/tool.png':b'SYNTHETIC IMAGE MARKER','assets/evidence.html':b'<section id="tool">evidence</section>'}
    def test_copy_is_escaped_and_template_like_data_stays_data(self):
        self.case['name']='Tool </title><script>alert(1)</script>'
        self.case['lead']='__MEDIA__ & <a href="x">plain text</a>'
        result=builder.render([self.case],self.files)['work/tool/index.html']
        self.assertNotIn(b'<script>',result)
        self.assertIn(b'&lt;script&gt;',result)
        self.assertIn(b'__MEDIA__ &amp; &lt;a',result)
        self.assertIn(b'href="/assets/evidence.html#tool"',result)
    def test_unlisted_media_and_evidence_never_enter_pages(self):
        for key,value in [('media','/private-note.png'),('evidence','/private-note.html')]:
            c=copy.deepcopy(self.case)
            if key=='media':c['media'][0]['src']=value
            else:c['evidence_url']=value
            with self.subTest(key=key),self.assertRaises(ValueError):builder.render([c],self.files)
    def test_unsafe_routes_actions_revisions_and_duplicates_refuse(self):
        variants=[]
        for key,value in [('slug','../escape'),('case_url','/elsewhere/'),('source_revision','1234')]:
            c=copy.deepcopy(self.case);c[key]=value;variants.append([c])
        c=copy.deepcopy(self.case);c['action']['url']='javascript:alert(1)';variants.append([c]);variants.append([self.case,copy.deepcopy(self.case)])
        for cases in variants:
            before=copy.deepcopy(cases)
            with self.subTest(cases=cases),self.assertRaises(ValueError):builder.render(cases,self.files)
            self.assertEqual(cases,before)

    def test_capture_details_refuse_out_of_bounds_or_non_numeric_geometry(self):
        crop={'x':0,'y':0,'width':80,'height':60,'source_width':100,'source_height':100,'caption':'Desktop detail.','alt':'The same recorded output.'}
        for key,value in [('x',-1),('width',101),('height',0),('x','0;display:none'),('source_width',True)]:
            case=copy.deepcopy(self.case);bad=copy.deepcopy(crop);bad[key]=value;case['media'][0]['mobile_details']=[bad]
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):builder.render([case],self.files)
        self.case['media'][0]['mobile_details']=[crop]
        page=builder.render([self.case],self.files)['work/tool/index.html']
        self.assertIn(b'Open full capture',page)
        self.assertIn(b'href="/assets/tool.png"',page)

    def test_media_breakpoint_is_bounded_integer_and_preserves_default(self):
        self.files['assets/tool-mobile.png']=b'SYNTHETIC PORTRAIT'
        self.case['media'][0]['mobile_src']='/assets/tool-mobile.png'
        self.assertIn(b'(max-width:640px)',builder.render([self.case],self.files)['work/tool/index.html'])
        self.case['media'][0]['mobile_width']=960
        self.assertIn(b'(max-width:960px)',builder.render([self.case],self.files)['work/tool/index.html'])
        for width in (True,0,1601,'960;display:none'):
            self.case['media'][0]['mobile_width']=width
            with self.subTest(width=width),self.assertRaises(ValueError):builder.render([self.case],self.files)

    def test_only_the_first_overview_is_prioritized(self):
        self.files['assets/second.png']=b'SYNTHETIC SECOND'
        self.case['media'].append({'src':'/assets/second.png','alt':'Second retained view','caption':'Second view'})
        page=builder.render([self.case],self.files)['work/tool/index.html']
        self.assertEqual(page.count(b'loading="eager" fetchpriority="high"'),1)
        self.assertEqual(page.count(b'loading="lazy"'),1)
        self.assertLess(page.index(b'loading="eager"'),page.index(b'loading="lazy"'))
