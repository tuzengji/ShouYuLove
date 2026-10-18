from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from prepare_cdn import SHARED, prepare, record, rewrite

BASE = 'https://assets.shouyulove.cn/v/test-1'


class CDNTests(unittest.TestCase):
    def test_assets_only_and_worker_origin(self):
        original = '''<a href="/signtrace/">query</a><img src="/images/a.png"/><style>a{src:url(/assets/font.woff2)}</style>{"baseURL":"/","buildAssetsDir":"/assets/","cdnURL":""}fetch("/__syl/portfolio-click/a");new URL("sortGeometryVertices-123.js",import.meta.url)'''
        actual = rewrite(original, BASE)
        self.assertIn('href="/signtrace/"', actual)
        self.assertIn(BASE + '/' + SHARED + '/images/a.png', actual)
        self.assertIn(BASE + '/' + SHARED + '/assets/font.woff2', actual)
        self.assertIn('"buildAssetsDir":"/assets/"', actual)
        self.assertIn('fetch("/__syl/portfolio-click/a")', actual)
        self.assertIn('new URL("/assets/sortGeometryVertices-123.js",location.href)', actual)
        manifest = '"/' + SHARED + '/shouyulove/works-manifest.v1.json"'
        self.assertEqual(rewrite(manifest, BASE), manifest)
        self.assertEqual(rewrite(actual, BASE), actual)
        self.assertIn(BASE + '-next/' + SHARED + '/images/a.png', rewrite(actual, BASE + '-next'))

    def test_whitelist_and_immutable_origin(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'source'
            asset = source / SHARED / 'assets/a.js'
            asset.parent.mkdir(parents=True)
            asset.write_text('fetch("/webgl/a.glb")')
            (source / 'index.html').write_text('<head></head><script src="/assets/a.js"></script>')
            (source / 'private.key').write_text('must not be exported')
            (source / 'assets').symlink_to(SHARED + '/assets')
            names = ['index.html', SHARED + '/assets/a.js']
            manifest = {'files': {n: record(source / n) for n in names},
                        'symlinks': {'assets': SHARED + '/assets'}, 'routes': {'/': 'index.html'}}
            manifest['bytes'] = sum(x['bytes'] for x in manifest['files'].values())
            prepare(source, manifest, root / 'out', BASE)
            self.assertEqual((root / 'out/site' / SHARED / 'assets/a.js').read_bytes(), asset.read_bytes())
            self.assertFalse((root / 'out/site/private.key').exists())
            uploaded = root / 'out/upload/v/test-1' / SHARED / 'assets/a.js'
            self.assertIn(BASE, uploaded.read_text())
            self.assertFalse((root / 'out/upload/v/test-1/index.html').exists())
            with self.assertRaises(ValueError):
                prepare(source, manifest, root / 'out', BASE)


if __name__ == '__main__':
    unittest.main()
