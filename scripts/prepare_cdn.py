#!/usr/bin/env python3
"""Stage a verified runtime and a separate, versioned public-assets upload."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

from runtime_snapshot import relative, require, verify

SHARED = 'sites/immersive-g-com-955afd14/shared'
ASSET_PREFIX = re.compile(r'''(?<=["'`(])/(?:sites/immersive-g-com-955afd14/shared/|(?=(?:assets|webgl|sounds|images|lotties)/))''')
CDN_PREFIX = re.compile(r'https://assets\.shouyulove\.cn/v/[a-zA-Z0-9_-]+(?=/' + SHARED + r'/)')
WORKER = re.compile(r'new URL\("(sortGeometryVertices-[\w.-]+\.js)",import\.meta\.url\)')
TEXT_TYPES = {'.js', '.css', '.json', '.svg'}


def rewrite(text, base):
    def replace(match):
        # The installation scope and start URL must remain on the main site.
        if text[match.end():].startswith(('shouyulove/works-manifest.', 'assets/sortGeometryVertices-')):
            return match.group()
        return base + '/' + SHARED + '/'

    result = CDN_PREFIX.sub(base, ASSET_PREFIX.sub(replace, text))
    # Nuxt uses this directory together with its page origin, including payloads.
    result = result.replace('"buildAssetsDir":"' + base + '/' + SHARED + '/assets/"',
                            '"buildAssetsDir":"/assets/"')
    # Classic workers cannot be constructed from a cross-origin module URL.
    result = WORKER.sub(lambda match: 'new URL("/assets/' + match[1] + '",location.href)', result)
    return result


def record(path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def prepare(source, manifest, destination, base):
    url = urlsplit(base)
    require(url.scheme == 'https' and url.netloc == 'assets.shouyulove.cn'
            and re.fullmatch(r'/v/[a-zA-Z0-9_-]+', url.path)
            and not url.query and not url.fragment,
            'Use the dedicated HTTPS asset host and a new /v/<release> prefix.')
    verify(source, manifest)
    require(not destination.exists(), 'Destination exists; preserve it and choose a new path.')
    runtime = destination / 'site'
    upload = destination / 'upload'
    result = copy.deepcopy(manifest)
    objects = {}
    runtime.mkdir(parents=True)
    for name in manifest['files']:
        target = runtime / relative(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative(name), target)
        if name.startswith(SHARED + '/') and 'works-manifest.' not in name:
            # Only the reviewed runtime manifest is exported, never the repository.
            object_name = url.path.lstrip('/') + '/' + name
            asset = upload / relative(object_name)
            asset.parent.mkdir(parents=True, exist_ok=True)
            if target.suffix in TEXT_TYPES:
                asset.write_text(rewrite(target.read_text(), base))
            else:
                shutil.copy2(target, asset)
            objects[object_name] = record(asset)
        elif target.suffix == '.html':
            text = rewrite(target.read_text(), base)
            preconnect = '<link rel="preconnect" href="https://assets.shouyulove.cn" crossorigin/>'
            if preconnect not in text:
                text = text.replace('</head>', preconnect + '</head>', 1)
            target.write_text(text)
            result['files'][name] = record(target)
    for name, target in manifest['symlinks'].items():
        (runtime / relative(name)).symlink_to(target, target_is_directory=True)
    result['bytes'] = sum(item['bytes'] for item in result['files'].values())
    (destination / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    asset_manifest = {'base': base, 'files': objects,
                      'bytes': sum(item['bytes'] for item in objects.values())}
    (destination / 'cdn-manifest.json').write_text(json.dumps(asset_manifest, indent=2) + '\n')
    verify(runtime, result, exact=True)
    return {'runtime_files': len(result['files']), 'cdn_files': len(objects),
            'cdn_bytes': asset_manifest['bytes'], 'base': base}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--base', required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    print(json.dumps(prepare(args.source, manifest, args.destination, args.base), indent=2))


if __name__ == '__main__':
    main()
