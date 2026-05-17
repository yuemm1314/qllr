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
  {
    path: '/bosses',
    name: 'BossList',
    component: () => import('@/views/BossList.vue'),
    meta: { title: 'Boss 笔记' },
  },
  {
    path: '/skill-ranking',
    name: 'skill-ranking',
    component: () => import('@/views/SkillRanking.vue'),
    meta: { title: '技能倍率排行' },
  },
  {
    path: '/bosses/:id',
    name: 'BossEditor',
    component: () => import('@/views/BossEditor.vue'),
    meta: { title: 'Boss 详情' },
  },
]

export const router = createRouter({
  history: createWebHashHistory(),
  routes,
})
