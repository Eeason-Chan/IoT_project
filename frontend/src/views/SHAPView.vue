<template>
  <div class="space-y-6">
    <div class="grid grid-cols-2 gap-4">
      <!-- Global Importance -->
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <h3 class="font-semibold text-gray-700 mb-4">Global Feature Importance</h3>
        <div ref="globalChart" class="h-72"></div>
      </div>

      <!-- Summary Scatter -->
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <h3 class="font-semibold text-gray-700 mb-4">SHAP Summary Scatter</h3>
        <div ref="scatterChart" class="h-72"></div>
      </div>
    </div>

    <!-- Local Explanation -->
    <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-gray-700">Local SHAP Explanation</h3>
        <div class="flex gap-2">
          <input v-model.number="recordId" type="number" min="1" placeholder="Record ID" class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm w-28" />
          <button @click="loadLocal" class="px-4 py-1.5 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition-colors">Analyze</button>
        </div>
      </div>
      <div ref="localChart" class="h-72"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { useXAIStore } from '../stores'

const store = useXAIStore()
const recordId = ref(1)
const globalChart = ref(null)
const scatterChart = ref(null)
const localChart = ref(null)
let globalInstance = null, scatterInstance = null, localInstance = null

const renderGlobal = () => {
  if (!globalChart.value || !store.shapGlobal.length) return
  if (globalInstance) globalInstance.dispose()
  globalInstance = echarts.init(globalChart.value)
  const data = [...store.shapGlobal].sort((a, b) => b.shap_value - a.shap_value)
  globalInstance.setOption({
    tooltip: {},
    grid: { left: '3%', right: '8%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: { type: 'value', axisLabel: { color: '#9ca3af' }, splitLine: { lineStyle: { color: '#f3f4f6' } } },
    yAxis: { type: 'category', data: data.map(d => d.feature), axisLabel: { color: '#6b7280' } },
    series: [{ type: 'bar', data: data.map(d => d.shap_value), barWidth: 16, itemStyle: { color: '#3b82f6', borderRadius: [0, 4, 4, 0] }, label: { show: true, position: 'right', formatter: '{c}', color: '#6b7280', fontSize: 10 } }]
  })
}

const renderScatter = () => {
  if (!scatterChart.value || !store.shapSummary.length) return
  if (scatterInstance) scatterInstance.dispose()
  scatterInstance = echarts.init(scatterChart.value)
  const data = store.shapSummary
  scatterInstance.setOption({
    tooltip: { trigger: 'item' },
    grid: { left: '3%', right: '4%', bottom: '10%', top: '5%', containLabel: true },
    xAxis: { type: 'value', name: 'Feature Value', axisLabel: { color: '#9ca3af' }, splitLine: { lineStyle: { color: '#f3f4f6' } } },
    yAxis: { type: 'value', name: 'SHAP Value', axisLabel: { color: '#9ca3af' } },
    series: [{ type: 'scatter', symbolSize: 5, data: data.map(d => [d.feature_value, d.shap_value]), itemStyle: { color: '#8b5cf6' } }]
  })
}

const renderLocal = () => {
  if (!localChart.value || !store.shapLocal) return
  if (localInstance) localInstance.dispose()
  localInstance = echarts.init(localChart.value)
  const vals = store.shapLocal.shap_values
  const features = Object.keys(vals)
  const values = Object.values(vals)
  localInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: { type: 'value', axisLabel: { color: '#9ca3af' }, splitLine: { lineStyle: { color: '#f3f4f6' } } },
    yAxis: { type: 'category', data: features, axisLabel: { color: '#6b7280' } },
    series: [{
      type: 'bar',
      data: values.map(v => ({ value: v, itemStyle: { color: v >= 0 ? '#10b981' : '#ef4444', borderRadius: v >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4] } })),
      barWidth: 16,
    }]
  })
}

const loadLocal = async () => {
  await store.fetchSHAPLocal(recordId.value)
  renderLocal()
}

onMounted(async () => {
  await Promise.all([store.fetchSHAPGlobal(), store.fetchSHAPSummary()])
  renderGlobal()
  renderScatter()
})
</script>