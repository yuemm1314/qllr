"""
从中文 Wiki 抓取角色头像与基本信息。
输出: ../src/data/wiki_avatars.json

用法（Windows）：
    cd scripts
    python -m venv .venv
    .venv\\Scripts\\pip install requests beautifulsoup4
    .venv\\Scripts\\python scrape_avatars.py
"""

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

WIKI_BASE = "https://wiki.biligame.com"
SOURCE_PAGES = [
    ("旅人图鉴2", "/octopathsp/%E6%97%85%E4%BA%BA%E5%9B%BE%E9%89%B42"),
    ("旅人图鉴", "/octopathsp/%E6%97%85%E4%BA%BA%E5%9B%BE%E9%89%B4"),
]
OUTPUT = Path(__file__).parent.parent / "src" / "data" / "wiki_avatars.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 qllr-scraper/0.1",
}


def fetch_page(path: str) -> str:
    url = urljoin(WIKI_BASE, path)
    print(f"[fetch] {url}")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_avatars(html: str) -> dict:
    """从图鉴页解析角色名 → 头像 URL 的映射。
    Wiki 图鉴页的结构是大量的角色卡片，每个卡片有一个链接和一张头像。
    """
    soup = BeautifulSoup(html, "html.parser")
    result = {}
    # 兼容多种结构：寻找所有指向 /octopathsp/角色名 的 <a>，里面通常包含一张 <img>
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("/octopathsp/"):
            continue
        title = a.get("title") or a.get_text(strip=True)
        if not title:
            continue
        img = a.find("img")
        if not img:
            continue
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        if src.startswith("//"):
            src = "https:" + src
        result[title] = {
            "avatar": src,
            "wikiPath": href,
            "wikiTitle": title,
        }
    return result


def main():
    merged = {}
    for label, path in SOURCE_PAGES:
        try:
            html = fetch_page(path)
            data = parse_avatars(html)
            print(f"  -> {label}: {len(data)} 个")
            merged.update(data)  # 后序覆盖前序
            time.sleep(1)
        except Exception as e:
            print(f"  !! {label} 失败: {e}")

    output = {
        "schema": "octopathsp-wiki-avatars-1",
        "sources": [
            {"label": label, "url": urljoin(WIKI_BASE, path)}
            for label, path in SOURCE_PAGES
        ],
        "mergePolicy": "同名时以后序来源为准",
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "count": len(merged),
        "byName": merged,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[done] wrote {OUTPUT} ({len(merged)} avatars)")


if __name__ == "__main__":
    main()
