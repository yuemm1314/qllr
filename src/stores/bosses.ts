import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { BossNote } from '@/types/boss'
import { createEmptyBossNote } from '@/types/boss'

/**
 * Boss 笔记 Store。结构与 teams 类似，本地持久化。
 */
export const useBossesStore = defineStore(
  'bosses',
  () => {
    const bosses = ref<BossNote[]>([])

    function create(name?: string): BossNote {
      const b = createEmptyBossNote(name)
      bosses.value.push(b)
      return b
    }

    function remove(id: string) {
      bosses.value = bosses.value.filter((b) => b.id !== id)
    }

    function findById(id: string): BossNote | null {
      return bosses.value.find((b) => b.id === id) ?? null
    }

    function touch(id: string) {
      const b = findById(id)
      if (b) b.updatedAt = Date.now()
    }

    function exportJson(): string {
      return JSON.stringify({ version: 1, bosses: bosses.value }, null, 2)
    }

    function importJson(text: string, mode: 'replace' | 'merge' = 'merge') {
      const parsed = JSON.parse(text)
      const incoming: BossNote[] = parsed.bosses ?? []
      if (mode === 'replace') {
        bosses.value = incoming
      } else {
        const map = new Map<string, BossNote>()
        for (const b of bosses.value) map.set(b.id, b)
        for (const b of incoming) map.set(b.id, b)
        bosses.value = Array.from(map.values())
      }
    }

    return {
      bosses,
      create,
      remove,
      findById,
      touch,
      exportJson,
      importJson,
    }
  },
  {
    persist: { key: 'qllr.bosses.v1' },
  },
)
