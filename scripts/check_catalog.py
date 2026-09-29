"""Check source-copy fidelity, project partitioning and safe generator failure."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
class Page(HTMLParser):
    def __init__(self,html):
        super().__init__();self.text=[];self.projects=[];self.links=[];self.images=[];self.feed(html)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'data-project' in a:self.projects.append(a['data-project'])
        if tag=='a':self.links.append(a)
        if tag=='img':self.images.append(a)
    def handle_data(self,data):self.text.append(data)
    @property
    def normalized(self):return ''.join(''.join(self.text).split())

def normalized(value):return ''.join(value.split())
content=json.loads((ROOT/'site-content.json').read_text())
original=json.loads((ROOT/'projects.json').read_text())
# Public document and JSON must agree; never silently ship a stale note snapshot.
from import_content import parse
copy_content,copy_projects=parse((ROOT/'content-source.md').read_text())
assert content==copy_content and original==copy_projects, 'Run import_content.py after reviewing source-copy changes'
home=Page((ROOT/'index.html').read_text())
for key in ('identity','meaning','summary','dream','vision','work','collaboration'):
    assert normalized(content[key]) in home.normalized,key
for item in content['principles']:assert normalized(item) in home.normalized
assert not home.images,'The homepage has no standalone photograph section'
for name,collection in [('sign-projects','sign'),('campus','campus')]:
    page=Page((ROOT/name/'index.html').read_text());expected=[p for p in original if p['collection']==collection]
    assert page.projects==[p['id'] for p in expected]
    for p in expected:
        for key in ('name','description','creator'):
            if key in p:assert normalized(p[key]) in page.normalized
        links=[a for a in page.links if a.get('href')==p['url']]
        assert links and all(a.get('target')=='_blank' and 'noopener' in a.get('rel','') for a in links)
(ROOT/'output').mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='catalog-check-',dir=ROOT/'output') as temp:
    case=Path(temp)
    for name in ('site-content.json','projects.json','scripts/sync_projects.py','home-assets/icons.svg','templates/base.html','templates/home.html','templates/collection.html'):
        path=case/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,path)
    def run(records):
        (case/'projects.json').write_text(json.dumps(records,ensure_ascii=False))
        return subprocess.run([sys.executable,'scripts/sync_projects.py'],cwd=case,capture_output=True,text=True)
    expanded=copy.deepcopy(original)
    for i in range(12):expanded.append(dict(id=f'example-{i}',name=f'测试 {i}',collection='sign' if i%2==0 else 'campus',category='测试',description='扩展检查',url=f'https://example.com/{i}'))
    expanded[-1]['name']='<script> & "文字"';expanded[-1]['creator']='<em>甲 & 乙</em>'
    r=run(expanded);assert r.returncode==0,r.stderr
    paths=['index.html','sign-projects/index.html','campus/index.html'];generated={p:(case/p).read_text() for p in paths}
    for collection,path in [('sign',paths[1]),('campus',paths[2])]:
        assert Page(generated[path]).projects==[p['id'] for p in expanded if p['collection']==collection]
    assert '&lt;script&gt; &amp; &quot;文字&quot;' in generated[paths[2]]
    assert '设计者：&lt;em&gt;甲 &amp; 乙&lt;/em&gt;' in generated[paths[2]]
    for broken in (original+[original[0]],[{**original[0],'url':'javascript:alert(1)'}],[{**original[0],'id':'../bad'}],[{**original[0],'icon':'missing'}],[{**original[0],'creator':123}],[{**original[0],'collection':'other'}]):
        assert run(broken).returncode!=0
        assert {p:(case/p).read_text() for p in paths}==generated,'Invalid input replaced a page'
    assert run([p for p in original if p['collection']=='sign']).returncode==0
    assert '这里暂时没有作品。' in (case/paths[2]).read_text()
print('PASS: all approved copy, four creator records, two catalogs, new-tab links, no standalone photo, escaping, expansion and fail-before-write validation.')
