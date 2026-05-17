<script setup lang="ts">
import { computed } from 'vue'
import type { Character } from '@/types/character'
import type { TeamSlot } from '@/types/team'
import { Plus, Close } from '@element-plus/icons-vue'

const props = defineProps<{
  slot: TeamSlot
  character: Character | null
  label?: string
  /** 'front' | 'back' 用于切换红蓝主题 */
  row: 'front' | 'back'
}>()

defineEmits<{
  click: []
  clear: []
}>()

const hpPct = computed(() => {
  if (!props.slot.hp || !props.slot.hpMax) return 100
  return Math.max(0, Math.min(100, (props.slot.hp / props.slot.hpMax) * 100))
})
const spPct = computed(() => {
  if (!props.slot.sp || !props.slot.spMax) return 100
  return Math.max(0, Math.min(100, (props.slot.sp / props.slot.spMax) * 100))
})
</script>

<template>
  <div
    class="slot"
    :class="[
      `jrpg-theme-${row}`,
      { filled: !!character, empty: !character },
    ]"
    @click="$emit('click')"
  >
    <!-- 左侧装饰条（红/蓝） -->
    <div class="side-bar"></div>

    <template v-if="character">
      <!-- 头像 -->
      <div class="portrait-wrap">
        <el-image :src="character.avatar" class="portrait" fit="cover" loading="lazy">
          <template #error>
            <div class="portrait-fallback">{{ character.name.slice(0, 2) }}</div>
          </template>
        </el-image>
      </div>

      <!-- 中央信息 -->
      <div class="info">
        <div class="info-top">
          <span class="name">{{ character.name }}</span>
          <span class="stars">
            {{ '★'.repeat(slot.awakening ?? 0) }}{{ '☆'.repeat(5 - (slot.awakening ?? 0)) }}
          </span>
        </div>
        <div class="info-stats">
          <div class="stat">
            <span class="stat-label">等级</span>
            <span class="stat-val">{{ slot.level ?? '—' }}</span>
          </div>
          <div class="stat-bars">
            <div class="bar-row">
              <span class="bar-label">HP</span>
              <div class="jrpg-bar">
                <div class="jrpg-bar-fill hp" :style="{ width: hpPct + '%' }"></div>
              </div>
              <span class="bar-val">
                {{ slot.hp ?? '—' }}<span v-if="slot.hpMax">/{{ slot.hpMax }}</span>
              </span>
            </div>
            <div class="bar-row">
              <span class="bar-label">SP</span>
              <div class="jrpg-bar">
                <div class="jrpg-bar-fill sp" :style="{ width: spPct + '%' }"></div>
              </div>
              <span class="bar-val">
                {{ slot.sp ?? '—' }}<span v-if="slot.spMax">/{{ slot.spMax }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右上清空按钮 -->
      <button class="clear-btn" @click.stop="$emit('clear')" title="移除">
        <el-icon><Close /></el-icon>
      </button>
    </template>

    <template v-else>
      <div class="empty-content">
        <el-icon class="empty-plus"><Plus /></el-icon>
        <span class="empty-label">{{ label || '空位' }}</span>
      </div>
    </template>
  </div>
</template>

<style scoped>
.slot {
  position: relative;
  display: flex;
  align-items: stretch;
  height: 86px;
  background:
    linear-gradient(180deg, rgba(255, 220, 150, 0.03), transparent 50%),
    var(--jrpg-bg-card);
  border: 1px solid var(--jrpg-border-gold);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
  box-shadow: var(--jrpg-shadow-card);
}
.slot:hover {
  border-color: var(--jrpg-border-gold-bright);
  background:
    linear-gradient(180deg, rgba(255, 220, 150, 0.08), transparent 50%),
    var(--jrpg-bg-card-hover);
  transform: translateY(-1px);
}
.slot.empty {
  border-style: dashed;
  background: var(--jrpg-bg-slot);
}
.slot.empty:hover {
  border-style: solid;
}

/* 左侧 4px 装饰条 */
.side-bar {
  width: 4px;
  background: linear-gradient(180deg, var(--row-color), var(--row-color-dim));
  box-shadow: 0 0 6px var(--row-color);
}
.slot.empty .side-bar {
  background: var(--jrpg-border);
  box-shadow: none;
  opacity: 0.4;
}

/* 头像 */
.portrait-wrap {
  width: 70px;
  height: 100%;
  padding: 6px;
  flex-shrink: 0;
  position: relative;
}
.portrait {
  width: 100%;
  height: 100%;
  border-radius: 3px;
  border: 1px solid var(--jrpg-border);
  background: var(--jrpg-bg-deep);
}
.portrait-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--jrpg-bg-deep);
  color: var(--jrpg-text-muted);
  font-size: 11px;
  border-radius: 3px;
}

/* 信息区 */
.info {
  flex: 1;
  min-width: 0;
  padding: 6px 10px 6px 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.info-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.name {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 14px;
  font-weight: 600;
  color: var(--jrpg-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.6);
}
.stars {
  font-size: 10px;
  color: var(--jrpg-text-gold);
  text-shadow: 0 0 4px rgba(241, 198, 82, 0.5);
  flex-shrink: 0;
  letter-spacing: 0px;
}

.info-stats {
  display: flex;
  gap: 8px;
  align-items: center;
}
.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-right: 8px;
  border-right: 1px solid var(--jrpg-border);
  flex-shrink: 0;
}
.stat-label {
  font-size: 9px;
  color: var(--jrpg-text-muted);
  line-height: 1;
}
.stat-val {
  font-size: 14px;
  font-weight: 600;
  color: var(--jrpg-text-gold);
  line-height: 1.2;
  font-family: 'Cinzel', 'Noto Serif SC', serif;
}
.stat-bars {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}
.bar-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
}
.bar-label {
  width: 18px;
  color: var(--jrpg-text-muted);
  flex-shrink: 0;
}
.bar-val {
  font-size: 10px;
  color: var(--jrpg-text-soft);
  min-width: 56px;
  text-align: right;
  font-family: 'Cinzel', monospace;
  flex-shrink: 0;
}
.jrpg-bar {
  flex: 1;
  min-width: 0;
}

/* 清空按钮 */
.clear-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid var(--jrpg-border);
  color: var(--jrpg-text-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
  font-size: 12px;
  padding: 0;
}
.slot:hover .clear-btn {
  opacity: 1;
}
.clear-btn:hover {
  background: var(--jrpg-front);
  border-color: var(--jrpg-front);
  color: #fff;
}

/* 空位样式 */
.empty-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.empty-plus {
  font-size: 24px;
  color: var(--jrpg-text-muted);
}
.empty-label {
  font-size: 11px;
  color: var(--jrpg-text-muted);
  letter-spacing: 1px;
}
</style>
