<script setup lang="ts">
import { computed } from 'vue'
import { useTeamsStore } from '@/stores/teams'
import { useCharactersStore } from '@/stores/characters'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Download,
  Upload,
  CopyDocument,
  Delete,
  Edit,
} from '@element-plus/icons-vue'
import type { Team } from '@/types/team'

const teams = useTeamsStore()
const characters = useCharactersStore()
const router = useRouter()

function newTeam() {
  const t = teams.create('新阵容 ' + (teams.teams.length + 1))
  router.push(`/teams/${t.id}`)
}

function edit(id: string) {
  router.push(`/teams/${id}`)
}

async function del(id: string, name: string) {
  try {
    await ElMessageBox.confirm(`确定删除阵容「${name}」？`, '确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    teams.remove(id)
    ElMessage.success('已删除')
  } catch {
    /* 取消 */
  }
}

function dup(id: string) {
  const t = teams.duplicate(id)
  if (t) ElMessage.success('已复制为「' + t.name + '」')
}

function exportAll() {
  const blob = new Blob([teams.exportJson()], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `qllr-teams-${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(a.href)
}

function importAll() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'application/json'
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return
    const text = await file.text()
    try {
      teams.importJson(text, 'merge')
      ElMessage.success('导入成功')
    } catch (e) {
      ElMessage.error('导入失败：' + (e as Error).message)
    }
  }
  input.click()
}

function fmtDate(ts: number) {
  return new Date(ts).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function teamFillCount(team: Team): number {
  return [...team.front, ...team.back].filter((s) => s.characterId).length
}

/** 获取阵容里 8 个槽位对应的角色（用于缩略图） */
function slotsOf(team: Team) {
  return {
    front: team.front.map((s) => characters.findById(s.characterId)),
    back: team.back.map((s) => characters.findById(s.characterId)),
  }
}

const sortedTeams = computed(() =>
  [...teams.teams].sort((a, b) => b.updatedAt - a.updatedAt),
)
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">⚔ 我的阵容</h2>
      <div class="actions">
        <el-button :icon="Upload" @click="importAll">导入</el-button>
        <el-button
          :icon="Download"
          @click="exportAll"
          :disabled="!teams.teams.length"
        >
          导出
        </el-button>
        <el-button type="primary" :icon="Plus" @click="newTeam">
          新建阵容
        </el-button>
      </div>
    </header>

    <el-empty
      v-if="!teams.teams.length"
      description="还没有阵容，点击右上角「新建阵容」开始"
    >
      <el-button type="primary" :icon="Plus" @click="newTeam">
        新建第一个阵容
      </el-button>
    </el-empty>

    <div v-else class="team-grid">
      <div
        v-for="t in sortedTeams"
        :key="t.id"
        class="team-card jrpg-card"
      >
        <div class="card-head">
          <span class="card-name">{{ t.name }}</span>
          <span class="card-fill">{{ teamFillCount(t) }}/8</span>
        </div>

        <!-- 4+4 缩略 -->
        <div class="thumbs">
          <div class="thumb-row front">
            <div
              v-for="(c, i) in slotsOf(t).front"
              :key="'f' + i"
              class="thumb"
              :class="{ filled: !!c }"
            >
              <el-image v-if="c" :src="c.avatar" fit="cover" loading="lazy">
                <template #error>
                  <span class="thumb-fb">{{ c.name.slice(0, 1) }}</span>
                </template>
              </el-image>
            </div>
          </div>
          <div class="thumb-row back">
            <div
              v-for="(c, i) in slotsOf(t).back"
              :key="'b' + i"
              class="thumb"
              :class="{ filled: !!c }"
            >
              <el-image v-if="c" :src="c.avatar" fit="cover" loading="lazy">
                <template #error>
                  <span class="thumb-fb">{{ c.name.slice(0, 1) }}</span>
                </template>
              </el-image>
            </div>
          </div>
        </div>

        <div class="card-tags" v-if="t.tags.length">
          <el-tag v-for="tag in t.tags" :key="tag" size="small">{{ tag }}</el-tag>
        </div>
        <div class="card-meta">{{ fmtDate(t.updatedAt) }}</div>

        <div class="card-actions">
          <el-button size="small" :icon="Edit" @click="edit(t.id)">
            编辑
          </el-button>
          <el-button size="small" :icon="CopyDocument" @click="dup(t.id)">
            复制
          </el-button>
          <el-button
            size="small"
            type="danger"
            :icon="Delete"
            @click="del(t.id, t.name)"
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
.actions {
  display: flex;
  gap: 8px;
}
.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}
.team-card {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-name {
  font-family: 'Noto Serif SC', serif;
  font-weight: 600;
  font-size: 16px;
  color: var(--jrpg-text);
}
.card-fill {
  font-family: 'Cinzel', monospace;
  font-size: 12px;
  color: var(--jrpg-text-gold);
  background: rgba(241, 198, 82, 0.1);
  border: 1px solid var(--jrpg-border-gold);
  padding: 2px 8px;
  border-radius: 10px;
}

.thumbs {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
  background: var(--jrpg-bg-deep);
  border: 1px solid var(--jrpg-border);
  border-radius: 4px;
}
.thumb-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
  position: relative;
  padding-left: 4px;
}
.thumb-row::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 2px;
}
.thumb-row.front::before {
  background: var(--jrpg-front);
}
.thumb-row.back::before {
  background: var(--jrpg-back);
}
.thumb {
  aspect-ratio: 1;
  background: var(--jrpg-bg-base);
  border: 1px solid var(--jrpg-border);
  border-radius: 2px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.thumb.filled {
  border-color: var(--jrpg-border-gold);
}
.thumb :deep(.el-image) {
  width: 100%;
  height: 100%;
}
.thumb-fb {
  font-size: 12px;
  color: var(--jrpg-text-muted);
}

.card-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
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
