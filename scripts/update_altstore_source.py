#!/usr/bin/env python3
"""
Update AltStore source.json by checking upstream GitHub Releases.

This template is designed for an "index-style" AltStore repo:
- It links IPA downloads directly to upstream GitHub Release assets.
- It does not mirror/re-upload third-party IPA files.

apps.json format:

[
  {
    "name": "Example App",
    "github": "owner/repo",
    "assetRegex": ".*\\.ipa$",
    "includePrereleases": false,
    "releaseLimit": 30
  }
]
"""

from __future__ import annotations

import json
import os
import plistlib
import re
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "source.json"
APPS_PATH = ROOT / "apps.json"


def request_json(url: str) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "altstore-repo-updater",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def download_file(url: str, path: Path) -> None:
    headers = {"User-Agent": "altstore-repo-updater"}
    # browser_download_url for public assets usually does not need Authorization.
    # Keeping token out avoids problems with release asset redirects.
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=300) as response:
        path.write_bytes(response.read())


def find_releases(repo: str, include_prereleases: bool, release_limit: int) -> list[dict[str, Any]]:
    limit = max(1, min(release_limit, 100))
    releases = request_json(f"https://api.github.com/repos/{repo}/releases?per_page={limit}")

    if include_prereleases:
        return [r for r in releases if not r.get("draft")]

    return [r for r in releases if not r.get("draft") and not r.get("prerelease")]


def pick_ipa_asset(release: dict[str, Any], asset_regex: str) -> dict[str, Any] | None:
    pattern = re.compile(asset_regex, re.IGNORECASE)
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        if pattern.fullmatch(name) or pattern.search(name):
            return asset
    return None


def read_ipa_info(ipa_path: Path) -> dict[str, str | None]:
    with zipfile.ZipFile(ipa_path) as zf:
        plist_candidates = [
            name for name in zf.namelist()
            if name.startswith("Payload/") and name.endswith(".app/Info.plist")
        ]
        if not plist_candidates:
            raise RuntimeError(f"No Payload/*.app/Info.plist found in {ipa_path.name}")

        # Prefer the shallowest .app Info.plist.
        plist_name = sorted(plist_candidates, key=lambda p: p.count("/"))[0]

        with zf.open(plist_name) as f:
            info = plistlib.load(f)

    return {
        "name": info.get("CFBundleDisplayName") or info.get("CFBundleName"),
        "bundleIdentifier": info.get("CFBundleIdentifier"),
        "version": info.get("CFBundleShortVersionString"),
        "buildVersion": info.get("CFBundleVersion"),
        "minOSVersion": info.get("MinimumOSVersion"),
    }


def parse_release_limit(config: dict[str, Any]) -> int:
    try:
        return int(config.get("releaseLimit", 20))
    except (TypeError, ValueError):
        return 20


def default_icon_url(config: dict[str, Any]) -> str:
    owner = config["github"].split("/", 1)[0]
    return f"https://github.com/{owner}.png"


def sync_app_metadata(app: dict[str, Any], app_info: dict[str, str | None], config: dict[str, Any]) -> bool:
    name = config.get("name") or app_info.get("name") or app["bundleIdentifier"]
    app_permissions = config.get("appPermissions", app.get("appPermissions", {"entitlements": [], "privacy": {}}))

    fields = {
        "name": name,
        "developerName": config.get("developerName") or config["github"].split("/")[0],
        "subtitle": config.get("subtitle") or "下载来自原作者 GitHub Releases",
        "localizedDescription": config.get("description") or (
            f"此条目为非官方精选索引。IPA 文件来自 {config['github']} 的 GitHub Releases。"
        ),
        "iconURL": config.get("iconURL") or app.get("iconURL") or default_icon_url(config),
        "tintColor": config.get("tintColor", app.get("tintColor", "#4185A9")),
        "category": config.get("category", app.get("category", "utilities")),
        "screenshots": config.get("screenshots", app.get("screenshots", [])),
        "appPermissions": app_permissions,
    }

    changed = False
    for key, value in fields.items():
        if app.get(key) != value:
            app[key] = value
            changed = True

    if "versions" not in app:
        app["versions"] = []
        changed = True

    return changed


