#!/usr/bin/env python3
"""Verify published CDN bytes, CORS and cache headers before switching HTML."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

from runtime_snapshot import relative, require


def check(origin, name, expected):
    relative(name)
    started = time.monotonic()
    try:
        request = Request(origin + '/' + quote(name), headers={
            'User-Agent': 'ShouYuLove-QA-CDN',
            'Origin': 'https://shouyulove.cn',
            'Referer': 'https://shouyulove.cn/',
            'Accept-Encoding': 'identity',
        })
        with urlopen(request, timeout=45) as response:
            data = response.read(expected['bytes'] + 1)
            headers = dict(response.headers.items())
            require(response.status == 200, 'Expected HTTP 200')
            require(len(data) == expected['bytes'], 'Size differs')
            require(hashlib.sha256(data).hexdigest() == expected['sha256'], 'SHA-256 differs')
            require(response.headers.get('Access-Control-Allow-Origin') == '*', 'CORS missing')
            require('max-age=31536000' in response.headers.get('Cache-Control', ''), 'One-year cache missing')
            mime = response.headers.get_content_type()
            if name.endswith('.js'):
                require(mime in ('application/javascript', 'text/javascript'), 'Invalid module MIME: ' + mime)
            if name.endswith('.wasm'):
                require(mime == 'application/wasm', 'Invalid WASM MIME: ' + mime)
            return {'path': name, 'passed': True, 'bytes': len(data),
                    'seconds': round(time.monotonic() - started, 3), 'headers': headers}
    except Exception as error:
        return {'path': name, 'passed': False, 'error': str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    base = urlsplit(manifest['base'])
    require(base.scheme == 'https' and base.netloc == 'assets.shouyulove.cn', 'Unexpected CDN origin')
    require(all(name.startswith(base.path.lstrip('/') + '/') for name in manifest['files']), 'Unexpected object prefix')
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=4) as pool:
        checks = list(pool.map(lambda item: check('https://' + base.netloc, *item), manifest['files'].items()))
    result = {'passed': all(item['passed'] for item in checks), 'files': len(checks),
              'seconds': round(time.monotonic() - started, 3), 'results': checks}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'results'}))
    for item in checks:
        if not item['passed']:
            print(json.dumps(item, ensure_ascii=False))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
