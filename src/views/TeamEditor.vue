<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTeamsStore } from '@/stores/teams'
import TeamSlot from '@/components/TeamSlot.vue'
import CharacterPicker from '@/components/CharacterPicker.vue'
import { ElMessage } from 'element-plus'
import { Back, Check } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const teams = useTeamsStore()

const teamId = computed(() => route.params.id as string)
const team = computed(() => teams.teams.find((t) => t.id === teamId.value) ?? null)

const pickerOpen = ref(false)
const pickingSlot = ref<{ row: 'front' | 'back'; index: number } | null>(null)

const resolved = computed(() => (team.value ? teams.resolve(team.value) : null))

const allPickedIds = computed(() => {
  if (!team.value) return []
  return [...team.value.front, ...team.value.back]
    .map((s) => s.characterId)
    .filter((x): x is string => !!x)
})

function openPicker(row: 'front' | 'back', index: number) {
  pickingSlot.value = { row, index }
  pickerOpen.value = true
}

function onPick(char: { id: string }) {
  if (!pickingSlot.value || !team.value) return
  teams.placeCharacter(
    team.value.id,
    pickingSlot.value.row,
    pickingSlot.value.index,
    char.id,
  )
  pickingSlot.value = null
}

function clearSlot(row: 'front' | 'back', index: number) {
  if (!team.value) return
  teams.placeCharacter(team.value.id, row, index, null)
}

// 自动保存反馈
const savedAt = ref<number | null>(null)
function markSaved() {
  if (!team.value) return
  teams.touch(team.value.id)
  savedAt.value = Date.now()
}

// 监听变化，节流提示
let saveTimer: ReturnType<typeof setTimeout> | null = null
watch(
  () => team.value && JSON.stringify(team.value),
  () => {
    if (saveTimer) clearTimeout(saveTimer)
    saveTimer = setTimeout(markSaved, 400)
  },
)

const savedHint = computed(() => {
  if (!savedAt.value) return ''
  const diff = Date.now() - savedAt.value
  if (diff < 3000) return '已自动保存'
  return ''
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <el-button :icon="Back" @click="router.push('/teams')">返回</el-button>
      <template v-if="team">
        <el-input
          v-model="team.name"
          class="name-input"
          placeholder="阵容名称"
        />
        <el-select
          v-model="team.tags"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="添加标签（可自由输入）"
          class="tag-select"
          :reserve-keyword="false"
        >
          <el-option label="周本" value="周本" />
          <el-option label="试炼" value="试炼" />
          <el-option label="主线" value="主线" />
          <el-option label="推图" value="推图" />
          <el-option label="速通" value="速通" />
        </el-select>
        <transition name="fade">
          <span v-if="savedHint" class="saved-hint">
            <el-icon><Check /></el-icon> {{ savedHint }}
          </span>
        </transition>
      </template>
    </header>

    <div v-if="!team" class="empty">
      <p>没有找到这个阵容，可能已被删除。</p>
      <el-button @click="router.push('/teams')">返回列表</el-button>
    </div>

    <div v-else-if="resolved" class="editor">
      <!-- 前后卫双列布局 -->
      <div class="dual-column">
        <section class="column jrpg-theme-front">
          <h3 class="jrpg-section-title front-title">前　卫</h3>
          <div class="slot-stack">
            <TeamSlot
              v-for="(rs, i) in resolved.front"
              :key="'f' + i"
              :slot="rs.slot"
              :character="rs.character"
              :label="'前卫 ' + (i + 1)"
              row="front"
              @click="openPicker('front', i)"
              @clear="clearSlot('front', i)"
            />
          </div>
        </section>

        <section class="column jrpg-theme-back">
          <h3 class="jrpg-section-title back-title">后　卫</h3>
          <div class="slot-stack">
            <TeamSlot
              v-for="(rs, i) in resolved.back"
              :key="'b' + i"
              :slot="rs.slot"
              :character="rs.character"
              :label="'后卫 ' + (i + 1)"
              row="back"
              @click="openPicker('back', i)"
              @clear="clearSlot('back', i)"
            />
          </div>
        </section>
      </div>

      <!-- 备注 -->
      <section class="notes-section">
        <h3 class="jrpg-section-title">备　注</h3>
        <el-input
          v-model="team.description"
          type="textarea"
          :rows="4"
          placeholder="攻略思路、技能时序、注意事项……"
        />
      </section>
    </div>

    <CharacterPicker
      v-model="pickerOpen"
      :already-picked-ids="allPickedIds"
      @pick="onPick"
    />
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
}
.name-input {
  width: 240px;
}
.tag-select {
  width: 280px;
}
.saved-hint {
  color: var(--jrpg-hp);
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.editor {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 双列布局 */
.dual-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.column {
  background:
    linear-gradient(
      180deg,
      rgba(0, 0, 0, 0.3),
      transparent 30%
    ),
    var(--jrpg-bg-base);
  border: 1px solid var(--jrpg-border);
  border-top: 2px solid var(--row-color);
  border-radius: 4px;
  padding: 8px 12px 14px;
  box-shadow: var(--jrpg-shadow-inset);
}
.front-title {
  color: #f5a89c !important;
  text-shadow: 0 0 8px rgba(200, 68, 59, 0.5), 0 1px 2px rgba(0, 0, 0, 0.8) !important;
}
.front-title::before,
.front-title::after {
  background: linear-gradient(90deg, transparent, var(--jrpg-front), transparent) !important;
}
.back-title {
  color: #9cc5f5 !important;
  text-shadow: 0 0 8px rgba(59, 109, 200, 0.5), 0 1px 2px rgba(0, 0, 0, 0.8) !important;
}
.back-title::before,
.back-title::after {
  background: linear-gradient(90deg, transparent, var(--jrpg-back), transparent) !important;
}
.slot-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.notes-section {
  max-width: 100%;
}
.empty {
  text-align: center;
  padding: 60px;
  color: var(--jrpg-text-soft);
}

/* 响应式：窄屏改单列 */
@media (max-width: 900px) {
  .dual-column {
    grid-template-columns: 1fr;
  }
}
</style>
