"""Render reviewed case records into static portfolio pages."""
import html
import json
import re
from urllib.parse import urlsplit

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
REVISION = re.compile(r"[0-9a-f]{40}\Z")

def escape(value):
    return html.escape(str(value), quote=True)

def url(value):
    if not isinstance(value,str):
        raise ValueError("Case URL must be text")
    parsed=urlsplit(value)
    if value.startswith("/") and not value.startswith("//") and not parsed.netloc:
        return value
    if parsed.scheme=="https" and parsed.netloc and not parsed.username and not parsed.password:
        return value
    raise ValueError("Case URLs must be local paths or public HTTPS links")

def paragraph(value):
    if not isinstance(value,str) or not value.strip():
        raise ValueError("Case copy must be nonempty text")
    return '<p>'+escape(value)+'</p>'

def action(record, primary=False):
    css='button' if primary else 'text-link'
    return '<a class="'+css+'" href="'+escape(url(record['url']))+'">'+escape(record['label'])+'</a>'

def details(image, src):
    crops=image.get('mobile_details',[])
    if not isinstance(crops,list):
        raise ValueError("Mobile details must be a list")
    rendered=[]
    for crop in crops:
        keys=('x','y','width','height','source_width','source_height')
        if any(type(crop.get(k)) is not int for k in keys):
            raise ValueError("Capture rectangles require integer dimensions")
        x,y,w,h,sw,sh=(crop[k] for k in keys)
        if x<0 or y<0 or min(w,h,sw,sh)<=0 or x+w>sw or y+h>sh:
            raise ValueError("Capture detail must stay within its source image")
        caption=crop['caption'];alt=crop['alt']
        if not isinstance(caption,str) or not caption.strip() or not isinstance(alt,str) or not alt.strip():
            raise ValueError("Capture detail requires accurate labels")
        style=';'.join('--'+k+':'+str(v) for k,v in zip(('crop-x','crop-y','crop-width','crop-height','source-width'),(x,y,w,h,sw)))
        rendered.append('<figure><a class="capture-detail" style="'+style+'" href="'+escape(src)+'"><img src="'+escape(src)+'" width="'+str(sw)+'" height="'+str(sh)+'" alt="'+escape(alt)+'" loading="lazy"></a><figcaption>'+escape(caption)+'</figcaption></figure>')
    return '<div class="mobile-details">'+''.join(rendered)+'</div>' if rendered else ''

