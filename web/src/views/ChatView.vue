<script setup lang="ts">
import { ref, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import MessageList from '@/components/MessageList.vue'
import MessageInput from '@/components/MessageInput.vue'

const store = useChatStore()
const messagesContainer = ref<HTMLElement | null>(null)

const scrollToBottom = (force = false) => {
  nextTick(() => {
    if (messagesContainer.value) {
      const container = messagesContainer.value
      const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 200
      if (force || isNearBottom) {
        container.scrollTop = container.scrollHeight
      }
    }
  })
}

watch(() => store.messages.length, () => scrollToBottom())

onMounted(() => {
  scrollToBottom(true)
  
  // Listen for session switch to scroll to bottom
  window.addEventListener('chat-session-switched', () => {
    scrollToBottom(true)
  })
})

onUnmounted(() => {
  window.removeEventListener('chat-session-switched', () => {})
})

// Mobile: exit chat mode and show session list
const exitChat = () => {
  store.isChatMode = false
  store.currentView = 'chatList'
}
</script>

<template>
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Top Bar -->
    <div 
      class="p-3 border-b flex items-center justify-between"
      :class="store.isDarkMode ? 'border-gray-700' : 'bg-white border-gray-200'"
    >
      <!-- Left: Back button (mobile only) + Agent info -->
      <div class="flex items-center gap-2">
        <!-- Back button (show on mobile when in chat mode) -->
        <button 
          v-if="store.isChatMode"
          @click="exitChat"
          class="md:hidden p-2 -ml-2"
          :class="store.isDarkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-100'"
        >
          <i class="bi bi-arrow-left text-lg"></i>
        </button>
        
        <!-- Agent info -->
        <span class="text-lg">{{ store.selectedAgent.identity.emoji }}</span>
        <span 
          class="text-sm font-medium"
          :class="store.isDarkMode ? 'text-white' : 'text-gray-900'"
        >{{ store.selectedAgent.identity.name }}</span>
        <span v-if="store.currentSession" class="text-xs opacity-60 font-mono ml-1 text-blue-400">{{ store.sessions.find(s => s.id === store.currentSession || s.key === store.currentSession)?.key }}</span>
      </div>

    </div>

    <!-- Messages -->
    <div 
      ref="messagesContainer" 
      class="flex-1 overflow-y-auto p-4 space-y-4"
      :class="store.isDarkMode ? 'bg-gray-900' : 'bg-gray-50'"
    >
      <div 
        v-if="store.messages.length === 0" 
        class="flex items-center justify-center h-full"
      >
        <div class="text-center">
          <div class="text-6xl mb-4">{{ store.selectedAgent.identity.emoji }}</div>
          <h2 
            class="text-2xl font-bold mb-2"
            :class="store.isDarkMode ? 'text-white' : 'text-gray-900'"
          >嗨，我是 {{ store.selectedAgent.identity.name }}</h2>
          <p 
            class="opacity-60"
            :class="store.isDarkMode ? 'text-gray-400' : 'text-gray-500'"
          >{{ store.selectedAgent.identity.theme }}</p>
        </div>
      </div>
      <MessageList v-else />
    </div>

    <!-- Input -->
    <MessageInput @sent="scrollToBottom(true)" />
  </div>
</template>
