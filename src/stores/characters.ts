import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Character } from '@/types/character'
import { dataSource } from '@/data'

/**
 * 角色库 Store：只负责加载/查询角色（来源于 dataSource）。
 * 这个 store 的数据是"只读"的——用户不能改 Wiki 数据，只能改自己的阵容。
 */
export const useCharactersStore = defineStore('characters', () => {
  const list = ref<Character[]>([])
  const loading = ref(false)
  const loaded = ref(false)
  const error = ref<string | null>(null)

  async function load() {
    if (loaded.value || loading.value) return
    loading.value = true
    error.value = null
    try {
      list.value = await dataSource.loadCharacters()
      loaded.value = true
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
      console.error('[characters] 加载失败', e)
    } finally {
      loading.value = false
    }
  }

  /** 根据 ID 查找角色 */
  const byId = computed(() => {
    const map = new Map<string, Character>()
    for (const c of list.value) map.set(c.id, c)
    return map
  })

  function findById(id: string | null | undefined): Character | null {
    if (!id) return null
    return byId.value.get(id) ?? null
  }

  return {
    list,
    loading,
    loaded,
    error,
    load,
    findById,
  }
})
