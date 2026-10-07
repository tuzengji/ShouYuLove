#!/usr/bin/env python3
"""Verify or export the exact public runtime without rebuilding or deploying it."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative(name):
    path = PurePosixPath(name)
    require(bool(name) and not path.is_absolute() and str(path) == name,
            'Invalid relative path: ' + name)
    require(all(part not in ('.', '..') for part in path.parts)
            and '\\' not in name and '\0' not in name, 'Unsafe path: ' + name)
    return Path(*path.parts)


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def load_manifest():
    manifest = json.loads((ROOT / 'runtime-manifest.json').read_text())
    files, links = manifest['files'], manifest['symlinks']
    require(not set(files) & set(links), 'Files and links overlap.')
    for name in [*files, *links]:
        path = relative(name)
        require(not any(parent.as_posix() in links for parent in path.parents),
                'Manifest entry below a symlink: ' + name)
    for name, record in files.items():
        require(isinstance(record['bytes'], int) and record['bytes'] >= 0,
                'Invalid size: ' + name)
        require(re.fullmatch('[0-9a-f]{64}', record['sha256']) is not None,
                'Invalid digest: ' + name)
    for target in links.values():
        relative(target)
    require(sum(record['bytes'] for record in files.values()) == manifest['bytes'],
            'Manifest total does not match its file sizes.')
    for route, name in manifest['routes'].items():
        require(route.startswith('/') and name in files, 'Unknown route: ' + route)
    return manifest


def entries(directory):
    result = set()
    for folder, dirs, files in os.walk(directory, followlinks=False):
        for name in dirs + files:
            path = Path(folder) / name
            if path.is_file() or path.is_symlink():
                result.add(path.relative_to(directory).as_posix())
    return result


def verify(directory, manifest, exact=False):
    directory = directory.resolve(strict=True)
    for name, record in manifest['files'].items():
        path = directory / relative(name)
        require(path.is_file() and not path.is_symlink(), 'Missing regular file: ' + name)
        require(path.resolve().is_relative_to(directory), 'File leaves runtime directory: ' + name)
        require(not any((directory / parent).is_symlink()
                        for parent in relative(name).parents), 'Symlink in file path: ' + name)
        require(path.stat().st_size == record['bytes'] and digest(path) == record['sha256'],
                'File mismatch: ' + name)
    for name, target in manifest['symlinks'].items():
        path = directory / relative(name)
        require(path.is_symlink() and str(path.readlink()) == target, 'Link mismatch: ' + name)
        require(path.resolve().is_dir() and path.resolve().is_relative_to(directory),
                'Broken or external link: ' + name)
    if exact:
        require(entries(directory) == set(manifest['files']) | set(manifest['symlinks']),
                'Runtime directory contains missing or unexpected entries.')
    return dict(passed=True, directory=str(directory), files=len(manifest['files']),
                symlinks=len(manifest['symlinks']), routes=len(manifest['routes']),
                bytes=manifest['bytes'], exact=exact)


def export(destination, manifest):
    verify(ROOT, manifest)
    require(not destination.exists() and not destination.is_symlink(),
            'Destination already exists; choose a new directory.')
    require('.git' not in destination.parts, 'Cannot export into Git metadata.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()
    for name in manifest['files']:
        target = destination / relative(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative(name), target)
    for name, target in manifest['symlinks'].items():
        link = destination / relative(name)
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(target, target_is_directory=True)
    return verify(destination, manifest, exact=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    check = commands.add_parser('verify')
    check.add_argument('--directory', type=Path, default=ROOT)
    check.add_argument('--exact', action='store_true')
    copy = commands.add_parser('export')
    copy.add_argument('destination', type=Path)
    args = parser.parse_args()
    manifest = load_manifest()
    result = (verify(args.directory, manifest, args.exact) if args.command == 'verify'
              else export(args.destination.absolute(), manifest))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
