#!/usr/bin/env python3
"""Certbot hook for the ShouYuLove lineage only; no Nginx config edits."""
from datetime import datetime, timezone
import fcntl
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

LINEAGE = Path('/etc/letsencrypt/live/shouyulove.cn')
ARCHIVE = Path('/etc/letsencrypt/archive/shouyulove.cn')
TLS = Path('/etc/shouyulove/tls')
NAMES = ('cert.pem', 'chain.pem', 'fullchain.pem', 'privkey.pem')


def main():
    # A certificate-specific hook must never activate another site's lineage.
    if os.environ.get('RENEWED_LINEAGE') != str(LINEAGE):
        return
    if set(os.environ.get('RENEWED_DOMAINS', '').split()) != {'shouyulove.cn', 'www.shouyulove.cn'}:
        raise RuntimeError('Unexpected certificate domain set')
    if os.geteuid() != 0:
        raise RuntimeError('Certificate deployment requires root')
    os.umask(0o077)
    with open('/run/lock/nginx-deploy.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not TLS.is_dir() or TLS.is_symlink():
            raise RuntimeError('Unexpected ShouYuLove TLS directory')
        for name in NAMES:
            if not (LINEAGE / name).resolve().is_relative_to(ARCHIVE):
                raise RuntimeError('Certificate source escapes its own archive')
            if not (TLS / name).is_file() or (TLS / name).is_symlink():
                raise RuntimeError('Expected existing copied ShouYuLove certificate')
        subprocess.run(['nginx', '-t'], check=True)
        subprocess.run(['openssl', 'x509', '-in', str(LINEAGE / 'cert.pem'),
                        '-noout', '-checkend', '86400'], check=True, capture_output=True)
        backup_root = Path('/var/backups/shouyulove-tls')
        backup_root.mkdir(mode=0o700, exist_ok=True)
        if backup_root.is_symlink() or backup_root.stat().st_uid != 0 or backup_root.stat().st_mode & 0o077:
            raise RuntimeError('TLS backup directory must be root-private')
        backup = backup_root / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:8])
        backup.mkdir(mode=0o700)
        for name in NAMES:
            shutil.copyfile(TLS / name, backup / name)
            (backup / name).chmod(0o600)
        with tempfile.TemporaryDirectory(prefix='.renewed-', dir=TLS.parent) as temporary:
            stage = Path(temporary)
            for name in NAMES:
                shutil.copyfile(LINEAGE / name, stage / name)
                (stage / name).chmod(0o600)
            try:
                for name in NAMES:
                    os.replace(stage / name, TLS / name)
                subprocess.run(['nginx', '-t'], check=True)
                subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
            except BaseException:
                for name in NAMES:
                    shutil.copyfile(backup / name, stage / name)
                    (stage / name).chmod(0o600)
                    os.replace(stage / name, TLS / name)
                subprocess.run(['nginx', '-t'], check=True)
                subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
                raise
        print('ShouYuLove TLS activated; Nginx configuration files were not modified.')


if __name__ == '__main__':
    main()
