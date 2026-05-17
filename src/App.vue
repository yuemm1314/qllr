<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCharactersStore } from '@/stores/characters'
import { User, Grid, Collection, Loading } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const charactersStore = useCharactersStore()

// 添加 loading 和 error 状态
const loading = computed(() => !charactersStore.loaded)
const error = computed(() => null) // 暂时没有错误处理

const activeMenu = computed(() => {
  if (route.path.startsWith('/characters')) return '/characters'
  if (route.path.startsWith('/bosses')) return '/bosses'
  return '/teams'
})

function go(path: string) {
  router.push(path)
}

onMounted(() => {
  charactersStore.load()
})
</script>

<template>
  <el-container class="app-root">
    <el-aside width="210px" class="app-aside">
      <div class="logo">
        <span class="logo-emoji">⚔</span>
        <div class="logo-text">
          <div class="logo-main">霸者阵容</div>
          <div class="logo-sub">OCTOPATH COTC</div>
        </div>
      </div>
      <el-menu :default-active="activeMenu" class="app-menu" @select="go">
        <el-menu-item index="/teams">
          <el-icon><Collection /></el-icon>
          <span>我的阵容</span>
        </el-menu-item>
        <el-menu-item index="/characters">
          <el-icon><User /></el-icon>
          <span>角色库</span>
        </el-menu-item>
        <el-menu-item index="/bosses">
          <el-icon><Grid /></el-icon>
          <span>Boss 笔记</span>
        </el-menu-item>
      </el-menu>
      <div class="aside-footer">
        <div class="footer-stat">
          角色库 {{ charactersStore.total }} 名
        </div>
      </div>
    </el-aside>

    <el-main class="app-main">
      <div v-if="loading" class="loading">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
        <p>正在加载角色数据…</p>
      </div>
      <div v-else-if="error" class="error">
        <el-alert
          :title="'数据加载失败：' + error"
          type="error"
          show-icon
          :closable="false"
        />
        <p style="margin-top: 12px">
          请确认已下载 wiki_avatars.json 和 wiki_active_skills_zh.json 到
          <code>src/data/</code>，然后重启 <code>npm run dev</code>。
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
  background:
    linear-gradient(180deg, var(--jrpg-bg-card), var(--jrpg-bg-deep));
  border-right: 1px solid var(--jrpg-border-gold);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.5);
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 16px;
  border-bottom: 1px solid var(--jrpg-border);
  background:
    linear-gradient(180deg, rgba(241, 198, 82, 0.08), transparent);
}
.logo-emoji {
  font-size: 28px;
  color: var(--jrpg-text-gold);
  text-shadow: 0 0 8px rgba(241, 198, 82, 0.5);
}
.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.logo-main {
  font-family: 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--jrpg-text-gold);
  letter-spacing: 2px;
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.6);
}
.logo-sub {
  font-family: 'Cinzel', serif;
  font-size: 10px;
  color: var(--jrpg-text-muted);
  letter-spacing: 1.5px;
}
.app-menu {
  flex: 1;
  border-right: none;
  padding-top: 8px;
}
.aside-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--jrpg-border);
  color: var(--jrpg-text-muted);
  font-size: 11px;
  font-family: 'Cinzel', monospace;
}
.footer-stat {
  text-align: center;
}
.app-main {
  padding: 24px 28px;
}
.loading,
.error {
  padding: 60px;
  text-align: center;
  color: var(--jrpg-text-soft);
}
.loading .el-icon {
  color: var(--jrpg-text-gold);
}
</style>
