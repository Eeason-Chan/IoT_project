import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/traffic/overview' },
    { path: '/traffic/overview', component: () => import('../views/TrafficOverview.vue') },
    { path: '/traffic/zones', component: () => import('../views/ZoneStats.vue') },
    { path: '/traffic/records', component: () => import('../views/DataRecords.vue') },
    { path: '/xai/shap', component: () => import('../views/SHAPView.vue') },
    { path: '/xai/lime', component: () => import('../views/LIMEView.vue') },
    { path: '/xai/compare', component: () => import('../views/CompareView.vue') },
  ]
})

export default router