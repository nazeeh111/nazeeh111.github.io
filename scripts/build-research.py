#!/usr/bin/env python3
"""Build the static research library. Python standard library; no runtime build step."""
from pathlib import Path
from html import escape
from datetime import date
import json

ROOT=Path(__file__).resolve().parents[1]
RESEARCH=ROOT/'research'
CATALOG=json.loads((RESEARCH/'catalog.json').read_text())
FILES={f['slug']:f for f in json.loads((RESEARCH/'manifest.json').read_text())['files']}
ORIGIN='https://nazeeh111.github.io'

def esc(value):return escape(str(value),quote=True)
def pretty_date(value):return date.fromisoformat(value).strftime('%b %d, %Y').replace(' 0',' ')
def size(value):return f'{value/1024/1024:.1f} MB' if value>=1024*1024 else f'{round(value/1024)} KB'
def display_date(study):
    value=study.get('displayDate',study.get('date'))
    return pretty_date(value)
def header(title,description,path,image=None):
    image=image or '/research/figures/phaseglass-quantum.webp'
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="author" content="Nazeeh Abdul-Hadi">
<meta name="color-scheme" content="dark"><meta name="theme-color" content="#0b0d10">
<title>{esc(title)} · Nazeeh Abdul-Hadi</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{ORIGIN}{path}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/research/style.css"><script src="/research/app.js" defer></script>
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{ORIGIN}{path}">
<meta property="og:image" content="{ORIGIN}{image}"><meta name="twitter:card" content="summary_large_image">
</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="shell site-header"><a class="identity" href="/">Nazeeh Abdul-Hadi</a>
<nav aria-label="Portfolio"><a href="/#projects">Projects</a><a href="/research/" {'aria-current="page"' if path=='/research/' else ''}>Research</a><a href="https://github.com/nazeeh111">GitHub ↗</a></nav></header>\n'''

def footer():return '''<footer class="shell site-footer"><a class="identity" href="/">Nazeeh Abdul-Hadi</a><nav aria-label="Footer"><a href="/research/">All studies</a><a href="/research/manifest.json">File manifest</a><a href="https://github.com/nazeeh111/nazeeh111.github.io">Site source ↗</a></nav></footer></body></html>\n'''

def bibliography(study):
    year=study['date'][:4]
    return f'''@misc{{abdulhadi{year}{study['id'].replace('-','')},
  author = {{Nazeeh Abdul-Hadi}},
  title = {{{study['title']}}},
  year = {{{year}}},
  url = {{{ORIGIN}/research/{study['id']}/}}
}}'''

def downloads(study):
    slug=study['id'];info=FILES[slug];text=study.get('format')=='Markdown'
    extension='md' if text else 'pdf';label='Report · Markdown' if text else f'Paper · PDF · {info["pages"]} pages'
    html=f'''<section id="downloads" class="reader-section downloads"><h2>Paper & sources</h2><p class="paper-title">{esc(study['title'])}</p><div class="download-list"><a href="/research/papers/{slug}.{extension}" download>{label}<span>{size(info['bytes'])} ↓</span></a>'''
    if not text:html+=f'<a href="/research/sources/{slug}.zip" download>Manuscript sources<span>ZIP ↓</span></a>'
    if study.get('repository'):html+=f'<a href="{esc(study["repository"])}">Code & evidence<span>GitHub ↗</span></a>'
    for supplement in study['supplements']:
        doc=FILES[supplement['id']]
        html+=f'<a class="companion" href="/research/papers/{supplement["id"]}.pdf" download><span>{esc(supplement["title"])}<small>{esc(display_date(supplement))}</small></span><span>{doc["pages"]} pages ↓</span></a>'
        html+=f'<a class="companion-source" href="/research/sources/{supplement["id"]}.zip" download>Companion manuscript sources<span>ZIP ↓</span></a>'
    html+='</div><details class="citation"><summary>Cite this study</summary><pre id="bibtex">'+esc(bibliography(study))+'</pre><button type="button" class="copy-button" hidden>Copy BibTeX</button><p id="copy-status" role="status" aria-live="polite"></p></details></section>'
    return html

def article(study):
    slug=study['id'];body=study['article'];ext='md' if study.get('format')=='Markdown' else 'pdf'
    html=header(body['title'],study['summary'],f'/research/{slug}/',body['figure'])
    html+=f'''<main id="main" class="shell"><div class="breadcrumb"><a href="/research/">← All studies</a><span>{esc(study['topic'])}</span></div>
