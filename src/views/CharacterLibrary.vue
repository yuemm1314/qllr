<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCharactersStore } from '@/stores/characters'
import CharacterCard from '@/components/CharacterCard.vue'
import type { Character } from '@/types/character'

const characters = useCharactersStore()
const keyword = ref('')
const selected = ref<Character | null>(null)
const detailVisible = ref(false)

const filtered = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return characters.list
  return characters.list.filter(
    (c) =>
      c.name.toLowerCase().includes(kw) ||
      c.activeSkills.some((s) => s.toLowerCase().includes(kw)),
  )
})

function openDetail(c: Character) {
  selected.value = c
  detailVisible.value = true
}

function openWiki(c: Character) {
  if (c.wikiPath) {
    window.open('https://wiki.biligame.com' + c.wikiPath, '_blank')
  }
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">⚔ 角 色 库</h2>
      <el-input
        v-model="keyword"
        placeholder="搜索角色名 / 技能名…"
        clearable
        style="width: 280px"
      />
    </header>

    <div class="stats">
      共 <b>{{ filtered.length }}</b> / {{ characters.list.length }} 个角色
    </div>

    <div class="grid">
      <CharacterCard
        v-for="c in filtered"
        :key="c.id"
        :character="c"
        clickable
        @click="openDetail"
      />
    </div>

    <el-dialog
      v-model="detailVisible"
      :title="selected?.name"
      width="560px"
      align-center
    >
      <div v-if="selected" class="detail">
        <div class="detail-head">
          <div class="big-portrait-wrap">
            <el-image :src="selected.avatar" class="big-portrait" fit="contain">
              <template #error>
                <div class="fallback">{{ selected.name.slice(0, 2) }}</div>
              </template>
            </el-image>
          </div>
          <div class="detail-meta">
            <h3 class="detail-name">{{ selected.name }}</h3>
            <p class="detail-id">{{ selected.id }}</p>
            <el-button v-if="selected.wikiPath" size="small" @click="openWiki(selected)">
              在 Wiki 中查看 ↗
            </el-button>
          </div>
        </div>
        <el-divider>主 动 技 能（{{ selected.activeSkills.length }}）</el-divider>
        <div v-if="selected.activeSkills.length" class="skill-list">
          <div v-for="(s, i) in selected.activeSkills" :key="i" class="skill-item">
            <span class="skill-num">{{ String(i + 1).padStart(2, '0') }}</span>
            <span class="skill-name">{{ s }}</span>
          </div>
        </div>
        <div v-else class="empty">没有技能数据，请运行爬虫更新</div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.page-title {
  margin: 0;
  font-family: 'Noto Serif SC', serif;
  letter-spacing: 4px;
  color: var(--jrpg-text-gold);
  font-size: 24px;
  text-shadow: 0 0 12px rgba(241, 198, 82, 0.3), 0 2px 4px rgba(0, 0, 0, 0.6);
}
.stats {
  color: var(--jrpg-text-soft);
  margin-bottom: 16px;
  font-size: 13px;
}
.stats b {
  color: var(--jrpg-text-gold);
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
}
.detail-head {
  display: flex;
  gap: 16px;
  align-items: center;
}
.big-portrait-wrap {
  width: 120px;
  height: 120px;
  border: 1px solid var(--jrpg-border-gold);
  border-radius: 4px;
  background:
    radial-gradient(circle, #3a2a18, var(--jrpg-bg-deep));
  flex-shrink: 0;
  padding: 4px;
}
.big-portrait {
  width: 100%;
  height: 100%;
}
.fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--jrpg-text-muted);
}
.detail-meta {
  flex: 1;
}
.detail-name {
  margin: 0 0 4px;
  font-family: 'Noto Serif SC', serif;
  color: var(--jrpg-text-gold);
  font-size: 20px;
}
.detail-id {
  margin: 0 0 12px;
  font-size: 11px;
  color: var(--jrpg-text-muted);
  font-family: 'Cinzel', monospace;
}
.skill-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 6px;
}
.skill-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--jrpg-border);
  border-radius: 3px;
  transition: all 0.2s;
}
.skill-item:hover {
  border-color: var(--jrpg-border-gold);
  background: rgba(241, 198, 82, 0.05);
}
.skill-num {
  font-family: 'Cinzel', monospace;
  font-size: 11px;
  color: var(--jrpg-text-muted);
}
.skill-name {
  font-size: 13px;
  color: var(--jrpg-text);
}
.empty {
  text-align: center;
  color: var(--jrpg-text-muted);
  padding: 20px;
}
</style>
