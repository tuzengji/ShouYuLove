"""Generate 1024px mobile normal maps with pinned Khronos KTX tools."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / 'output/deployment/shouyulove-fast-20261009'
TOOLS = ROOT / 'output/tools/ktx-software-v4.4.2/expanded/KTX-Software-4.4.2-Darwin-arm64-tools.pkg/Payload/usr/local/bin'
VERSION = 'syl-v1-1-fast'


def main():
    output = RECORDS / 'mobile-textures'
    output.mkdir(exist_ok=True)
    source = RECORDS / 'before-site/sites/immersive-g-com-955afd14/shared/webgl/about/model/textures/ktx2/ultralow'
    results = []
    for number in ['05', '06']:
        original = source / f'normal_{number}.ktx2'
        png = RECORDS / f'normal_{number}-source.png'
        result = output / f'normal_{number}.{VERSION}.ktx2'
        subprocess.run([str(TOOLS / 'ktx'), 'extract', '--transcode', 'rgba8', str(original), str(png)], check=True)
        subprocess.run([str(TOOLS / 'toktx'), '--t2', '--resize', '1024x1024', '--assign_oetf', 'linear', '--assign_primaries', 'none', '--encode', 'uastc', '--uastc_quality', '2', '--zcmp', '18', str(result), str(png)], check=True)
        subprocess.run([str(TOOLS / 'ktx'), 'validate', str(result)], check=True)
        data = result.read_bytes()
        assert struct.unpack_from('<2I', data, 20) == (1024, 1024)
        assert len(data) < original.stat().st_size / 2
        results.append(dict(source=str(original.relative_to(ROOT)), file=result.name, width=1024, height=1024, before_bytes=original.stat().st_size, after_bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    (RECORDS / 'mobile-textures.json').write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
