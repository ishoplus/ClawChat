<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import { marked } from 'marked'

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

const renderMarkdown = (content: string) => {
  try {
    return marked.parse(content) as string
  } catch {
    return content
  }
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    store.showToast('已複製到剪貼簿')
  } catch {
    store.showToast('複製失敗', 'error')
  }
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
      <h2 class="font-bold" :class="store.isDarkMode ? 'text-white' : 'text-gray-900'">
        <i class="bi bi-folder me-2"></i>Workspace
      </h2>
      <button 
        @click="store.fetchSessions()"
        class="p-2 rounded-lg transition-colors hover:bg-dark-hover"
        :class="store.isDarkMode ? 'hover:bg-dark-hover' : 'hover:bg-gray-200'"
        title="重新整理"
      >
        <i class="bi bi-arrow-clockwise"></i>
      </button>
    </div>

    <!-- File Browser -->
    <div class="flex-1 overflow-hidden flex flex-col">
      <!-- Breadcrumb with home button -->
      <div class="px-2 py-2 border-b flex items-center gap-1 overflow-x-auto"
        :class="store.isDarkMode ? 'border-dark-border' : 'border-gray-200'"
      >
        <button 
          @click="store.fileBrowserNavigate('')"
          class="text-xs text-blue-400 hover:text-blue-300 whitespace-nowrap flex items-center gap-1"
        >
          <i class="bi bi-house"></i> 根目錄
        </button>
        <template v-for="(p, idx) in store.fileBrowserPath" :key="idx">
          <span class="text-gray-500">/</span>
          <button 
            @click="store.fileBrowserNavigate(store.fileBrowserPath.slice(0, idx + 1).join('/'))"
            class="text-xs text-blue-400 hover:text-blue-300 whitespace-nowrap"
          >
            {{ p }}
          </button>
        </template>
      </div>
      
      <!-- Loading -->
      <div v-if="store.fileBrowserLoading" class="text-center text-gray-500 text-xs py-4">
        <i class="bi bi-hourglass-split animate-spin"></i> 載入中...
      </div>
      
      <!-- Files -->
      <div v-else-if="store.fileBrowserFiles.length === 0" class="text-center text-gray-500 text-xs py-4">
        沒有檔案
      </div>
      <div v-else class="flex-1 overflow-y-auto p-2">
        <button
          v-for="file in store.fileBrowserFiles"
          :key="file.path"
          @click="store.openFile(file)"
          class="w-full p-2 text-left flex items-center gap-2 rounded text-sm transition-colors truncate mb-1"
          :class="store.isDarkMode ? 'hover:bg-dark-hover text-gray-300' : 'hover:bg-gray-100 text-gray-700'"
        >
          <i class="bi" :class="file.type === 'directory' ? 'bi-folder' : 'bi-file-text'"></i>
          <span class="truncate">{{ file.name }}</span>
          <span v-if="file.type === 'file'" class="text-xs text-gray-500 ml-auto">
            {{ store.formatFileSize(file.size || 0) }}
          </span>
        </button>
      </div>
    </div>

    <!-- Session List Preview -->
    <div class="border-t flex-shrink-0"
      :class="store.isDarkMode ? 'border-dark-border' : 'border-gray-200'"
    >
      <button 
        @click="store.toggleFileBrowser()"
        class="w-full flex items-center justify-between text-xs uppercase tracking-wider p-3 rounded-lg"
        :class="store.isDarkMode ? 'bg-dark-hover' : 'bg-gray-100'"
      >
        <span :class="store.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
          <i class="bi bi-chat-dots me-1"></i> 最近的對話
        </span>
        <i class="bi" :class="store.currentView === 'chat' ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
      </button>
      
      <div v-if="store.currentView === 'chat'" class="max-h-48 overflow-y-auto p-2">
        <button 
          v-for="session in store.sessions.slice(0, 5)" 
          :key="session.id"
          @click="store.switchSession(session)"
          class="w-full p-2 rounded flex items-center gap-2 text-xs transition-colors text-left mb-1 truncate"
          :class="(session.id === store.currentSession || session.key === store.currentSession) 
            ? (store.isDarkMode ? 'bg-blue-500 text-white' : 'bg-blue-600 text-white') 
            : (store.isDarkMode ? 'hover:bg-dark-hover text-gray-300' : 'hover:bg-gray-100 text-gray-700')"
        >
          <span>{{ getSourceIcon(session.source) }}</span>
          <span class="truncate">{{ session.name || '未命名' }}</span>
        </button>
      </div>
    </div>
  </aside>

  <!-- File Preview Modal -->
  <div v-if="store.filePreviewContent !== null" class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" @click.self="store.closeFilePreview()">
    <div 
      class="rounded-lg max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col border"
      :class="store.isDarkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'"
    >
      <div 
        class="flex items-center justify-between p-3 border-b"
        :class="store.isDarkMode ? 'border-gray-700' : 'border-gray-200'"
      >
        <div class="flex items-center gap-2">
          <i class="bi bi-file-text"></i>
          <span class="font-medium truncate">{{ store.filePreviewPath }}</span>
        </div>
        <div class="flex items-center gap-2">
          <button 
            @click="copyToClipboard(store.filePreviewContent || '')"
            class="p-1"
            :class="store.isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'"
            title="複製內容"
          >
            <i class="bi bi-clipboard"></i>
          </button>
          <button 
            @click="store.closeFilePreview()" 
            class="p-1"
            :class="store.isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      </div>
      <div class="flex-1 overflow-auto p-3">
        <!-- 圖片預覽 -->
        <div v-if="store.filePreviewImage" class="flex justify-center">
          <img :src="store.filePreviewImage" class="max-w-full max-h-[70vh] object-contain rounded-lg" />
        </div>
        <!-- Markdown 預覽 -->
        <div v-else-if="store.isMarkdownFile(store.filePreviewPath)" 
          class="markdown-body text-sm p-4 rounded-lg"
          :class="store.isDarkMode ? 'text-gray-300 bg-gray-800' : 'text-gray-800 bg-gray-50'"
          v-html="renderMarkdown(store.filePreviewContent || '')"></div>
        <!-- 純文字預覽 -->
        <pre v-else
          class="text-xs whitespace-pre-wrap overflow-auto"
          :class="store.isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >{{ store.filePreviewContent }}</pre>
      </div>
    </div>
  </div>
</template>
