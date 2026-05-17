<script setup lang="ts">
import { computed, ref } from 'vue';
import { useCharactersStore } from '@/stores/characters';
import { WEAPON_LABEL, ELEMENT_LABEL, ELEMENT_COLOR } from '@/data/labels';
import type { SkillRankingsFile, RankingEntry } from '@/types/skillRanking';
import rankingData from '@/data/skill_rankings.json';

const store = useCharactersStore();
store.load();

const data = rankingData as unknown as SkillRankingsFile;

const WEAPONS = ['sword', 'spear', 'dagger', 'axe', 'bow', 'staff', 'book', 'fan'] as const;
const ELEMENTS = ['fire', 'ice', 'thunder', 'wind', 'light', 'dark'] as const;

const activeBucket = ref<string>('element:fire');
const typeFilter = ref<'all' | 'active' | 'ultimate'>('all');

const currentList = computed<RankingEntry[]>(() => {
  const all = data.rankings[activeBucket.value] || [];
  if (typeFilter.value === 'all') return all;
  return all.filter((e) => e.skillType === typeFilter.value);
});

const bucketLabel = computed(() => {
  const [kind, key] = activeBucket.value.split(':');
  if (kind === 'weapon') return `${WEAPON_LABEL[key as keyof typeof WEAPON_LABEL]} 武器`;
  return `${ELEMENT_LABEL[key as keyof typeof ELEMENT_LABEL]} 属性`;
});

function avatarOf(name: string) {
  return store.findByName(name)?.avatar;
}

function expandRow(row: RankingEntry, expandedRows: RankingEntry[]) {
  const idx = expandedRows.indexOf(row);
  if (idx >= 0) expandedRows.splice(idx, 1);
  else expandedRows.push(row);
}
const expandedRows = ref<RankingEntry[]>([]);
</script>

<template>
  <div class="rank-page">
    <div class="page-head">
      <h2>✦ 技能倍率排行榜</h2>
      <div class="meta">
        总计 {{ data.totalEntries }} 条攻击技能 · 生成于 {{ data.generatedAt }}
      </div>
    </div>

    <div class="bucket-bar">
      <div class="bucket-group">
        <span class="group-label">武器：</span>
        <button
          v-for="w in WEAPONS"
          :key="'w'+w"
          :class="{ active: activeBucket === `weapon:${w}` }"
          @click="activeBucket = `weapon:${w}`"
        >{{ WEAPON_LABEL[w] }}</button>
      </div>
      <div class="bucket-group">
        <span class="group-label">属性：</span>
        <button
          v-for="e in ELEMENTS"
          :key="'e'+e"
          :class="{ active: activeBucket === `element:${e}` }"
          :style="activeBucket === `element:${e}` ? { borderColor: ELEMENT_COLOR[e], color: ELEMENT_COLOR[e] } : {}"
          @click="activeBucket = `element:${e}`"
        >{{ ELEMENT_LABEL[e] }}</button>
      </div>
      <div class="bucket-group">
        <span class="group-label">类型：</span>
        <button :class="{ active: typeFilter==='all' }" @click="typeFilter='all'">全部</button>
        <button :class="{ active: typeFilter==='active' }" @click="typeFilter='active'">主动</button>
        <button :class="{ active: typeFilter==='ultimate' }" @click="typeFilter='ultimate'">必杀&EX</button>
      </div>
    </div>

    <h3 class="bucket-title">{{ bucketLabel }} · Top {{ currentList.length }}</h3>

    <el-table :data="currentList" size="small" border :row-class-name="() => 'rank-row'">
      <el-table-column label="#" width="60" align="center">
        <!-- 关键: 直接用 index+1, 不读 row.rank, 避免老数据残留 -->
        <template #default="{ $index }">{{ $index + 1 }}</template>
      </el-table-column>
      
      <el-table-column label="角色" width="160">
        <template #default="{ row }">
          <div class="cell-char">
            <el-avatar :size="28" :src="avatarOf(row.characterName)" />
            <span>{{ row.characterName }}</span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="skillName" label="技能" min-width="160" />
      
      <!-- 关键: 加宽到 110, nowrap 防止换行 -->
      <el-table-column label="类型" width="110" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="row.skillType==='ultimate' ? 'danger' : 'primary'"
                  style="white-space:nowrap">
            {{ row.skillType === 'ultimate' ? '必杀/EX' : '主动' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column label="威力×次数" width="110" align="center">
        <template #default="{ row }">{{ row.power }} × {{ row.hits }} = {{ row.baseMultiplier }}</template>
      </el-table-column>
      <el-table-column label="被动加成" width="100" align="center">
        <template #default="{ row }">×{{ row.buffMultiplier }}</template>
      </el-table-column>
      <el-table-column label="总倍率" width="110" align="center" sortable
                       :sort-method="(a,b)=>a.finalMultiplier-b.finalMultiplier">
        <template #default="{ row }">
          <b style="color:#e6a23c">{{ row.finalMultiplier }}</b>
        </template>
      </el-table-column>
      <el-table-column label="启动" width="80" align="center">
        <template #default="{ row }">
          {{ row.turnCost ? `${row.turnCost}回合` : '常驻' }}
        </template>
      </el-table-column>
    </el-table>

    <details class="rules-block">
      <summary>计算规则说明</summary>
      <ul>
        <li v-for="(v, k) in data.rules" :key="k"><b>{{ k }}：</b>{{ v }}</li>
      </ul>
    </details>
  </div>
</template>

<style scoped>
.rank-page { padding: 16px 20px; color: var(--jrpg-text, #e9d8b3); }
.page-head h2 { color: var(--jrpg-gold, #d4b06a); margin: 0 0 4px; }
.meta { color: var(--jrpg-text-dim, #aa9876); font-size: 12px; margin-bottom: 16px; }

.bucket-bar {
  display: flex; flex-direction: column; gap: 8px;
  background: #2b2218; border: 1px solid #5a4632;
  padding: 10px 12px; border-radius: 6px; margin-bottom: 14px;
}
.bucket-group { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.group-label { color: #aa9876; font-size: 13px; min-width: 48px; }
.bucket-bar button {
  background: #1f1810; border: 1px solid #5a4632;
  color: #aa9876; padding: 3px 12px; border-radius: 4px;
  cursor: pointer; font-size: 13px;
}
.bucket-bar button.active {
  border-color: #d4b06a; color: #d4b06a; background: #2b2218;
}

.bucket-title {
  color: #d4b06a; margin: 10px 0;
  border-bottom: 1px solid #5a4632; padding-bottom: 4px;
}

.cell-char {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-table) {
  --el-table-bg-color: #2b2218;
  --el-table-tr-bg-color: #2b2218;
  --el-table-row-hover-bg-color: #3a2d1f;
  --el-table-border-color: #5a4632;
  --el-table-text-color: #e9d8b3;
  --el-table-header-bg-color: #1f1810;
  --el-table-header-text-color: #d4b06a;
}

:deep(.el-table tr),
:deep(.el-table td.el-table__cell),
:deep(.el-table th.el-table__cell) {
  background-color: #2b2218 !important;
}

:deep(.el-table tbody tr:hover > td.el-table__cell) {
  background-color: #3a2d1f !important;
}

.empty { text-align: center; padding: 30px; color: #aa9876; }

.rules-block { margin-top: 18px; background: #1f1810; padding: 8px 12px; border-radius: 4px; }
.rules-block summary { color: #d4b06a; cursor: pointer; }
.rules-block ul { margin: 6px 0 0; padding-left: 18px; }
.rules-block li { font-size: 12px; color: #aa9876; margin: 2px 0; }
</style>
