<template>
  <div class="flex h-screen bg-gray-50">
    <!-- Sidebar -->
    <aside class="w-56 bg-gray-900 flex flex-col">
      <div class="p-4">
        <h1 class="text-lg font-bold text-white">XAI Traffic</h1>
        <p class="text-xs text-gray-400">Urban Traffic Dashboard</p>
      </div>
      <nav class="flex-1 py-4">
        <div class="px-3 mb-1">
          <p class="text-xs text-gray-500 uppercase tracking-wider px-3 mb-2">Traffic</p>
        </div>
        <router-link to="/traffic/overview" class="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors" active-class="bg-gray-800 text-white border-r-2 border-blue-500">
          <span class="text-sm">📊</span><span class="text-sm">Overview</span>
        </router-link>
        <router-link to="/traffic/zones" class="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors" active-class="bg-gray-800 text-white border-r-2 border-blue-500">
          <span class="text-sm">🗺️</span><span class="text-sm">Zones</span>
        </router-link>
        <router-link to="/traffic/records" class="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors" active-class="bg-gray-800 text-white border-r-2 border-blue-500">
          <span class="text-sm">📋</span><span class="text-sm">Records</span>
        </router-link>

        <div class="px-3 mt-6 mb-1">
          <p class="text-xs text-gray-500 uppercase tracking-wider px-3 mb-2">XAI Analysis</p>
        </div>
        <router-link to="/xai/shap" class="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors" active-class="bg-gray-800 text-white border-r-2 border-blue-500">
          <span class="text-sm">🔍</span><span class="text-sm">SHAP</span>
        </router-link>
        <router-link to="/xai/lime" class="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors" active-class="bg-gray-800 text-white border-r-2 border-blue-500">
          <span class="text-sm">⚡</span><span class="text-sm">LIME</span>
        </router-link>
        <router-link to="/xai/compare" class="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors" active-class="bg-gray-800 text-white border-r-2 border-blue-500">
          <span class="text-sm">⚖️</span><span class="text-sm">Compare</span>
        </router-link>
      </nav>

      <div class="p-4 border-t border-gray-800">
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-green-500"></div>
          <span class="text-xs text-gray-400">System Online</span>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-auto">
      <header class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-800">{{ pageTitle }}</h2>
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-500">{{ currentDate }}</span>
          <div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-medium">A</div>
        </div>
      </header>
      <div class="p-6">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const pageTitle = computed(() => {
  const titles = {
    '/traffic/overview': 'Traffic Overview',
    '/traffic/zones': 'Zone Statistics',
    '/traffic/records': 'Data Records',
    '/xai/shap': 'SHAP Explanations',
    '/xai/lime': 'LIME Explanations',
    '/xai/compare': 'SHAP vs LIME',
  }
  return titles[route.path] || 'Dashboard'
})
const currentDate = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
</script>