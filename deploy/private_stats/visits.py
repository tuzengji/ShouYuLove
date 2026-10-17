#!/usr/bin/env python3
"""Private daily page-request counts; no HTTP server and no plaintext visitor storage."""
import argparse
from contextlib import closing
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
from urllib.parse import unquote

DIRECTORY = Path('/var/lib/shouyulove-stats')
SOCKET = Path('/run/shouyulove-stats/collector.sock')
PORTFOLIO_CATALOG = Path('/var/www/shouyulove-home/portfolio/projects.json')
BEIJING = timezone(timedelta(hours=8))
BOT = re.compile(r'bot|spider|crawler|headless|ShouYuLove-QA|curl|wget|python|healthcheck', re.I)
HTML_TYPES = {'text/html', 'application/xhtml+xml'}
PAGE_DESTINATIONS = {'document', 'iframe', 'frame'}
RESOURCE_SUFFIX = re.compile(r'\.(?:js|mjs|css|json|xml|txt|map|png|jpe?g|gif|webp|avif|svg|ico|woff2?|ttf|otf|mp[34]|webm|ogg|wav|pdf|zip|gz|wasm|glb|ktx2)$', re.I)
PROJECT_NAMES = {
    'main': '以手予爱主站',
    'portfolio': '心创组作品集',
    'signtrace': '以手寻语 SignTrace',
    'dict': '分社手语词典',
    'chuanqinghuiyi': '传情会意·手语版',
    'catchpot': '接锅',
    '2026-sign-language-cultural-festival': '2026 手语文化节',
    '2026-year-end-summary': '手语分社骨干年终总结',
    'signplay': '指间趣游 SignPlay',
    'shouyu': '手语论坛历史资料',
    'loveheart': '爱心社论坛历史资料',
}


def portfolio_catalog():
    # Read the current release so adding a work needs no collector restart.
    try:
        catalog = json.loads(PORTFOLIO_CATALOG.read_text())
        return {k: v for k, v in catalog.items()
                if re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}', k)
                and isinstance(v, str) and 0 < len(v) <= 200}
    except (OSError, ValueError, AttributeError, TypeError):
        return {}


def visitor_day(key, event):
    stamp = datetime.fromisoformat(event['time'])
    if stamp.tzinfo is None:
        raise ValueError('Missing event timezone')
    day = stamp.astimezone(BEIJING).date().isoformat()
    address = str(ipaddress.ip_address(event['address']))
    return day, hmac.new(key, address.encode(), hashlib.sha256).hexdigest()


def project_key(path):
    """Known aliases share a project; new route prefixes are included automatically."""
    if path in {'/', '/index.html', '/index.htm'}:
        return 'main'
    prefix = path.strip('/').split('/', 1)[0]
    if prefix == 'vocab':
        return 'signtrace'
    if prefix == 'the-studio':
        return 'main'
    if prefix == 'projects':
        return 'portfolio' if path.rstrip('/') == '/projects' else 'main'
    if prefix in PROJECT_NAMES and prefix != 'main':
        return prefix
    return 'path:/' + prefix


def project_name(key):
    return PROJECT_NAMES.get(key, key.removeprefix('path:'))


def page_path(event):
    """Classify document responses, retaining the requested route before rewrites."""
    raw = event.get('path', '')
    if not isinstance(raw, str) or len(raw) > 2048:
        return None
    path = unquote(raw.split('?', 1)[0].split('#', 1)[0], errors='strict')
    if not path.startswith('/') or path.startswith('//') or any(ord(c) < 32 or ord(c) == 127 or c in '\\?#' for c in path):
        return None
    if event.get('host', 'shouyulove.cn').lower() not in {'shouyulove.cn', 'www.shouyulove.cn'}:
        return None
    destination = event.get('destination', '').lower()
    if destination not in {'', '-'} | PAGE_DESTINATIONS:
        return None
    if 'prefetch' in (event.get('purpose', '') + ' ' + event.get('sec_purpose', '')).lower():
        return None
    content_type = event.get('content_type', '').split(';', 1)[0].strip().lower()
    upstream_type = event.get('upstream_type', '').split(';', 1)[0].strip().lower()
    html = content_type in HTML_TYPES or (content_type in {'', '-'} and upstream_type in HTML_TYPES)
    # 304 omits Content-Type on static files and some upstreams.
    if not html and event.get('status') == 304 and content_type in {'', '-'} and upstream_type in {'', '-'}:
        resolved = event.get('resolved_path', path)
        html = (not RESOURCE_SUFFIX.search(path) and
                (destination in PAGE_DESTINATIONS or resolved.lower().endswith(('.html', '.htm')) or
                 'text/html' in event.get('accept', '').lower()))
    if not html:
        return None
    if path.endswith(('/index.html', '/index.htm')):
        path = path.rsplit('/', 1)[0] + '/'
    return path


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
    connection.execute('''CREATE TABLE IF NOT EXISTS project_health (
        project TEXT PRIMARY KEY, received INTEGER NOT NULL, accepted INTEGER NOT NULL,
        first_received TEXT NOT NULL, last_received TEXT NOT NULL, last_accepted TEXT)''')
    connection.execute('''CREATE TABLE IF NOT EXISTS portfolio_clicks (
        day TEXT, visitor TEXT, project TEXT, count INTEGER NOT NULL,
        PRIMARY KEY(day,visitor,project))''')
    connection.execute('''CREATE TABLE IF NOT EXISTS portfolio_click_health (
        project TEXT PRIMARY KEY, received INTEGER NOT NULL, accepted INTEGER NOT NULL,
        first_received TEXT NOT NULL, last_received TEXT NOT NULL, last_accepted TEXT)''')
    connection.commit()
    return connection, key


