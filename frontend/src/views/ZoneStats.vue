<template>
  <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
    <h2 class="text-lg font-semibold text-gray-800 mb-4">Zone Ranking by Stress Index</h2>
    <div ref="barChart" class="h-96"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { useTrafficStore } from '../stores'

const store = useTrafficStore()
const barChart = ref(null)
let chartInstance = null

onMounted(async () => {
  await store.fetchZoneStats()
  if (barChart.value) {
    chartInstance = echarts.init(barChart.value)
    const data = store.zoneStats

    chartInstance.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '8%', bottom: '3%', top: '3%', containLabel: true },
      xAxis: {
        type: 'value',
        name: 'Avg Stress Index',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f3f4f6' } },
        axisLabel: { color: '#9ca3af' }
      },
      yAxis: {
        type: 'category',
        data: data.map(d => d.zone),
        axisLine: { lineStyle: { color: '#e5e7eb' } },
        axisLabel: { color: '#6b7280', fontSize: 11 }
      },
      series: [{
        type: 'bar',
        data: data.map(d => ({
          value: d.avg_stress,
          itemStyle: {
            color: d.avg_stress > 60 ? '#ef4444' : d.avg_stress > 45 ? '#f59e0b' : '#10b981',
            borderRadius: [0, 4, 4, 0]
          }
        })),
        barWidth: 18,
        label: { show: true, position: 'right', formatter: '{c}', color: '#6b7280', fontSize: 11 }
      }]
    })
  }
})
</script>