"""A bound note remains authoritative while the repository snapshot is refreshed."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location('content_source', Path(__file__).resolve().parents[1] / 'scripts/content_source.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ContentSourceTests(unittest.TestCase):
    def test_note_updates_refresh_snapshot_and_missing_binding_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            snapshot = root / 'content-source.md'
            snapshot.write_text('旧副本', encoding='utf-8')
            self.assertEqual(module.source_path(root), snapshot)
            note = root / '原稿.md'
            note.write_text('新原稿', encoding='utf-8')
            (root / '.content-source-path').write_text(str(note), encoding='utf-8')
            for text in ['新原稿', '再次更新的原稿']:
                note.write_text(text, encoding='utf-8')
                module.sync_snapshot(root, module.source_path(root).read_text(encoding='utf-8'))
                self.assertEqual(snapshot.read_text(encoding='utf-8'), text)
                self.assertEqual(note.read_text(encoding='utf-8'), text)
            note.unlink()
            with self.assertRaises(FileNotFoundError):
                module.source_path(root)
