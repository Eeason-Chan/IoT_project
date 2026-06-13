<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
      <h2 class="text-lg font-semibold text-gray-800">Data Records</h2>
      <div class="flex gap-2">
        <button v-for="s in ['record_id','stress_index','traffic_density']" :key="s" @click="sortBy(s)" :class="['px-3 py-1 text-xs rounded-lg', currentSort===s?'bg-blue-500 text-white':'bg-gray-100 text-gray-600']">{{ s }}</button>
      </div>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="p-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
            <th class="p-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Density</th>
            <th class="p-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Horn/min</th>
            <th class="p-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Speed</th>
            <th class="p-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Signal Wait</th>
            <th class="p-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Weather</th>
            <th class="p-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Road Quality</th>
            <th class="p-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Driver</th>
            <th class="p-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stress</th>
            <th class="p-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Level</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="r in store.records.items" :key="r.record_id" class="hover:bg-gray-50 transition-colors">
            <td class="p-3 text-gray-800 font-medium">{{ r.record_id }}</td>
            <td class="p-3 text-gray-600">{{ r.traffic_density }}</td>
            <td class="p-3 text-gray-600">{{ r.horn_events_per_min }}</td>
            <td class="p-3 text-gray-600">{{ r.avg_speed }}</td>
            <td class="p-3 text-gray-600">{{ r.signal_wait_time }}</td>
            <td class="p-3 text-gray-600">{{ r.weather_condition }}</td>
            <td class="p-3 text-gray-600">{{ r.road_quality_score }}</td>
            <td class="p-3 text-gray-600">{{ r.driver_experience_level }}</td>
            <td class="p-3 text-gray-600">{{ r.stress_index }}</td>
            <td class="p-3">
              <span :class="['px-2 py-1 rounded-full text-xs font-medium text-white', r.stress_level=='High'?'bg-red-500':r.stress_level=='Medium'?'bg-yellow-500':'bg-green-500']">
                {{ r.stress_level }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="px-5 py-3 border-t border-gray-100 flex items-center justify-between bg-gray-50">
      <button @click="prevPage" :disabled="page<=1" class="px-4 py-1.5 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">Previous</button>
      <span class="text-sm text-gray-500">Page {{ page }} of {{ Math.ceil(store.records.total/pageSize) || 1 }}</span>
      <button @click="nextPage" class="px-4 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600">Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTrafficStore } from '../stores'

const store = useTrafficStore()
const page = ref(1)
const pageSize = 20
const currentSort = ref('record_id')

const prevPage = () => { page.value--; load() }
const nextPage = () => { page.value++; load() }
const sortBy = (s) => { currentSort.value = s; page.value = 1; load() }
const load = async () => { await store.fetchRecords(page.value, pageSize) }

onMounted(load)
</script>