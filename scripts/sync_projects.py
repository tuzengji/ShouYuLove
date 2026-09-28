"""Build all three navigation surfaces from one validated project catalog."""
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
catalog = json.loads((ROOT / 'projects.json').read_text())
if not isinstance(catalog, list):
    raise ValueError('projects.json must contain an array')
icons = {item.get('id') for item in ET.parse(ROOT / 'home-assets/icons.svg').getroot()}
ids, rows, shortcuts, slides = set(), [], [], []

def icon(name, extra=''):
    return f'<svg class="icon {extra}" aria-hidden="true"><use href="./home-assets/icons.svg#{name}"></use></svg>'

for project in catalog:
    for field in ('id', 'name', 'category', 'description', 'url'):
        if not isinstance(project.get(field), str) or not project[field].strip():
            raise ValueError(f'Project requires a nonempty {field}: {project!r}')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', project['id']):
        raise ValueError(f'Project id must be a lowercase slug: {project["id"]}')
    if project['id'] in ids:
        raise ValueError(f'Duplicate project id: {project["id"]}')
    ids.add(project['id'])
    if 'creator' in project and (not isinstance(project['creator'], str) or not project['creator'].strip()):
        raise ValueError('Project creator must be a nonempty string when provided')
    url = urlparse(project['url'])
    if url.scheme not in {'https', 'http'} or not url.netloc:
        raise ValueError(f'Project URL must be an HTTP(S) address: {project["url"]}')
    symbol = project.get('icon', 'arrow-up-right')
    if symbol not in icons:
        raise ValueError(f'Unknown icon: {symbol}')
    p = {key: escape(str(value), quote=True) for key, value in project.items()}
    row_creator = f'<span class="project-creator">创作者：{p["creator"]}</span>' if 'creator' in p else ''
    slide_creator = f'<p class="slide-creator">创作者：{p["creator"]}</p>' if 'creator' in p else ''
    rows.append(f'''          <a class="project-item" data-project="{p['id']}" data-category="{p['category']}" href="{p['url']}" target="_blank" rel="noopener">
            <span class="project-icon">{icon(symbol)}</span>
            <span class="project-copy"><span class="project-name">{p['name']}</span><span class="project-summary">{p['description']}</span>{row_creator}</span>
            <span class="project-go">{icon('arrow-up-right')}</span>
          </a>''')
    if len(shortcuts) < 3:
        shortcuts.append(f'''            <a class="quick-link" href="{p['url']}" target="_blank" rel="noopener">{icon(symbol)}<span>{p['name']}</span>{icon('arrow-up-right', 'quick-arrow')}</a>''')
    slides.append(f'''        <article id="work-{p['id']}" class="project-slide journey-panel" data-label="{p['name']}" aria-labelledby="slide-{p['id']}">
          <div class="slide-copy"><h2 class="slide-title" id="slide-{p['id']}"><a class="slide-link" href="{p['url']}" target="_blank" rel="noopener">{p['name']}{icon('arrow-up-right')}</a></h2><p class="slide-description">{p['description']}</p>{slide_creator}</div>
          <div class="project-art" aria-hidden="true">{icon(symbol)}</div>
        </article>''')

path = ROOT / 'index.html'
html = path.read_text()
for slot, content in (('PROJECTS', rows), ('SHORTCUTS', shortcuts), ('SHOWCASE', slides)):
    html, count = re.subn(
        rf'<!-- {slot}:START -->.*?<!-- {slot}:END -->',
        lambda _, key=slot, lines=content: f'<!-- {key}:START -->\n' + '\n'.join(lines) + f'\n        <!-- {key}:END -->',
        html, flags=re.S,
    )
    if count != 1:
        raise ValueError(f'Expected exactly one {slot} slot in index.html')
# No write takes place until every record and every output slot has been validated.
path.write_text(html)
print(f'Synced {len(rows)} projects, {len(shortcuts)} shortcuts and {len(slides)} showcase panels.')