def ensure_app_entry(source: dict[str, Any], app_info: dict[str, str | None], config: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    bundle_id = app_info["bundleIdentifier"]
    if not bundle_id:
        raise RuntimeError(f"Cannot find CFBundleIdentifier for {config['github']}")

    for app in source.setdefault("apps", []):
        if app.get("bundleIdentifier") == bundle_id:
            changed = sync_app_metadata(app, app_info, config)
            if bundle_id not in source.setdefault("featuredApps", []):
                source["featuredApps"].append(bundle_id)
                changed = True
            return app, changed

    app = {
        "bundleIdentifier": bundle_id,
        "versions": [],
    }
    sync_app_metadata(app, app_info, config)
    source["apps"].append(app)

    if bundle_id not in source.setdefault("featuredApps", []):
        source["featuredApps"].append(bundle_id)

    return app, True


def version_exists(app: dict[str, Any], version: str, build_version: str) -> bool:
    for item in app.get("versions", []):
        if item.get("version") == version and item.get("buildVersion") == build_version:
            return True
    return False


def update_one(source: dict[str, Any], config: dict[str, Any]) -> bool:
    repo = config["github"]
    asset_regex = config.get("assetRegex", r".*\.ipa$")
    include_prereleases = bool(config.get("includePrereleases", False))
    release_limit = parse_release_limit(config)

    releases = find_releases(repo, include_prereleases, release_limit)
    if not releases:
        print(f"[skip] {repo}: no releases")
        return False

    for release in releases:
        asset = pick_ipa_asset(release, asset_regex)
        if not asset:
            continue

        ipa_url = asset["browser_download_url"]
        with tempfile.TemporaryDirectory() as tmp:
            ipa_path = Path(tmp) / asset["name"]
            print(f"[download] {repo}: {asset['name']}")
            download_file(ipa_url, ipa_path)
            app_info = read_ipa_info(ipa_path)

        version = app_info.get("version")
        build_version = app_info.get("buildVersion")
        if not version or not build_version:
            raise RuntimeError(f"Cannot find version/buildVersion in IPA for {repo}")

        app, metadata_changed = ensure_app_entry(source, app_info, config)
        if version_exists(app, version, build_version):
            print(f"[ok] {repo}: already has {version} ({build_version})")
            return metadata_changed

        description = release.get("body") or f"Updated from {repo} {release.get('tag_name', '')}".strip()
        if release.get("html_url"):
            description = f"{description}\n\nUpstream release: {release['html_url']}"

        # AltStore descriptions should stay reasonably short. Keep release notes but cap very long bodies.
        if len(description) > 4000:
            description = description[:3900] + "\n\n…"

        version_entry: dict[str, Any] = {
            "version": version,
            "buildVersion": build_version,
            "date": (release.get("published_at") or release.get("created_at") or "")[:10],
            "localizedDescription": description,
            "downloadURL": ipa_url,
            "size": int(asset.get("size") or 0),
        }

        if app_info.get("minOSVersion"):
            version_entry["minOSVersion"] = app_info["minOSVersion"]

        app.setdefault("versions", []).insert(0, version_entry)
        print(f"[update] {repo}: added {version} ({build_version})")
        return True

    print(f"[skip] {repo}: no IPA asset matched {asset_regex}")
    return False


def main() -> None:
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    apps = json.loads(APPS_PATH.read_text(encoding="utf-8"))

    changed = False
    for config in apps:
        # Ignore placeholder entry.
        if config.get("github") == "owner/repo":
            print("[skip] placeholder owner/repo")
            continue

        try:
            changed = update_one(source, config) or changed
        except Exception as exc:
            print(f"[error] {config.get('github')}: {exc}")
            # Continue with other apps instead of failing the whole source.
            # Change this to `raise` if you prefer strict failures.

    if changed:
        SOURCE_PATH.write_text(
            json.dumps(source, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("[done] source.json updated")
    else:
        print("[done] no changes")


if __name__ == "__main__":
    main()
