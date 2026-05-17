import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { type Team, createEmptyTeam, type ResolvedTeamSlot } from '@/types/team'
import { useCharactersStore } from './characters'

/**
 * 阵容 Store：用户保存的所有阵容。
 * 通过 pinia-plugin-persistedstate 自动持久化到 localStorage。
 */
export const useTeamsStore = defineStore(
  'teams',
  () => {
    const teams = ref<Team[]>([])
    /** 当前正在编辑的阵容 ID */
    const editingId = ref<string | null>(null)

    const editing = computed<Team | null>(() => {
      if (!editingId.value) return null
      return teams.value.find((t) => t.id === editingId.value) ?? null
    })

    function create(name?: string): Team {
      const t = createEmptyTeam(name)
      teams.value.push(t)
      return t
    }

    function remove(id: string) {
      teams.value = teams.value.filter((t) => t.id !== id)
      if (editingId.value === id) editingId.value = null
    }

    function duplicate(id: string): Team | null {
      const t = teams.value.find((x) => x.id === id)
      if (!t) return null
      const copy: Team = {
        ...JSON.parse(JSON.stringify(t)),
        id: crypto.randomUUID(),
        name: t.name + ' (副本)',
        createdAt: Date.now(),
        updatedAt: Date.now(),
      }
      teams.value.push(copy)
      return copy
    }

    function setEditing(id: string | null) {
      editingId.value = id
    }

    /** 把一个 Team 解析成带角色对象的形式（UI 用） */
    function resolve(team: Team): {
      front: ResolvedTeamSlot[]
      back: ResolvedTeamSlot[]
    } {
      const characters = useCharactersStore()
      const map = (slots: typeof team.front) =>
        slots.map((slot) => ({
          slot,
          character: characters.findById(slot.characterId),
        }))
      return {
        front: map(team.front),
        back: map(team.back),
      }
    }

    function touch(id: string) {
      const t = teams.value.find((x) => x.id === id)
      if (t) t.updatedAt = Date.now()
    }

    /** 在阵容的指定位置放入一个角色 */
    function placeCharacter(
      teamId: string,
      row: 'front' | 'back',
      index: number,
      characterId: string | null,
    ) {
      const t = teams.value.find((x) => x.id === teamId)
      if (!t) return
      t[row][index].characterId = characterId
      touch(teamId)
    }

    /** 导出 JSON 备份 */
    function exportJson(): string {
      return JSON.stringify({ version: 1, teams: teams.value }, null, 2)
    }

    /** 导入 JSON 备份 */
    function importJson(text: string, mode: 'replace' | 'merge' = 'merge') {
      const parsed = JSON.parse(text)
      const incoming: Team[] = parsed.teams ?? []
      if (mode === 'replace') {
        teams.value = incoming
      } else {
        // 合并：用 id 去重，新数据覆盖旧数据
        const map = new Map<string, Team>()
        for (const t of teams.value) map.set(t.id, t)
        for (const t of incoming) map.set(t.id, t)
        teams.value = Array.from(map.values())
      }
    }

    return {
      teams,
      editingId,
      editing,
      create,
      remove,
      duplicate,
      setEditing,
      resolve,
      placeCharacter,
      touch,
      exportJson,
      importJson,
    }
  },
  {
    persist: {
      key: 'qllr.teams.v1',
    },
  },
)
