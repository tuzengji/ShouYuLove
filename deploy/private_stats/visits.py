#!/usr/bin/env python3
"""Private daily page-request counts; no HTTP server and no plaintext visitor storage."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import ipaddress
import json
import os
from pathlib import Path
import re
import secrets
import socket
import sqlite3
import stat

DIRECTORY = Path('/var/lib/shouyulove-stats')
SOCKET = Path('/run/shouyulove-stats/collector.sock')
BEIJING = timezone(timedelta(hours=8))
BOT = re.compile(r'bot|spider|crawler|headless|ShouYuLove-QA|curl|wget|python|healthcheck', re.I)


def open_database(directory=DIRECTORY):
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    key_path = directory / 'secret.key'
    if not key_path.exists():
        with os.fdopen(os.open(key_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), 'wb') as stream:
            stream.write(secrets.token_bytes(32))
    key = key_path.read_bytes()
    assert len(key) == 32
    database = directory / 'visits.sqlite'
    connection = sqlite3.connect(database)
    database.chmod(0o600)
    connection.execute('PRAGMA journal_mode=WAL')
    connection.execute('CREATE TABLE IF NOT EXISTS visits (day TEXT, visitor TEXT, path TEXT, count INTEGER NOT NULL, PRIMARY KEY(day,visitor,path))')
    connection.execute('CREATE TABLE IF NOT EXISTS collector_health (id INTEGER PRIMARY KEY, received INTEGER, last_received TEXT)')
    connection.execute('INSERT OR IGNORE INTO collector_health VALUES(1,0,NULL)')
    connection.commit()
    return connection, key


def record(connection, key, event):
    if event.get('method') != 'GET' or event.get('status') not in (200, 304) or BOT.search(event.get('ua', '')):
        return False
    path = event.get('path', '')
    if path in ('/', '/index.html'):
        path = '/'
    elif path in ('/portfolio/', '/portfolio/index.html'):
        path = '/portfolio/'
    elif re.fullmatch(r'/(projects|the-studio)/[a-z0-9-]+/(index\.html)?', path):
        path = path.removesuffix('index.html')
    elif path in ('/the-studio/', '/the-studio/index.html'):
        path = '/the-studio/'
    else:
        return False
    stamp = datetime.fromisoformat(event['time'])
    if stamp.tzinfo is None:
        return False
    day = stamp.astimezone(BEIJING).date().isoformat()
    address = str(ipaddress.ip_address(event['address']))
    visitor = hmac.new(key, address.encode(), hashlib.sha256).hexdigest()
    with connection:
        connection.execute('INSERT INTO visits VALUES(?,?,?,1) ON CONFLICT(day,visitor,path) DO UPDATE SET count=count+1', (day, visitor, path))
    return True


def report(database, days=30):
    if not database.exists():
        return {'days': [], 'total': {'views': 0, 'visitors': 0}, 'pages': []}
    with sqlite3.connect('file:' + str(database) + '?mode=ro', uri=True) as connection:
        since = (datetime.now(BEIJING).date() - timedelta(days=days-1)).isoformat()
        rows = connection.execute('SELECT day,SUM(count),COUNT(DISTINCT visitor) FROM visits WHERE day >= ? GROUP BY day ORDER BY day DESC', (since,)).fetchall()
        total = connection.execute('SELECT COALESCE(SUM(count),0),COUNT(DISTINCT visitor) FROM visits').fetchone()
        pages = connection.execute('SELECT day,path,SUM(count),COUNT(DISTINCT visitor) FROM visits WHERE day >= ? GROUP BY day,path ORDER BY day DESC,path', (rows[-1][0] if rows else '9999-12-31',)).fetchall()
        health = connection.execute('SELECT received,last_received FROM collector_health WHERE id=1').fetchone()
    return {'days': [{'date': d, 'views': v, 'visitors': u} for d,v,u in rows],
            'total': {'views': total[0], 'visitors': total[1]},
            'pages': [{'date':d,'path':p,'views':v,'visitors':u} for d,p,v,u in pages],
            'collector': {'received':health[0], 'last_received':health[1]}}


def serve():
    os.umask(0o077)
    connection, key = open_database()
    if SOCKET.exists():
        assert stat.S_ISSOCK(SOCKET.stat().st_mode), 'Unexpected collector socket file'
        SOCKET.unlink()
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as receiver:
        receiver.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 262144)
        receiver.bind(str(SOCKET))
        SOCKET.chmod(0o660)
        while True:
            raw = receiver.recv(65535)
            with connection:
                connection.execute('UPDATE collector_health SET received=received+1,last_received=? WHERE id=1', (datetime.now(timezone.utc).isoformat(),))
            start = raw.find(b'{')
            if start < 0:
                continue
            try:
                record(connection, key, json.loads(raw[start:]))
            except (ValueError, KeyError, TypeError):
                continue


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['serve', 'report'])
    parser.add_argument('--days', type=int, default=30)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    if args.command == 'serve':
        serve()
    else:
        if not 1 <= args.days <= 3660:
            parser.error('days must be between 1 and 3660')
        result = report(DIRECTORY / 'visits.sqlite', args.days)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print('日期         访问次数  访客数')
            for row in result['days']:
                print(f"{row['date']}  {row['views']:8d}  {row['visitors']:6d}")
            print(f"累计        {result['total']['views']:8d}  {result['total']['visitors']:6d}")
