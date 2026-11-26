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
    css='folio-action' if primary else 'folio-secondary'
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
        caption=crop.get('caption');alt=crop['alt']
        if (caption is not None and (not isinstance(caption,str) or not caption.strip())) or not isinstance(alt,str) or not alt.strip():
            raise ValueError("Capture detail requires accurate labels")
        style=';'.join('--'+k+':'+str(v) for k,v in zip(('crop-x','crop-y','crop-width','crop-height','source-width'),(x,y,w,h,sw)))
        caption_html='<figcaption>'+escape(caption)+'</figcaption>' if caption is not None else ''
        rendered.append('<figure><a class="capture-detail" style="'+style+'" href="'+escape(src)+'"><img src="'+escape(src)+'" width="'+str(sw)+'" height="'+str(sh)+'" alt="'+escape(alt)+'" loading="lazy"></a>'+caption_html+'</figure>')
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
        if slug=='vibescope':
            media.append('<section class="case-comparison" aria-labelledby="comparison-title"><h2 id="comparison-title">Display gain, fixed measurement</h2><div class="frame-comparison" style="--reveal:50%"><figure class="frame-original"><picture><source srcset="/assets/featured/vibescope/original-frame72.webp" type="image/webp"><img src="/assets/featured/vibescope/original-frame72.png" width="320" height="192" alt="Original recorded synthetic frame72."></picture><figcaption>Original</figcaption></figure><figure class="frame-enhanced"><picture><source srcset="/assets/featured/vibescope/enhanced-frame72.webp" type="image/webp"><img src="/assets/featured/vibescope/enhanced-frame72.png" width="320" height="192" alt="The same recorded frame with visualization gain20."></picture><figcaption>Visualization ×20</figcaption></figure><span class="comparison-divider" aria-hidden="true"></span></div><div class="comparison-control" hidden><label for="frame-reveal">Reveal enhanced view</label><input id="frame-reveal" type="range" min="0" max="100" value="50" step="1" aria-describedby="comparison-note"><div class="comparison-ends" aria-hidden="true"><span>Original</span><span>Visualization ×20</span></div></div><p id="comparison-note">Both stored gain runs analyze the original frames: 7.30 Hz and 0.280 px remain fixed. This control reveals recorded images, not a new measurement.</p></section>')
        for image_index,image in enumerate(case['media']):
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
            loading=' loading="eager" fetchpriority="high"' if image_index==0 else ' loading="lazy"'
            media.append('<figure class="'+css+'"><div class="capture-overview"><picture>'+mobile+'<img src="'+escape(src)+'" alt="'+escape(image['alt'])+'"'+loading+'></picture></div>'+crops+'<figcaption>'+escape(image['caption'])+' <a class="full-capture-link" href="'+escape(src)+'">Open full capture</a></figcaption></figure>')
        evidence=url(case['evidence_url'])
        if evidence.startswith('/') and evidence.split('#',1)[0][1:]not in files:
            raise ValueError("Case evidence must be in the public source inventory")
        extra=''.join(paragraph(p)for p in case.get('technical_details',[]))
        if case.get('notices_url'):
            notice=url(case['notices_url'])
            if not notice.startswith('/') or notice[1:] not in files:
                raise ValueError("Case notices must be a listed public asset")
            extra+='<p><a href="'+escape(notice)+'">Source, data and license notices</a></p>' 
        if slug=='photonsmith':
            extra+='<p><a href="/assets/featured/photonsmith-hero/">Retained figure data, source ZIP and precise figure meaning</a></p>'
        if slug=='nstack':
            data=files['assets/featured/nstack-search.json'].decode('utf-8')
            json.loads(data)
            media.append('<figure class="case-media"><pre><code>'+escape(data)+'</code></pre><figcaption>Complete recorded source-only search output. Installation and target-runtime acceptance are separate.</figcaption></figure>')
        guide=case.get('reader_guide')
        guide_html='<details class="record-detail"><summary>'+escape(guide['label'])+'</summary>'+paragraph(guide['instructions'])+'</details>' if guide else ''
        recorded=''
        if revision:
            recorded='<p class="case-source"><a href="'+escape(repo+'/tree/'+revision)+'">Source revision <code>'+escape(revision[:12])+'</code></a></p>'
        default_headings={'problem':'Research question','mechanism':'Method','observed_result':'Result'}
        headings=case.get('story_headings',{})
        if not isinstance(headings,dict) or not set(headings)<=set(default_headings):
            raise ValueError("Unknown case story heading")
        if any(not isinstance(label,str) or not label.strip() for label in headings.values()):
            raise ValueError("Case story headings must be nonempty text")
        default_headings.update(headings)
        page=r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__NAME__ · Nazeeh Abdul-Hadi</title>
