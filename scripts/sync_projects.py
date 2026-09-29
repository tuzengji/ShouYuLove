"""Render the homepage and two catalogs from approved copy and project records."""
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
content = json.loads((ROOT / 'site-content.json').read_text())
catalog = json.loads((ROOT / 'projects.json').read_text())
COLLECTIONS = content['collections']
if set(COLLECTIONS) != {'sign', 'campus'}:
    raise ValueError('Expected the two approved collections')
for key, collection in COLLECTIONS.items():
    if collection['path'] != {'sign': 'sign-projects', 'campus': 'campus'}[key]:
        raise ValueError('Do not change public collection routes')
if not isinstance(catalog, list):
    raise ValueError('projects.json must contain an array')
icons = {item.get('id') for item in ET.parse(ROOT / 'home-assets/icons.svg').getroot()}
ids = set()
for project in catalog:
    for field in ('id', 'name', 'collection', 'category', 'description', 'url'):
        if not isinstance(project.get(field), str) or not project[field].strip():
            raise ValueError(f'Project requires a nonempty {field}')
    if project['collection'] not in COLLECTIONS:
        raise ValueError('Unknown project collection')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', project['id']) or project['id'] in ids:
        raise ValueError('Project id must be a unique lowercase slug')
    ids.add(project['id'])
    if 'creator' in project and (not isinstance(project['creator'], str) or not project['creator'].strip()):
        raise ValueError('Project creator must be a nonempty string when provided')
    url = urlparse(project['url'])
    if url.scheme not in {'https', 'http'} or not url.netloc:
        raise ValueError('Project URL must be an HTTP(S) address')
    if project.get('icon', 'arrow-up-right') not in icons:
        raise ValueError('Unknown project icon')
for key in ('identity', 'meaning', 'summary', 'dream', 'vision', 'work', 'collaboration'):
    if not isinstance(content.get(key), str) or not content[key].strip():
        raise ValueError(f'Missing public copy: {key}')
if not content.get('principles') or any(not isinstance(p, str) for p in content['principles']):
    raise ValueError('Missing principles')

def render(template, values):
    def replace(match):
        if match[1] not in values:
            raise ValueError(f'Missing template value: {match[1]}')
        return values[match[1]]
    return re.sub(r'@@([A-Z]+)@@', replace, template)

def artwork(project):
    id = project['id']
    if id == 'signtrace':
        return '<span class="trace-orbit orbit-one"></span><span class="trace-orbit orbit-two"></span><span class="trace-orbit orbit-three"></span><span class="trace-character display">语</span><span class="art-word" lang="en">SignTrace</span>'
    if id == 'dictionary':
        return '<div class="dictionary-grid">'+''.join(f'<span>{char}</span>' for char in '手语世界以手予爱学习表达')+'</div>'
    if id == 'chuanqinghuiyi':
        return '<span class="game-character display">传</span><span class="game-character display">情</span><span class="game-character display">绘</span><span class="game-character display">意</span>'
    if id == 'pinhaoke':
        return '<div class="course-grid">'+''.join('<i></i>' for _ in range(28))+'</div><span class="course-word display">拼好课</span>'
    return '<span class="generic-art display">'+escape(project['name'])+'</span>'

def project_rows(projects):
    rows = []
    for index, project in enumerate(projects):
        p = {key: escape(str(value), quote=True) for key, value in project.items()}
        art = p['id'] if p['id'] in {'signtrace','dictionary','chuanqinghuiyi','pinhaoke'} else 'generic'
        creator = f'<p class="project-creator">设计者：{p["creator"]}</p>' if 'creator' in p else ''
        rows.append(f'''<article class="project grid project-{art}" id="work-{p['id']}" data-project="{p['id']}" aria-labelledby="title-{p['id']}">
  <a class="project-media" href="{p['url']}" target="_blank" rel="noopener" aria-label="打开{p['name']}，在新标签页" data-cursor="进入">
    <div class="art art-{art}" aria-hidden="true">{artwork(project)}</div><span class="media-entry" aria-hidden="true">{p['name']} <span>↗</span></span>
  </a>
  <div class="project-copy"><h3 class="display" id="title-{p['id']}"><a href="{p['url']}" target="_blank" rel="noopener">{p['name']} <span aria-hidden="true">↗</span></a></h3><p class="project-description">{p['description']}</p>{creator}</div><span class="quick-name display" aria-hidden="true">{p['name']}</span>
</article>''')
    return '\n'.join(rows) if rows else '<p class="empty-state">这里暂时没有作品。</p>'

