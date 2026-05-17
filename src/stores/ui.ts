import { defineStore } from 'pinia'
import { ref } from 'vue'

/** UI 状态：暗黑模式、当前选中的标签页等 */
export const useUiStore = defineStore(
  'ui',
  () => {
    const darkMode = ref(false)
    const sidebarCollapsed = ref(false)

    function toggleDark() {
      darkMode.value = !darkMode.value
      applyDark()
    }

    function applyDark() {
      const html = document.documentElement
      if (darkMode.value) html.classList.add('dark')
      else html.classList.remove('dark')
    }

    return { darkMode, sidebarCollapsed, toggleDark, applyDark }
  },
  {
    persist: { key: 'qllr.ui.v1' },
  },
)