<meta name="description" content="__DESCRIPTION__">
<link rel="canonical" href="https://nazeeh111.github.io__ROUTE__">
<link rel="icon" href="/assets/favicon.svg">
<link rel="stylesheet" href="/assets/design/portfolio.css">
<link rel="stylesheet" href="/assets/design/interior.css">
</head>
<body class="folio-interior case-register">
<a class="skip" href="#main">Skip to content</a>
<header class="folio-band">
  <div class="folio-width folio-nav">
    <a class="folio-mark" href="/" aria-label="Nazeeh Abdul-Hadi home">Nazeeh Abdul-Hadi</a>
    <nav aria-label="Main navigation"><a href="/work/">Work</a><a href="/research/">Research</a><a href="/#about">About</a></nav>
  </div>
</header>
<main id="main">
  <div class="folio-band">
    <div class="folio-width case-opening">
      <div><a class="back-to-work" href="/work/#projects">Work index</a><h1>__NAME__</h1></div>
      <div class="case-entry"><p class="folio-lead">__DESCRIPTION__</p><div class="folio-actions">__ACTIONS__</div>__GUIDE__</div>
    </div>
  </div>
  <div class="folio-width case-reader">
    <div class="case-evidence">__MEDIA__</div>
    <div class="case-account">
      <section class="result-ledger"><h2>__RESULTHEAD__</h2>__RESULT__<h3>Interpretation</h3><p>__SCOPE__</p></section>
      <div class="case-argument">
        <section><h2>__PROBLEMHEAD__</h2>__PROBLEM__</section>
        <section><h2>__MECHANISMHEAD__</h2>__MECHANISM__</section>
      </div>
    </div>
    <section class="case-appendix">
      <div><h2>Foundations</h2>__FOUNDATIONS__</div>
      <div><h2>Sources and supporting evidence</h2>__EXTRA__<p class="case-source"><a href="__EVIDENCE__">Recorded evidence and limits</a><a href="__REPO__">Project source</a></p>__RECORDED__</div>
    </section>
  </div>
</main>
<footer class="folio-band">
  <div class="folio-width interior-footer"><a href="/">Nazeeh Abdul-Hadi</a><nav aria-label="Footer"><a href="/work/#projects">All projects</a><a href="/research/">Research</a><a href="https://github.com/nazeeh111">GitHub</a></nav></div>
</footer>
</body>
</html>'''
        values={'NAME':name,'DESCRIPTION':escape(case['lead']),'ROUTE':escape(route),'ACTIONS':action(case['action'],True)+action(case['secondary_action']),'GUIDE':guide_html,'SCOPE':escape(case['scope_note']),'MEDIA':''.join(media),'PROBLEMHEAD':escape(default_headings['problem']),'MECHANISMHEAD':escape(default_headings['mechanism']),'RESULTHEAD':escape(default_headings['observed_result']),'PROBLEM':paragraph(case['problem']),'MECHANISM':paragraph(case['mechanism']),'RESULT':paragraph(case['observed_result']),'FOUNDATIONS':paragraph(case['foundations']),'EXTRA':extra,'EVIDENCE':escape(evidence),'REPO':escape(repo),'RECORDED':recorded}
        page=re.sub(r'__([A-Z]+)__',lambda match:values[match[1]],page)
        if slug=='vibescope':
            page=page.replace('</head>','<script src="/assets/portfolio.js" defer></script></head>')
        outputs['work/'+slug+'/index.html']=page.encode('utf-8')
    return outputs
