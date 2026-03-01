<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { marked } from 'marked'

const store = useChatStore()

const loadBoard = async () => {
  store.boardLoading = true
  try {
    const resp = await fetch('/api/board')
    const data = await resp.json()
    store.boardContent = data.content || data.error || '無法載入留言板'
  } catch (e: any) {
    store.boardContent = '載入失敗: ' + e.message
  }
  store.boardLoading = false
}

onMounted(() => {
  loadBoard()
})

watch(() => store.currentView, (v) => {
  if (v === 'board') loadBoard()
})
</script>

<template>
  <div 
    class="view-content flex-1 overflow-y-auto p-4 md:p-6"
    :class="store.isDarkMode ? 'bg-[#0f0f0f]' : 'bg-gray-50'"
  >
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold flex items-center gap-3">
          <span 
            class="w-10 h-10 rounded-xl flex items-center justify-center"
            :class="store.isDarkMode ? 'bg-blue-500' : 'bg-blue-500'"
          >
            <i class="bi bi-chat-square-text text-white"></i>
          </span>
          公共留言板
        </h2>
        
        <button 
          @click="loadBoard"
          :disabled="store.boardLoading"
          class="p-2 rounded-lg transition-colors"
          :class="store.isDarkMode 
            ? 'bg-dark-secondary hover:bg-dark-hover text-gray-400' 
            : 'bg-white hover:bg-gray-100 text-gray-600'"
        >
          <i class="bi bi-arrow-clockwise" :class="store.boardLoading ? 'animate-spin' : ''"></i>
        </button>
      </div>

      <!-- Content -->
      <div 
        class="rounded-2xl border overflow-hidden"
        :class="store.isDarkMode 
          ? 'bg-dark-secondary border-dark-border shadow-lg shadow-black/20' 
          : 'bg-white border-gray-200 shadow-md'"
      >
        <!-- Loading -->
        <div 
          v-if="store.boardLoading && !store.boardContent" 
          class="flex flex-col items-center justify-center py-16"
        >
          <div class="w-12 h-12 border-4 border-t-transparent rounded-full animate-spin mb-4 border-blue-500"></div>
          <p :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-400'">載入中...</p>
        </div>

        <!-- Empty -->
        <div 
          v-else-if="!store.boardContent" 
          class="text-center py-12"
          :class="store.isDarkMode ? 'text-gray-500' : 'text-gray-400'"
        >
          <i class="bi bi-inbox text-4xl mb-4 block"></i>
          <p>尚無留言</p>
        </div>

        <!-- Content -->
        <div 
          v-else 
          class="p-6 markdown-body"
          :class="store.isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          v-html="marked(store.boardContent)"
        ></div>
      </div>
    </div>
  </div>
</template>
