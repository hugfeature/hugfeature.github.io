#!/usr/bin/env python3
"""Submit changed public URLs to IndexNow using only the Python standard library."""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
import time
from pathlib import Path

HOST = "hugfeature.github.io"
BASE = f"https://{HOST}"
KEY = "18cc8171cbb91d26cec196aa1f0b0e9f"
KEY_LOCATION = f"{BASE}/{KEY}.txt"
SITE_WIDE = {"_config.yml", "harness.md", "index.md", "scripts/indexnow_submit.py"}
SITE_WIDE_PREFIXES = ("_layouts/", "_includes/", "_data/")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def changed_files(before: str, after: str) -> list[str]:
    if not before or set(before) == {"0"}:
        return []
    try:
        return [p for p in git("diff", "--name-only", before, after).splitlines() if p]
    except subprocess.CalledProcessError:
        return []


def front_matter_permalink(path: Path) -> str | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("permalink:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    if path.name == "index.md":
        return "/"
    return None


def all_public_urls() -> set[str]:
    urls = {BASE + "/", BASE + "/harness/"}
    for path in list(Path("_posts").glob("*.md")) + list(Path(".").glob("*.md")):
        permalink = front_matter_permalink(path)
        if permalink:
            urls.add(BASE + permalink)
    return urls


def urls_for_changes(paths: list[str]) -> set[str]:
    if not paths:
        return all_public_urls()
    if any(p in SITE_WIDE or p.startswith(SITE_WIDE_PREFIXES) for p in paths):
        return all_public_urls()

    urls: set[str] = set()
    for name in paths:
        path = Path(name)
        if name.startswith("_posts/") or (path.parent == Path(".") and path.suffix == ".md"):
            permalink = front_matter_permalink(path)
            if permalink:
                urls.add(BASE + permalink)
    return urls


def wait_for_key() -> None:
    for attempt in range(12):
        try:
            with urllib.request.urlopen(KEY_LOCATION, timeout=10) as response:
                content = response.read().decode("utf-8").strip()
                if response.status == 200 and content == KEY:
                    print("IndexNow key is live.")
                    return
        except Exception as exc:
            print(f"Waiting for deployed key ({attempt + 1}/12): {exc}")
        time.sleep(10)
    raise RuntimeError(f"IndexNow key not reachable at {KEY_LOCATION}")


def submit(urls: set[str]) -> None:
    if not urls:
        print("No public URLs changed; nothing to submit.")
        return
    wait_for_key()
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": sorted(urls),
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.indexnow.org/IndexNow",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        print(f"IndexNow HTTP {response.status}: submitted {len(urls)} URL(s)")
        for url in sorted(urls):
            print(url)


if __name__ == "__main__":
    before = sys.argv[1] if len(sys.argv) > 1 else ""
    after = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    submit(urls_for_changes(changed_files(before, after)))
