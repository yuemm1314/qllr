# -*- coding: utf-8 -*-
"""
读取 src/data/wiki_character_details.json
输出 src/data/skill_rankings.json
规则:
- 倍率 = 满BP威力 × 满BP次数 × Π(被动威力乘数) × Π(神业乘数)
- 暴击不计, 队友buff不计, 自身buff计入(标注启动回合)
- 弱点1.3不乘
- 8武器 + 6属性, 每榜 Top 20
- 去重: 同(角色, 技能, 触发条件) 在同榜只保留最大值
"""
import json, re, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "data" / "wiki_character_details.json"
DST = ROOT / "src" / "data" / "skill_rankings.json"

WEAPONS  = ["剑","枪","短剑","斧","弓","杖","书","扇"]
ELEMENTS = ["火","冰","雷","风","光","暗"]

# 1) 不算攻击技 (纯辅助 / 纯buff)
NON_ATTACK_KW = ["回复","治愈","复活","附加","赋予","加护","守护","鼓舞","祈祷",
                 "增益","BUFF","buff","提升","降低","减少","解除"]

# 2) 威力&次数提取
RE_POWER = re.compile(r"威力\s*([0-9０-９]+(?:/[0-9０-９]+)*)")
RE_HITS  = re.compile(r"([0-9０-９]+)\s*次")
RE_TIMES = re.compile(r"([0-9０-９]+)\s*回")

def to_int(s): return int(re.sub(r"[^\d]","", s or "0") or 0)
def last_val(s):
    """取斜杠分段的最后一档(满BP)"""
    parts = re.split(r"[/／]", s)
    return to_int(parts[-1])

# 只识别两类: 神业(×2) 和 威力提升100%(×2)
# 其他小幅度威力提升 (30%/50% 等) 一律不计, 保持整数倍率
PASSIVE_RULES = [
    # 神业: 文本含"神业"且后面跟回合数, 或"追加发动/再次发动"
    (re.compile(r"神业"),               "divine",     lambda m: 2.0),
    (re.compile(r"追加发动|再次发动"),    "divine",     lambda m: 2.0),
    # 威力提升 100% (含"全心全力"这种固定 100% 别名)
    (re.compile(r"威力.*?提升\s*100\s*%"), "self_power", lambda m: 2.0),
    (re.compile(r"威力\s*\+\s*100\s*%"),   "self_power", lambda m: 2.0),
    (re.compile(r"全心全力"),              "self_power", lambda m: 2.0),
]

def is_attack_skill(name: str, effect: str) -> bool:
    if not effect: return False
    if not re.search(r"威力\s*\d", effect): return False
    # 排除纯辅助
    for kw in NON_ATTACK_KW:
        if kw in name and "攻击" not in name:
            return False
    return True

def parse_skill_base(skill: dict):
    """返回 (power, hits, sourceText) 取满BP档"""
    text = skill.get("bpEffect") or skill.get("effect") or ""
    pm = RE_POWER.search(text)
    if not pm: return None
    power = last_val(pm.group(1))
    hm = RE_HITS.search(text) or RE_TIMES.search(text)
    hits = to_int(hm.group(1)) if hm else 1
    return power, hits, text

def collect_passive_mults(passives: list, ultimates: list):
    """返回 [(label, mult, turnCost)], turnCost=0 表示常驻"""
    out = []
    # 常驻被动
    for p in passives or []:
        text = (p.get("name","") + " " + p.get("effect","")).strip()
        for rgx, kind, fn in PASSIVE_RULES:
            m = rgx.search(text)
            if m:
                out.append((p.get("name","被动"), fn(m), 0, kind))
                break   # 关键: 每条被动只算一次
    # 必杀/EX 自buff (需要释放)
    for u in ultimates or []:
        text = (u.get("name","") + " " + u.get("effect","") + " " + u.get("bpEffect","")).strip()
        for rgx, kind, fn in PASSIVE_RULES:
            if kind == "divine": continue   # 神业不会出现在必杀文本上
            m = rgx.search(text)
            if m:
                out.append((u.get("name","必杀"), fn(m), 1, kind))
                break
    return out

