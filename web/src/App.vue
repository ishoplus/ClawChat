<script setup lang="ts">
import { onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import Sidebar from '@/components/Sidebar.vue'
import ChatView from '@/views/ChatView.vue'
import BoardView from '@/views/BoardView.vue'
import ScheduleView from '@/views/ScheduleView.vue'
import ManageView from '@/views/ManageView.vue'
import Toast from '@/components/Toast.vue'
import MobileNav from '@/components/MobileNav.vue'
import NewChatModal from '@/components/modals/NewChatModal.vue'

const store = useChatStore()

onMounted(async () => {
  store.loadTheme()
  await store.fetchSessions()
  
  if (store.currentSession) {
    store.messages = store.getSessionMessages(store.currentSession, store.selectedAgent.id)
  }
})
</script>

<template>
  <div 
    class="flex h-screen"
    :class="store.isDarkMode ? 'bg-dark-bg text-white' : 'bg-white text-gray-900'"
  >
    <!-- Desktop Sidebar -->
    <Sidebar class="hidden md:flex" />

    <!-- Main Content -->
    <main class="flex-1 flex flex-col overflow-hidden">
      <ChatView v-if="store.currentView === 'chat'" />
      <BoardView v-else-if="store.currentView === 'board'" />
      <ScheduleView v-else-if="store.currentView === 'schedule'" />
      <ManageView v-else-if="store.currentView === 'manage'" />
    </main>

    <!-- Mobile Nav (hidden when in chat mode) -->
    <MobileNav v-if="!store.isChatMode" class="md:hidden" />

    <!-- Toast Notifications -->
    <Toast />

    <!-- New Chat Modal -->
    <NewChatModal v-if="store.showNewChatModal" />
  </div>
</template>
