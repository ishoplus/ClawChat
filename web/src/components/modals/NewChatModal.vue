<script setup lang="ts">
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
</script>

<template>
  <div 
    class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
    @click.self="store.showNewChatModal = false"
  >
    <div 
      class="rounded-2xl w-full max-w-md shadow-2xl overflow-hidden"
      :class="store.isDarkMode ? 'bg-dark-secondary' : 'bg-white'"
    >
      <!-- Header -->
      <div 
        class="p-4 border-b flex items-center justify-between"
        :class="store.isDarkMode ? 'border-dark-border' : 'border-gray-200'"
      >
        <h3 class="font-bold text-lg">新對話</h3>
        <button 
          @click="store.showNewChatModal = false" 
          class="p-2 rounded-lg transition-colors"
          :class="store.isDarkMode ? 'hover:bg-dark-hover' : 'hover:bg-gray-100'"
        >
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <!-- Body -->
      <div class="p-4">
        <p 
          class="text-sm mb-4"
          :class="store.isDarkMode ? 'text-gray-400' : 'text-gray-500'"
        >
          選擇一個 Agent 開始新對話
        </p>
        
        <div class="space-y-2 max-h-[60vh] overflow-y-auto">
          <button
            v-for="agent in store.agents"
            :key="agent.id"
            @click="store.createNewSession(agent)"
            class="w-full p-4 rounded-xl flex items-center gap-3 transition-colors text-left"
            :class="store.isDarkMode 
              ? 'bg-dark-hover hover:bg-dark-border' 
              : 'bg-gray-100 hover:bg-gray-200'"
          >
            <span class="text-2xl">{{ agent.identity.emoji }}</span>
            <div class="flex-1">
              <div class="font-medium">{{ agent.identity.name }}</div>
              <div class="text-xs opacity-60">{{ agent.identity.theme }}</div>
            </div>
            <i class="bi bi-chevron-right opacity-50"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
