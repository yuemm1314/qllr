<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTeamsStore } from '@/stores/teams'
import { useCharactersStore } from '@/stores/characters'
import TeamSlot from '@/components/TeamSlot.vue'
import CharacterPicker from '@/components/CharacterPicker.vue'
import { ElMessage } from 'element-plus'
import { Back } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const teams = useTeamsStore()
const characters = useCharactersStore()

const teamId = computed(() => route.params.id as string)
const team = computed(() => teams.teams.find((t) => t.id === teamId.value) ?? null)

const pickerOpen = ref(false)
const pickingSlot = ref<{ row: 'front' | 'back'; index: number } | null>(null)

const resolved = computed(() => (team.value ? teams.resolve(team.value) : null))

const allPickedIds = computed(() => {
  if (!team.value) return []
  return [...team.value.front, ...team.value.back]
    .map((s) => s.characterId)
    .filter((x): x is string => !!x)
})

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

function clearSlot(row: 'front' | 'back', index: number) {
  if (!team.value) return
  teams.placeCharacter(team.value.id, row, index, null)
}

function saveName() {
  if (!team.value) return
  teams.touch(team.value.id)
  ElMessage.success('已保存')
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <el-button :icon="Back" @click="router.push('/teams')">返回</el-button>
      <template v-if="team">
        <el-input
          v-model="team.name"
          class="name-input"
          @change="saveName"
          placeholder="阵容名称"
        />
        <el-select
          v-model="team.tags"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="标签（可自由输入）"
          class="tag-select"
          @change="saveName"
        >
          <el-option v-for="t in ['周本', '试炼', '主线', '推图', '速通']" :key="t" :label="t" :value="t" />
        </el-select>
      </template>
    </header>

    <div v-if="!team" class="empty">
      没有找到这个阵容，可能已被删除。
      <el-button @click="router.push('/teams')">返回列表</el-button>
    </div>

    <div v-else-if="resolved" class="editor">
      <section class="row">
        <h3 class="row-title">前卫</h3>
        <div class="slot-grid">
          <TeamSlot
            v-for="(rs, i) in resolved.front"
            :key="'f' + i"
            :character="rs.character"
            :label="'前卫 ' + (i + 1)"
            @click="openPicker('front', i)"
            @clear="clearSlot('front', i)"
          />
        </div>
      </section>

      <section class="row">
        <h3 class="row-title">后卫</h3>
        <div class="slot-grid">
          <TeamSlot
            v-for="(rs, i) in resolved.back"
            :key="'b' + i"
            :character="rs.character"
            :label="'后卫 ' + (i + 1)"
            @click="openPicker('back', i)"
            @clear="clearSlot('back', i)"
          />
        </div>
      </section>

      <section class="row">
        <h3 class="row-title">备注</h3>
        <el-input
          v-model="team.description"
          type="textarea"
          :rows="4"
          placeholder="攻略思路、技能时序、注意事项……"
          @change="saveName"
        />
      </section>
    </div>

    <CharacterPicker
      v-model="pickerOpen"
      :already-picked-ids="allPickedIds"
      @pick="onPick"
    />
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 24px;
}
.name-input {
  width: 260px;
}
.tag-select {
  width: 280px;
}
.editor {
  display: flex;
  flex-direction: column;
  gap: 28px;
}
.row-title {
  margin: 0 0 12px;
  font-size: 16px;
  color: var(--color-text-secondary);
}
.slot-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  max-width: 720px;
}
.empty {
  text-align: center;
  padding: 40px;
  color: var(--color-text-secondary);
}
</style>
