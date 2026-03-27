<script setup lang="ts">
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
</script>

<template>
  <div class="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex flex-col gap-2">
    <div 
      v-for="toast in store.toasts" 
      :key="toast.id"
      class="px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 text-lg font-medium animate-slide-in"
      :class="toast.type === 'error' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'"
    >
      <i class="bi" :class="toast.type === 'error' ? 'bi-exclamation-circle' : 'bi-check-circle'"></i>
      <span>{{ toast.message }}</span>
    </div>
  </div>
</template>
