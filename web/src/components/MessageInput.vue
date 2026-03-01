<script setup lang="ts">
import { useChatStore } from '@/stores/chat'

const emit = defineEmits<{
  sent: []
}>()

const store = useChatStore()

const onSubmit = () => {
  store.sendMessage()
  emit('sent')
}

const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files) {
    store.handleImageUpload(target.files)
  }
  target.value = ''
}
</script>

<template>
  <div class="p-4 pb-20 lg:pb-4">
    <!-- Image Previews -->
    <div v-if="store.uploadedImages.length > 0" class="mb-2 flex gap-2 flex-wrap">
      <div v-for="(img, idx) in store.uploadedImages" :key="idx" class="relative">
        <img :src="img.preview" class="w-16 h-16 object-cover rounded-lg border">
        <button 
          @click="store.removeImage(idx)"
          class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs"
        >
          ×
        </button>
      </div>
    </div>

    <!-- Input -->
    <form @submit.prevent="onSubmit" class="flex gap-2">
      <!-- Upload Button -->
      <label 
        class="rounded-lg px-3 py-2 cursor-pointer transition-colors"
        :class="[
          store.isDarkMode 
            ? 'bg-dark-secondary hover:bg-dark-hover border border-dark-border' 
            : 'bg-gray-100 hover:bg-gray-200 border border-gray-200',
          store.isLoading ? 'opacity-50 cursor-not-allowed' : ''
        ]"
      >
        <input 
          type="file" 
          accept="image/*"
          multiple
          @change="onFileChange"
          :disabled="store.isLoading"
          class="hidden"
        >
        <i class="bi bi-image text-xl"></i>
      </label>

      <!-- Text Input -->
      <input 
        v-model="store.inputText"
        :disabled="store.isLoading"
        type="text" 
        placeholder="輸入訊息..."
        class="flex-1 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
        :class="store.isDarkMode 
          ? 'bg-dark-secondary border border-dark-border' 
          : 'bg-gray-100 border border-gray-200'"
      >

      <!-- Send Button -->
      <button 
        type="submit"
        :disabled="store.isLoading || (!store.inputText.trim() && store.uploadedImages.length === 0)"
        class="bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2 transition-colors"
      >
        <i class="bi bi-send"></i>
      </button>
    </form>
  </div>
</template>
