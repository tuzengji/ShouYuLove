"""Daily requests, anonymous deduplication, filtering and private storage."""
import importlib.util
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
            event = dict(time='2026-10-11T16:01:00+00:00', address='192.0.2.1', path='/portfolio/index.html', method='GET', status=200, ua='Chrome Mobile')
            self.assertTrue(visits.record(connection,key,event))
            self.assertTrue(visits.record(connection,key,event))
            self.assertTrue(visits.record(connection,key,{**event,'path':'/index.html'}))
            self.assertTrue(visits.record(connection,key,{**event,'address':'192.0.2.2','status':304}))
            for change in [dict(path='/assets/entry.js'),dict(path='/catchpot/'),dict(status=308),dict(method='HEAD'),dict(ua='ShouYuLove-QA'),dict(ua='Googlebot')]:
                self.assertFalse(visits.record(connection,key,{**event,**change}))
            connection.close()
            result = visits.report(directory/'visits.sqlite')
            self.assertEqual(result['days'],[dict(date='2026-10-12',views=4,visitors=2)])
            self.assertEqual(result['total'],dict(views=4,visitors=2))
            self.assertNotIn('192.0.2',json.dumps(result))
            self.assertNotIn(b'192.0.2.1',(directory/'visits.sqlite').read_bytes())
            self.assertEqual((directory/'secret.key').stat().st_mode & 0o777,0o600)
            self.assertEqual((directory/'visits.sqlite').stat().st_mode & 0o777,0o600)


if __name__ == '__main__':
    unittest.main()
