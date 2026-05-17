<script setup lang="ts">
import type { Character } from '@/types/character'

defineProps<{
  character: Character
  /** 是否显示为小尺寸（阵容槽位中用） */
  compact?: boolean
  /** 是否可点击 */
  clickable?: boolean
}>()

defineEmits<{
  click: [character: Character]
}>()
</script>

<template>
  <div
    class="char-card"
    :class="{ compact, clickable }"
    @click="clickable && $emit('click', character)"
  >
    <div class="avatar-wrap">
      <el-image
        :src="character.avatar"
        :alt="character.name"
        fit="cover"
        loading="lazy"
        class="avatar"
      >
        <template #error>
          <div class="avatar-fallback">{{ character.name.slice(0, 2) }}</div>
        </template>
      </el-image>
      <span v-if="character.rarity" class="rarity">
        {{ '★'.repeat(character.rarity) }}
      </span>
    </div>
    <div class="info">
      <div class="name">{{ character.name }}</div>
      <div v-if="!compact" class="meta">
        <el-tag v-if="character.job" size="small">{{ character.job }}</el-tag>
        <el-tag v-if="character.weapon" size="small" type="info">
          {{ character.weapon }}
        </el-tag>
        <el-tag v-if="character.element" size="small" type="warning">
          {{ character.element }}
        </el-tag>
      </div>
      <div v-if="!compact && character.activeSkills.length" class="skills">
        <span class="skills-label">技能</span>
        <span class="skills-count">{{ character.activeSkills.length }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.char-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  gap: 12px;
  align-items: center;
  transition: all 0.2s;
}
.char-card.clickable {
  cursor: pointer;
}
.char-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--el-color-primary);
}
.char-card.compact {
  padding: 6px;
  flex-direction: column;
  text-align: center;
  gap: 4px;
}
.avatar-wrap {
  position: relative;
  flex-shrink: 0;
}
.avatar {
  width: 56px;
  height: 56px;
  border-radius: 6px;
  background: #eee;
}
.compact .avatar {
  width: 48px;
  height: 48px;
}
.avatar-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ddd;
  color: #666;
  font-size: 12px;
  border-radius: 6px;
}
.rarity {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: #f1c40f;
  color: #fff;
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 4px;
}
.info {
  flex: 1;
  min-width: 0;
}
.name {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.compact .name {
  font-size: 12px;
}
.meta {
  margin-top: 4px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.skills {
  margin-top: 4px;
  font-size: 12px;
  color: var(--color-text-secondary);
}
.skills-count {
  margin-left: 4px;
  color: var(--el-color-primary);
  font-weight: 600;
}
</style>
