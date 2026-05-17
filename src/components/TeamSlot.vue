<script setup lang="ts">
import type { Character } from '@/types/character'
import { Plus, Close } from '@element-plus/icons-vue'

defineProps<{
  character: Character | null
  label?: string
}>()

defineEmits<{
  click: []
  clear: []
}>()
</script>

<template>
  <div class="slot" :class="{ filled: !!character }" @click="$emit('click')">
    <template v-if="character">
      <el-image :src="character.avatar" class="slot-avatar" fit="cover" loading="lazy">
        <template #error>
          <div class="avatar-fallback">{{ character.name.slice(0, 2) }}</div>
        </template>
      </el-image>
      <div class="slot-name">{{ character.name }}</div>
      <el-button
        class="slot-clear"
        size="small"
        circle
        :icon="Close"
        @click.stop="$emit('clear')"
      />
    </template>
    <template v-else>
      <el-icon class="slot-plus"><Plus /></el-icon>
      <div class="slot-label">{{ label || '空位' }}</div>
    </template>
  </div>
</template>

<style scoped>
.slot {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1.2;
  border: 2px dashed var(--color-border);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  background: var(--color-bg-card);
  transition: all 0.2s;
}
.slot:hover {
  border-color: var(--el-color-primary);
  border-style: solid;
}
.slot.filled {
  border-style: solid;
  border-color: var(--color-border);
}
.slot-avatar {
  width: 64px;
  height: 64px;
  border-radius: 8px;
}
.avatar-fallback {
  width: 100%;
  height: 100%;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 12px;
  border-radius: 8px;
}
.slot-name {
  font-size: 12px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
  padding: 0 6px;
}
.slot-plus {
  font-size: 28px;
  color: var(--color-text-secondary);
}
.slot-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}
.slot-clear {
  position: absolute;
  top: 4px;
  right: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}
.slot:hover .slot-clear {
  opacity: 1;
}
</style>