def record(connection, key, event):
    if event.get('method') != 'GET' or event.get('status') not in (200, 304) or BOT.search(event.get('ua', '')):
        return False
    path = page_path(event)
    if path is None:
        return False
    if datetime.fromisoformat(event['time']).tzinfo is None:
        return False
    day, visitor = visitor_day(key, event)
    with connection:
        connection.execute('INSERT INTO visits VALUES(?,?,?,1) ON CONFLICT(day,visitor,path) DO UPDATE SET count=count+1', (day, visitor, path))
    return True


def record_portfolio_click(connection, key, event):
    project = event.get('project', '')
    if (event.get('method') != 'POST' or event.get('status') != 204 or
            event.get('portfolio_source') != '1' or event.get('same_origin') != '1' or
            event.get('host') not in {'shouyulove.cn', 'www.shouyulove.cn'} or
            event.get('path') != '/__syl/portfolio-click/' + project or
            event.get('destination', '') not in {'', '-', 'empty'} or
            'prefetch' in (event.get('purpose', '') + ' ' + event.get('sec_purpose', '')).lower() or
            project not in portfolio_catalog()):
        return False
    day, visitor = visitor_day(key, event)
    accepted = not BOT.search(event.get('ua', ''))
    now = datetime.now(timezone.utc).isoformat()
    with connection:
        if accepted:
            connection.execute('''INSERT INTO portfolio_clicks VALUES(?,?,?,1)
                ON CONFLICT(day,visitor,project) DO UPDATE SET count=count+1''', (day, visitor, project))
        connection.execute('''INSERT INTO portfolio_click_health VALUES(?,1,?,?,?,?)
            ON CONFLICT(project) DO UPDATE SET received=received+1, accepted=accepted+excluded.accepted,
            last_received=excluded.last_received,
            last_accepted=COALESCE(excluded.last_accepted,last_accepted)''',
            (project, int(accepted), now, now, now if accepted else None))
    return bool(accepted)


def collect_event(connection, key, event):
    """Observe HTML delivery per project without counting QA/bots as visits."""
    if event.get('kind') == 'portfolio_click':
        return record_portfolio_click(connection, key, event)
    accepted = record(connection, key, event)
    if event.get('method') != 'GET' or event.get('status') not in (200, 304):
        return accepted
    path = page_path(event)
    if path is not None:
        now = datetime.now(timezone.utc).isoformat()
        with connection:
            connection.execute('''INSERT INTO project_health VALUES(?,1,?,?,?,?)
                ON CONFLICT(project) DO UPDATE SET
                received=received+1, accepted=accepted+excluded.accepted,
                last_received=excluded.last_received,
                last_accepted=COALESCE(excluded.last_accepted,last_accepted)''',
                (project_key(path), int(accepted), now, now, now if accepted else None))
    return accepted


