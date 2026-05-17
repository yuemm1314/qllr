<script setup lang="ts">
import { computed } from 'vue'
import { useBossesStore } from '@/stores/bosses'
import { useTeamsStore } from '@/stores/teams'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Delete,
  Edit,
  Warning,
} from '@element-plus/icons-vue'

const bosses = useBossesStore()
const teams = useTeamsStore()
const router = useRouter()

function newBoss() {
  const b = bosses.create('新 Boss')
  router.push(`/bosses/${b.id}`)
}

function edit(id: string) {
  router.push(`/bosses/${id}`)
}

async function del(id: string, name: string) {
  try {
    await ElMessageBox.confirm(`确定删除 Boss 笔记「${name}」？`, '确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    bosses.remove(id)
    ElMessage.success('已删除')
  } catch {
    /* 取消 */
  }
}

function fmtDate(ts: number) {
  return new Date(ts).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function relatedTeamNames(ids: string[]): string[] {
  return ids
    .map((id) => teams.teams.find((t) => t.id === id)?.name)
    .filter((n): n is string => !!n)
}

const sortedBosses = computed(() =>
  [...bosses.bosses].sort((a, b) => b.updatedAt - a.updatedAt),
)
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">⚔ Boss 笔 记</h2>
      <el-button type="primary" :icon="Plus" @click="newBoss">新建笔记</el-button>
    </header>

    <el-empty
      v-if="!bosses.bosses.length"
      description="还没有 Boss 笔记。记录弱点、机制、关联阵容，下次打更快上手。"
    >
      <el-button type="primary" :icon="Plus" @click="newBoss">
        新建第一篇笔记
      </el-button>
    </el-empty>

    <div v-else class="boss-grid">
      <div v-for="b in sortedBosses" :key="b.id" class="boss-card jrpg-card">
        <div class="card-head">
          <el-icon class="boss-icon"><Warning /></el-icon>
          <span class="boss-name">{{ b.name }}</span>
        </div>

        <div class="weakness" v-if="b.weakWeapons.length || b.weakElements.length">
          <span class="weakness-label">弱点</span>
          <el-tag
            v-for="w in b.weakWeapons"
            :key="'w' + w"
            size="small"
            type="info"
          >
            {{ w }}
          </el-tag>
          <el-tag
            v-for="e in b.weakElements"
            :key="'e' + e"
            size="small"
            type="warning"
          >
            {{ e }}
          </el-tag>
        </div>
        <div v-else class="weakness-empty">未记录弱点</div>

        <div v-if="b.mechanics" class="mech-preview">
          {{ b.mechanics.slice(0, 60) }}{{ b.mechanics.length > 60 ? '…' : '' }}
        </div>

        <div v-if="b.relatedTeamIds.length" class="related">
          <span class="related-label">关联阵容</span>
          <span class="related-list">
            {{ relatedTeamNames(b.relatedTeamIds).join('、') || '已删除' }}
          </span>
        </div>

        <div class="card-meta">{{ fmtDate(b.updatedAt) }}</div>

        <div class="card-actions">
          <el-button size="small" :icon="Edit" @click="edit(b.id)">编辑</el-button>
          <el-button
            size="small"
            type="danger"
            :icon="Delete"
            @click="del(b.id, b.name)"
          >
            删除
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.page-title {
  margin: 0;
  font-family: 'Noto Serif SC', serif;
  letter-spacing: 4px;
  color: var(--jrpg-text-gold);
  font-size: 24px;
  text-shadow: 0 0 12px rgba(241, 198, 82, 0.3), 0 2px 4px rgba(0, 0, 0, 0.6);
}
.boss-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.boss-card {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.card-head {
  display: flex;
  align-items: center;
  gap: 8px;
}
.boss-icon {
  color: var(--jrpg-front);
  font-size: 18px;
}
.boss-name {
  font-family: 'Noto Serif SC', serif;
  font-weight: 600;
  font-size: 16px;
  color: var(--jrpg-text);
  flex: 1;
}
.weakness {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}
.weakness-label {
  font-size: 11px;
  color: var(--jrpg-text-muted);
  margin-right: 2px;
}
.weakness-empty {
  font-size: 11px;
  color: var(--jrpg-text-muted);
  font-style: italic;
}
.mech-preview {
  font-size: 12px;
  color: var(--jrpg-text-soft);
  background: rgba(0, 0, 0, 0.25);
  padding: 6px 8px;
  border-left: 2px solid var(--jrpg-border-gold);
  border-radius: 2px;
  line-height: 1.5;
}
.related {
  font-size: 12px;
  color: var(--jrpg-text-soft);
}
.related-label {
  color: var(--jrpg-text-muted);
  margin-right: 4px;
}
.card-meta {
  color: var(--jrpg-text-muted);
  font-size: 11px;
  font-family: 'Cinzel', monospace;
}
.card-actions {
  display: flex;
  gap: 6px;
  margin-top: 2px;
}
</style>