<article><header class="article-header"><div class="eyebrow">{esc(study['name'])}</div><h1>{esc(body['title'])}</h1>
<p class="article-question">{esc(body['question'])}</p><div class="article-meta"><span>Nazeeh Abdul-Hadi</span><span>{esc(study['outcome'])}</span><span data-date-status="{esc(study.get('dateStatus','verified'))}">{esc(display_date(study))}</span></div>
<div class="article-links"><a href="/research/papers/{slug}.{ext}" download>{'Original report' if ext=='md' else 'Paper PDF'} ↓</a><a href="#downloads">Sources & citation</a></div></header>
<div class="reader-layout"><aside class="contents"><nav aria-label="Study contents"><span>In this study</span><a href="#method">Method</a><a href="#results">Results</a><a href="#interpretation">Interpretation</a><a href="#limits">Limitations</a><a href="#downloads">Paper & sources</a></nav></aside>
<div class="reader-content"><section id="method" class="reader-section"><h2>Method</h2>'''
    if study.get('lineage'):html+=f'<p class="lineage"><strong>{esc(study["lineage"])}.</strong> {esc(study["versionNote"])}</p>'
    for paragraph in body['method']:html+=f'<p>{esc(paragraph)}</p>'
    if body.get('equation'):
        eq=body['equation'];html+=f'<div class="equation"><h3>{esc(eq["label"])}</h3>{eq["html"]}<p>{esc(eq["explanation"])}</p></div>'
    html+='</section><section id="results" class="reader-section"><h2>Results</h2><div class="table-scroll" role="region" aria-label="Study results" tabindex="0"><table><thead><tr>'
    for column in body['columns']:html+=f'<th scope="col">{esc(column)}</th>'
    html+='</tr></thead><tbody>'
    for row in body['rows']:
        html+='<tr>'+f'<th scope="row">{esc(row[0])}</th>'+''.join(f'<td>{esc(value)}</td>' for value in row[1:])+'</tr>'
    html+='</tbody></table></div>'
    if body.get('resultNote'):html+=f'<p>{esc(body["resultNote"])}</p>'
    html+=f'<figure class="study-figure"><a href="{esc(body["figure"])}" aria-label="View full-size study figure"><img src="{esc(body["figure"])}" alt="{esc(body["alt"])}" width="{body["figureWidth"]}" height="{body["figureHeight"]}" decoding="async"></a><figcaption>{esc(body["caption"])}</figcaption></figure></section>'
    html+=f'<section id="interpretation" class="reader-section"><h2>Interpretation</h2><p>{esc(body["interpretation"])}</p></section><section id="limits" class="reader-section"><h2>Limitations</h2><ul>'
    for limitation in body['limits']:html+=f'<li>{esc(limitation)}</li>'
    html+='</ul></section>'+downloads(study)+'</div></div></article><nav class="article-end" aria-label="Research navigation"><a href="/research/">← Back to the research library</a></nav></main>'+footer()
    (RESEARCH/slug/'index.html').write_text(html)
    (RESEARCH/slug/'citation.bib').write_text(bibliography(study)+'\n')

html=header('Research','Study write-ups, results, original papers, and manuscript sources.','/research/')
html+='''<main id="main" class="shell"><header class="library-intro"><div class="eyebrow">Independent research</div><h1>Research</h1><p>Physics, numerical methods, sensing, agents, and finance.</p><div class="library-actions"><a href="/research/all-papers.zip" download>Download all papers <span>14 PDFs + 1 report · 2.5 MB ↓</span></a></div></header>
<section class="library" aria-label="Research studies"><form class="search-form" role="search" hidden><label for="paper-search">Search studies</label><div class="search-row"><input id="paper-search" type="search" name="q" placeholder="Search topics, methods, or results…" autocomplete="off"><button type="reset" class="reset-search">Clear</button></div><fieldset><legend>Filter by topic</legend><div class="filters"><button type="button" data-topic="all" aria-pressed="true">All studies</button>'''
for topic in dict.fromkeys(d['topic'] for d in CATALOG):html+=f'<button type="button" data-topic="{esc(topic)}" aria-pressed="false">{esc(topic)}</button>'
html+='''</div></fieldset></form><div class="results-line"><p id="result-count" role="status" aria-live="polite">12 studies</p></div><div class="paper-list">'''
for study in CATALOG:
    slug=study['id'];body=study['article']
    terms=' '.join([study['name'],study['title'],study['topic'],study['summary'],study['outcome'],study['finding'],study.get('lineage',''),body['title']])
    html+=f'''<article class="paper-row" data-category="{esc(study['topic'])}" data-search="{esc(terms.lower())}"><div class="paper-meta"><span>{esc(study.get('lineage',study['topic']))}</span><span>{esc(study['name'])}</span></div><h2><a href="/research/{slug}/">{esc(body['title'])}</a></h2><p>{esc(study['summary'])}</p><div class="paper-bottom"><span class="outcome">{esc(study['outcome'])}</span><a href="/research/{slug}/" class="study-link">Read study ↗</a></div><p class="paper-date" data-date-status="{esc(study.get('dateStatus','verified'))}">{esc(display_date(study))}</p></article>'''
html+='''</div><div class="empty-state" hidden><h2>No matching studies</h2><p>Try another search or clear the filter.</p><button type="button" id="show-all">Show all studies</button></div></section></main>'''+footer()
(RESEARCH/'index.html').write_text(html)
for study in CATALOG:article(study)
# Keep the previously published report URL, with one canonical reading page.
(RESEARCH/'counterpatch'/'report.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url=./"><link rel="canonical" href="https://nazeeh111.github.io/research/counterpatch/"><title>COUNTERPATCH study</title></head><body><p><a href="./">Read the COUNTERPATCH study</a></p></body></html>\n''')
print(f'Built library and {len(CATALOG)} study readers.')