def render(cases, files):
    if not isinstance(cases,list) or not cases:
        raise ValueError("Reviewed cases must be a nonempty list")
    outputs={};known=set()
    for case in cases:
        slug=case['slug']
        if not isinstance(slug,str) or not SLUG.fullmatch(slug) or slug in known:
            raise ValueError("Case slug must be unique and safe")
        known.add(slug)
        if case['case_url']!='/work/'+slug+'/':
            raise ValueError("Case path and slug disagree")
        name=escape(case['name']);route=case['case_url'];repo=url(case['repository_url'])
        revision=case.get('source_revision')
        if revision is not None and (not isinstance(revision,str) or not REVISION.fullmatch(revision)):
            raise ValueError("Recorded case revision must be a full Git hash")
        media=[]
        for image in case['media']:
            src=url(image['src'])
            if not src.startswith('/') or src[1:]not in files:
                raise ValueError("Case media must be a listed public asset")
            mobile=''
            if image.get('mobile_src'):
                m=url(image['mobile_src'])
                if not m.startswith('/') or m[1:]not in files:
                    raise ValueError("Case mobile image must be a listed public asset")
                width=image.get('mobile_width',640)
                if type(width) is not int or not 320<=width<=1600:
                    raise ValueError("Case mobile width must be an integer between320 and1600")
                mobile='<source media="(max-width:'+str(width)+'px)" srcset="'+escape(m)+'">'
            crops=details(image,src)
            css='case-media has-details' if crops else 'case-media'
            media.append('<figure class="'+css+'"><a class="capture-overview" href="'+escape(src)+'"><picture>'+mobile+'<img src="'+escape(src)+'" alt="'+escape(image['alt'])+'" loading="lazy"></picture></a>'+crops+'<figcaption>'+escape(image['caption'])+' <a class="full-capture-link" href="'+escape(src)+'">Open full capture <span aria-hidden="true">↗</span></a></figcaption></figure>')
        evidence=url(case['evidence_url'])
        if evidence.startswith('/') and evidence.split('#',1)[0][1:]not in files:
            raise ValueError("Case evidence must be in the public source inventory")
        extra=''.join(paragraph(p)for p in case.get('technical_details',[]))
        if slug=='nstack':
            data=files['assets/featured/nstack-search.json'].decode('utf-8')
            json.loads(data)
            media.append('<figure class="case-media"><pre><code>'+escape(data)+'</code></pre><figcaption>Complete recorded source-only search output. Installation and target-runtime acceptance are separate.</figcaption></figure>')
        recorded=''
        if revision:
            recorded='<p class="case-source">Recorded case source: <a href="'+escape(repo+'/tree/'+revision)+'">'+escape(revision)+'</a></p>'
        page=r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__NAME__ · Nazeeh Abdul-Hadi</title><meta name="description" content="__DESCRIPTION__"><link rel="canonical" href="https://nazeeh111.github.io__ROUTE__"><link rel="icon" href="/assets/favicon.svg"><link rel="stylesheet" href="/assets/design/portfolio.css"><link rel="preload" href="/assets/fonts/RethinkSans.ttf" as="font" type="font/ttf" crossorigin></head><body><a class="skip" href="#main">Skip to content</a><header class="site-header shell"><a class="brand" href="/" aria-label="Nazeeh Abdul-Hadi home"><img src="/assets/identity.png" width="32" height="32" alt=""><span>Nazeeh Abdul-Hadi</span></a><nav class="site-nav" aria-label="Main navigation"><a href="/work/">Work</a><a href="/research/">Research</a><a href="/#about">About</a></nav></header><main class="case-page shell" id="main"><div class="case-hero"><div><h1>__NAME__</h1><p class="case-lead">__DESCRIPTION__</p><div class="case-actions">__ACTIONS__</div></div><p class="case-scope">__SCOPE__</p></div>__MEDIA__<section class="case-text"><div><h2>The problem</h2>__PROBLEM__</div><div><h2>The mechanism</h2>__MECHANISM__</div></section><section class="case-text"><div><h2>The observed result</h2>__RESULT__</div><div><h2>Foundations</h2>__FOUNDATIONS__</div></section><section class="case-details"><h2>Inspect the details</h2>__EXTRA__<p class="case-source"><a href="__EVIDENCE__">Recorded evidence and limits</a> · <a href="__REPO__">Project source</a></p>__RECORDED__</section></main><footer class="site-footer"><div class="shell footer-top"><a class="brand" href="/">Nazeeh Abdul-Hadi</a><nav aria-label="Footer"><a href="/work/">All projects</a><a href="/research/">Research</a><a href="https://github.com/nazeeh111">GitHub</a></nav></div></footer></body></html>'''
        values={'NAME':name,'DESCRIPTION':escape(case['lead']),'ROUTE':escape(route),'ACTIONS':action(case['action'],True)+action(case['secondary_action']),'SCOPE':escape(case['scope_note']),'MEDIA':''.join(media),'PROBLEM':paragraph(case['problem']),'MECHANISM':paragraph(case['mechanism']),'RESULT':paragraph(case['observed_result']),'FOUNDATIONS':paragraph(case['foundations']),'EXTRA':extra,'EVIDENCE':escape(evidence),'REPO':escape(repo),'RECORDED':recorded}
        page=re.sub(r'__([A-Z]+)__',lambda match:values[match[1]],page)
        outputs['work/'+slug+'/index.html']=page.encode('utf-8')
    return outputs
