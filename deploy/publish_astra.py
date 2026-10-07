#!/usr/bin/env python3
"""Run on the server after uploading the isolated Astra release."""

from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def replace_file(path, content):
    temporary = path.with_name(path.name + ".astra-new")
    temporary.write_bytes(content)
    temporary.chmod(0o644)
    os.replace(temporary, path)


def switch(home, release):
    temporary = home.with_name(home.name + ".astra-new")
    temporary.symlink_to(release)
    os.replace(temporary, home)


def get(path):
    request = urllib.request.Request("http://127.0.0.1" + path,
                                     headers={"Host": "shouyulove.cn"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def main():
    stage = Path(__file__).resolve().parent
    state = json.loads((stage / "request.json").read_text())
    name = state["release"]
    assert re.fullmatch(r"\d{8}T\d{6}Z-astra-home", name)
    home = Path("/var/www/shouyulove-home")
    release = Path("/var/www/shouyulove-home-releases") / name
    backup = Path("/etc/nginx/backups") / ("shouyulove-home-" + name)
    site = Path("/etc/nginx/sites-available/shouyulove")
    snippet = Path("/etc/nginx/snippets/shouyulove-home.conf")
    assert str(home.resolve()) == state["old_release"]
    for path, key in ((site, "old_site_sha256"), (snippet, "old_snippet_sha256"),
                      (home / "index.html", "old_home_sha256")):
        assert digest(path) == state[key], str(path)
    assert digest(backup / "site.conf") == state["old_site_sha256"]
    assert digest(backup / "snippet.conf") == state["old_snippet_sha256"]
    assert digest(stage / "manifest.json") == state["manifest_sha256"]
    assert digest(stage / "nginx-home.locations.conf") == state["new_snippet_sha256"]
    manifest = json.loads((stage / "manifest.json").read_text())
    expected = set(manifest["files"]) | set(manifest["symlinks"])
    actual = {str(p.relative_to(release)) for p in release.rglob("*")
              if p.is_file() or p.is_symlink()}
    assert actual == expected, "Uploaded release file list differs"
    for relative, record in manifest["files"].items():
        path = release / relative
        assert path.resolve().is_relative_to(release.resolve()), relative
        assert path.stat().st_size == record["bytes"], relative
        assert digest(path) == record["sha256"], relative
        path.chmod(0o644)
    for relative, target in manifest["symlinks"].items():
        path = release / relative
        assert str(path.readlink()) == target, relative
        assert path.resolve().is_relative_to(release.resolve()) and path.is_dir(), relative
    for path in release.rglob("*"):
        if path.is_dir() and not path.is_symlink():
            path.chmod(0o755)
    release.chmod(0o755)
    print(json.dumps({"verified_files": len(manifest["files"]), "bytes": manifest["bytes"]}), flush=True)

    changed = False
    try:
        changed = True
        replace_file(snippet, (stage / "nginx-home.locations.conf").read_bytes())
        subprocess.run(["nginx", "-t"], check=True)
        switch(home, release)
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
        assert digest(site) == state["old_site_sha256"], "Parent site configuration changed"
        # Reload returns before the old workers have stopped accepting requests.
        readiness = []
        for attempt in range(40):
            status, content = get("/the-studio/")
            value = hashlib.sha256(content).hexdigest()
            readiness.append({"attempt": attempt + 1, "status": status,
                              "sha256": value, "bytes": len(content)})
            if status == 200 and value == manifest["files"]["the-studio/index.html"]["sha256"]:
                break
            time.sleep(0.25)
        else:
            raise AssertionError({"route": "/the-studio/", "readiness": readiness})
        routes = {}
        for route in manifest["routes"]:
            status, content = get(route)
            assert status == 200, (route, status)
            filename = route.strip("/") + "/index.html" if route != "/" else "index.html"
            assert hashlib.sha256(content).hexdigest() == manifest["files"][filename]["sha256"], route
            routes[route] = status
        subsites = {route: get(route)[0] for route in
                    ("/signtrace/", "/chuanqinghuiyi/", "/dict/entries")}
        assert all(status == 200 for status in subsites.values()), subsites
        retired = {route: get(route)[0] for route in
                   ("/home-assets/garden.bundle.js", "/sign-projects/", "/campus/")}
        assert all(status == 404 for status in retired.values()), retired
        result = {"release": str(release), "previous_release": state["old_release"],
                  "backup": str(backup), "verified_files": len(manifest["files"]),
                  "verified_bytes": manifest["bytes"], "routes": routes,
                  "subsites": subsites, "retired": retired,
                  "readiness": readiness,
                  "parent_config_sha256": digest(site), "snippet_sha256": digest(snippet)}
        (backup / "release.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result), flush=True)
    except BaseException:
        if changed:
            switch(home, Path(state["old_release"]))
            replace_file(snippet, (backup / "snippet.conf").read_bytes())
            subprocess.run(["nginx", "-t"], check=True)
            subprocess.run(["systemctl", "reload", "nginx"], check=True)
            print("Previous homepage and configuration restored", flush=True)
        raise


if __name__ == "__main__":
    main()
