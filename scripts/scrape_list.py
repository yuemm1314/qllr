"""
List Pass: 抓取"旅人图鉴"和"旅人图鉴2"列表页。
输出: src/data/wiki_character_list.json
"""
import json
import re
import time
import sys
from pathlib import Path
from urllib.parse import urljoin
import urllib3
import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://wiki.biligame.com"
LIST_PAGES = [
    "/octopathsp/旅人图鉴",
    "/octopathsp/旅人图鉴2",
]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

WEAPON_MAP = {
    "Icon-剣": "sword", "Icon-槍": "spear", "Icon-短剣": "dagger",
    "Icon-斧": "axe", "Icon-弓": "bow", "Icon-杖": "staff",
    "Icon-本": "book", "Icon-扇": "fan",
}
ELEMENT_MAP = {
    "Icon-火": "fire", "Icon-氷": "ice", "Icon-雷": "thunder",
    "Icon-風": "wind", "Icon-光": "light", "Icon-闇": "dark",
}
INFLUENCE_MAP = {
    "富": "wealth", "権力": "power", "名声": "fame",
    "拥有": "possession", "支配": "dominance",
    "認可": "recognition", "认可": "recognition",
}

def norm_alt(alt: str) -> str:
    alt = alt.replace(".png", "")
    alt = re.sub(r"の画像$", "", alt)
    return alt

def alt_to_weapon(alt): return WEAPON_MAP.get(norm_alt(alt))
def alt_to_element(alt): return ELEMENT_MAP.get(norm_alt(alt))

def alt_to_influence(alt):
    m = re.search(r"影响力图标-([^.]+)", alt)
    if not m:
        return None
    return INFLUENCE_MAP.get(m.group(1))

def find_character_table(soup):
    """页面上有多个 wikitable（筛选器+角色表），找到含 soc-filter-item 的那张。"""
    for t in soup.find_all("table"):
        if t.find("tr", class_="soc-filter-item"):
            return t
    return None

def parse_list_page(html: str):
    soup = BeautifulSoup(html, "lxml")
    table = find_character_table(soup)
    if not table:
        print("  [warn] 未找到包含 soc-filter-item 的角色表")
        return []

    data_rows = table.find_all("tr", class_="soc-filter-item")
    chars = []

    for tr in data_rows:
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 7:
            continue

        # 第 1 列：角色名 + 头像 + wiki 链接
        name_cell = tds[0]
        wiki_title = None
        wiki_path = None
        for a in name_cell.find_all("a"):
            href = a.get("href", "")
            if href and "/octopathsp/" in href and not re.search(r"\.(png|jpg|gif|webp)$", href, re.I):
                wiki_path = href
                wiki_title = a.get("title") or a.get_text(strip=True)
                break
        if not wiki_title:
            # 兜底：单元格纯文本
            wiki_title = name_cell.get_text(strip=True)

        img = name_cell.find("img")
        avatar = img.get("src") if img else None

        # 第 2 列：职业
        job_p = tds[1].find("p")
        job = job_p.get_text(strip=True) if job_p else tds[1].get_text(strip=True)

        # 第 3 列：初始星级
        rarity_txt = tds[2].get_text(strip=True)
        rarity = int(rarity_txt) if rarity_txt.isdigit() else None

        # 第 4 列：影响力
        infl_img = tds[3].find("img")
        infl_p = tds[3].find("p")
        influence_key = alt_to_influence(infl_img.get("alt", "")) if infl_img else None
        influence_text = infl_p.get_text(strip=True) if infl_p else tds[3].get_text(strip=True) or None

        # 第 5 列：卡池
        gacha = tds[4].get_text("\n", strip=True)

        # 第 6, 7 列：国服 / 日服 实装日期
        cn_date = tds[5].get_text(strip=True) if len(tds) > 5 else ""
        jp_date = tds[6].get_text(strip=True) if len(tds) > 6 else ""

        # 第 8 列：突破弱点
        weapons, elements = [], []
        if len(tds) > 7:
            for im in tds[7].find_all("img"):
                alt = im.get("alt", "")
                w = alt_to_weapon(alt)
                e = alt_to_element(alt)
                if w and w not in weapons:
                    weapons.append(w)
                elif e and e not in elements:
                    elements.append(e)

        chars.append({
            "name": wiki_title,
            "wikiPath": wiki_path,
            "wikiUrl": urljoin(BASE, wiki_path) if wiki_path else None,
            "avatar": avatar,
            "job": job,
            "rarity": rarity,
            "influence": influence_key,
            "influenceText": influence_text,
            "gacha": gacha,
            "cnReleaseDate": cn_date or None,
            "jpReleaseDate": jp_date or None,
            "weakness": {"weapons": weapons, "elements": elements},
        })
    return chars

def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    all_chars = []
    seen = set()
    for path in LIST_PAGES:
        url = urljoin(BASE, path)
        print(f"[fetch] {url}")
        resp = session.get(url, timeout=30, verify=False)
        resp.encoding = "utf-8"
        chars = parse_list_page(resp.text)
        print(f"  parsed {len(chars)} rows")
        for c in chars:
            if c["name"] in seen:
                continue
            seen.add(c["name"])
            all_chars.append(c)
        time.sleep(1.0)

    def sort_key(c):
        return (c.get("cnReleaseDate") or "").replace("/", "")
    all_chars.sort(key=sort_key, reverse=True)

    out_path = Path(__file__).parent.parent / "src" / "data" / "wiki_character_list.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out = {
        "schema": "octopathsp-wiki-character-list-1",
        "source": [urljoin(BASE, p) for p in LIST_PAGES],
        "fetchedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(all_chars),
        "characters": all_chars,
    }
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[done] wrote {len(all_chars)} characters to {out_path}")

    print("\n--- Top 10 latest (CN release) ---")
    for c in all_chars[:10]:
        ws = "/".join(c["weakness"]["weapons"]) or "-"
        es = "/".join(c["weakness"]["elements"]) or "-"
        print(f"  {c['cnReleaseDate']}  {c['name']:<12}  {c['job']:<4}  "
              f"★{c['rarity']}  weak:[{ws}][{es}]")

if __name__ == "__main__":
    sys.exit(main())
