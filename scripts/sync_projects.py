"""Generate the homepage collection links and two standalone project catalogs."""
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
COLLECTIONS = {
    'sign': {'name': '手语作品', 'path': 'sign-projects', 'icon': 'book-open-text',
             'description': '围绕手语学习与表达，探索查询工具、互动游戏和无障碍交流。'},
    'campus': {'name': '燕园服务', 'path': 'campus', 'icon': 'squares-four',
               'description': '心创组成员为北大同学开发的实用工具，让校园学习与生活更方便。'},
}
catalog = json.loads((ROOT / 'projects.json').read_text())
if not isinstance(catalog, list):
    raise ValueError('projects.json must contain an array')
icons = {item.get('id') for item in ET.parse(ROOT / 'home-assets/icons.svg').getroot()}
ids, rows = set(), {key: [] for key in COLLECTIONS}

def icon(name, prefix='./', extra=''):
    return f'<svg class="icon {extra}" aria-hidden="true"><use href="{prefix}home-assets/icons.svg#{name}"></use></svg>'

def navigation(prefix='./', active=None):
    about = '#about' if prefix == './' else '../#about'
    links = [f'<a href="{about}">关于心创组</a>']
    for key, collection in COLLECTIONS.items():
        emphasis = ' class="nav-projects"' if active is None or key == active else ''
        current = ' aria-current="page"' if key == active else ''
        links.append(f'<a{emphasis}{current} href="{prefix}{collection["path"]}/">{collection["name"]}</a>')
    return ''.join(links)

def row(project, prefix='./', external=True):
    p = {key: escape(str(value), quote=True) for key, value in project.items()}
    creator = f'<span class="project-creator">创作者：{p["creator"]}</span>' if 'creator' in p else ''
    target = ' target="_blank" rel="noopener"' if external else ''
    return f'''          <a class="project-item" data-project="{p['id']}" data-category="{p['category']}" href="{p['url']}"{target}>
            <span class="project-icon">{icon(p.get('icon', 'arrow-up-right'), prefix)}</span>
            <span class="project-copy"><span class="project-name">{p['name']}</span><span class="project-summary">{p['description']}</span>{creator}</span>
            <span class="project-go">{icon('arrow-up-right', prefix)}</span>
          </a>'''

for project in catalog:
    for field in ('id', 'name', 'collection', 'category', 'description', 'url'):
        if not isinstance(project.get(field), str) or not project[field].strip():
            raise ValueError(f'Project requires a nonempty {field}')
    if project['collection'] not in COLLECTIONS:
        raise ValueError('Unknown project collection')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', project['id']):
        raise ValueError('Project id must be a lowercase slug')
    if project['id'] in ids:
        raise ValueError(f'Duplicate project id: {project["id"]}')
    ids.add(project['id'])
    if 'creator' in project and (not isinstance(project['creator'], str) or not project['creator'].strip()):
        raise ValueError('Project creator must be a nonempty string when provided')
    url = urlparse(project['url'])
    if url.scheme not in {'https', 'http'} or not url.netloc:
        raise ValueError('Project URL must be an HTTP(S) address')
    if project.get('icon', 'arrow-up-right') not in icons:
        raise ValueError('Unknown project icon')
    rows[project['collection']].append(row(project, '../'))

home = (ROOT / 'index.html').read_text()
shortcuts, slides, collection_rows = [], [], []
for key, collection in COLLECTIONS.items():
    name, description, symbol = (collection[x] for x in ('name', 'description', 'icon'))
    url = f'./{collection["path"]}/'
    shortcuts.append(f'<a class="quick-link" href="{url}">{icon(symbol)}<span>{name}</span>{icon("arrow-up-right", extra="quick-arrow")}</a>')
    slides.append(f'''<article id="work-{key}" class="project-slide journey-panel" data-label="{name}" aria-labelledby="slide-{key}">
      <div class="slide-copy"><h2 class="slide-title collection-title" id="slide-{key}"><a class="slide-link" href="{url}">{name}{icon('arrow-up-right')}</a></h2><p class="slide-description">{description}</p></div>
      <div class="project-art" aria-hidden="true">{icon(symbol)}</div>
    </article>''')
    collection_rows.append(row({'id': key, 'name': name, 'category': name, 'description': description, 'url': url, 'icon': symbol}, external=False))
for slot, content in (('PROJECTS', collection_rows), ('SHORTCUTS', shortcuts), ('SHOWCASE', slides)):
    home, count = re.subn(rf'<!-- {slot}:START -->.*?<!-- {slot}:END -->',
        lambda _: f'<!-- {slot}:START -->\n' + '\n'.join(content) + f'\n<!-- {slot}:END -->', home, flags=re.S)
    if count != 1:
        raise ValueError(f'Expected exactly one {slot} slot in index.html')
home, count = re.subn(r'(<nav class="primary-nav" aria-label="主导航">).*?(</nav>)',
    lambda match: match[1] + navigation() + match[2], home, flags=re.S)
if count != 1:
    raise ValueError('Expected one homepage navigation')

template = (ROOT / 'templates/collection.html').read_text()
outputs = {ROOT / 'index.html': home}
for key, collection in COLLECTIONS.items():
    page = template
    values = {'TITLE': collection['name'], 'DESCRIPTION': collection['description'],
              'PATH': collection['path'], 'NAV': navigation('../', key),
              'PROJECTS': '\n'.join(rows[key]) if rows[key] else '<p class="collection-empty">这里暂时没有作品。</p>'}
    for token, value in values.items():
        marker = f'@@{token}@@'
        if marker not in page:
            raise ValueError(f'Missing template marker: {marker}')
        page = page.replace(marker, value)
    if re.search(r'@@[A-Z]+@@', page):
        raise ValueError('Unresolved collection template marker')
    outputs[ROOT / collection['path'] / 'index.html'] = page
# Validate all records and all pages before changing any generated output.
for path, html in outputs.items():
    path.parent.mkdir(exist_ok=True)
    path.write_text(html)
print(f'Synced {len(catalog)} projects into two collection pages and homepage links.')
