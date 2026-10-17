#!/usr/bin/env python3
"""Root-only, loopback Nginx lab. Never loads or reloads the production server."""
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import tempfile
import time

repo = Path(__file__).resolve().parents[1]
root = Path(tempfile.mkdtemp(prefix='syl-dict-lab-', dir='/var/tmp'))
root.chmod(0o700)
processes = []


def wait_port(port):
    for _ in range(100):
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=.1):
                return
        except OSError:
            time.sleep(.05)
    raise RuntimeError(f'Lab port {port} unavailable')


try:
    (root / 'videos').mkdir()
    (root / 'videos/qa.mp4').write_bytes(b'qa-video' * 100)
    key = secrets.token_hex(32)
    (root / 'key').write_text(key)
    (root / 'signing.conf').write_text(f'secure_link_md5 "$syl_dict_expires $syl_dict_sid {key}";\n')
    source = repo / 'deploy/aliyun/nginx'
    snippets = [
        source / 'snippets/shouyulove-dict-guard.conf',
        source / 'snippets/shouyulove-dict-limits.conf',
        source / 'snippets/shouyulove-dict-video-guard.conf',
        Path('/etc/nginx/snippets/shouyu-content-access-auth.conf'),
    ]
    def translate(text):
        return (text.replace('/etc/shouyulove/dict-guard-signing.conf', str(root / 'signing.conf'))
                .replace('/run/shouyulove-dict-guard/guard.sock', str(root / 'guard.sock'))
                .replace('/etc/nginx/snippets/', str(root) + '/')
                .replace('/var/lib/shouyu/videos/', str(root / 'videos') + '/')
                .replace('http://127.0.0.1:18081', 'http://127.0.0.1:18991')
                .replace('http://127.0.0.1:8092', 'http://127.0.0.1:18991'))
    for f in snippets:
        (root / f.name).write_text(translate(f.read_text()))
    site = (source / 'shouyulove.server.conf').read_text()
    dictionary = site[site.index('    # 国家通用手语词典'):site.index('    # The contact page')]
    config = f'''
user root;
worker_processes auto;
worker_rlimit_nofile 65536;
pid {root}/nginx.pid;
error_log {root}/error.log warn;
events {{ worker_connections 768; }}
http {{
  access_log off;
  include {source}/conf.d/shouyulove-limits.conf;
  include {source}/conf.d/shouyulove-dictionary-limits.conf;
  upstream shouyu_dict_backend {{ server 127.0.0.1:18991; }}
  server {{
    listen 127.0.0.1:18992 ssl;
    http2 on;
    http2_max_concurrent_streams 32;
    server_name shouyulove.cn;
    ssl_certificate {root}/cert.pem;
    ssl_certificate_key {root}/cert.key;
    limit_req_status 429;
    limit_conn_status 429;
    {translate(dictionary)}
    location /baseline/ {{ limit_conn syl_conn 24; proxy_pass http://127.0.0.1:18991/hold/; }}
    location /unrelated/ {{ limit_req zone=syl_req burst=120 nodelay; limit_conn syl_conn 24; proxy_pass http://127.0.0.1:18991; }}
  }}
}}
'''
    (root / 'nginx.conf').write_text(config)
    subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1',
                    '-subj', '/CN=shouyulove.cn', '-keyout', str(root / 'cert.key'),
                    '-out', str(root / 'cert.pem')], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['nginx', '-t', '-c', str(root / 'nginx.conf'), '-p', str(root)], check=True)
    with (root / 'processes.log').open('w') as log:
        env = {**os.environ, 'GUARD_SOCKET': str(root / 'guard.sock'), 'GUARD_SECRET_FILE': str(root / 'key')}
        processes.append(subprocess.Popen(['node', str(repo / 'deploy/dictionary_guard/guard.mjs')], env=env, stdout=log, stderr=log))
        processes.append(subprocess.Popen(['node', str(repo / 'tests/dictionary_mock.mjs')], stdout=log, stderr=log))
        wait_port(18991)
        for _ in range(100):
            if (root / 'guard.sock').exists(): break
            time.sleep(.05)
        processes.append(subprocess.Popen(['nginx', '-c', str(root / 'nginx.conf'), '-p', str(root), '-g', 'daemon off;'], stdout=log, stderr=log))
        wait_port(18992)
        result = subprocess.run(['node', str(repo / 'tests/dictionary_nat.mjs')], timeout=120)
        if result.returncode:
            print('LAB ERROR LOG (last 25 lines)', flush=True)
            print('\n'.join((root / 'error.log').read_text().splitlines()[-25:]), flush=True)
        raise SystemExit(result.returncode)
finally:
    for proc in reversed(processes):
        proc.terminate()
    for proc in reversed(processes):
        try: proc.wait(timeout=5)
        except subprocess.TimeoutExpired: proc.kill(); proc.wait()
    shutil.rmtree(root)
