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
      <h2>角色库</h2>
      <div class="header-right">
        <el-input
          v-model="keyword"
          placeholder="搜索角色名 / 技能名…"
          clearable
          style="width: 280px"
        />
      </div>
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

    <el-dialog v-model="detailVisible" :title="selected?.name" width="600px">
      <div v-if="selected" class="detail">
        <div class="detail-head">
          <el-image :src="selected.avatar" class="detail-avatar" fit="cover">
            <template #error>
              <div class="fallback">{{ selected.name.slice(0, 2) }}</div>
            </template>
          </el-image>
          <div>
            <h3 style="margin: 0 0 8px">{{ selected.name }}</h3>
            <el-button v-if="selected.wikiPath" size="small" @click="openWiki(selected)">
              在 Wiki 中查看
            </el-button>
          </div>
        </div>
        <el-divider>主动技能（{{ selected.activeSkills.length }}）</el-divider>
        <div class="skill-list">
          <el-tag
            v-for="(s, i) in selected.activeSkills"
            :key="i"
            size="large"
            class="skill-tag"
          >
            {{ s }}
          </el-tag>
        </div>
        <div v-if="!selected.activeSkills.length" class="empty">
          没有技能数据，请运行爬虫更新
        </div>
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
.page-header h2 {
  margin: 0;
}
.stats {
  color: var(--color-text-secondary);
  margin-bottom: 16px;
  font-size: 14px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}
.detail-head {
  display: flex;
  gap: 16px;
  align-items: center;
}
.detail-avatar {
  width: 88px;
  height: 88px;
  border-radius: 8px;
}
.fallback {
  width: 100%;
  height: 100%;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}
.skill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.skill-tag {
  font-size: 14px;
}
.empty {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 20px;
}
</style>
