<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { Character } from '@/types/character'
import type { TeamSlot } from '@/types/team'
import { Refresh, Delete } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: boolean
  slot: TeamSlot | null
  character: Character | null
  row: 'front' | 'back'
  index: number
}>()

const emit = defineEmits<{
  'update:modelValue': [v: boolean]
  /** 保存编辑后的 slot 字段（characterId 不变） */
  save: [patch: Partial<TeamSlot>]
  /** 请求切换角色（打开角色选择器） */
  switch: []
  /** 清空槽位 */
  clear: []
}>()

// 本地草稿，避免编辑过程中实时改外部状态
const draft = ref<TeamSlot>({
  characterId: null,
  level: undefined,
  awakening: undefined,
  hp: undefined,
  hpMax: undefined,
  sp: undefined,
  spMax: undefined,
})

watch(
  () => [props.modelValue, props.slot],
  () => {
    if (props.modelValue && props.slot) {
      draft.value = { ...props.slot }
    }
  },
  { immediate: true },
)

function close() {
  emit('update:modelValue', false)
}
function onSave() {
  emit('save', { ...draft.value })
  close()
}
function onSwitch() {
  emit('switch')
  close()
}
function onClear() {
  emit('clear')
  close()
}

const title = computed(() => {
  const place = props.row === 'front' ? '前卫' : '后卫'
  return `${place} ${props.index + 1} · ${props.character?.name ?? '空位'}`
})

// 快捷设置：体力/精力填满
function fillHp() {
  if (draft.value.hpMax) draft.value.hp = draft.value.hpMax
}
function fillSp() {
  if (draft.value.spMax) draft.value.sp = draft.value.spMax
}
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    :title="title"
    width="460px"
    align-center
  >
    <template v-if="character">
      <div class="head">
        <el-image :src="character.avatar" fit="contain" class="head-avatar">
          <template #error>
            <div class="fb">{{ character.name.slice(0, 2) }}</div>
          </template>
        </el-image>
        <div class="head-info">
          <div class="head-name">{{ character.name }}</div>
          <div class="head-skills">主动技能 {{ character.activeSkills.length }} 个</div>
        </div>
      </div>

      <el-divider>个 人 配 置</el-divider>

      <div class="form">
        <div class="form-row">
          <label>等级</label>
          <el-input-number
            v-model="draft.level"
            :min="1"
            :max="200"
            :step="10"
            placeholder="如 120"
            controls-position="right"
            style="width: 140px"
          />
        </div>

        <div class="form-row">
          <label>觉醒</label>
          <el-rate
            v-model="(draft.awakening as number)"
            :max="5"
            :colors="['#f1c652', '#f1c652', '#f1c652']"
            void-color="#3a2a18"
            allow-half="false"
            clearable
          />
          <span class="muted">{{ draft.awakening ?? 0 }} / 5</span>
        </div>

        <div class="form-row two-input">
          <label>HP</label>
          <el-input-number
            v-model="draft.hp"
            :min="0"
            :max="draft.hpMax ?? 999999"
            placeholder="当前"
            controls-position="right"
            style="width: 120px"
          />
          <span class="sep">/</span>
          <el-input-number
            v-model="draft.hpMax"
            :min="0"
            :max="999999"
            placeholder="最大"
            controls-position="right"
            style="width: 120px"
          />
          <el-button size="small" link @click="fillHp" :disabled="!draft.hpMax">
            填满
          </el-button>
        </div>

        <div class="form-row two-input">
          <label>SP</label>
          <el-input-number
            v-model="draft.sp"
            :min="0"
            :max="draft.spMax ?? 999999"
            placeholder="当前"
            controls-position="right"
            style="width: 120px"
          />
          <span class="sep">/</span>
          <el-input-number
            v-model="draft.spMax"
            :min="0"
            :max="999999"
            placeholder="最大"
            controls-position="right"
            style="width: 120px"
          />
          <el-button size="small" link @click="fillSp" :disabled="!draft.spMax">
            填满
          </el-button>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="footer">
        <div class="footer-left">
          <el-button :icon="Refresh" @click="onSwitch">切换角色</el-button>
          <el-button :icon="Delete" type="danger" @click="onClear">清空</el-button>
        </div>
        <div class="footer-right">
          <el-button @click="close">取消</el-button>
          <el-button type="primary" @click="onSave">保存</el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.head {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 4px 0 8px;
}
.head-avatar {
  width: 64px;
  height: 64px;
  border-radius: 4px;
  border: 1px solid var(--jrpg-border-gold);
  background: radial-gradient(circle, #3a2a18, var(--jrpg-bg-deep));
}
.fb {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--jrpg-text-muted);
}
.head-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: var(--jrpg-text-gold);
}
.head-skills {
  font-size: 12px;
  color: var(--jrpg-text-muted);
  margin-top: 4px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.form-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.form-row label {
  width: 50px;
  flex-shrink: 0;
  color: var(--jrpg-text-soft);
  font-size: 13px;
  text-align: right;
}
.form-row.two-input {
  flex-wrap: wrap;
}
.sep {
  color: var(--jrpg-text-muted);
}
.muted {
  color: var(--jrpg-text-muted);
  font-size: 12px;
  font-family: 'Cinzel', monospace;
}

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.footer-left {
  display: flex;
  gap: 8px;
}
.footer-right {
  display: flex;
  gap: 8px;
}
</style>
