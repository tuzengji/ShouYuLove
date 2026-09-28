"""Integration check: expansion, escaping, and fail-before-write validation."""
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
    (case / 'scripts').mkdir()
    (case / 'home-assets').mkdir()
    for name in ('index.html', 'projects.json', 'scripts/sync_projects.py', 'home-assets/icons.svg'):
        shutil.copy2(ROOT / name, case / name)
    original = json.loads((case / 'projects.json').read_text())
    expanded = copy.deepcopy(original)
    for i in range(12):
        expanded.append({'id': f'example-{i}', 'name': f'测试项目 {i}', 'category': '活动协作', 'description': '仅用于本地扩展验证', 'url': f'https://example.com/project/{i}'})
    expanded[-1]['name'] = '<script> & "文字"'
    expanded[-1]['creator'] = '<em>甲 & 乙</em>'
    (case / 'projects.json').write_text(json.dumps(expanded, ensure_ascii=False))
    result = subprocess.run([sys.executable, 'scripts/sync_projects.py'], cwd=case, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    generated = (case / 'index.html').read_text()
    assert generated.count('class="project-item"') == 15
    assert generated.count('class="project-slide journey-panel"') == 15
    assert generated.count('class="quick-link"') == 3
    assert '<script> & "文字"' not in generated
    assert '&lt;script&gt; &amp; &quot;文字&quot;' in generated
    assert generated.count('创作者：&lt;em&gt;甲 &amp; 乙&lt;/em&gt;') == 2
    assert '<em>甲 & 乙</em>' not in generated
    creator_count = sum('creator' in project for project in expanded)
    assert generated.count('class="project-creator"') == creator_count
    assert generated.count('class="slide-creator"') == creator_count
    fixture = generated.replace('./home-assets/', '../home-assets/')
    (ROOT / 'output/qa-daylight-expanded.html').write_text(fixture)
    for broken in (
        original + [original[0]],
        [{**original[0], 'url': 'javascript:alert(1)'}],
        [{**original[0], 'icon': 'missing-icon'}],
        [{**original[0], 'id': '../bad-path'}],
        [{**original[0], 'creator': 123}],
        [{**original[0], 'creator': '   '}],
    ):
        (case / 'projects.json').write_text(json.dumps(broken, ensure_ascii=False))
        result = subprocess.run([sys.executable, 'scripts/sync_projects.py'], cwd=case, capture_output=True, text=True)
        assert result.returncode != 0
        assert (case / 'index.html').read_text() == generated, 'Invalid input overwrote the last valid page'
print('PASS: 15 projects, escaped text and optional creators on both surfaces, three shortcuts; invalid records leave HTML intact.')
