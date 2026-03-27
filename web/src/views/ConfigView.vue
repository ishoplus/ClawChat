<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
const config = ref<any>(null)
const loading = ref(true)
const activeTab = ref('agents')

const tabs = [
  { id: 'agents', label: 'Agents', icon: 'bi-robot' },
  { id: 'channels', label: 'Channels', icon: 'bi-chat-dots' },
  { id: 'gateway', label: 'Gateway', icon: 'bi-hdd' },
  { id: 'models', label: 'Models', icon: 'bi-cpu' },
  { id: 'plugins', label: 'Plugins', icon: 'bi-puzzle' },
]

const fetchConfig = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/config')
    const data = await res.json()
    config.value = data.config || data
  } catch (e) {
    console.error('Failed to fetch config:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchConfig())
watch(() => store.currentView, (v) => { if (v === 'config') fetchConfig() })
</script>

<template>
  <div 
    class="flex-1 flex flex-col overflow-hidden"
    :class="store.isDarkMode ? 'bg-[#0f0f0f]' : 'bg-gray-50'"
  >
    <!-- Header -->
    <div 
      class="p-4 border-b flex items-center justify-between"
      :class="store.isDarkMode ? 'border-dark-border' : 'border-gray-200'"
    >
      <h2 class="font-bold text-lg" :class="store.isDarkMode ? 'text-white' : 'text-gray-900'">
        <i class="bi bi-gear me-2"></i>配置
      </h2>
      <button 
        @click="fetchConfig"
        class="p-2 rounded-lg transition-colors"
        :class="store.isDarkMode ? 'hover:bg-dark-hover' : 'hover:bg-gray-100'"
        title="刷新"
      >
        <i class="bi bi-arrow-clockwise"></i>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <i class="bi bi-hourglass-split animate-spin text-2xl mb-2"></i>
        <p class="text-sm opacity-60">載入中...</p>
      </div>
    </div>

    <!-- Tabs -->
    <div v-else class="flex-1 flex flex-col overflow-hidden">
      <div 
        class="flex gap-1 p-2 border-b overflow-x-auto"
        :class="store.isDarkMode ? 'border-dark-border' : 'border-gray-200'"
      >
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-colors"
          :class="activeTab === tab.id 
            ? (store.isDarkMode ? 'bg-blue-500 text-white' : 'bg-blue-500 text-white')
            : (store.isDarkMode ? 'text-gray-400 hover:bg-dark-hover' : 'text-gray-600 hover:bg-gray-100')"
        >
          <i class="bi" :class="tab.icon"></i>
          <span class="ml-1">{{ tab.label }}</span>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-4">
        
        <!-- Agents Tab -->
        <div v-if="activeTab === 'agents'" class="space-y-4">
          <div 
            v-for="agent in config?.agents?.list" 
            :key="agent.id"
            class="rounded-lg border p-4"
            :class="store.isDarkMode ? 'bg-dark-secondary border-dark-border' : 'bg-white border-gray-200'"
          >
            <div class="flex items-center gap-3 mb-2">
              <span class="text-2xl">{{ agent.identity?.emoji || '🤖' }}</span>
              <div>
                <div class="font-medium" :class="store.isDarkMode ? 'text-white' : 'text-gray-900'">
                  {{ agent.identity?.name || agent.name }}
                </div>
                <div class="text-xs opacity-60 font-mono">{{ agent.id }}</div>
              </div>
            </div>
            <div class="text-sm opacity-70" :class="store.isDarkMode ? 'text-gray-400' : 'text-gray-600'">
              {{ agent.identity?.theme || agent.workspace }}
            </div>
            <div class="mt-2 text-xs font-mono opacity-50">
              {{ agent.workspace }}
            </div>
          </div>
        </div>

        <!-- Channels Tab -->
        <div v-else-if="activeTab === 'channels'" class="space-y-4">
          <div 
            v-for="(channelData, channelName) in config?.channels" 
            :key="channelName"
            class="rounded-lg border p-4"
            :class="store.isDarkMode ? 'bg-dark-secondary border-dark-border' : 'bg-white border-gray-200'"
          >
            <div class="font-medium mb-2 flex items-center gap-2" :class="store.isDarkMode ? 'text-white' : 'text-gray-900'">
              <i class="bi bi-chat-dots"></i>
              {{ channelName }}
            </div>
            <div v-if="channelData?.accounts" class="space-y-2">
              <div 
                v-for="(account, accountId) in channelData.accounts" 
                :key="accountId"
                class="text-sm"
              >
                <div class="font-mono opacity-70">{{ accountId }}</div>
                <div class="text-xs ml-2 opacity-50">
                  Bot: {{ account.botToken?.slice(0, 10) }}...{{ account.botToken?.slice(-5) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Gateway Tab -->
        <div v-else-if="activeTab === 'gateway'" class="space-y-4">
          <div 
            class="rounded-lg border p-4"
            :class="store.isDarkMode ? 'bg-dark-secondary border-dark-border' : 'bg-white border-gray-200'"
          >
            <h3 class="font-medium mb-3" :class="store.isDarkMode ? 'text-white' : 'text-gray-900'">Gateway 設置</h3>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="opacity-60">Port</span>
                <span class="font-mono">{{ config?.gateway?.port }}</span>
              </div>
              <div class="flex justify-between">
                <span class="opacity-60">Mode</span>
                <span class="font-mono">{{ config?.gateway?.mode }}</span>
              </div>
              <div class="flex justify-between">
                <span class="opacity-60">Bind</span>
                <span class="font-mono">{{ config?.gateway?.bind }}</span>
              </div>
              <div class="flex justify-between">
                <span class="opacity-60">Auth Mode</span>
                <span class="font-mono">{{ config?.gateway?.auth?.mode }}</span>
              </div>
              <div class="flex justify-between">
                <span class="opacity-60">Token</span>
                <span class="font-mono text-xs">{{ config?.gateway?.auth?.token?.slice(0, 12) }}...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Models Tab -->
        <div v-else-if="activeTab === 'models'" class="space-y-4">
          <div 
            v-for="(provider, name) in config?.models?.providers" 
            :key="name"
            class="rounded-lg border p-4"
            :class="store.isDarkMode ? 'bg-dark-secondary border-dark-border' : 'bg-white border-gray-200'"
          >
            <h3 class="font-medium mb-2" :class="store.isDarkMode ? 'text-white' : 'text-gray-900'">
              {{ name }}
            </h3>
            <div class="text-xs opacity-60 mb-3">{{ provider.baseUrl }}</div>
            <div class="space-y-2">
              <div 
                v-for="model in provider.models" 
                :key="model.id"
                class="flex items-center justify-between text-sm p-2 rounded"
                :class="store.isDarkMode ? 'bg-dark-hover' : 'bg-gray-100'"
              >
                <span>{{ model.name }}</span>
                <span class="text-xs opacity-50 font-mono">{{ model.id }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Plugins Tab -->
        <div v-else-if="activeTab === 'plugins'" class="space-y-4">
          <div 
            v-for="(plugin, name) in config?.plugins?.entries" 
            :key="name"
            class="rounded-lg border p-4 flex items-center justify-between"
            :class="store.isDarkMode ? 'bg-dark-secondary border-dark-border' : 'bg-white border-gray-200'"
          >
            <div class="flex items-center gap-2">
              <i class="bi bi-puzzle"></i>
              <span class="font-medium" :class="store.isDarkMode ? 'text-white' : 'text-gray-900'">{{ name }}</span>
            </div>
            <span 
              class="text-xs px-2 py-1 rounded"
              :class="plugin.enabled ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'"
            >
              {{ plugin.enabled ? 'Enabled' : 'Disabled' }}
            </span>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
