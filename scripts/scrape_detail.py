"""
Detail Pass: 读取 wiki_character_list.json，抓取每个角色的详情页。
- 增量模式：已在 wiki_character_details.json 里的角色跳过
- --limit N    : 只处理前 N 个（按国服日期倒序）
- --force NAME : 强制重爬指定角色（可多次）
- --all        : 处理全部角色

输出: src/data/wiki_character_details.json
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin
import urllib3
import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://wiki.biligame.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}

DATA_DIR = Path(__file__).parent.parent / "src" / "data"
LIST_FILE = DATA_DIR / "wiki_character_list.json"
DETAIL_FILE = DATA_DIR / "wiki_character_details.json"

# 三类技能 tab 的 div id（来自参考脚本验证）
SKILL_CATEGORIES = [
    ("chinese-active",   "active"),    # 主动
    ("chinese-passive",  "passive"),   # 被动
    ("chinese-ultimate", "ultimate"),  # 必杀&EX
    # special 暂时跳过；如需要可加 ("chinese-special", "special"),
]

# MAX 属性表的行键（中文 -> 英文 key）
STAT_KEY_MAP = {
    "HP": "hp", "SP": "sp",
    "物攻": "patk", "物防": "pdef",
    "属攻": "eatk", "属防": "edef",
    "会心": "crit", "速度": "spd",
}

def fetch(session, url, retries=3):
    last = None
    for i in range(retries):
        try:
            r = session.get(url, timeout=30, verify=False)
            r.encoding = "utf-8"
            if r.status_code == 200 and r.text:
                return r.text
            last = f"status={r.status_code}"
        except Exception as e:
            last = str(e)
        time.sleep(2.0 * (i + 1))
    raise RuntimeError(f"fetch failed after {retries} tries: {last}")

def parse_basic_info(soup):
    """解析"XX基本信息"表，返回 dict。"""
    info = {}
    # 找紧跟在 "基本信息" 标题后的第一张 wikitable
    heading = soup.find(lambda tag: tag.name in ("h2", "h3")
                        and "基本信息" in tag.get_text(strip=True))
    table = heading.find_next("table") if heading else None
    if not table:
        return info

    for tr in table.find_all("tr"):
        th = tr.find("th")
        td = tr.find("td")
        if not th or not td:
            continue
        key = th.get_text(strip=True)
        # 影响力/职业等取 <p> 文字，避免图片 alt 干扰
        p = td.find("p")
        if p:
            val = p.get_text(" ", strip=True)
        else:
            val = td.get_text(" ", strip=True)
        info[key] = val
    return info

def parse_max_stats(soup):
    """解析"XX MAX属性"表，返回 6 星 120 级满觉数值。"""
    stats = {}
    heading = soup.find(lambda tag: tag.name in ("h2", "h3")
                        and "MAX属性" in tag.get_text(strip=True))
    table = heading.find_next("table") if heading else None
    if not table:
        return stats

    for tr in table.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if len(cells) < 3:
            continue
        name = cells[0].get_text(strip=True)
        key = STAT_KEY_MAP.get(name)
        if not key:
            continue
        # 第 3 列形如 "3496 (218)"，第一个整数就是 120 级满值
        text = cells[2].get_text(" ", strip=True)
        m = re.search(r"(\d+)", text)
        if m:
            stats[key] = int(m.group(1))
    return stats

def parse_skill_box(box):
    """从一个 .skillbox 解析单条技能。"""
    name_div = box.find("div", class_="skillbox-name")
    skill_name = name_div.get_text(strip=True) if name_div else ""

    sp_div = box.find("div", class_="skillbox-sp")
    skill_cost = sp_div.get_text(" ", strip=True) if sp_div else ""

    # 收集图标 tag（属性、buff/debuff、进化标记等）
    tags = []
    for img in box.find_all("img"):
        alt = img.get("alt", "")
        if "Icon-" in alt:
            tag = alt.replace(".png", "")
            if tag not in tags:
                tags.append(tag)

    # 技能效果表
    effect_lines = []
    bp_effect = ""
    enhance_effect = ""
    enhance_cond = ""
    content_table = box.find("table", class_="skillbox-content")
    if content_table:
        for tr in content_table.find_all("tr"):
            cells = tr.find_all("td")
            if not cells:
                continue
            if len(cells) == 1:
                # 主效果（colspan=2）
                effect_lines.append(cells[0].get_text("\n", strip=True))
            elif len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                value = cells[1].get_text(" / ", strip=True)
                if "BP" in label:
                    bp_effect = value
                elif "能力强化效果" in label:
                    enhance_effect = value
                elif "强化学习条件" in label:
                    enhance_cond = value

    return {
        "name": skill_name,
        "cost": skill_cost,
        "tags": tags,
        "effect": "\n".join(effect_lines).strip(),
        "bpEffect": bp_effect,
        "enhanceEffect": enhance_effect,
        "enhanceCondition": enhance_cond,
    }

def parse_skills(soup):
    """按三类（主动/被动/必杀&EX）分别解析技能。"""
    out = {"active": [], "passive": [], "ultimate": []}
    for div_id, key in SKILL_CATEGORIES:
        container = soup.find("div", id=div_id)
        if not container:
            continue
        for box in container.find_all("div", class_="skillbox"):
            try:
                out[key].append(parse_skill_box(box))
            except Exception as e:
                print(f"    [warn] skill parse error in {div_id}: {e}")
    return out

def parse_detail(html):
    soup = BeautifulSoup(html, "lxml")
    return {
        "basicInfo": parse_basic_info(soup),
        "maxStats": parse_max_stats(soup),
        "skills": parse_skills(soup),
    }

def load_existing():
    if not DETAIL_FILE.exists():
        return {}
    try:
        data = json.loads(DETAIL_FILE.read_text(encoding="utf-8"))
        return data.get("characters", {})
    except Exception:
        return {}

def save_details(characters_dict):
    out = {
        "schema": "octopathsp-wiki-character-details-1",
        "fetchedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(characters_dict),
        "characters": characters_dict,
    }
    DETAIL_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=2),
                           encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10,
                    help="只处理前 N 个角色（按国服日期倒序，默认 10）")
    ap.add_argument("--all", action="store_true",
                    help="处理 list 中的全部角色，覆盖 --limit")
    ap.add_argument("--force", action="append", default=[],
                    help="强制重爬指定角色名，可多次")
    ap.add_argument("--sleep", type=float, default=1.5,
                    help="每次请求间隔秒数")
    args = ap.parse_args()

    if not LIST_FILE.exists():
        print(f"[error] 缺少 {LIST_FILE}，请先运行 scrape_list.py")
        sys.exit(1)

    list_data = json.loads(LIST_FILE.read_text(encoding="utf-8"))
    all_chars = list_data["characters"]

    if args.all:
        targets = all_chars
    else:
        targets = all_chars[:args.limit]

    existing = load_existing()
    force_set = set(args.force)

    session = requests.Session()
    session.headers.update(HEADERS)

    new_count = 0
    skip_count = 0
    fail = []

    for i, ch in enumerate(targets, 1):
        name = ch["name"]
        url = ch.get("wikiUrl")
        if not url:
            print(f"[{i}/{len(targets)}] {name}: 无 wikiUrl, skip")
            continue

        if name in existing and name not in force_set:
            skip_count += 1
            print(f"[{i}/{len(targets)}] {name}: 已存在, skip")
            continue

        print(f"[{i}/{len(targets)}] {name}  <- {url}")
        try:
            html = fetch(session, url)
            detail = parse_detail(html)
            existing[name] = {
                "name": name,
                "wikiUrl": url,
                "fetchedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                **detail,
            }
            new_count += 1
            stats = detail["maxStats"]
            skills = detail["skills"]
            print(f"    HP={stats.get('hp')} SP={stats.get('sp')} "
                  f"物攻={stats.get('patk')} 属攻={stats.get('eatk')} | "
                  f"主动{len(skills['active'])} 被动{len(skills['passive'])} "
                  f"必杀{len(skills['ultimate'])}")
        except Exception as e:
            print(f"    [error] {e}")
            fail.append(name)

        time.sleep(args.sleep)

        # 每 20 个保存一次，避免中断丢失
        if new_count and new_count % 20 == 0:
            save_details(existing)
            print(f"    [checkpoint] saved {len(existing)} characters")

    save_details(existing)
    print(f"\n[done] 新增 {new_count}, 跳过 {skip_count}, 失败 {len(fail)}, "
          f"总计 {len(existing)}")
    print(f"        wrote -> {DETAIL_FILE}")
    if fail:
        print(f"[failed] {fail}")

if __name__ == "__main__":
    sys.exit(main())
