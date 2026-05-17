<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCharactersStore } from '@/stores/characters'
import { useUiStore } from '@/stores/ui'
import { Moon, Sunny, User, Grid, Collection } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const charactersStore = useCharactersStore()
const ui = useUiStore()

const activeMenu = computed(() => {
  if (route.path.startsWith('/characters')) return '/characters'
  return '/teams'
})

function go(path: string) {
  router.push(path)
}

onMounted(() => {
  charactersStore.load()
  ui.applyDark()
})
</script>

<template>
  <el-container class="app-root">
    <el-aside width="200px" class="app-aside">
      <div class="logo">
        <span class="logo-emoji">⚔️</span>
        <span class="logo-text">霸者阵容</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="app-menu"
        @select="go"
        background-color="transparent"
      >
        <el-menu-item index="/teams">
          <el-icon><Collection /></el-icon>
          <span>我的阵容</span>
        </el-menu-item>
        <el-menu-item index="/characters">
          <el-icon><User /></el-icon>
          <span>角色库</span>
        </el-menu-item>
        <el-menu-item index="/bosses" disabled>
          <el-icon><Grid /></el-icon>
          <span>Boss 笔记（待开发）</span>
        </el-menu-item>
      </el-menu>
      <div class="aside-footer">
        <el-button
          :icon="ui.darkMode ? Sunny : Moon"
          circle
          @click="ui.toggleDark()"
          :title="ui.darkMode ? '切换到亮色' : '切换到暗色'"
        />
      </div>
    </el-aside>

    <el-main class="app-main">
      <div v-if="charactersStore.loading" class="loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        正在加载角色数据…
      </div>
      <div v-else-if="charactersStore.error" class="error">
        <el-alert
          :title="'数据加载失败：' + charactersStore.error"
          type="error"
          show-icon
          :closable="false"
        />
        <p style="margin-top: 12px">
          请确认已按 README 第 3 步把 wiki_avatars.json 和 wiki_active_skills_zh.json
          放到 <code>src/data/</code> 下，然后重启 <code>npm run dev</code>。
        </p>
      </div>
      <router-view v-else />
    </el-main>
  </el-container>
</template>

<style scoped>
.app-root {
  height: 100%;
}
.app-aside {
  background: var(--color-bg-card);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid var(--color-border);
}
.logo-emoji {
  font-size: 22px;
}
.app-menu {
  flex: 1;
  border-right: none;
}
.aside-footer {
  padding: 12px;
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: center;
}
.app-main {
  padding: 24px;
}
.loading,
.error {
  padding: 40px;
  text-align: center;
  color: var(--color-text-secondary);
}
</style>
