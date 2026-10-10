"""Resolve the canonical Markdown and retain a public repository snapshot."""
from pathlib import Path


def source_path(root):
    binding = root / '.content-source-path'
    if not binding.exists():
        return root / 'content-source.md'
    source = Path(binding.read_text(encoding='utf-8').strip()).expanduser()
    if not source.is_absolute():
        raise ValueError('The bound content source must be an absolute path.')
    if not source.is_file():
        raise FileNotFoundError('Bound content source is unavailable: ' + str(source))
    return source


def sync_snapshot(root, text):
    snapshot = root / 'content-source.md'
    if snapshot.exists() and snapshot.read_text(encoding='utf-8') == text:
        return
    temporary = snapshot.with_name(snapshot.name + '.new')
    temporary.write_text(text, encoding='utf-8')
    temporary.replace(snapshot)
