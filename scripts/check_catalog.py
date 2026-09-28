"""Integration checks for partitioned pages, escaping, and fail-before-write validation."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
(ROOT / 'output').mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='catalog-check-', dir=ROOT / 'output') as temporary:
    case = Path(temporary)
    for name in ('index.html', 'projects.json', 'scripts/sync_projects.py', 'home-assets/icons.svg', 'templates/collection.html'):
        destination = case / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, destination)
    original = json.loads((case / 'projects.json').read_text())
    expanded = copy.deepcopy(original)
    for i in range(12):
        expanded.append({'id': f'example-{i}', 'name': f'测试项目 {i}', 'collection': 'sign' if i % 2 == 0 else 'campus', 'category': '活动协作', 'description': '仅用于本地扩展验证', 'url': f'https://example.com/project/{i}'})
    expanded[-1]['name'] = '<script> & "文字"'
    expanded[-1]['creator'] = '<em>甲 & 乙</em>'
    def run(records):
        (case / 'projects.json').write_text(json.dumps(records, ensure_ascii=False))
        return subprocess.run([sys.executable, 'scripts/sync_projects.py'], cwd=case, capture_output=True, text=True)
    result = run(expanded)
    assert result.returncode == 0, result.stderr
    paths = ['index.html', 'sign-projects/index.html', 'campus/index.html']
    generated = {name: (case / name).read_text() for name in paths}
    assert generated['index.html'].count('class="quick-link"') == 2
    assert generated['index.html'].count('class="project-slide journey-panel"') == 2
    for collection, path in [('sign', paths[1]), ('campus', paths[2])]:
        html = generated[path]
        expected = [p for p in expanded if p['collection'] == collection]
        assert html.count('class="project-item"') == len(expected)
        assert html.count('class="project-creator"') == sum('creator' in p for p in expected)
        for project in expanded:
            assert (f'data-project="{project["id"]}"' in html) == (project['collection'] == collection)
        assert '@@' not in html
    campus = generated[paths[2]]
    assert '&lt;script&gt; &amp; &quot;文字&quot;' in campus
    assert '创作者：&lt;em&gt;甲 &amp; 乙&lt;/em&gt;' in campus
    assert '<script> & "文字"' not in campus and '<em>甲 & 乙</em>' not in campus
    for broken in (
        original + [original[0]],
        [{**original[0], 'url': 'javascript:alert(1)'}],
        [{**original[0], 'icon': 'missing-icon'}],
        [{**original[0], 'id': '../bad-path'}],
        [{**original[0], 'creator': 123}],
        [{**original[0], 'creator': '   '}],
        [{**original[0], 'collection': '../wrong'}],
    ):
        assert run(broken).returncode != 0
        assert {name: (case / name).read_text() for name in paths} == generated
    # An empty collection gets an explicit empty state; no projects leak across pages.
    assert run([p for p in original if p['collection'] == 'sign']).returncode == 0
    assert '这里暂时没有作品。' in (case / paths[2]).read_text()
print('PASS: collection partitioning, expansion, escaped creators, empty state and invalid-input protection across three pages.')