def classify_weakness(char: dict, skill_text: str):
    """返回该技能命中的 (武器列表, 属性列表)"""
    weapons, elems = set(), set()
    # 角色自身武器
    cw = (char.get("weakness") or {}).get("weapons") or []
    for w in cw:
        if w in WEAPONS: weapons.add(w)
    # 技能文本里显式提到的属性
    for e in ELEMENTS:
        if re.search(rf"{e}属性|\b{e}\b", skill_text):
            elems.add(e)
    # 技能文本里显式提到的武器
    for w in WEAPONS:
        if re.search(rf"{w}属性|{w}伤害", skill_text):
            weapons.add(w)
    return weapons, elems

def norm_name(s: str) -> str:
    return re.sub(r"\s+", "", (s or "")).strip()

def main():
    if not SRC.exists():
        print(f"[error] 未找到 {SRC}", file=sys.stderr); sys.exit(1)
    data = json.loads(SRC.read_text(encoding="utf-8"))
    chars = data.get("characters") or data  # 兼容两种结构

    # bucket[cat] -> dict[(char,skill,kind)] = entry  (天然去重, 同key保留最大)
    bucket = defaultdict(dict)

    for ch in chars:
        name = ch.get("name") or ch.get("title")
        if not name: continue
        details = ch.get("details") or ch
        actives    = details.get("activeSkills")  or details.get("active")   or []
        ultimates  = details.get("ultimateSkills") or details.get("ultimate") or []
        passives   = details.get("passiveSkills") or details.get("passive")  or []

        passive_mults = collect_passive_mults(passives, ultimates)
        passive_factor = 1.0
        passive_labels = []
        max_turn = 0
        for label, mult, turn, kind in passive_mults:
            passive_factor *= mult
            passive_labels.append(f"{label}(×{mult:g}{'/常驻' if turn==0 else f'/启动{turn}回合'})")
            max_turn = max(max_turn, turn)

        for skill_list, skill_kind in [(actives,"active"),(ultimates,"ultimate")]:
            for sk in skill_list:
                sk_name = sk.get("name","")
                effect  = (sk.get("effect","") + " " + sk.get("bpEffect","")).strip()
                if not is_attack_skill(sk_name, effect): continue
                base = parse_skill_base(sk)
                if not base: continue
                power, hits, text = base
                base_mult = power * hits
                final = base_mult * passive_factor

                weapons, elems = classify_weakness(ch, text)
                # 兜底: 主动近战默认带角色第一个武器
                if not weapons and skill_kind=="active" and (ch.get("weakness",{}).get("weapons")):
                    weapons.add(ch["weakness"]["weapons"][0])

                entry = {
                    "character": name,
                    "avatar": ch.get("avatar"),
                    "job": ch.get("job"),
                    "skill": sk_name,
                    "kind": skill_kind,
                    "power": power, "hits": hits,
                    "base": base_mult,
                    "passiveFactor": int(passive_factor) if passive_factor == int(passive_factor) else round(passive_factor, 2),
                    "passiveLabels": passive_labels,
                    "final": round(final, 1),
                    "turnCost": max_turn,
                    "effect": text[:200],
                }
                # 去重 key: 不区分 active/ultimate, 同技能整库只留一条
                dedup_key = (name, norm_name(sk_name))

                for w in weapons:
                    cat = f"weapon:{w}"
                    cur = bucket[cat].get(dedup_key)
                    if (not cur) or entry["final"] > cur["final"]:
                        bucket[cat][dedup_key] = entry
                for e in elems:
                    cat = f"element:{e}"
                    cur = bucket[cat].get(dedup_key)
                    if (not cur) or entry["final"] > cur["final"]:
                        bucket[cat][dedup_key] = entry

    # 排序 + Top 20 + 重新写 rank
    rankings = {}
    for cat, dct in bucket.items():
        items = sorted(dct.values(), key=lambda x: x["final"], reverse=True)[:20]
        for i, it in enumerate(items, 1):
            it["rank"] = i          # 关键: 写回真实名次
        rankings[cat] = items

    out = {
        "schema": "skill_rankings.v2",
        "generatedAt": data.get("fetchedAt"),
        "weapons": WEAPONS,
        "elements": ELEMENTS,
        "rankings": rankings,
    }
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] 写入 {DST}")
    # Quick check
    for w in WEAPONS:
        top = rankings.get(f"weapon:{w}", [])[:3]
        print(f"  {w}榜 Top3:", [(t['rank'], t['character'], t['skill'], t['final']) for t in top])
    for e in ELEMENTS:
        top = rankings.get(f"element:{e}", [])[:3]
        print(f"  {e}榜 Top3:", [(t['rank'], t['character'], t['skill'], t['final']) for t in top])

if __name__ == "__main__":
    main()
