"""
读取 wiki_avatars.json，遍历每个角色的 Wiki 详情页，提取主动技能名。
输出: ../src/data/wiki_active_skills_zh.json
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

WIKI_BASE = "https://wiki.biligame.com"
AVATAR_FILE = Path(__file__).parent.parent / "src" / "data" / "wiki_avatars.json"
OUTPUT = Path(__file__).parent.parent / "src" / "data" / "wiki_active_skills_zh.json"

HEADERS = {"User-Agent": "Mozilla/5.0 qllr-scraper/0.1"}


def fetch(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_active_skills(html: str) -> list[str]:
    """从角色详情页提取主动技能中文名。
    Wiki 详情页一般有一个 id="chinese-active" 的容器，里面是技能表。
    具体结构可能随 Wiki 改版变化，这里只做最基本的提取。
    """
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find(id="chinese-active")
    if not container:
        return []
    skills = []
    for el in container.find_all(["a", "b", "td"]):
        text = el.get_text(strip=True)
        if not text or len(text) > 30:
            continue
        if text in skills:
            continue
        skills.append(text)
    return skills[:20]  # 上限


def main():
    if not AVATAR_FILE.exists():
        print(f"[error] 缺少 {AVATAR_FILE}，请先运行 scrape_avatars.py")
        return
    avatars = json.loads(AVATAR_FILE.read_text(encoding="utf-8"))
    by_character = {}
    names = list(avatars["byName"].keys())
    total = len(names)
    for i, name in enumerate(names, 1):
        info = avatars["byName"][name]
        url = urljoin(WIKI_BASE, info["wikiPath"])
        print(f"[{i}/{total}] {name}")
        try:
            html = fetch(url)
            skills = parse_active_skills(html)
            by_character[name] = {
                "activeSkillsZh": skills,
                "wikiUrl": url,
                "wikiTitle": name,
                "count": len(skills),
            }
            time.sleep(0.5)
        except Exception as e:
            print(f"  !! 失败: {e}")
            by_character[name] = {
                "activeSkillsZh": [],
                "wikiUrl": url,
                "wikiTitle": name,
                "count": 0,
            }

    output = {
        "schema": "octopathsp-wiki-active-skills-zh-1",
        "sourceAvatarIndex": "src/data/wiki_avatars.json",
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "characterCount": len(by_character),
        "byCharacter": by_character,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[done] wrote {OUTPUT}")


if __name__ == "__main__":
    main()
