<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'

const store = useChatStore()

const fetchManageData = async () => {
  try {
    const [statusRes, agentsRes, channelsRes, sessionsRes] = await Promise.all([
      fetch('/api/status'),
      fetch('/api/agents'),
      fetch('/api/channels'),
      fetch('/api/sessions')
    ])
    
    const statusData = await statusRes.json()
    const agentsData = await agentsRes.json()
    const channelsData = await channelsRes.json()
    const sessionsData = await sessionsRes.json()
    
    store.systemStatus = { 
      status: statusData.status || 'unknown',
      gateway: statusData.gateway,
      ngrokUrl: statusData.ngrokUrl
    }
    store.manageAgents = agentsData.agents || []
    store.manageChannels = channelsData.channels || {}
    store.manageSessions = sessionsData.sessions || []
  } catch (e) {
    store.systemStatus.status = 'error'
  }
}

onMounted(() => fetchManageData())
watch(() => store.currentView, (v) => { if (v === 'manage') fetchManageData() })
</script>

<template>
  <div 
    class="view-content flex-1 overflow-y-auto p-4"
    :class="store.isDarkMode ? 'bg-[#0f0f0f]' : 'bg-gray-50'"
  >
    <div class="max-w-2xl mx-auto">
      <!-- Status Card -->
      <div class="mb-6">
        <h3 
          class="text-xs uppercase tracking-wider mb-3"
          :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-500'"
        >
          系統狀態
        </h3>
        <div 
          class="rounded-lg p-4 border space-y-3"
          :class="store.isDarkMode ? 'bg-dark-secondary border-dark-border' : 'bg-white border-gray-200'"
        >
          <div class="flex items-center gap-3">
            <div 
              class="w-3 h-3 rounded-full"
              :class="store.systemStatus.status === 'online' ? 'bg-green-500' : 'bg-red-500'"
            ></div>
            <span class="font-medium">Gateway {{ store.systemStatus.status }}</span>
          </div>
          
          <div v-if="store.systemStatus.ngrokUrl">
            <div 
              class="text-xs mb-2"
              :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-400'"
            >
              公開網址
            </div>
            <a 
              :href="store.systemStatus.ngrokUrl" 
              target="_blank"
              class="text-blue-400 hover:text-blue-300 text-sm break-all"
            >
              {{ store.systemStatus.ngrokUrl }}
            </a>
          </div>
        </div>
      </div>

      <!-- Agents -->
      <div class="mb-6">
        <h3 
          class="text-xs uppercase tracking-wider mb-3"
          :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-500'"
        >
          Agents ({{ store.manageAgents.length }})
        </h3>
        <div class="space-y-2">
          <div 
            v-for="agent in store.manageAgents" 
            :key="agent.id"
            class="rounded-lg p-3 border flex items-center gap-3"
            :class="store.isDarkMode 
              ? 'bg-dark-secondary border-dark-border hover:border-dark-hover' 
              : 'bg-white border-gray-200 hover:border-gray-300'"
          >
            <span class="text-2xl">{{ agent.identity?.emoji || '🤖' }}</span>
            <div class="flex-1 min-w-0">
              <div class="font-medium truncate">{{ agent.name || agent.id }}</div>
              <div 
                class="text-xs truncate"
                :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-400'"
              >
                {{ agent.id }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Channels -->
      <div class="mb-6">
        <h3 
          class="text-xs uppercase tracking-wider mb-3"
          :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-500'"
        >
          Channels
        </h3>
        <div class="space-y-2">
          <div 
            v-for="(info, name) in store.manageChannels" 
            :key="name"
            class="rounded-lg p-3 border flex items-center gap-3"
            :class="store.isDarkMode 
              ? 'bg-dark-secondary border-dark-border' 
              : 'bg-white border-gray-200'"
          >
            <div 
              class="w-10 h-10 rounded-lg flex items-center justify-center text-xl"
              :class="store.isDarkMode ? 'bg-green-500/20' : 'bg-green-100'"
            >
              📱
            </div>
            <div class="flex-1">
              <div class="font-medium capitalize">{{ name }}</div>
              <div 
                class="text-xs"
                :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-400'"
              >
                {{ info.accountCount || 0 }} accounts
              </div>
            </div>
            <span 
              class="text-xs px-2 py-1 rounded"
              :class="info.enabled 
                ? 'bg-green-500/20 text-green-400' 
                : 'bg-red-500/20 text-red-400'"
            >
              {{ info.enabled ? 'Enabled' : 'Disabled' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Gateway Config -->
      <div>
        <h3 
          class="text-xs uppercase tracking-wider mb-3"
          :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-500'"
        >
          Gateway
        </h3>
        <div 
          class="rounded-lg p-3 border text-sm"
          :class="store.isDarkMode ? 'bg-dark-secondary border-dark-border' : 'bg-white border-gray-200'"
        >
          <div class="flex justify-between py-1">
            <span :class="store.isDarkMode ? 'text-gray-400' : 'text-gray-500'">HTTP Port</span>
            <span>{{ store.systemStatus.gateway?.port || 18789 }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
