<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-gray-800">SHAP vs LIME Comparison</h2>
      <div class="flex gap-2">
        <input v-model.number="recordId" type="number" min="1" placeholder="Record ID" class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm w-28" />
        <button @click="loadCompare" class="px-4 py-1.5 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition-colors">Compare</button>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-purple-500 text-lg">🔍</span>
          <h3 class="font-semibold text-gray-700">SHAP Explanation</h3>
          <span class="ml-auto text-xs px-2 py-0.5 bg-purple-50 text-purple-600 rounded-full">TreeExplainer</span>
        </div>
        <div ref="shapChart" class="h-80"></div>
      </div>
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-orange-500 text-lg">⚡</span>
          <h3 class="font-semibold text-gray-700">LIME Explanation</h3>
          <span class="ml-auto text-xs px-2 py-0.5 bg-orange-50 text-orange-600 rounded-full">LimeTabularExplainer</span>
        </div>
        <div ref="limeChart" class="h-80"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { useXAIStore } from '../stores'

const store = useXAIStore()
const recordId = ref(1)
const shapChart = ref(null)
const limeChart = ref(null)
let shapInstance = null, limeInstance = null

const render = () => {
  if (!store.compare) return

  if (shapChart.value && store.compare.shap) {
    if (shapInstance) shapInstance.dispose()
    shapInstance = echarts.init(shapChart.value)
    const vals = store.compare.shap
    const features = Object.keys(vals)
    const values = Object.values(vals)
    shapInstance.setOption({
      tooltip: {},
      grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
      xAxis: { type: 'value', axisLabel: { color: '#9ca3af' }, splitLine: { lineStyle: { color: '#f3f4f6' } } },
      yAxis: { type: 'category', data: features, axisLabel: { color: '#6b7280' } },
      series: [{ type: 'bar', data: values.map(v => ({ value: v, itemStyle: { color: v >= 0 ? '#10b981' : '#ef4444', borderRadius: v >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4] } })), barWidth: 18 }]
    })
  }

  if (limeChart.value && store.compare.lime) {
    if (limeInstance) limeInstance.dispose()
    limeInstance = echarts.init(limeChart.value)
    const weights = store.compare.lime
    const features = Object.keys(weights)
    const values = Object.values(weights)
    limeInstance.setOption({
      tooltip: {},
      grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
      xAxis: { type: 'value', axisLabel: { color: '#9ca3af' }, splitLine: { lineStyle: { color: '#f3f4f6' } } },
      yAxis: { type: 'category', data: features, axisLabel: { color: '#6b7280' } },
      series: [{ type: 'bar', data: values.map(v => ({ value: v, itemStyle: { color: v >= 0 ? '#10b981' : '#ef4444', borderRadius: v >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4] } })), barWidth: 18 }]
    })
  }
}

const loadCompare = async () => {
  await store.fetchCompare(recordId.value)
  render()
}

onMounted(async () => {
  await store.fetchCompare(recordId.value)
  render()
})
</script>