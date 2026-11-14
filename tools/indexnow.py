#!/usr/bin/env python3
"""Tell IndexNow (Bing and partners) which URLs exist, after a deploy.

    python3 tools/indexnow.py          # reads public/sitemap.xml

Bing's index also feeds ChatGPT search and Copilot. The key is public by design:
it is served as /<key>.txt so the search engine can check that we own the site.
"""
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.content import SITE  # noqa: E402


def main():
    key = SITE["indexnow_key"]
    host = SITE["domain"].split("//")[1]
    urls = sorted(set(re.findall(r"<loc>(.*?)</loc>", (ROOT / "public" / "sitemap.xml").read_text(encoding="utf-8"))))
    body = json.dumps({"host": host, "key": key, "keyLocation": f"{SITE['domain']}/{key}.txt", "urlList": urls}).encode()
    request = urllib.request.Request(
        "https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"IndexNow: {response.status} for {len(urls)} URLs")
    except urllib.error.HTTPError as error:
        print(f"IndexNow: HTTP {error.code} {error.reason}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
