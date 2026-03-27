<script setup lang="ts">
import { useChatStore } from '@/stores/chat'

const store = useChatStore()

const getSourceIcon = (source?: string) => {
  const icons: Record<string, string> = {
    telegram: '📱',
    discord: '💬',
    webchat: '🌐',
    cron: '⏰'
  }
  return icons[source || ''] || '💬'
}
</script>

<template>
  <aside 
    class="w-64 flex flex-col border-r"
    :class="store.isDarkMode ? 'bg-dark-bg border-dark-border' : 'bg-gray-50 border-gray-200'"
  >
    <!-- Header -->
    <div class="p-4 border-b flex items-center justify-between"
      :class="store.isDarkMode ? 'border-dark-border' : 'border-gray-200'"
    >
      <h2 class="font-bold" :class="store.isDarkMode ? 'text-white' : 'text-gray-900'">對話</h2>
      <div class="flex gap-1">
        <button 
          @click="store.fetchSessions()"
          class="p-2 rounded-lg transition-colors hover:bg-dark-hover"
          :class="store.isDarkMode ? 'hover:bg-dark-hover' : 'hover:bg-gray-200'"
          title="重新整理"
        >
          <i class="bi bi-arrow-clockwise"></i>
        </button>
        <button 
          @click="store.showNewChatModal = true"
          class="p-2 rounded-lg transition-colors text-blue-500"
          :class="store.isDarkMode ? 'hover:bg-dark-hover' : 'hover:bg-gray-200'"
          title="新對話"
        >
          <i class="bi bi-plus-circle text-xl"></i>
        </button>
      </div>
    </div>

    <!-- Agent Filter -->
    <div class="px-2 py-2 border-b"
      :class="store.isDarkMode ? 'border-dark-border' : 'border-gray-200'"
    >
      <select 
        v-model="store.selectedFilterAgent"
        class="w-full rounded-lg px-3 py-2 text-sm border"
        :class="store.isDarkMode ? 'bg-dark-hover border-dark-border text-white' : 'bg-white border-gray-200 text-gray-900'"
      >
        <option value="">所有 Agent</option>
        <option v-for="agent in store.agents" :key="agent.id" :value="agent.id">
          {{ agent.identity.emoji }} {{ agent.identity.name }}
        </option>
      </select>
    </div>

    <!-- Session List -->
    <div class="flex-1 overflow-y-auto p-2">
      <button 
        v-for="session in store.displayedSessions" 
        :key="session.id"
        @click="console.log('Sidebar click:', session.id, session.key, 'currentSession:', store.currentSession); store.switchSession(session)"
        class="w-full p-3 rounded-lg flex items-center gap-3 mb-1 transition-colors text-left"
        :class="(session.id === store.currentSession || session.key === store.currentSession) 
          ? (store.isDarkMode ? 'bg-blue-500 text-white' : 'bg-blue-600 text-white') 
          : (store.isDarkMode ? 'hover:bg-dark-hover bg-gray-800 text-white' : 'hover:bg-gray-100 bg-white text-gray-900')"
      >
        <div 
          class="w-10 h-10 rounded-full flex items-center justify-center text-lg flex-shrink-0"
          :class="(session.id === store.currentSession || session.key === store.currentSession) ? (store.isDarkMode ? 'bg-white/20' : 'bg-white/30') : (store.isDarkMode ? 'bg-dark-border' : 'bg-gray-200')"
        >
          {{ getSourceIcon(session.source) }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="font-medium truncate" :class="store.isDarkMode ? 'text-white' : 'text-gray-900'">{{ session.name }}</div>
          <div class="text-xs truncate opacity-80 font-mono text-yellow-400">ID: {{ session.id?.slice(0, 12) }}</div>
          <div class="text-xs truncate opacity-80 font-mono text-blue-300">KEY: {{ session.key?.slice(0, 30) }}</div>
          <div class="text-xs truncate opacity-70">
            <span class="text-green-400" v-if="session.key && session.key.startsWith('agent:') && !session.key.includes('agent:agent')">✓</span>
            <span class="text-red-400" v-else>⚠</span>
            <span v-if="store.agents.find(a => a.id === session.agentId)" class="ml-1">
              {{ store.agents.find(a => a.id === session.agentId)?.identity.emoji }}
            </span>
            <span v-else>{{ session.preview || '尚無訊息' }}</span>
          </div>
        </div>
      </button>
    </div>

    <!-- Bottom Nav -->
    <div 
      class="p-2 border-t flex justify-around"
      :class="store.isDarkMode ? 'border-dark-border' : 'border-gray-200'"
    >
      <button 
        @click="store.currentView = 'chat'"
        class="p-2 rounded-lg transition-colors"
        :class="store.currentView === 'chat' ? (store.isDarkMode ? 'bg-blue-500 text-white' : 'bg-blue-500 text-white') : (store.isDarkMode ? 'text-gray-400' : 'text-gray-500')"
        title="對話"
      >
        <i class="bi bi-chat-dots"></i>
      </button>
      <button 
        @click="store.currentView = 'board'"
        class="p-2 rounded-lg transition-colors"
        :class="store.currentView === 'board' ? (store.isDarkMode ? 'bg-blue-500 text-white' : 'bg-blue-500 text-white') : (store.isDarkMode ? 'text-gray-400' : 'text-gray-500')"
        title="留言板"
      >
        <i class="bi bi-chat-square-text"></i>
      </button>
      <button 
        @click="store.currentView = 'schedule'"
        class="p-2 rounded-lg transition-colors"
        :class="store.currentView === 'schedule' ? (store.isDarkMode ? 'bg-blue-500 text-white' : 'bg-blue-500 text-white') : (store.isDarkMode ? 'text-gray-400' : 'text-gray-500')"
        title="排程"
      >
        <i class="bi bi-clock"></i>
      </button>
      <button 
        @click="store.currentView = 'manage'"
        class="p-2 rounded-lg transition-colors"
        :class="store.currentView === 'manage' ? (store.isDarkMode ? 'bg-blue-500 text-white' : 'bg-blue-500 text-white') : (store.isDarkMode ? 'text-gray-400' : 'text-gray-500')"
        title="管理"
      >
        <i class="bi bi-gear"></i>
      </button>
      <button 
        @click="store.currentView = 'config'"
        class="p-2 rounded-lg transition-colors"
        :class="store.currentView === 'config' ? (store.isDarkMode ? 'bg-blue-500 text-white' : 'bg-blue-500 text-white') : (store.isDarkMode ? 'text-gray-400' : 'text-gray-500')"
        title="配置"
      >
        <i class="bi bi-sliders"></i>
      </button>
      <button 
        @click="store.toggleTheme"
        class="p-2 rounded-lg transition-colors"
        :class="store.isDarkMode ? 'text-yellow-400' : 'text-gray-600'"
        :title="store.isDarkMode ? '淺色模式' : '深色模式'"
      >
        <i class="bi" :class="store.isDarkMode ? 'bi-sun' : 'bi-moon'"></i>
      </button>
    </div>
  </aside>
</template>
