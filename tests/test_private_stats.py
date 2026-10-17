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

    def test_projects_group_aliases_and_new_projects_without_losing_history(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            connection, key = visits.open_database(directory)
            today = datetime.now(visits.BEIJING).date().isoformat()
            rows = [(today, 'one', '/signtrace/', 3),
                    (today, 'one', '/vocab', 2),
                    (today, 'two', '/signtrace/vocab', 1),
                    (today, 'one', '/portfolio/', 4),
                    (today, 'one', '/future-project/first', 5),
                    (today, 'one', '/future-project/second', 2),
                    (today, 'two', '/projects/jieguo/', 1)]
            connection.executemany('INSERT INTO visits VALUES(?,?,?,?)', rows)
            connection.commit()
            # Report remains usable before the new health table is installed.
            connection.execute('DROP TABLE project_health')
            connection.commit()
            connection.close()
            result = visits.report(directory/'visits.sqlite', 30)
            totals = {r['project']: r for r in result['projects']}
            self.assertEqual((totals['signtrace']['views'], totals['signtrace']['visitors']), (6, 2))
            self.assertEqual((totals['path:/future-project']['views'], totals['path:/future-project']['visitors']), (7, 1))
            self.assertEqual(totals['main']['views'], 1)
            self.assertEqual(totals['dict']['views'], 0)
            self.assertEqual(sum(r['views'] for r in result['projects']), result['period']['views'])
            self.assertEqual(sum(r['views'] for r in result['project_days']), result['period']['views'])
            self.assertEqual(result['period']['visitors'], 2)
            self.assertEqual(result['project_collector'], [])
            self.assertEqual(result['coverage']['first_recorded_date'], today)
            self.assertEqual(len(result['days']), 1)  # No invented zeros before collection began.
            connection, same_key = visits.open_database(directory)
            self.assertEqual(key, same_key)
            self.assertEqual(connection.execute('SELECT SUM(count) FROM visits').fetchone()[0], 18)
            connection.close()

    def test_candidate_observation_can_verify_every_project_without_fake_visits(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            connection, key = visits.open_database(directory)
            event = dict(time=datetime.now(timezone.utc).isoformat(), address='192.0.2.1',
                         method='GET', status=200, ua='ShouYuLove-QA', content_type='text/html')
            for path in ['/', '/portfolio/', '/signtrace/', '/dict/entries', '/chuanqinghuiyi/',
                         '/catchpot/', '/2026-sign-language-cultural-festival/',
                         '/2026-year-end-summary/', '/signplay/', '/shouyu/html/', '/loveheart/html/']:
                self.assertFalse(visits.collect_event(connection, key, {**event, 'path':path}))
            self.assertFalse(visits.collect_event(connection, key, {**event, 'path':'/api/items', 'content_type':'application/json'}))
            self.assertTrue(visits.collect_event(connection, key, {**event, 'path':'/dict/entry/123', 'ua':'Browser'}))
            self.assertTrue(visits.collect_event(connection, key, {**event, 'path':'/new-project/', 'ua':'Browser'}))
            connection.close()
            result = visits.report(directory/'visits.sqlite')
            self.assertEqual(result['period'], {'views':2,'visitors':1})
            health = {r['project']:r for r in result['project_collector']}
            self.assertEqual(set(health), set(visits.PROJECT_NAMES) | {'path:/new-project'})
            self.assertEqual((health['dict']['received'], health['dict']['accepted']), (2, 1))
            self.assertIsNone(health['portfolio']['last_accepted'])
            self.assertIsNotNone(health['portfolio']['first_received'])
            self.assertNotIn('192.0.2.1', json.dumps(result))

    def test_report_missing_database_keeps_unknown_coverage_and_future_rows_out_of_period(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            result = visits.report(directory/'visits.sqlite')
            self.assertEqual(result['days'], [])
            self.assertIsNone(result['coverage']['first_recorded_date'])
            self.assertEqual(len(result['projects']), len(visits.PROJECT_NAMES))
            self.assertFalse((directory/'visits.sqlite').exists())
            connection, _ = visits.open_database(directory)
            tomorrow = (datetime.now(visits.BEIJING).date() + timedelta(days=1)).isoformat()
            connection.execute('INSERT INTO visits VALUES(?,?,?,?)',(tomorrow,'one','/',9))
            connection.commit()
            connection.close()
            self.assertEqual(visits.report(directory/'visits.sqlite')['period']['views'],0)


if __name__ == '__main__':
    unittest.main()
