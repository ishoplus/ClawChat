<script setup lang="ts">
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
</script>

<template>
  <div class="relative">
    <button 
      @click="store.showModelDropdown = !store.showModelDropdown"
      class="rounded-lg px-3 py-2 flex items-center gap-2 transition-colors"
      :class="store.isDarkMode 
        ? 'bg-dark-secondary hover:bg-dark-hover' 
        : 'bg-gray-100 hover:bg-gray-200'"
    >
      <i class="bi bi-cpu text-gray-400"></i>
      <span class="text-sm">{{ store.selectedModelName }}</span>
      <i class="bi bi-chevron-down text-gray-500 text-xs"></i>
    </button>

    <!-- Dropdown -->
    <div 
      v-if="store.showModelDropdown"
      class="absolute top-full right-0 mt-1 rounded-lg shadow-xl z-50 overflow-hidden"
      :class="store.isDarkMode ? 'bg-dark-secondary' : 'bg-white'"
    >
      <button
        v-for="model in store.models"
        :key="model.id"
        @click="store.selectModel(model.id); store.showModelDropdown = false"
        class="w-full px-4 py-2 flex items-center gap-3 transition-colors text-left"
        :class="[
          store.isDarkMode ? 'hover:bg-dark-hover' : 'hover:bg-gray-100',
          model.id === store.selectedModel ? (store.isDarkMode ? 'bg-dark-hover' : 'bg-gray-50') : ''
        ]"
      >
        <div class="text-sm">
          <div class="font-medium">{{ model.name }}</div>
        </div>
        <i 
          v-if="model.id === store.selectedModel" 
          class="bi bi-check text-green-500 ml-2"
        ></i>
      </button>
    </div>
  </div>
</template>
