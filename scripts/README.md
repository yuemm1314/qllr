# 数据爬虫

从中文 Wiki 抓取角色与技能数据，输出到 `../src/data/*.json`。

## 用法（Windows PowerShell）

```powershell
cd scripts
python -m venv .venv
.venv\Scripts\pip install requests beautifulsoup4

# 抓角色头像（输出到 src/data/wiki_avatars.json）
.venv\Scripts\python scrape_avatars.py

# 抓技能（依赖上一步的产物，输出到 src/data/wiki_active_skills_zh.json）
.venv\Scripts\python scrape_skills.py
