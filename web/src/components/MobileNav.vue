<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import type { ViewType } from '@/types/index'

const store = useChatStore()

const tabs = [
  { key: 'chatList', icon: 'bi-chat-dots', label: '對話' },
  { key: 'board', icon: 'bi-chat-square-text', label: '留言' },
  { key: 'schedule', icon: 'bi-clock', label: '排程' },
  { key: 'manage', icon: 'bi-gear', label: '管理' },
  { key: 'config', icon: 'bi-sliders', label: '配置' },
] as const

const selectSession = (session: any) => {
  store.switchSession(session)
}

const onTabClick = (key: string) => {
  store.isChatMode = false
  store.currentView = (key === 'chatList' ? 'chatList' : key) as ViewType
}

const getSourceIcon = (source?: string) => {
  const icons: Record<string, string> = {
    telegram: '📱',
    discord: '💬',
    webchat: '🌐',
    cron: '⏰'
  }
  return icons[source || ''] || '💬'
}

const getSessionAge = (updatedAt?: number) => {
  if (!updatedAt) return ""
  const diff = Date.now() - updatedAt
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return "剛剛"
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h`
  const days = Math.floor(hours / 24)
  return `${days}d`
}

const isChatTab = () => {
  return store.currentView === 'chatList' || store.currentView === 'chat'
}
</script>

<template>
  <div 
    class="lg:hidden fixed bottom-0 left-0 right-0 z-[100] flex flex-col"
    :class="store.isDarkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'"
    style="padding-bottom: env(safe-area-inset-bottom, 0px);"
  >
    <!-- Session List (when on chat tab) -->
    <div v-if="isChatTab()" class="flex-1 overflow-y-auto" style="max-height: 60vh;">
      <button 
        v-for="session in store.displayedSessions" 
        :key="session.id"
        @click="selectSession(session)"
        class="w-full p-4 flex items-center gap-3 text-left border-b dark:border-gray-700 dark:hover:bg-gray-800 hover:bg-gray-50"
      >
        <div 
          class="w-12 h-12 rounded-full flex items-center justify-center text-xl flex-shrink-0 dark:bg-gray-800 bg-gray-100"
        >
          {{ getSourceIcon(session.source) }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="font-medium truncate dark:text-white text-gray-900">{{ session.name }}</div>
          <div class="text-xs dark:text-gray-400 text-gray-500 truncate">{{ session.preview || '尚無訊息' }}</div>
        </div>
        <div class="text-xs dark:text-gray-500 text-gray-400">{{ getSessionAge(session.updatedAt) }}</div>
      </button>
    </div>

    <!-- Bottom Nav -->
    <nav 
      class="border-t flex dark:border-gray-700"
    >
      <button 
        v-for="tab in tabs"
        :key="tab.key"
        @click="onTabClick(tab.key)"
        class="flex-1 py-3 flex flex-col items-center gap-0.5"
        :class="(tab.key === 'chatList' ? isChatTab() : store.currentView === tab.key) ? 'text-blue-500' : 'dark:text-gray-400 text-gray-500'"
      >
        <i class="bi text-xl" :class="tab.icon"></i>
        <span class="text-[10px]">{{ tab.label }}</span>
      </button>
    </nav>
  </div>
</template>
