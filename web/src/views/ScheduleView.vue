<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'

const store = useChatStore()

const loadSchedules = async () => {
  store.scheduleLoading = true
  try {
    const [schedulesResp, cronsResp] = await Promise.all([
      fetch('/api/schedules'),
      fetch('/api/cron')
    ])
    const schedulesData = await schedulesResp.json()
    const cronsData = await cronsResp.json()
    
    store.schedules = schedulesData.schedules || []
    store.cronJobs = cronsData.jobs || []
  } catch (e) {
    console.error('載入排程失敗:', e)
  }
  store.scheduleLoading = false
}

const getJobIcon = (target?: string) => {
  const icons: Record<string, string> = {
    isolated: '🔧', code: '💻', rich: '💰', 'skill-manager': '🛡️',
    startup: '🚀', travel: '✈️', chef: '🍳', ip: '📋', nexchip: '🔬',
    shared: '📋', main: '⚡️'
  }
  return icons[target || ''] || '🤖'
}

onMounted(() => loadSchedules())
watch(() => store.currentView, (v) => { if (v === 'schedule') loadSchedules() })
</script>

<template>
  <div 
    class="view-content flex-1 overflow-y-auto p-4"
    :class="store.isDarkMode ? 'bg-[#0f0f0f]' : 'bg-white'"
  >
    <!-- Loading -->
    <div v-if="store.scheduleLoading" class="flex items-center justify-center h-64">
      <div class="text-center" :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-400'">
        <i class="bi bi-hourglass-split animate-spin text-3xl"></i>
        <p class="mt-2">載入中...</p>
      </div>
    </div>

    <div v-else class="max-w-7xl mx-auto">
      <!-- Header -->
      <div 
        class="rounded-xl p-4 mb-4 border"
        :class="store.isDarkMode ? 'bg-dark-secondary border-dark-border' : 'bg-gray-100 border-gray-200'"
      >
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold flex items-center gap-2" :class="store.isDarkMode ? 'text-white' : 'text-gray-900'">
            <i class="bi bi-clock"></i>
            排程總覽
          </h2>
          <button 
            @click="loadSchedules"
            class="p-2 rounded-lg transition-colors"
            :class="store.isDarkMode ? 'hover:bg-dark-hover text-gray-400' : 'hover:bg-gray-200 text-gray-600'"
          >
            <i class="bi bi-arrow-clockwise"></i>
          </button>
        </div>
      </div>

      <!-- Stats -->
      <div class="flex gap-2 mb-4">
        <span 
          class="px-3 py-1.5 rounded-md text-sm font-medium"
          :class="store.isDarkMode ? 'bg-dark-secondary text-white' : 'bg-gray-100 text-gray-700'"
        >
          全部 ({{ store.cronJobs.length }})
        </span>
        <span class="px-3 py-1.5 rounded-md text-sm font-medium text-green-500">
          啟用 ({{ store.cronJobs.filter(j => j.enabled).length }})
        </span>
        <span 
          class="px-3 py-1.5 rounded-md text-sm font-medium"
          :class="store.isDarkMode ? 'text-gray-400' : 'text-gray-500'"
        >
          停用 ({{ store.cronJobs.filter(j => !j.enabled).length }})
        </span>
      </div>

      <!-- Jobs -->
      <div class="grid gap-3">
        <div 
          v-if="store.cronJobs.length === 0"
          class="text-center py-12"
          :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-400'"
        >
          <i class="bi bi-clock text-4xl mb-4 block"></i>
          <p :class="store.isDarkMode ? 'text-gray-400' : 'text-gray-500'">尚無排程任務</p>
        </div>

        <div 
          v-for="job in store.cronJobs" 
          :key="job.id"
          class="rounded-xl border overflow-hidden"
          :class="store.isDarkMode 
            ? 'bg-dark-secondary border-dark-border hover:border-dark-hover' 
            : 'bg-white border-gray-200 hover:border-gray-300'"
        >
          <!-- Header -->
          <div 
            class="p-4 cursor-pointer"
            @click="store.expandedJob = store.expandedJob === job.id ? null : job.id"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div 
                  class="w-3 h-3 rounded-full"
                  :class="job.enabled ? 'bg-green-500 animate-pulse' : 'bg-gray-500'"
                ></div>
                <span class="text-xl">{{ getJobIcon(job.sessionTarget) }}</span>
                <div>
                  <h4 class="font-semibold" :class="store.isDarkMode ? 'text-white' : 'text-gray-900'">{{ job.name }}</h4>
                  <p 
                    class="text-sm font-mono"
                    :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-500'"
                  >{{ job.schedule }}</p>
                </div>
              </div>
              
              <div class="flex items-center gap-3">
                <span 
                  v-if="job.nextRun"
                  class="text-sm text-green-500 hidden sm:block"
                >
                  下次: {{ job.nextRun }}
                </span>
                <span 
                  class="text-xs px-2 py-1 rounded"
                  :class="job.enabled 
                    ? 'bg-green-500/20 text-green-400' 
                    : 'bg-gray-500/20 text-gray-400'"
                >
                  {{ job.enabled ? '啟用' : '停用' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Expanded Details -->
          <div 
            v-if="store.expandedJob === job.id"
            class="border-t p-4 space-y-3"
            :class="store.isDarkMode ? 'border-dark-border bg-dark-hover/30' : 'border-gray-200 bg-gray-50'"
          >
            <div class="grid grid-cols-2 gap-3">
              <div 
                class="rounded-lg p-3"
                :class="store.isDarkMode ? 'bg-dark-secondary' : 'bg-white'"
              >
                <p class="text-xs mb-1" :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-400'">目標</p>
                <p class="font-medium">{{ job.sessionTarget || '全局' }}</p>
              </div>
              <div 
                class="rounded-lg p-3"
                :class="store.isDarkMode ? 'bg-dark-secondary' : 'bg-white'"
              >
                <p class="text-xs mb-1" :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-400'">狀態</p>
                <p :class="job.lastStatus === 'ok' ? 'text-green-500' : 'text-red-400'">
                  {{ job.lastStatus || 'unknown' }}
                </p>
              </div>
            </div>
            
            <div v-if="job.lastError" 
              class="p-3 rounded-lg border border-red-500/30 bg-red-500/10"
            >
              <span class="text-sm text-red-400">錯誤：{{ job.lastError }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
