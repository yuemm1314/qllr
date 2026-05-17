<script setup lang="ts">
import type { Character } from '@/types/character'

defineProps<{
  character: Character
  compact?: boolean
  clickable?: boolean
}>()

defineEmits<{
  click: [character: Character]
}>()
</script>

<template>
  <div
    class="char-card jrpg-card"
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
    </div>
    <div class="info">
      <div class="name">{{ character.name }}</div>
      <div v-if="!compact" class="meta">
        <span v-if="character.activeSkills.length" class="skills-badge">
          <span class="skills-icon">⚔</span>
          技能 {{ character.activeSkills.length }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.char-card {
  padding: 10px;
  display: flex;
  gap: 10px;
  align-items: center;
  transition: all 0.2s;
}
.char-card.clickable {
  cursor: pointer;
}
.char-card.clickable:hover {
  transform: translateY(-2px);
  border-color: var(--jrpg-border-gold-bright);
  box-shadow: var(--jrpg-shadow-card), 0 0 12px rgba(241, 198, 82, 0.25);
}
.char-card.compact {
  padding: 6px;
  flex-direction: column;
  text-align: center;
  gap: 4px;
}
.avatar-wrap {
  flex-shrink: 0;
}
.avatar {
  width: 52px;
  height: 52px;
  border-radius: 3px;
  border: 1px solid var(--jrpg-border);
  background: var(--jrpg-bg-deep);
}
.compact .avatar {
  width: 46px;
  height: 46px;
}
.avatar-fallback {
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
.info {
  flex: 1;
  min-width: 0;
}
.name {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-weight: 600;
  color: var(--jrpg-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.6);
}
.compact .name {
  font-size: 12px;
}
.meta {
  margin-top: 4px;
}
.skills-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--jrpg-text-soft);
  background: rgba(0, 0, 0, 0.3);
  padding: 1px 6px;
  border-radius: 8px;
  border: 1px solid var(--jrpg-border);
}
.skills-icon {
  color: var(--jrpg-text-gold);
}
</style>
