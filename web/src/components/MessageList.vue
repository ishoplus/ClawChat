<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import { marked } from 'marked'

const store = useChatStore()

const renderContent = (content: string | { type: string; text?: string }[]) => {
  const text = Array.isArray(content) 
    ? content.find((c: any) => c.type === 'text')?.text || ''
    : content
  try {
    return marked.parse(text) as string
  } catch {
    return text
  }
}

const copyMessage = async (content: string | { type: string; text?: string }[]) => {
  const text = Array.isArray(content) 
    ? content.find((c: any) => c.type === 'text')?.text || ''
    : content
  try {
    await navigator.clipboard.writeText(text)
    store.showToast('已複製到剪貼簿')
  } catch {
    store.showToast('複製失敗', 'error')
  }
}
</script>

<template>
  <div>
    <div 
      v-for="(msg, idx) in store.messages" 
      :key="idx"
      class="flex gap-3"
      :class="msg.role === 'user' ? 'flex-row-reverse' : ''"
    >
      <!-- Avatar -->
      <div 
        class="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xl"
        :class="msg.role === 'user' 
          ? (store.isDarkMode ? 'bg-dark-hover' : 'bg-gray-200') 
          : msg.role === 'toolResult'
            ? (store.isDarkMode ? 'bg-purple-900' : 'bg-purple-100')
            : (store.isDarkMode ? 'bg-dark-secondary' : 'bg-gray-100')"
      >
        {{ msg.role === 'user' ? '👤' : msg.role === 'toolResult' ? '🔧' : store.selectedAgent.identity.emoji }}
      </div>

      <!-- Content -->
      <div 
        class="max-w-[70%] rounded-lg"
        :class="msg.role === 'user' 
          ? 'bg-blue-500 text-white' 
          : msg.role === 'toolResult'
            ? (store.isDarkMode ? 'bg-purple-900/50 text-purple-100' : 'bg-purple-50 text-purple-900')
            : (store.isDarkMode ? 'bg-dark-secondary text-white' : 'bg-gray-100 text-gray-700')"
      >
        <!-- Header -->
        <div class="flex items-center justify-between gap-2 px-3 pt-2 pb-1">
          <span class="text-[10px] opacity-50">{{ store.formatTime(msg.timestamp) }}</span>
          <button 
            v-if="msg.role !== 'user'"
            @click="copyMessage(msg.content)"
            class="text-xs opacity-50 hover:opacity-100"
            title="複製訊息"
          >
            <i class="bi bi-clipboard"></i>
          </button>
        </div>

        <!-- Body -->
        <div class="p-3">
          <!-- Images -->
          <div v-if="msg.images?.length" class="mb-2 flex gap-1 flex-wrap">
            <img 
              v-for="(img, i) in msg.images" 
              :key="i"
              :src="img" 
              class="max-w-32 max-h-32 rounded"
            >
          </div>

          <!-- Content -->
          <div 
            v-if="msg.role === 'assistant' || msg.role === 'toolResult'" 
            class="markdown-body"
            v-html="renderContent(msg.content)"
          ></div>
          <div v-else-if="msg.role === 'user'" class="whitespace-pre-wrap">
            {{ typeof msg.content === 'string' ? msg.content : msg.content.find?.((c: any) => c.type === 'text')?.text }}
          </div>

          <!-- Thinking -->
          <div 
            v-if="msg.thinking" 
            class="mt-2 p-2 bg-yellow-900/30 border border-yellow-700/50 rounded text-xs text-yellow-200 whitespace-pre-wrap"
          >
            <div class="flex items-center gap-1 mb-1">
              <span class="text-yellow-400">🤔</span>
              <span class="text-yellow-300 font-medium">思考過程</span>
            </div>
            <div class="opacity-80">{{ msg.thinking }}</div>
          </div>

          <!-- Error -->
          <div v-if="msg.error" class="mt-2 text-red-400 text-sm">
            <i class="bi bi-exclamation-triangle"></i> {{ msg.error }}
          </div>
        </div>
      </div>
    </div>

    <!-- Typing Indicator -->
    <div v-if="store.isLoading" class="flex gap-3">
      <div 
        class="w-8 h-8 rounded-full flex items-center justify-center text-xl"
        :class="store.isDarkMode ? 'bg-dark-secondary' : 'bg-gray-100'"
      >
        {{ store.selectedAgent.identity.emoji }}
      </div>
      <div 
        class="rounded-lg px-4 py-3"
        :class="store.isDarkMode ? 'bg-dark-secondary' : 'bg-gray-100'"
      >
        <div class="flex gap-1">
          <span class="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
          <span class="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
          <span class="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
        </div>
      </div>
    </div>
  </div>
</template>
