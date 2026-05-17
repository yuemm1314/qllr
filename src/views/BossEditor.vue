<script setup lang="ts">
import { computed, watch, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBossesStore } from '@/stores/bosses'
import { useTeamsStore } from '@/stores/teams'
import { Back, Check } from '@element-plus/icons-vue'
import type { WeaponType, ElementType } from '@/types/character'

const route = useRoute()
const router = useRouter()
const bosses = useBossesStore()
const teams = useTeamsStore()

const bossId = computed(() => route.params.id as string)
const boss = computed(() => bosses.findById(bossId.value))

const WEAPONS: WeaponType[] = ['剑', '枪', '短剑', '斧', '弓', '杖', '扇', '书']
const ELEMENTS: ElementType[] = ['火', '冰', '雷', '风', '光', '暗']

const teamOptions = computed(() =>
  teams.teams.map((t) => ({ value: t.id, label: t.name })),
)

const savedAt = ref<number | null>(null)
let saveTimer: ReturnType<typeof setTimeout> | null = null
watch(
  () => boss.value && JSON.stringify(boss.value),
  () => {
    if (!boss.value) return
    if (saveTimer) clearTimeout(saveTimer)
    saveTimer = setTimeout(() => {
      bosses.touch(boss.value!.id)
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
      <el-button :icon="Back" @click="router.push('/bosses')">返回</el-button>
      <template v-if="boss">
        <el-input
          v-model="boss.name"
          class="name-input"
          placeholder="Boss 名称"
        />
        <transition name="fade">
          <span v-if="savedHint" class="saved-hint">
            <el-icon><Check /></el-icon> {{ savedHint }}
          </span>
        </transition>
      </template>
    </header>

    <div v-if="!boss" class="empty">
      <p>没有找到这个 Boss 笔记。</p>
      <el-button @click="router.push('/bosses')">返回列表</el-button>
    </div>

    <div v-else class="editor">
      <!-- 弱点 -->
      <section class="section">
        <h3 class="jrpg-section-title">弱　点</h3>
        <div class="form-row">
          <label>武器弱点</label>
          <el-checkbox-group v-model="boss.weakWeapons" class="cbgrp">
            <el-checkbox-button
              v-for="w in WEAPONS"
              :key="w"
              :label="w"
              :value="w"
            >
              {{ w }}
            </el-checkbox-button>
          </el-checkbox-group>
        </div>
        <div class="form-row">
          <label>元素弱点</label>
          <el-checkbox-group v-model="boss.weakElements" class="cbgrp">
            <el-checkbox-button
              v-for="e in ELEMENTS"
              :key="e"
              :label="e"
              :value="e"
            >
              {{ e }}
            </el-checkbox-button>
          </el-checkbox-group>
        </div>
        <div class="form-row">
          <label>护盾值</label>
          <el-input-number
            v-model="boss.shield"
            :min="0"
            :max="999"
            placeholder="如 8"
            controls-position="right"
            style="width: 160px"
          />
          <span class="hint-text">破盾所需的耐性数</span>
        </div>
      </section>

      <!-- 机制 -->
      <section class="section">
        <h3 class="jrpg-section-title">机制 & 攻略</h3>
        <div class="sub-label">关键机制</div>
        <el-input
          v-model="boss.mechanics"
          type="textarea"
          :rows="3"
          placeholder="如：每 3 回合大招、HP 50% 召唤从者、倒计时减 BP……"
        />
        <div class="sub-label">个人攻略笔记</div>
        <el-input
          v-model="boss.notes"
          type="textarea"
          :rows="5"
          placeholder="自己的打法记录、关键技能时序、注意事项……"
        />
      </section>

      <!-- 关联阵容 -->
      <section class="section">
        <h3 class="jrpg-section-title">关联阵容</h3>
        <el-select
          v-model="boss.relatedTeamIds"
          multiple
          filterable
          placeholder="选择能打这个 Boss 的阵容"
          style="width: 100%"
        >
          <el-option
            v-for="opt in teamOptions"
            :key="opt.value"
            :value="opt.value"
            :label="opt.label"
          />
        </el-select>
        <div v-if="!teams.teams.length" class="hint-text">
          还没有阵容，先去「我的阵容」创建一些
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.name-input {
  width: 260px;
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
  gap: 28px;
  max-width: 900px;
}
.section {
  background:
    linear-gradient(180deg, rgba(0, 0, 0, 0.25), transparent 30%),
    var(--jrpg-bg-base);
  border: 1px solid var(--jrpg-border);
  border-top: 2px solid var(--jrpg-border-gold);
  border-radius: 4px;
  padding: 8px 16px 16px;
}
.form-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  flex-wrap: wrap;
}
.form-row label {
  width: 80px;
  flex-shrink: 0;
  color: var(--jrpg-text-soft);
  font-size: 13px;
  text-align: right;
}
.cbgrp {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.sub-label {
  margin: 14px 0 6px;
  font-size: 12px;
  color: var(--jrpg-text-muted);
  letter-spacing: 1px;
}
.hint-text {
  font-size: 12px;
  color: var(--jrpg-text-muted);
}
.empty {
  text-align: center;
  padding: 60px;
  color: var(--jrpg-text-soft);
}
</style>
