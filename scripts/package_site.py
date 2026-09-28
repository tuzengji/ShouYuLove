"""Package only public homepage files; archives and research stay private."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parent.parent
out = root / 'output/shouyulove-home-daylight.zip'
out.parent.mkdir(exist_ok=True)
files = [root / 'index.html'] + sorted(p for p in (root / 'home-assets').rglob('*') if p.is_file() and p.name != '.DS_Store')
with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
    for file in files:
        archive.write(file, file.relative_to(root))
with ZipFile(out) as archive:
    assert archive.testzip() is None
    assert all(name == 'index.html' or name.startswith('home-assets/') for name in archive.namelist())
print(f'{out}\n{len(files)} files, {out.stat().st_size:,} bytes; no archives or research included.')