def click_report(connection, since, today):
    names = portfolio_catalog()
    result = {'period': {'clicks': 0, 'visitors': 0}, 'days': [], 'project_days': [],
              'projects': [{'project': k, 'name': v, 'clicks': 0, 'visitors': 0} for k, v in names.items()],
              'first_recorded_date': None, 'collector': []}
    if connection is None or not connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='portfolio_clicks'").fetchone():
        return result
    period = connection.execute('SELECT COALESCE(SUM(count),0),COUNT(DISTINCT visitor) FROM portfolio_clicks WHERE day BETWEEN ? AND ?', (since, today)).fetchone()
    result['period'] = {'clicks': period[0], 'visitors': period[1]}
    result['first_recorded_date'] = connection.execute('SELECT MIN(day) FROM portfolio_clicks').fetchone()[0]
    rows = connection.execute('SELECT day,SUM(count),COUNT(DISTINCT visitor) FROM portfolio_clicks WHERE day BETWEEN ? AND ? GROUP BY day ORDER BY day DESC', (since, today))
    result['days'] = [{'date': d, 'clicks': c, 'visitors': u} for d, c, u in rows]
    totals = {r['project']: r for r in result['projects']}
    for k, c, u in connection.execute('SELECT project,SUM(count),COUNT(DISTINCT visitor) FROM portfolio_clicks WHERE day BETWEEN ? AND ? GROUP BY project', (since, today)):
        totals[k] = {'project': k, 'name': names.get(k, k), 'clicks': c, 'visitors': u}
    result['projects'] = sorted(totals.values(), key=lambda r: (-r['clicks'], r['project']))
    rows = connection.execute('SELECT day,project,SUM(count),COUNT(DISTINCT visitor) FROM portfolio_clicks WHERE day BETWEEN ? AND ? GROUP BY day,project ORDER BY day DESC,project', (since, today))
    result['project_days'] = [{'date': d, 'project': k, 'name': names.get(k, k), 'clicks': c, 'visitors': u} for d, k, c, u in rows]
    if connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='portfolio_click_health'").fetchone():
        rows = connection.execute('SELECT project,received,accepted,first_received,last_received,last_accepted FROM portfolio_click_health ORDER BY project')
        result['collector'] = [{'project': k, 'name': names.get(k, k), 'received': r, 'accepted': a,
                                'first_received': f, 'last_received': l, 'last_accepted': v} for k, r, a, f, l, v in rows]
    return result


