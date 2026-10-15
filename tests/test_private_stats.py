"""Daily requests, anonymous deduplication, filtering and private storage."""
import importlib.util
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('visits', Path(__file__).resolve().parents[1] / 'deploy/private_stats/visits.py')
visits = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visits)


class PrivateStatisticsTests(unittest.TestCase):
    def test_days_counts_filters_and_storage(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            connection, key = visits.open_database(directory)
            event = dict(time='2026-10-11T16:01:00+00:00', address='192.0.2.1', path='/portfolio/index.html', method='GET', status=200, ua='Chrome Mobile', content_type='text/html; charset=utf-8')
            self.assertTrue(visits.record(connection,key,event))
            self.assertTrue(visits.record(connection,key,event))
            self.assertTrue(visits.record(connection,key,{**event,'path':'/index.html'}))
            self.assertTrue(visits.record(connection,key,{**event,'address':'192.0.2.2','status':304}))
            for change in [dict(path='/assets/entry.js',content_type='application/javascript'),dict(path='/catchpot/api/projects',content_type='application/json'),dict(status=308),dict(method='HEAD'),dict(ua='ShouYuLove-QA'),dict(ua='Googlebot')]:
                self.assertFalse(visits.record(connection,key,{**event,**change}))
            connection.close()
            result = visits.report(directory/'visits.sqlite', 3660)
            self.assertEqual(result['days'],[dict(date='2026-10-12',views=4,visitors=2)])
            self.assertEqual(result['total'],dict(views=4,visitors=2))
            self.assertNotIn('192.0.2',json.dumps(result))
            self.assertNotIn(b'192.0.2.1',(directory/'visits.sqlite').read_bytes())
            self.assertEqual((directory/'secret.key').stat().st_mode & 0o777,0o600)
            self.assertEqual((directory/'visits.sqlite').stat().st_mode & 0o777,0o600)

    def test_arbitrary_pages_cached_pages_and_original_routes(self):
        event = dict(status=200, content_type='text/html; charset=utf-8', destination='document', host='shouyulove.cn')
        for path in ['/', '/portfolio/', '/catchpot/', '/signtrace/', '/dict/entries', '/chuanqinghuiyi/',
                     '/2026-sign-language-cultural-festival/', '/2026-year-end-summary/', '/signplay/',
                     '/future-project/deep/page', '/new/page.html', '/loveheart/12345', '/shouyu/']:
            with self.subTest(path=path):
                self.assertEqual(visits.page_path({**event,'path':path}), path)
        self.assertEqual(visits.page_path({**event,'path':'/future/route?token=private','resolved_path':'/index.html'}), '/future/route')
        self.assertEqual(visits.page_path({**event,'path':'/new/index.html?search=private'}), '/new/')
        self.assertEqual(visits.page_path({**event,'path':'/%E6%96%B0%E9%A1%B5%E9%9D%A2/'}), '/新页面/')
        for mime in ['text/html', 'TEXT/HTML; charset=UTF-8', 'application/xhtml+xml']:
            self.assertEqual(visits.page_path({**event,'path':'/new/', 'content_type':mime}), '/new/')
        for headers in [dict(destination='document'),dict(resolved_path='/new/index.html'),
                        dict(accept='text/html,application/xhtml+xml'),dict(upstream_type='text/html')]:
            cached = {**event, 'path':'/new/', 'status':304, 'content_type':'', 'destination':'', **headers}
            with self.subTest(headers=headers):
                self.assertEqual(visits.page_path(cached), '/new/')

    def test_assets_api_prefetch_and_invalid_paths_are_excluded(self):
        event = dict(status=200, path='/new/', content_type='text/html', destination='document')
        changes = [dict(content_type='application/json'), dict(content_type='image/png'),
                   dict(destination='empty'), dict(destination='script'), dict(purpose='prefetch'),
                   dict(sec_purpose='prefetch;prerender'), dict(host='unrelated.example'),
                   dict(path='//other.example/a'), dict(path='/bad%0Apath'), dict(path='/bad%3Ftoken'),
                   dict(path='relative.html'), dict(path='/bad\\path')]
        for change in changes:
            with self.subTest(change=change):
                self.assertIsNone(visits.page_path({**event, **change}))
        for path in ['/asset.js', '/api/items.json', '/icon.png', '/data.bin']:
            self.assertIsNone(visits.page_path(dict(path=path,status=304,content_type='',destination='',accept='*/*')))
        self.assertIsNone(visits.page_path(dict(path='/asset.js',status=304,destination='document',accept='text/html')))

    def test_retains_history_and_deduplicates_across_pages(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            connection, key = visits.open_database(directory)
            old_day = (datetime.now(visits.BEIJING).date() - timedelta(days=60)).isoformat()
            connection.execute('INSERT INTO visits VALUES(?,?,?,?)', (old_day,'old-visitor','/',7))
            connection.commit()
            connection.close()
            connection, restored_key = visits.open_database(directory)
            self.assertEqual(key, restored_key)
            event = dict(time=datetime.now(timezone.utc).isoformat(), address='192.0.2.1',method='GET',status=200,ua='Browser',content_type='text/html')
            for path in ['/catchpot/', '/brand-new/page.html?search=private', '/catchpot/']:
                self.assertTrue(visits.record(connection,key,{**event,'path':path}))
            connection.close()
            result = visits.report(directory/'visits.sqlite',30)
            self.assertEqual(result['period'],dict(views=3,visitors=1))
            self.assertEqual(result['total'],dict(views=10,visitors=2))
            self.assertEqual(len(result['pages']),2)
            self.assertNotIn('search=',json.dumps(result))
            self.assertNotIn('192.0.2.1',json.dumps(result))


if __name__ == '__main__':
    unittest.main()
