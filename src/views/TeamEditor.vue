<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTeamsStore } from '@/stores/teams'
import { useCharactersStore } from '@/stores/characters'
import TeamSlot from '@/components/TeamSlot.vue'
import CharacterPicker from '@/components/CharacterPicker.vue'
import SlotEditDialog from '@/components/SlotEditDialog.vue'
import { ElMessage } from 'element-plus'
import { Back, Check } from '@element-plus/icons-vue'
import type { TeamSlot as TeamSlotType } from '@/types/team'

const route = useRoute()
const router = useRouter()
const teams = useTeamsStore()
const charactersStore = useCharactersStore()

const teamId = computed(() => route.params.id as string)
const team = computed(() => teams.teams.find((t) => t.id === teamId.value) ?? null)
const resolved = computed(() => (team.value ? teams.resolve(team.value) : null))

const allPickedIds = computed(() => {
  if (!team.value) return []
  return [...team.value.front, ...team.value.back]
    .map((s) => s.characterId)
    .filter((x): x is string => !!x)
})

// === 角色选择器 ===
const pickerOpen = ref(false)
const pickingSlot = ref<{ row: 'front' | 'back'; index: number } | null>(null)

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

// === 槽位编辑弹窗 ===
const editOpen = ref(false)
const editing = ref<{ row: 'front' | 'back'; index: number } | null>(null)

const editingSlot = computed<TeamSlotType | null>(() => {
  if (!editing.value || !team.value) return null
  return team.value[editing.value.row][editing.value.index]
})
const editingChar = computed(() =>
  charactersStore.findById(editingSlot.value?.characterId ?? null),
)

function handleSlotClick(row: 'front' | 'back', index: number) {
  if (!team.value) return
  const slot = team.value[row][index]
  if (slot.characterId) {
    // 已有角色 → 打开编辑弹窗
    editing.value = { row, index }
    editOpen.value = true
  } else {
    // 空位 → 直接打开选择器
    openPicker(row, index)
  }
}

function clearSlot(row: 'front' | 'back', index: number) {
  if (!team.value) return
  teams.placeCharacter(team.value.id, row, index, null)
}

function saveEdit(patch: Partial<TeamSlotType>) {
  if (!editing.value || !team.value) return
  const { row, index } = editing.value
  // 直接合并到响应式 slot 对象
  Object.assign(team.value[row][index], patch)
  teams.touch(team.value.id)
  ElMessage.success('已保存')
}

function switchFromEdit() {
  if (!editing.value) return
  openPicker(editing.value.row, editing.value.index)
}

function clearFromEdit() {
  if (!editing.value) return
  clearSlot(editing.value.row, editing.value.index)
  ElMessage.success('已清空')
}

// === 自动保存反馈 ===
const savedAt = ref<number | null>(null)
let saveTimer: ReturnType<typeof setTimeout> | null = null
watch(
  () => team.value && JSON.stringify({ name: team.value.name, tags: team.value.tags, desc: team.value.description }),
  () => {
    if (!team.value) return
    if (saveTimer) clearTimeout(saveTimer)
    saveTimer = setTimeout(() => {
      teams.touch(team.value!.id)
      savedAt.value = Date.now()
    }, 500)
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
          placeholder="添加标签"
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
      <div class="hint">
        💡 点击空位添加角色，点击已有角色可编辑等级/觉醒/HP/SP
      </div>

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
              @click="handleSlotClick('front', i)"
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
              @click="handleSlotClick('back', i)"
              @clear="clearSlot('back', i)"
            />
          </div>
        </section>
      </div>

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

    <!-- 角色选择器 -->
    <CharacterPicker
      v-model="pickerOpen"
      :already-picked-ids="allPickedIds"
      @pick="onPick"
    />

    <!-- 槽位编辑弹窗 -->
    <SlotEditDialog
      v-if="editing"
      v-model="editOpen"
      :slot="editingSlot"
      :character="editingChar"
      :row="editing.row"
      :index="editing.index"
      @save="saveEdit"
      @switch="switchFromEdit"
      @clear="clearFromEdit"
    />
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
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

.hint {
  color: var(--jrpg-text-muted);
  font-size: 12px;
  margin-bottom: 16px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.25);
  border-left: 2px solid var(--jrpg-border-gold);
  border-radius: 2px;
}

.editor {
  display: flex;
  flex-direction: column;
  gap: 28px;
}
.dual-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.column {
  background:
    linear-gradient(180deg, rgba(0, 0, 0, 0.3), transparent 30%),
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
.empty {
  text-align: center;
  padding: 60px;
  color: var(--jrpg-text-soft);
}
@media (max-width: 900px) {
  .dual-column {
    grid-template-columns: 1fr;
  }
}
</style>
