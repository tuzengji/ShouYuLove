"""Portfolio activations stay separate from views and retain private history."""
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('visits', ROOT / 'deploy/private_stats/visits.py')
visits = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visits)


class PortfolioClickTests(unittest.TestCase):
    def test_external_clicks_daily_counts_filters_and_new_catalog(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            catalog = root / 'projects.json'
            catalog.write_text(json.dumps({'beida-zhidao': '北大知道', 'signtrace': '以手寻语'}))
            with patch.object(visits, 'PORTFOLIO_CATALOG', catalog):
                connection, key = visits.open_database(root / 'private')
                today = datetime.now(visits.BEIJING).date().isoformat()
                connection.execute('INSERT INTO visits VALUES(?,?,?,?)', (today, 'old-visitor', '/', 42))
                connection.commit()
                event = dict(kind='portfolio_click', time=datetime.now(timezone.utc).isoformat(),
                             address='192.0.2.1', host='shouyulove.cn', method='POST', status=204,
                             ua='Browser', project='beida-zhidao', path='/__syl/portfolio-click/beida-zhidao',
                             portfolio_source='1', same_origin='1', destination='empty')
                self.assertTrue(visits.collect_event(connection, key, event))
                self.assertTrue(visits.collect_event(connection, key, event))
                yesterday = datetime.now(timezone.utc) - timedelta(days=1)
                self.assertTrue(visits.collect_event(connection, key, {**event, 'time': yesterday.isoformat()}))
                self.assertTrue(visits.collect_event(connection, key, {**event, 'address': '192.0.2.2'}))
                for changes in [dict(method='GET'), dict(status=200), dict(portfolio_source='0'),
                                dict(same_origin='0'), dict(ua='ShouYuLove-QA'), dict(ua='Googlebot'),
                                dict(host='other.example'), dict(destination='document'), dict(purpose='prefetch'),
                                dict(project='unknown', path='/__syl/portfolio-click/unknown'),
                                dict(path='/__syl/portfolio-click/signtrace')]:
                    with self.subTest(changes=changes):
                        self.assertFalse(visits.collect_event(connection, key, {**event, **changes}))
                # A newly published work is eligible without restarting this collector.
                catalog.write_text(json.dumps({'beida-zhidao': '北大知道', 'signtrace': '以手寻语', 'new-work': '新作品'}))
                self.assertTrue(visits.collect_event(connection, key,
                    {**event, 'project': 'new-work', 'path': '/__syl/portfolio-click/new-work'}))
                connection.close()
                result = visits.report(root / 'private/visits.sqlite')
                self.assertEqual(result['period'], {'views': 42, 'visitors': 1})
                clicks = result['portfolio_clicks']
                self.assertEqual(clicks['period'], {'clicks': 5, 'visitors': 2})
                self.assertEqual(len(clicks['days']), 2)
                self.assertEqual(len(clicks['project_days']), 3)
                totals = {r['project']: r for r in clicks['projects']}
                self.assertEqual(totals['beida-zhidao']['clicks'], 4)
                self.assertEqual(totals['signtrace']['clicks'], 0)
                health = {r['project']: r for r in clicks['collector']}
                self.assertEqual((health['beida-zhidao']['received'], health['beida-zhidao']['accepted']), (6, 4))
                self.assertNotIn('192.0.2', json.dumps(result))
                self.assertNotIn(b'192.0.2', (root / 'private/visits.sqlite').read_bytes())
                connection, restored_key = visits.open_database(root / 'private')
                self.assertEqual(restored_key, key)
                self.assertEqual(connection.execute('SELECT SUM(count) FROM visits').fetchone()[0], 42)
                connection.close()

    def test_readonly_old_schema_and_missing_catalog(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(visits, 'PORTFOLIO_CATALOG', root / 'missing.json'):
                connection, key = visits.open_database(root / 'private')
                connection.execute('DROP TABLE portfolio_clicks')
                connection.execute('DROP TABLE portfolio_click_health')
                connection.commit()
                connection.close()
                self.assertEqual(visits.report(root / 'private/visits.sqlite')['portfolio_clicks']['period'],
                                 {'clicks': 0, 'visitors': 0})
                connection, same_key = visits.open_database(root / 'private')
                self.assertEqual(key, same_key)
                connection.close()


if __name__ == '__main__':
    unittest.main()
