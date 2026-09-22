#!/usr/bin/env python3
"""Validate generated Jekyll output without third-party dependencies."""
import json
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.h1 = 0; self.ids = []; self.links = []; self.titles = []; self.title = None
        self.description = []; self.canonicals = []; self.schemas = []; self.schema = None
        self.headings = []; self.lang = ''; self.noindex = False
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag == 'html': self.lang = a.get('lang')
        if tag == 'h1': self.h1 += 1
        if tag in ('h1','h2','h3','h4','h5','h6'): self.headings.append(int(tag[1]))
        if tag == 'title': self.title = ''
        if tag == 'meta' and a.get('name') == 'description': self.description.append(a.get('content',''))
        if tag == 'meta' and a.get('name') == 'robots': self.noindex = 'noindex' in a.get('content','')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonicals.append(a.get('href',''))
        if tag == 'script' and a.get('type') == 'application/ld+json': self.schema = ''
        for key in ('href','src'):
            if key in a: self.links.append(a[key])
    def handle_data(self, data):
        if self.title is not None: self.title += data
        if self.schema is not None: self.schema += data
    def handle_endtag(self, tag):
        if tag == 'title' and self.title is not None: self.titles.append(self.title.strip()); self.title = None
        if tag == 'script' and self.schema is not None:
            self.schemas.append(json.loads(self.schema)); self.schema = None

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site').resolve()
errors = []
def check(condition, message):
    if not condition: errors.append(message)
files = list(root.rglob('*.html'))
check(bool(files), 'No built HTML found')
pages = {f: Page(f.read_text()) for f in files}
titles = []
for file, page in pages.items():
    label = str(file.relative_to(root))
    check(page.h1 == 1, f'{label}: expected one H1, got {page.h1}')
    check(page.lang == 'zh-CN', f'{label}: wrong lang')
    check(len(page.titles) == 1 and bool(page.titles[0]), f'{label}: missing/duplicate title')
    titles += page.titles
    check(len(page.description) == 1 and bool(page.description[0].strip()), f'{label}: missing/duplicate description')
    check(len(page.canonicals) == 1, f'{label}: canonical count')
    expected = '/' + label.removesuffix('index.html')
    check(page.canonicals == ['https://hugfeature.github.io' + expected], f'{label}: wrong canonical {page.canonicals}')
    check(len(page.ids) == len(set(page.ids)), f'{label}: duplicate IDs')
    check(bool(page.schemas), f'{label}: no JSON-LD')
    for before, after in zip(page.headings, page.headings[1:]):
        check(after <= before + 1, f'{label}: heading jump H{before} -> H{after}')
    for link in page.links:
        resolved = urlsplit(urljoin('https://hugfeature.github.io' + expected, link))
        if resolved.scheme not in ('http','https') or resolved.netloc != 'hugfeature.github.io': continue
        path = root / unquote(resolved.path).lstrip('/')
        if resolved.path.endswith('/') or path.is_dir(): path = path / 'index.html'
        check(path.is_file(), f'{label}: broken internal link {link}')
        if resolved.fragment and path in pages:
            check(unquote(resolved.fragment) in pages[path].ids, f'{label}: missing anchor {link}')
check(len(titles) == len(set(titles)), 'Duplicate titles across pages')
required = ['index.html','harness/index.html','about/index.html','tags/index.html','series/index.html','404.html','robots.txt','sitemap.xml','feed.xml','search.json','assets/social-card.png',
'agent-reliability/ai-testing/2026/09/21/agent-hidden-failures.html',
'engineering/patent/2026/09/21/how-to-apply-technical-patent.html',
'harness/what-is-agent-harness/index.html']
for filename in required: check((root/filename).is_file(), f'Missing {filename}')
if (root/'sitemap.xml').is_file():
    tree = ET.parse(root/'sitemap.xml')
    urls = [n.text for n in tree.findall('.//{*}loc')]
    check('https://hugfeature.github.io/' in urls, 'Homepage absent from sitemap')
    check(not any('/search' in u or '/404' in u for u in urls), 'Search or 404 indexed')
    for u in urls:
        path = root / unquote(urlsplit(u).path).lstrip('/')
        if path.is_dir(): path = path/'index.html'
        check(path.is_file(), f'Sitemap points to missing file: {u}')
if (root/'feed.xml').is_file():
    tree = ET.parse(root/'feed.xml')
    check(len(tree.findall('{*}entry')) >= 3, 'Feed missing published posts')
if (root/'search.json').is_file():
    index = json.loads((root/'search.json').read_text())
    check(len(index) >= 3, 'Search index missing posts')
    for post in index: check(all(post.get(k) for k in ['title','description','tags','content','url']), 'Incomplete search entry')
if (root/'robots.txt').is_file():
    check('Sitemap: https://hugfeature.github.io/sitemap.xml' in (root/'robots.txt').read_text(), 'robots sitemap missing')
for file, page in pages.items():
    if any('/'+str(file.relative_to(root)) == '/'+p for p in required[-3:]):
        schema = next((s for s in page.schemas if s.get('@type') == 'BlogPosting'), None)
        check(schema is not None, f'{file.name}: missing BlogPosting')
        if schema: check(bool(schema.get('datePublished')) and bool(schema.get('dateModified')), f'{file.name}: missing schema dates')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'PASS: {len(pages)} HTML pages, internal links/anchors, headings, metadata, JSON-LD, legacy URLs, sitemap, feed and search index.')
