<!-- src/views/CharacterLibrary.vue -->
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useCharactersStore } from '@/stores/characters';
import {
  WEAPON_LABEL, ELEMENT_LABEL, ELEMENT_COLOR,
  INFLUENCE_LABEL, STAT_LABEL,
} from '@/data/labels';
import type { Character, SkillDetail } from '@/types/character';

const store = useCharactersStore();
const keyword = ref('');
const selected = ref<Character | null>(null);
const activeSkillTab = ref<'active' | 'passive' | 'ultimate'>('active');

onMounted(() => store.load());

const filtered = computed(() => {
  const k = keyword.value.trim().toLowerCase();
  if (!k) return store.characters;
  return store.characters.filter((c) => {
    if (c.name.toLowerCase().includes(k)) return true;
    if (c.job?.toLowerCase().includes(k)) return true;
    const skills = c.details?.skills;
    if (skills) {
      const all = [...skills.active, ...skills.passive, ...skills.ultimate];
      if (all.some((s) => s.name.toLowerCase().includes(k))) return true;
    }
    return false;
  });
});

function openDetail(c: Character) {
  selected.value = c;
  activeSkillTab.value = 'active';
}

const STAT_ORDER: Array<keyof typeof STAT_LABEL> = [
  'hp', 'sp', 'patk', 'pdef', 'eatk', 'edef', 'crit', 'spd',
];

function currentSkills(): SkillDetail[] {
  const s = selected.value?.details?.skills;
  if (!s) return [];
  return s[activeSkillTab.value] || [];
}
</script>

