import { defineStore } from 'pinia'
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const useTrafficStore = defineStore('traffic', {
  state: () => ({
    summary: null,
    distribution: null,
    timeseries: [],
    zoneStats: [],
    records: { items: [], total: 0 },
  }),
  actions: {
    async fetchSummary() {
      const { data } = await api.get('/traffic/summary')
      this.summary = data
    },
    async fetchDistribution() {
      const { data } = await api.get('/traffic/distribution')
      this.distribution = data
    },
    async fetchTimeseries(granularity = 'hour') {
      const { data } = await api.get(`/traffic/timeseries?granularity=${granularity}`)
      this.timeseries = data
    },
    async fetchZoneStats() {
      const { data } = await api.get('/traffic/zone-stats')
      this.zoneStats = data
    },
    async fetchRecords(page = 1, pageSize = 20) {
      const { data } = await api.get(`/traffic/records?page=${page}&page_size=${pageSize}`)
      this.records = data
    },
  }
})

export const useXAIStore = defineStore('xai', {
  state: () => ({
    shapGlobal: [],
    shapLocal: null,
    limeLocal: null,
    shapSummary: [],
    compare: null,
  }),
  actions: {
    async fetchSHAPGlobal() {
      const { data } = await api.get('/xai/shap/global')
      this.shapGlobal = data.features
    },
    async fetchSHAPLocal(recordId) {
      const { data } = await api.get(`/xai/shap/local/${recordId}`)
      this.shapLocal = data
    },
    async fetchSHAPSummary() {
      const { data } = await api.get('/xai/shap/summary')
      this.shapSummary = data.data
    },
    async fetchLIMELocal(recordId) {
      const { data } = await api.get(`/xai/lime/local/${recordId}`)
      this.limeLocal = data
    },
    async fetchCompare(recordId) {
      const { data } = await api.get(`/xai/compare/${recordId}`)
      this.compare = data
    },
  }
})

export const useSystemStore = defineStore('system', {
  state: () => ({
    health: null,
    stats: null,
  }),
  actions: {
    async fetchHealth() {
      const { data } = await api.get('/system/health')
      this.health = data
    },
    async fetchStats() {
      const { data } = await api.get('/system/stats')
      this.stats = data
    },
  }
})