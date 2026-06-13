<template>
  <div class="space-y-6">
    <!-- KPI Cards -->
    <div class="grid grid-cols-4 gap-4">
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm font-medium text-gray-500">Avg Stress Index</span>
          <span class="text-xs px-2 py-1 bg-blue-50 text-blue-600 rounded-full">Live</span>
        </div>
        <div class="text-3xl font-bold text-gray-800">{{ summary?.avg_stress ?? '-' }}</div>
        <p class="text-xs text-gray-400 mt-1">Across all records</p>
      </div>

      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm font-medium text-gray-500">Total Records</span>
          <span class="text-xs px-2 py-1 bg-green-50 text-green-600 rounded-full">Loaded</span>
        </div>
        <div class="text-3xl font-bold text-gray-800">{{ summary?.total?.toLocaleString() ?? '-' }}</div>
        <p class="text-xs text-gray-400 mt-1">Cleaned dataset</p>
      </div>

      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm font-medium text-gray-500">High Stress Ratio</span>
          <span class="text-xs px-2 py-1 bg-red-50 text-red-600 rounded-full">Alert</span>
        </div>
        <div class="text-3xl font-bold text-red-500">{{ summary?.high_stress_ratio ?? '-' }}%</div>
        <p class="text-xs text-gray-400 mt-1">Above threshold</p>
      </div>

      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm font-medium text-gray-500">System Status</span>
          <span class="text-xs px-2 py-1 bg-green-50 text-green-600 rounded-full">OK</span>
        </div>
        <div class="text-3xl font-bold text-green-500">✓</div>
        <p class="text-xs text-gray-400 mt-1">All services healthy</p>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-3 gap-4">
      <!-- Distribution Pie -->
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <h3 class="font-semibold text-gray-700 mb-4">Stress Distribution</h3>
        <div ref="pieChart" class="h-64"></div>
      </div>

      <!-- Timeseries Line -->
      <div class="col-span-2 bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-700">Stress Trend</h3>
          <div class="flex gap-2">
            <button @click="loadTimeseries('hour')" :class="['px-3 py-1 text-xs rounded-lg transition-colors', gran=='hour'?'bg-blue-500 text-white':'bg-gray-100 text-gray-600 hover:bg-gray-200']">Hourly</button>
            <button @click="loadTimeseries('day')" :class="['px-3 py-1 text-xs rounded-lg transition-colors', gran=='day'?'bg-blue-500 text-white':'bg-gray-100 text-gray-600 hover:bg-gray-200']">Daily</button>
          </div>
        </div>
        <div ref="lineChart" class="h-64"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { useTrafficStore } from '../stores'

const store = useTrafficStore()
const summary = ref(null)
const pieChart = ref(null)
const lineChart = ref(null)
const gran = ref('hour')

let pieInstance = null
let lineInstance = null

const loadTimeseries = async (g) => {
  gran.value = g
  await store.fetchTimeseries(g)
  renderLine()
}

const renderPie = () => {
  if (!pieChart.value) return
  if (pieInstance) pieInstance.dispose()
  pieInstance = echarts.init(pieChart.value)
  const d = store.distribution
  if (!d) return

  pieInstance.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: '#6b7280' } },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold' }
      },
      data: [
        { value: d.low.count, name: 'Low', itemStyle: { color: '#10b981' } },
        { value: d.medium.count, name: 'Medium', itemStyle: { color: '#f59e0b' } },
        { value: d.high.count, name: 'High', itemStyle: { color: '#ef4444' } },
      ]
    }]
  })
}

const renderLine = () => {
  if (!lineChart.value) return
  if (lineInstance) lineInstance.dispose()
  lineInstance = echarts.init(lineChart.value)
  const data = store.timeseries
  if (!data.length) return

  lineInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: data.map(d => d.period),
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisLabel: { color: '#9ca3af', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      name: 'Avg Stress',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f3f4f6' } },
      axisLabel: { color: '#9ca3af' }
    },
    series: [{
      data: data.map(d => d.avg_stress),
      type: 'line',
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 2 },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(59,130,246,0.3)' }, { offset: 1, color: 'rgba(59,130,246,0.05)' }] } },
      itemStyle: { color: '#3b82f6' },
      symbol: 'circle',
      symbolSize: 6,
    }]
  })
}

onMounted(async () => {
  await Promise.all([store.fetchSummary(), store.fetchDistribution(), store.fetchTimeseries('hour')])
  summary.value = store.summary
  renderPie()
  renderLine()
})
</script>