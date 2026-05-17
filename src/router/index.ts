import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/teams' },
  {
    path: '/teams',
    name: 'TeamList',
    component: () => import('@/views/TeamList.vue'),
    meta: { title: '我的阵容' },
  },
  {
    path: '/teams/:id',
    name: 'TeamEditor',
    component: () => import('@/views/TeamEditor.vue'),
    meta: { title: '阵容编辑器' },
  },
  {
    path: '/characters',
    name: 'CharacterLibrary',
    component: () => import('@/views/CharacterLibrary.vue'),
    meta: { title: '角色库' },
  },
]

export const router = createRouter({
  // 用 hash 模式避免 GitHub Pages 部署时的路由问题
  history: createWebHashHistory(),
  routes,
})
