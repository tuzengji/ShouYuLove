"""A reload can briefly route new connections through an old Nginx worker."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location('publish_astra', Path(__file__).resolve().parents[1] / 'deploy/publish_astra.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


def connection(location):
    response = Mock(status=302)
    response.getheader.return_value = location
    client = Mock()
    client.getresponse.return_value = response
    return client


class ExternalRedirectReadinessTests(unittest.TestCase):
    def test_old_worker_then_new_worker_keeps_exact_target_check(self):
        target = 'https://39.96.206.228/?qa=where-to-study'
        old, new = connection('/'), connection(target)
        with patch.object(publisher, 'HTTPConnection', side_effect=[old, new]), patch.object(publisher.time, 'sleep'):
            observed = publisher.wait_for_external_redirect('/where-to-study/?qa=where-to-study', target, attempts=3)
        self.assertEqual([item['location'] for item in observed], ['/', target])
        old.close.assert_called_once()
        new.close.assert_called_once()

    def test_persistently_wrong_redirect_still_fails(self):
        wrong = connection('/')
        with patch.object(publisher, 'HTTPConnection', return_value=wrong), patch.object(publisher.time, 'sleep'):
            with self.assertRaises(AssertionError):
                publisher.wait_for_external_redirect('/where-to-study/', 'https://39.96.206.228/', attempts=3)


if __name__ == '__main__':
    unittest.main()
