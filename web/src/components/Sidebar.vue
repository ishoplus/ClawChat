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

const getBreadcrumb = () => {
  if (store.fileBrowserPath.length === 0) return '根目錄'
  return store.fileBrowserPath.join(' / ')
}

const renderMarkdown = (content: string) => {
  try {
    return marked.parse(content) as string
  } catch {
    return content
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
      <h2 class="font-bold">對話</h2>
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
        :class="store.isDarkMode ? 'bg-dark-hover border-dark-border' : 'bg-white border-gray-200'"
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
          ? 'bg-blue-500 text-white' 
          : (store.isDarkMode ? 'hover:bg-dark-hover bg-gray-800' : 'hover:bg-gray-100 bg-white')"
      >
        <div 
          class="w-10 h-10 rounded-full flex items-center justify-center text-lg flex-shrink-0"
          :class="(session.id === store.currentSession || session.key === store.currentSession) ? 'bg-white/20' : (store.isDarkMode ? 'bg-dark-border' : 'bg-gray-200')"
        >
          {{ getSourceIcon(session.source) }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="font-medium truncate">{{ session.name }}</div>
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

    <!-- File Browser -->
    <div v-if="store.currentView === 'chat'" class="border-t p-2"
      :class="store.isDarkMode ? 'border-dark-border' : 'border-gray-200'"
    >
      <button 
        @click="store.toggleFileBrowser()"
        class="w-full flex items-center justify-between text-xs uppercase tracking-wider mb-2 p-2 rounded-lg"
        :class="store.isDarkMode ? 'bg-dark-hover' : 'bg-gray-100'"
      >
        <span><i class="bi bi-folder me-1"></i> Workspace</span>
        <i class="bi" :class="store.showFileBrowser ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
      </button>
      
      <div v-if="store.showFileBrowser" class="space-y-1">
        <!-- Breadcrumb with home button -->
        <div class="flex items-center gap-1 mb-2 overflow-x-auto">
          <button 
            @click="store.fileBrowserNavigate('')"
            class="text-xs text-blue-400 hover:text-blue-300 whitespace-nowrap flex items-center gap-1"
          >
            <i class="bi bi-house"></i> 根目錄
          </button>
          <template v-for="(p, idx) in store.fileBrowserPath" :key="idx">
            <span class="text-gray-600">/</span>
            <button 
              @click="store.fileBrowserNavigate(store.fileBrowserPath.slice(0, idx + 1).join('/'))"
              class="text-xs text-blue-400 hover:text-blue-300 whitespace-nowrap"
            >
              {{ p }}
            </button>
          </template>
        </div>
        
        <!-- Loading -->
        <div v-if="store.fileBrowserLoading" class="text-center text-gray-500 text-xs py-2">
          <i class="bi bi-hourglass-split animate-spin"></i> 載入中...
        </div>
        
        <!-- Files -->
        <div v-else-if="store.fileBrowserFiles.length === 0" class="text-center text-gray-500 text-xs py-2">
          沒有檔案
        </div>
        <button
          v-else
          v-for="file in store.fileBrowserFiles"
          :key="file.path"
          @click="store.openFile(file)"
          class="w-full p-2 text-left flex items-center gap-2 rounded text-sm transition-colors truncate"
          :class="store.isDarkMode ? 'hover:bg-dark-hover' : 'hover:bg-gray-100'"
        >
          <i class="bi" :class="file.type === 'directory' ? 'bi-folder' : 'bi-file-text'"></i>
          <span class="truncate">{{ file.name }}</span>
          <span v-if="file.type === 'file'" class="text-xs text-gray-500 ml-auto">
            {{ store.formatFileSize(file.size || 0) }}
          </span>
        </button>
      </div>
    </div>

    <!-- File Preview Modal -->
    <div v-if="store.filePreviewContent !== null" class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" @click.self="store.closeFilePreview()">
      <div class="bg-gray-900 rounded-lg max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col border border-gray-700">
        <div class="flex items-center justify-between p-3 border-b border-gray-700">
          <div class="flex items-center gap-2">
            <i class="bi bi-file-text"></i>
            <span class="font-medium truncate">{{ store.filePreviewPath }}</span>
          </div>
          <div class="flex items-center gap-2">
            <button 
              @click="navigator.clipboard.writeText(store.filePreviewContent || '')"
              class="text-gray-400 hover:text-white p-1"
              title="複製內容"
            >
              <i class="bi bi-clipboard"></i>
            </button>
            <button @click="store.closeFilePreview()" class="text-gray-400 hover:text-white">
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
          <div v-else-if="store.isMarkdownFile(store.filePreviewPath)" class="markdown-body text-sm text-gray-300" v-html="renderMarkdown(store.filePreviewContent || '')"></div>
          <!-- 純文字預覽 -->
          <pre v-else class="text-xs text-gray-300 whitespace-pre-wrap">{{ store.filePreviewContent }}</pre>
        </div>
      </div>
    </div>

    <!-- Bottom Nav -->
    <div 
      class="p-2 border-t flex justify-around"
      :class="store.isDarkMode ? 'border-dark-border' : 'border-gray-200'"
    >
      <button 
        @click="store.currentView = 'board'"
        class="p-2 rounded-lg transition-colors"
        :class="store.currentView === 'board' ? 'bg-blue-500 text-white' : 'text-gray-400'"
        title="留言板"
      >
        <i class="bi bi-chat-square-text"></i>
      </button>
      <button 
        @click="store.currentView = 'schedule'"
        class="p-2 rounded-lg transition-colors"
        :class="store.currentView === 'schedule' ? 'bg-blue-500 text-white' : 'text-gray-400'"
        title="排程"
      >
        <i class="bi bi-clock"></i>
      </button>
      <button 
        @click="store.currentView = 'manage'"
        class="p-2 rounded-lg transition-colors"
        :class="store.currentView === 'manage' ? 'bg-blue-500 text-white' : 'text-gray-400'"
        title="管理"
      >
        <i class="bi bi-gear"></i>
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