<template>
  <div class="char-lib">
    <div class="lib-header">
      <h2>✦ 角色库</h2>
      <div class="header-meta">
        共 {{ store.total }} 个角色 · 已收录详情 {{ store.detailedCount }}
      </div>
      <el-input
        v-model="keyword"
        placeholder="搜索角色名 / 职业 / 技能名…"
        clearable
        style="max-width: 320px"
      />
    </div>

    <div class="grid">
      <div
        v-for="c in filtered"
        :key="c.name"
        class="card"
        :class="{ 'card-detailed': c.details }"
        @click="openDetail(c)"
      >
        <div class="avatar-wrap">
          <img v-if="c.avatar" :src="c.avatar" :alt="c.name" loading="lazy" />
          <div v-else class="avatar-placeholder">无</div>
        </div>
        <div class="card-body">
          <div class="name">{{ c.name }}</div>
          <div class="meta">
            <span class="job">{{ c.job }}</span>
            <span v-if="c.rarity" class="rarity">★{{ c.rarity }}</span>
          </div>
          <div class="weak-row">
            <span
              v-for="w in c.weakness.weapons"
              :key="'w' + w"
              class="badge weak-weapon"
            >{{ WEAPON_LABEL[w] }}</span>
            <span
              v-for="e in c.weakness.elements"
              :key="'e' + e"
              class="badge weak-element"
              :style="{ borderColor: ELEMENT_COLOR[e], color: ELEMENT_COLOR[e] }"
            >{{ ELEMENT_LABEL[e] }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      :model-value="!!selected"
      @update:model-value="(v) => !v && (selected = null)"
      :title="selected?.name"
      width="720px"
      append-to-body
      class="char-detail-dialog"
    >
      <template v-if="selected">
        <div class="detail-head">
          <img v-if="selected.avatar" :src="selected.avatar" class="detail-avatar" />
          <div class="detail-info">
            <div class="row">
              <span class="label">职业：</span>{{ selected.job }}
              <span class="sep">|</span>
              <span class="label">星级：</span>★{{ selected.rarity }}
            </div>
            <div class="row" v-if="selected.influence">
              <span class="label">影响力：</span>
              {{ INFLUENCE_LABEL[selected.influence] }}（{{ selected.influenceText }}）
            </div>
            <div class="row">
              <span class="label">突破弱点：</span>
              <span
                v-for="w in selected.weakness.weapons"
                :key="'dw' + w"
                class="badge weak-weapon"
              >{{ WEAPON_LABEL[w] }}</span>
              <span
                v-for="e in selected.weakness.elements"
                :key="'de' + e"
                class="badge weak-element"
                :style="{ borderColor: ELEMENT_COLOR[e], color: ELEMENT_COLOR[e] }"
              >{{ ELEMENT_LABEL[e] }}</span>
            </div>
            <div class="row" v-if="selected.cnReleaseDate">
              <span class="label">国服实装：</span>{{ selected.cnReleaseDate }}
            </div>
            <div class="row">
              <a
                v-if="selected.wikiUrl"
                :href="selected.wikiUrl"
                target="_blank"
                class="wiki-link"
              >在 Wiki 中查看 ↗</a>
            </div>
          </div>
        </div>

        <!-- MAX 属性 -->
        <h3 class="section-title">MAX 属性（6 星 120 级）</h3>
        <template v-if="selected.details?.maxStats">
          <div class="stat-grid">
            <div
              v-for="k in STAT_ORDER"
              :key="k"
              class="stat-cell"
            >
              <div class="stat-label">{{ STAT_LABEL[k] }}</div>
              <div class="stat-value">
                {{ selected.details.maxStats[k] ?? '—' }}
              </div>
            </div>
          </div>
        </template>
        <div v-else class="empty-tip">
          此角色详情尚未爬取。运行：
          <code>python scripts\scrape_detail.py --force {{ selected.name }}</code>
        </div>

        <!-- 技能 -->
        <template v-if="selected.details">
          <h3 class="section-title">技能</h3>
          <div class="skill-tabs">
            <button
              v-for="tab in (['active','passive','ultimate'] as const)"
              :key="tab"
              :class="{ active: activeSkillTab === tab }"
              @click="activeSkillTab = tab"
            >
              {{ tab === 'active' ? '主动'
                : tab === 'passive' ? '被动'
                : '必杀 & EX' }}
              <span class="count">
                {{ selected.details.skills[tab].length }}
              </span>
            </button>
          </div>
          <div class="skill-list">
            <div
              v-for="(s, idx) in currentSkills()"
              :key="idx"
              class="skill-item"
            >
              <div class="skill-head">
                <span class="skill-name">{{ s.name }}</span>
                <span v-if="s.cost" class="skill-cost">{{ s.cost }}</span>
              </div>
              <pre class="skill-effect">{{ s.effect }}</pre>
              <div v-if="s.bpEffect" class="skill-extra">
                <span class="label">BP 加成：</span>{{ s.bpEffect }}
              </div>
              <div v-if="s.enhanceEffect" class="skill-extra">
                <span class="label">能力强化：</span>{{ s.enhanceEffect }}
              </div>
            </div>
          </div>
        </template>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.char-lib { padding: 16px 20px; }
.lib-header {
  display: flex; align-items: center; gap: 16px;
  margin-bottom: 16px; flex-wrap: wrap;
}
.lib-header h2 { color: var(--jrpg-gold, #d4b06a); margin: 0; }
.header-meta { color: var(--jrpg-text-dim, #aa9876); font-size: 13px; }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 10px;
}
.card {
  background: var(--jrpg-bg-card, #2b2218);
  border: 1px solid var(--jrpg-border, #5a4632);
  border-radius: 6px;
  padding: 8px;
  cursor: pointer;
  transition: transform .12s, border-color .12s;
  display: flex; gap: 8px; align-items: center;
}
.card:hover {
  transform: translateY(-2px);
  border-color: var(--jrpg-gold, #d4b06a);
}
.card-detailed { border-left: 3px solid var(--jrpg-gold, #d4b06a); }

.avatar-wrap {
  width: 56px; height: 56px; flex-shrink: 0;
  background: #1a140d;
  border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
.avatar-wrap img { width: 100%; height: 100%; object-fit: contain; }
.avatar-placeholder { color: #555; font-size: 12px; }

.card-body { flex: 1; min-width: 0; }
.name {
  color: var(--jrpg-text, #e9d8b3);
  font-weight: 600; font-size: 14px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.meta { font-size: 12px; color: var(--jrpg-text-dim, #aa9876); margin: 2px 0; }
.meta .rarity { color: var(--jrpg-gold, #d4b06a); margin-left: 6px; }
.weak-row { display: flex; flex-wrap: wrap; gap: 3px; margin-top: 4px; }

.badge {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 11px;
  border: 1px solid;
  line-height: 1.5;
}
.weak-weapon { border-color: #8a6f47; color: #d4b06a; background: #1f1810; }
.weak-element { background: transparent; }

/* dialog */
.detail-head { display: flex; gap: 14px; align-items: flex-start; }
.detail-avatar {
  width: 120px; height: 120px; object-fit: contain;
  background: #1a140d; border-radius: 4px; padding: 4px;
}
.detail-info { flex: 1; }
.detail-info .row {
  margin: 4px 0; font-size: 13px; color: var(--jrpg-text, #e9d8b3);
}
.detail-info .label { color: var(--jrpg-text-dim, #aa9876); margin-right: 4px; }
.detail-info .sep { margin: 0 8px; color: #5a4632; }
.wiki-link { color: var(--jrpg-gold, #d4b06a); text-decoration: underline; }

.section-title {
  color: var(--jrpg-gold, #d4b06a);
  font-size: 15px;
  margin: 20px 0 10px;
  border-bottom: 1px solid #5a4632;
  padding-bottom: 4px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}
.stat-cell {
  background: #1f1810;
  border: 1px solid #5a4632;
  border-radius: 4px;
  padding: 6px 8px;
  text-align: center;
}
.stat-label { color: #aa9876; font-size: 11px; }
.stat-value { color: #e9d8b3; font-size: 16px; font-weight: 600; }

.skill-tabs { display: flex; gap: 6px; margin-bottom: 10px; }
.skill-tabs button {
  background: #1f1810;
  border: 1px solid #5a4632;
  color: #aa9876;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.skill-tabs button.active {
  border-color: #d4b06a;
  color: #d4b06a;
  background: #2b2218;
}
.skill-tabs .count {
  margin-left: 4px; font-size: 11px; opacity: .7;
}

.skill-list { display: flex; flex-direction: column; gap: 8px; }
.skill-item {
  background: #1f1810;
  border: 1px solid #5a4632;
  border-radius: 4px;
  padding: 8px 10px;
}
.skill-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 4px;
}
.skill-name { color: #d4b06a; font-weight: 600; }
.skill-cost { color: #aa9876; font-size: 12px; }
.skill-effect {
  color: #e9d8b3;
  font-size: 12.5px;
  margin: 4px 0;
  white-space: pre-wrap;
  font-family: inherit;
}
.skill-extra {
  font-size: 12px; color: #c0a878; margin-top: 2px;
}
.skill-extra .label { color: #aa9876; }
.empty-tip {
  color: #aa9876; font-size: 13px; padding: 10px;
  background: #1f1810; border-radius: 4px;
}
.empty-tip code {
  background: #0f0c08; padding: 2px 6px; border-radius: 3px;
  color: #d4b06a; font-size: 12px;
}
</style>