def nav(prefix, active):
    about = '#about' if active is None else '../#about'
    current = ' aria-current="page"' if active else ''
    return f'<a href="{about}">关于心创组</a><a class="nav-portfolio" href="{prefix}#works"{current}>作品集</a>'

def collection_links(prefix, active=None, descriptions=False):
    links = []
    for key, c in COLLECTIONS.items():
        current = ' aria-current="page"' if key == active else ''
        desc = f'<span class="collection-description">{escape(c["description"])}</span>' if descriptions else ''
        links.append(f'<a href="{prefix}{c["path"]}/"{current}><span class="collection-name">{escape(c["name"])} <span aria-hidden="true">↗</span></span>{desc}</a>')
    return ''.join(links)

base = (ROOT/'templates/base.html').read_text()
home_template = (ROOT/'templates/home.html').read_text()
collection_template = (ROOT/'templates/collection.html').read_text()
plain = {key.upper():escape(value) for key,value in content.items() if isinstance(value,str)}
outputs = {}
for active in (None, 'sign', 'campus'):
    prefix = './' if active is None else '../'
    c = COLLECTIONS.get(active)
    path = c['path']+'/' if c else ''
    title = f'{c["name"]} · 以手予爱 ShouYuLove' if c else content['brand']
    values = {**plain, 'TITLE':escape(title), 'DESCRIPTION':escape(c['description'] if c else content['summary']),
        'PREFIX':prefix, 'PATH':path, 'PAGE':active or 'home', 'NAV':nav(prefix,active),
        'PRINCIPLES':''.join(f'<li>{escape(p)}</li>' for p in content['principles']),
        'MENULINKS':collection_links(prefix,active,True), 'CREDIT':''}
    if active is None:
        values['IDENTITY'] = escape(content['identity']).replace('手语分社心创组','<span class="identity-group">手语分社心创组</span>')
        values['DREAM'] = ''.join('<span class="reveal-line">'+escape(part)+'</span>' for part in re.findall(r'.+?(?:。|，(?=都)|$)',content['dream']))
        values['COLLECTIONLINKS'] = collection_links(prefix,descriptions=True)
        core, other = (COLLECTIONS['sign'], COLLECTIONS['campus'])
        values.update(
            CORENAME=escape(core['name']), COREDESCRIPTION=escape(core['description']),
            COREPATH=prefix+core['path']+'/', COREPROJECTS=project_rows([p for p in catalog if p['collection']=='sign']),
            OTHERNAME=escape(other['name']), OTHERDESCRIPTION=escape(other['description']),
            OTHERPATH=prefix+other['path']+'/', OTHERPROJECTS=project_rows([p for p in catalog if p['collection']=='campus']),
        )
        values['CONTENT'] = render(home_template, values)
    else:
        other = COLLECTIONS['campus' if active == 'sign' else 'sign']
        values.update(COLLECTIONTITLE=escape(c['name']),COLLECTIONDESCRIPTION=escape(c['description']),
            COLLECTIONTABS=collection_links(prefix,active), OTHERPATH='../'+other['path']+'/', OTHERNAME=escape(other['name']),
            PROJECTS=project_rows([p for p in catalog if p['collection']==active]))
        values['CONTENT'] = render(collection_template,values)
    outputs[ROOT/path/'index.html'] = render(base, values)
# All records and templates are validated before any generated page is replaced.
for path, html in outputs.items():
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(html)
print(f'Synced {len(catalog)} projects and approved copy into three public pages.')
