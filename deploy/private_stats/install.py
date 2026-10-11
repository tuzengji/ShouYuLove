#!/usr/bin/env python3
"""Install the owner-only collector independently of the public runtime whitelist."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import time

source = Path(__file__).resolve().parent
targets = {
    'visits.py': (Path('/opt/shouyulove-stats/visits.py'), 0o640),
    'shouyulove-stats.service': (Path('/etc/systemd/system/shouyulove-stats.service'), 0o644),
    'nginx-format.conf': (Path('/etc/nginx/conf.d/shouyulove-visit-format.conf'), 0o644),
    'shouyulove-stats': (Path('/usr/local/bin/shouyulove-stats'), 0o755),
}
for name, (destination, mode) in targets.items():
    if destination.exists():
        assert destination.read_bytes() == (source/name).read_bytes(), 'Existing collector installation differs'
    else:
        destination.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
        shutil.copy2(source/name, destination)
    destination.chmod(mode)
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','enable','--now','shouyulove-stats.service'],check=True)
for _ in range(30):
    if Path('/run/shouyulove-stats/collector.sock').exists():
        break
    time.sleep(.1)
else:
    raise AssertionError('Collector socket not ready')
subprocess.run(['nginx','-t'],check=True)
result = {'active':subprocess.check_output(['systemctl','is-active','shouyulove-stats.service'],text=True).strip(),
          'files':{str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path,_ in targets.values()},
          'database_mode':oct(Path('/var/lib/shouyulove-stats/visits.sqlite').stat().st_mode & 0o777),
          'public_endpoint':False}
(source/'installed.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
