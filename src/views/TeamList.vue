<script setup lang="ts">
import { useTeamsStore } from '@/stores/teams'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Upload, CopyDocument, Delete, Edit } from '@element-plus/icons-vue'

const teams = useTeamsStore()
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
  return new Date(ts).toLocaleString('zh-CN')
}

function teamFillCount(team: (typeof teams.teams)[number]): number {
  const all = [...team.front, ...team.back]
  return all.filter((s) => s.characterId).length
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2>我的阵容</h2>
      <div class="actions">
        <el-button :icon="Upload" @click="importAll">导入</el-button>
        <el-button :icon="Download" @click="exportAll" :disabled="!teams.teams.length">
          导出
        </el-button>
        <el-button type="primary" :icon="Plus" @click="newTeam">新建阵容</el-button>
      </div>
    </header>

    <el-empty v-if="!teams.teams.length" description="还没有阵容，点击右上角「新建阵容」">
      <el-button type="primary" :icon="Plus" @click="newTeam">新建阵容</el-button>
    </el-empty>

    <div v-else class="team-grid">
      <el-card v-for="t in teams.teams" :key="t.id" class="team-card" shadow="hover">
        <div class="team-head">
          <span class="team-name">{{ t.name }}</span>
          <span class="team-fill">{{ teamFillCount(t) }}/8</span>
        </div>
        <div class="team-tags" v-if="t.tags.length">
          <el-tag v-for="tag in t.tags" :key="tag" size="small">{{ tag }}</el-tag>
        </div>
        <div class="team-meta">更新于 {{ fmtDate(t.updatedAt) }}</div>
        <div class="team-actions">
          <el-button size="small" :icon="Edit" @click="edit(t.id)">编辑</el-button>
          <el-button size="small" :icon="CopyDocument" @click="dup(t.id)">复制</el-button>
          <el-button
            size="small"
            type="danger"
            :icon="Delete"
            @click="del(t.id, t.name)"
          >
            删除
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-header h2 {
  margin: 0;
}
.actions {
  display: flex;
  gap: 8px;
}
.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.team-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.team-name {
  font-weight: 600;
  font-size: 16px;
}
.team-fill {
  background: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}
.team-tags {
  margin-bottom: 8px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.team-meta {
  color: var(--color-text-secondary);
  font-size: 12px;
  margin-bottom: 12px;
}
.team-actions {
  display: flex;
  gap: 6px;
}
</style>
