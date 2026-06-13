<template>
  <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-800">LIME Local Explanation</h2>
      <div class="flex gap-2">
        <input v-model.number="recordId" type="number" min="1" placeholder="Record ID" class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm w-28" />
        <button @click="loadLocal" class="px-4 py-1.5 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition-colors">Analyze</button>
      </div>
    </div>
    <div ref="limeChart" class="h-80"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { useXAIStore } from '../stores'

const store = useXAIStore()
const recordId = ref(1)
const limeChart = ref(null)
let chartInstance = null

const render = () => {
  if (!limeChart.value || !store.limeLocal) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(limeChart.value)
  const weights = store.limeLocal.lime_weights
  const features = Object.keys(weights)
  const values = Object.values(weights)

  chartInstance.setOption({
    tooltip: {},
    grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: { type: 'value', axisLabel: { color: '#9ca3af' }, splitLine: { lineStyle: { color: '#f3f4f6' } } },
    yAxis: { type: 'category', data: features, axisLabel: { color: '#6b7280' } },
    series: [{
      type: 'bar',
      data: values.map(v => ({ value: v, itemStyle: { color: v >= 0 ? '#10b981' : '#ef4444', borderRadius: v >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4] } })),
      barWidth: 18,
    }]
  })
}

const loadLocal = async () => {
  await store.fetchLIMELocal(recordId.value)
  render()
}

onMounted(async () => {
  await store.fetchLIMELocal(recordId.value)
  render()
})
</script>