def report(database, days=30):
    today = datetime.now(BEIJING).date().isoformat()
    since = (datetime.now(BEIJING).date() - timedelta(days=days-1)).isoformat()
    empty = {'days': [], 'total': {'views': 0, 'visitors': 0},
             'period': {'views': 0, 'visitors': 0}, 'pages': [], 'project_days': [],
             'projects': [{'project': k, 'name': v, 'views': 0, 'visitors': 0}
                          for k, v in PROJECT_NAMES.items()],
             'coverage': {'requested_start': since, 'requested_end': today,
                          'first_recorded_date': None, 'last_recorded_date': None},
             'portfolio_clicks': click_report(None, since, today),
             'project_collector': [], 'collector': {'received': 0, 'last_received': None}}
    if not database.exists():
        return empty
    with closing(sqlite3.connect('file:' + str(database) + '?mode=ro', uri=True)) as connection:
        connection.create_function('project_key', 1, project_key, deterministic=True)
        rows = connection.execute('SELECT day,SUM(count),COUNT(DISTINCT visitor) FROM visits WHERE day BETWEEN ? AND ? GROUP BY day ORDER BY day DESC', (since, today)).fetchall()
        total = connection.execute('SELECT COALESCE(SUM(count),0),COUNT(DISTINCT visitor) FROM visits').fetchone()
        period = connection.execute('SELECT COALESCE(SUM(count),0),COUNT(DISTINCT visitor) FROM visits WHERE day BETWEEN ? AND ?', (since, today)).fetchone()
        pages = connection.execute('SELECT day,path,SUM(count),COUNT(DISTINCT visitor) FROM visits WHERE day BETWEEN ? AND ? GROUP BY day,path ORDER BY day DESC,path', (since, today)).fetchall()
        projects = connection.execute('SELECT project_key(path),SUM(count),COUNT(DISTINCT visitor) FROM visits WHERE day BETWEEN ? AND ? GROUP BY project_key(path)', (since, today)).fetchall()
        project_days = connection.execute('SELECT day,project_key(path),SUM(count),COUNT(DISTINCT visitor) FROM visits WHERE day BETWEEN ? AND ? GROUP BY day,project_key(path) ORDER BY day DESC,project_key(path)', (since, today)).fetchall()
        dates = connection.execute('SELECT MIN(day),MAX(day) FROM visits').fetchone()
        health = connection.execute('SELECT received,last_received FROM collector_health WHERE id=1').fetchone()
        project_health = []
        clicks = click_report(connection, since, today)
        if connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='project_health'").fetchone():
            project_health = connection.execute('SELECT project,received,accepted,first_received,last_received,last_accepted FROM project_health ORDER BY project').fetchall()
    project_totals = {r['project']: r for r in empty['projects']}
    for k, v, u in projects:
        project_totals[k] = {'project': k, 'name': project_name(k), 'views': v, 'visitors': u}
    return {'days': [{'date': d, 'views': v, 'visitors': u} for d,v,u in rows],
            'total': {'views': total[0], 'visitors': total[1]},
            'period': {'views': period[0], 'visitors': period[1]},
            'pages': [{'date':d,'path':p,'views':v,'visitors':u} for d,p,v,u in pages],
            'projects': sorted(project_totals.values(), key=lambda r: (-r['views'], r['project'])),
            'project_days': [{'date':d,'project':k,'name':project_name(k),'views':v,'visitors':u}
                             for d,k,v,u in project_days],
            'coverage': {'requested_start':since,'requested_end':today,
                         'first_recorded_date':dates[0],'last_recorded_date':dates[1]},
            'collector': {'received':health[0], 'last_received':health[1]},
            'portfolio_clicks': clicks,
            'project_collector': [{'project':k,'name':project_name(k),'received':r,'accepted':a,
                                   'first_received':f,'last_received':l,'last_accepted':v}
                                  for k,r,a,f,l,v in project_health]}


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
                collect_event(connection, key, json.loads(raw[start:]))
            except (ValueError, KeyError, TypeError, AttributeError):
                continue


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['serve', 'report'])
    parser.add_argument('--days', type=int, default=30)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--pages', action='store_true', help='Show per-day page totals in text reports')
    parser.add_argument('--projects', action='store_true', help='Show project totals and per-day project counts')
    parser.add_argument('--clicks', action='store_true', help='Show portfolio outbound activations separately from page views')
    parser.add_argument('--health', action='store_true', help='Show per-project HTML delivery observations, including QA/bots')
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
            coverage = result['coverage']
            print(f"查询范围：{coverage['requested_start']} 至 {coverage['requested_end']}（北京时间，今日未结束）")
            print(f"最早保存的访问日期：{coverage['first_recorded_date'] or '暂无记录'}；此前没有记录的日期不视为零访问。")
            print('日期         访问次数  访客数')
            for row in result['days']:
                print(f"{row['date']}  {row['views']:8d}  {row['visitors']:6d}")
            print(f"累计        {result['total']['views']:8d}  {result['total']['visitors']:6d}")
            print(f"近{args.days}天      {result['period']['views']:8d}  {result['period']['visitors']:6d}")
            if args.projects:
                print('\n访问次数  访客数  项目（访客数按项目去重，不能相加）')
                for row in result['projects']:
                    print(f"{row['views']:8d}  {row['visitors']:6d}  {row['name']}")
                print('\n日期         访问次数  访客数  项目')
                for row in result['project_days']:
                    print(f"{row['date']}  {row['views']:8d}  {row['visitors']:6d}  {row['name']}")
            if args.health:
                print('\n项目采集观测（含测试和机器人候选；从升级后开始，不是历史访问量）')
                for row in result['project_collector']:
                    print(f"{row['name']}  候选 {row['received']}  计入 {row['accepted']}  最近接收 {row['last_received']}")
                print('\n作品集跳转采集观测（含 QA，不是页面访问量）')
                for row in result['portfolio_clicks']['collector']:
                    print(f"{row['name']}  候选 {row['received']}  计入 {row['accepted']}  最近接收 {row['last_received']}")
            if args.clicks:
                clicks = result['portfolio_clicks']
                print('\n作品集入口跳转（点击次数，不代表目标网页成功加载）')
                print(f"近{args.days}天：{clicks['period']['clicks']} 次，{clicks['period']['visitors']} 位估算访客")
                print(f"最早保存的跳转日期：{clicks['first_recorded_date'] or '暂无记录'}；上线前的跳转无法补回。")
                print('跳转次数  访客数  作品')
                for row in clicks['projects']:
                    print(f"{row['clicks']:8d}  {row['visitors']:6d}  {row['name']}")
                print('\n日期         跳转次数  访客数  作品')
                for row in clicks['project_days']:
                    print(f"{row['date']}  {row['clicks']:8d}  {row['visitors']:6d}  {row['name']}")
            if args.pages:
                print('\n日期         访问次数  访客数  页面')
                for row in result['pages']:
                    print(f"{row['date']}  {row['views']:8d}  {row['visitors']:6d}  {row['path']}")
