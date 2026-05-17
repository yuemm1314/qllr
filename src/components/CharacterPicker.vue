<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCharactersStore } from '@/stores/characters'
import type { Character } from '@/types/character'
import CharacterCard from './CharacterCard.vue'

const props = defineProps<{
  modelValue: boolean
  /** 已经在阵容里的角色 ID（会被高亮 / 标记） */
  alreadyPickedIds?: string[]
}>()

const emit = defineEmits<{
  'update:modelValue': [v: boolean]
  pick: [character: Character]
}>()

const characters = useCharactersStore()
const keyword = ref('')

const filtered = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return characters.list
  return characters.list.filter((c) => {
    if (c.name.toLowerCase().includes(kw)) return true
    if (c.activeSkills.some((s) => s.toLowerCase().includes(kw))) return true
    return false
  })
})

function close() {
  emit('update:modelValue', false)
}

function pick(c: Character) {
  emit('pick', c)
  close()
}
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="选择角色"
    width="80%"
    top="6vh"
    :close-on-click-modal="true"
  >
    <el-input
      v-model="keyword"
      placeholder="搜索角色名 / 技能名…"
      clearable
      style="margin-bottom: 16px"
      :prefix-icon="'Search'"
    />
    <div class="picker-grid">
      <div
        v-for="c in filtered"
        :key="c.id"
        class="picker-item"
        :class="{ picked: alreadyPickedIds?.includes(c.id) }"
      >
        <CharacterCard :character="c" compact clickable @click="pick" />
      </div>
    </div>
    <div v-if="!filtered.length" class="empty">没有匹配的角色</div>
    <template #footer>
      <span class="hint">共 {{ filtered.length }} / {{ characters.list.length }} 个</span>
      <el-button @click="close">关闭</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.picker-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 10px;
  max-height: 60vh;
  overflow-y: auto;
  padding: 4px;
}
.picker-item.picked {
  opacity: 0.45;
}
.empty {
  text-align: center;
  padding: 40px;
  color: var(--color-text-secondary);
}
.hint {
  float: left;
  color: var(--color-text-secondary);
  font-size: 13px;
}
</style>
