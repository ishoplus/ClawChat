import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Agent, Model, Message, Session, Toast, UploadedImage, ViewType, CronJob, Schedule, SystemStatus, ChannelInfo } from '@/types'

const STORAGE_KEY = 'clawchat_sessions'

export const useChatStore = defineStore('chat', () => {
  // Agents
  const agents = ref<Agent[]>([
    { id: 'main', name: 'Kai', identity: { emoji: '⚡', name: 'Kai', theme: 'Reliable, Sharp, Proactive, Efficient.' }},
    { id: 'rich', name: 'Rich', identity: { emoji: '💰', name: 'Rich', theme: 'Professional, Analytical, Prudent, Strategic.' }},
    { id: 'code', name: 'code', identity: { emoji: '💻', name: 'Code', theme: 'Technical, Precise, Efficient, Problem-solving.' }},
    { id: 'skill-manager', name: 'Skill Manager', identity: { emoji: '🛡️', name: '技能管家', theme: 'Professional, Helpful, Systematic, Security-focused.' }},
    { id: 'nexchip', name: 'nexchip', identity: { emoji: '🔬', name: 'nexchip', theme: 'Expert in Semiconductor Manufacturing & AI Agent Development' }},
    { id: 'chef', name: '廚師小幫手', identity: { emoji: '🍳', name: '廚師小幫手', theme: '細心、熱情、有條理的廚房助手' }},
    { id: 'travel', name: 'travel', identity: { emoji: '✈️', name: '旅行小幫手', theme: '熱情、周到、專業的海外旅遊助手' }},
    { id: 'ip', name: '專利審查', identity: { emoji: '📋', name: '專利審查', theme: '專業、嚴謹務實、建設性批評' }},
    { id: 'startup', name: 'startup', identity: { emoji: '🚀', name: '創業小幫手', theme: '積極、主動、務實、富創意' }}
  ])

  // Models
  const models = ref<Model[]>([
    { id: 'minimax-portal/MiniMax-M2.1', name: 'MiniMax M2.1' },
    { id: 'minimax-portal/MiniMax-M2.5', name: 'MiniMax M2.5 (視覺)', supportsVision: true },
    { id: 'minimax-portal/MiniMax-M2.1-lightning', name: 'MiniMax M2.1 Lightning' },
    { id: 'zai/glm-4.7', name: 'GLM-4.7' },
    { id: 'zai/glm-5', name: 'GLM-5' },
    { id: 'google/gemini-3-flash-preview', name: 'Gemini Flash', supportsVision: true },
  ])

  // State
  const selectedAgent = ref<Agent>(agents.value[0]!)
  const selectedModel = ref(models.value[0]!.id)
  const messages = ref<Message[]>([])
  const inputText = ref('')
  const isLoading = ref(false)
  const currentView = ref<ViewType>('chat')
  const currentSession = ref<string | null>(null)
  const sessions = ref<Session[]>([])
  const uploadedImages = ref<UploadedImage[]>([])
  const toasts = ref<Toast[]>([])
  
  // UI State
  const isDarkMode = ref(true)
  const showNewChatModal = ref(false)
  const showAgentDropdown = ref(false)
  const showModelDropdown = ref(false)
  const selectedFilterAgent = ref<string>('')
  const isChatMode = ref(false) // Mobile: true when in active chat (hides bottom nav)
  
  // Board
  const boardContent = ref('')
  const boardLoading = ref(false)
  const boardAutoRefresh = ref(true)
  
  // Schedule
  const schedules = ref<Schedule[]>([])
  const cronJobs = ref<CronJob[]>([])
  const scheduleLoading = ref(false)
  const expandedJob = ref<string | null>(null)
  
  // Manage
  const systemStatus = ref<SystemStatus>({ status: 'loading' })
  const manageAgents = ref<Agent[]>([])
  const manageChannels = ref<Record<string, ChannelInfo>>({})
  const manageSessions = ref<Session[]>([])
  
  // File Browser
  const showFileBrowser = ref(false)
  const fileBrowserLoading = ref(false)
  const fileBrowserFiles = ref<{ name: string; path: string; type: 'file' | 'directory'; size?: number }[]>([])
  const fileBrowserPath = ref<string[]>([])
  const filePreviewContent = ref<string | null>(null)
  const filePreviewPath = ref<string>('')
  const filePreviewImage = ref<string | null>(null)
  
  const isImageFile = (filename: string) => {
    if (!filename) return false
    const ext = filename.toLowerCase().split('.').pop()
    return ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'].includes(ext || '')
  }
  
  const isMarkdownFile = (filename: string) => {
    if (!filename) return false
    const ext = filename.toLowerCase().split('.').pop()
    return ['md', 'markdown', 'mdown', 'mkd'].includes(ext || '')
  }

  // Computed
  const displayedSessions = computed(() => {
    let filtered = sessions.value
    if (selectedFilterAgent.value) {
      filtered = filtered.filter(s => s.agentId === selectedFilterAgent.value)
    }
    return filtered.slice(0, 20)
  })
  const selectedModelName = computed(() => models.value.find(m => m.id === selectedModel.value)?.name || selectedModel.value)

  // Actions
  const selectAgent = (agent: Agent) => {
    selectedAgent.value = agent
  }

  const selectModel = (modelId: string) => {
    selectedModel.value = modelId
  }

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    const id = Date.now()
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 3000)
  }

  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value
    localStorage.setItem('clawchat_theme', isDarkMode.value ? 'dark' : 'light')
    document.documentElement.classList.toggle('light', !isDarkMode.value)
  }

  // File Browser
  const toggleFileBrowser = async () => {
    showFileBrowser.value = !showFileBrowser.value
    if (showFileBrowser.value && fileBrowserFiles.value.length === 0) {
      await fileBrowserNavigate('')
    }
  }
  
  const fileBrowserNavigate = async (path: string) => {
    fileBrowserLoading.value = true
    fileBrowserPath.value = path ? path.split('/') : []
    
    try {
      const url = `/api/agent/${selectedAgent.value.id}/files?path=${encodeURIComponent(path)}`
      const res = await fetch(url)
      const data = await res.json()
      fileBrowserFiles.value = data.files || []
    } catch (e) {
      console.error('Failed to load files:', e)
      fileBrowserFiles.value = []
    } finally {
      fileBrowserLoading.value = false
    }
  }
  
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }
  
  const openFile = async (file: { name: string; path: string; type: 'file' | 'directory' }) => {
    if (file.type === 'directory') {
      const fullPath = fileBrowserPath.value.join('/') 
        ? fileBrowserPath.value.join('/') + '/' + file.path 
        : file.path
      await fileBrowserNavigate(fullPath)
      return
    }
    
    // 讀取檔案內容
    try {
      const fullPath = fileBrowserPath.value.join('/') 
        ? fileBrowserPath.value.join('/') + '/' + file.path 
        : file.path
      const url = `/api/agent/${selectedAgent.value.id}/files?path=${encodeURIComponent(fullPath)}`
      const res = await fetch(url)
      const data = await res.json()
      
      if (data.error) {
        showToast(data.error, 'error')
        return
      }
      
      filePreviewPath.value = fullPath
      
      // 圖片直接顯示
      if (isImageFile(file.name)) {
        filePreviewImage.value = data.content // base64 圖片
        filePreviewContent.value = 'IMAGE_PLACEHOLDER'
        return
      }
      
      filePreviewImage.value = null
      filePreviewContent.value = data.content || data.error || '無法預覽'
    } catch (e) {
      showToast('無法讀取檔案', 'error')
    }
  }
  
  const closeFilePreview = () => {
    filePreviewContent.value = null
    filePreviewPath.value = ''
  }

  const loadTheme = () => {
    const saved = localStorage.getItem('clawchat_theme')
    if (saved) {
      isDarkMode.value = saved === 'dark'
    }
    document.documentElement.classList.toggle('light', !isDarkMode.value)
  }

  const formatTime = (timestamp?: number) => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    const now = new Date()
    const isToday = date.toDateString() === now.toDateString()
    const isYesterday = new Date(now.getTime() - 86400000).toDateString() === date.toDateString()
    const time = date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
    if (isToday) return `今天 ${time}`
    if (isYesterday) return `昨天 ${time}`
    return `${date.getMonth() + 1}/${date.getDate()} ${time}`
  }

  // Session Management
  const saveSessions = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      sessions: sessions.value,
      currentSession: currentSession.value,
      selectedAgentId: selectedAgent.value.id
    }))
  }

  const getSessionMessages = (sessionId: string, agentId: string): Message[] => {
    try {
      const key = `clawchat_${agentId}_${sessionId}`
      const saved = localStorage.getItem(key)
      return saved ? JSON.parse(saved) : []
    } catch {
      return []
    }
  }

  const saveSessionMessages = (sessionId: string, agentId: string, msgs: Message[]) => {
    try {
      const key = `clawchat_${agentId}_${sessionId}`
      localStorage.setItem(key, JSON.stringify(msgs))
    } catch {}
  }

  const createNewSession = (agent?: Agent) => {
    if (agent) selectedAgent.value = agent
    const newId = `session_${Date.now()}`
    sessions.value.unshift({ 
      id: newId, 
      name: '新對話', 
      preview: '',
      agentId: selectedAgent.value.id,
      key: newId
    })
    currentSession.value = newId
    messages.value = []
    saveSessions()
    showNewChatModal.value = false
  }

  const switchSession = async (session: Session) => {
    console.log('[switchSession] INPUT - session.id:', session.id, 'key:', session.key)
    
    // Save current session - use session.id for localStorage (backward compatibility)
    if (currentSession.value && messages.value.length > 0) {
      // Find current session by key or id to get the correct agentId
      const currentSessionData = sessions.value.find(s => 
        s.key === currentSession.value || s.id === currentSession.value
      )
      const currentAgentId = currentSessionData?.agentId || selectedAgent.value.id
      // Use session.id for localStorage (original behavior)
      const storageId = currentSessionData?.id || currentSession.value
      saveSessionMessages(storageId, currentAgentId, messages.value)
    }

    // Switch agent if needed
    if (session.agentId) {
      const agent = agents.value.find(a => a.id === session.agentId)
      if (agent) selectedAgent.value = agent
    }

    // Use key for display tracking
    const targetKey = session.key || session.id
    currentSession.value = targetKey
    currentView.value = 'chat'
    isChatMode.value = true  // Mobile: enter chat mode
    
    console.log('[switchSession] currentSession.value set to:', currentSession.value)

    // Use session.id for API call (Gateway expects UUID id, not key suffix)
    try {
      const res = await fetch(`/api/session/${session.id}/messages`)
      const data = await res.json()
      if (data.messages?.length) {
        messages.value = data.messages.map((m: any) => ({
          role: m.role,
          content: m.content,
          timestamp: new Date(m.timestamp).getTime()
        }))
      } else {
        // Fallback to local - use session.id for storage lookup
        messages.value = getSessionMessages(session.id, session.agentId || selectedAgent.value.id)
      }
    } catch {
      messages.value = getSessionMessages(session.id, session.agentId || selectedAgent.value.id)
    }

    saveSessions()
  }

  // Image handling
  const handleImageUpload = (files: FileList) => {
    for (const file of files) {
      if (!file.type.startsWith('image/')) continue
      const reader = new FileReader()
      reader.onload = (e) => {
        uploadedImages.value.push({
          name: file.name,
          type: file.type,
          dataUrl: e.target?.result as string,
          preview: e.target?.result as string
        })
      }
      reader.readAsDataURL(file)
    }
  }

  const removeImage = (index: number) => {
    uploadedImages.value.splice(index, 1)
  }

  // API Calls
  const fetchSessions = async () => {
    try {
      const res = await fetch('/api/sessions')
      const data = await res.json()
      
      // 直接使用 API 返回的數據
      const gatewaySessions: Session[] = (data.sessions || []).map((gs: any) => ({
        id: gs.id,
        key: gs.key || gs.id,
        name: gs.name || gs.label || '新對話',
        preview: '',
        agentId: gs.agentId,
        source: gs.source,
        isGateway: true,
        updatedAt: gs.updatedAt
      }))
      
      if (gatewaySessions.length === 0) {
        gatewaySessions.push({ 
          id: `session_${Date.now()}`, 
          name: '新對話', 
          agentId: selectedAgent.value.id,
          key: `session_${Date.now()}`
        })
      }

      gatewaySessions.sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0))
      sessions.value = gatewaySessions
      
      if (!currentSession.value && sessions.value.length > 0) {
        currentSession.value = sessions.value[0]!.key || sessions.value[0]!.id
      }
    } catch (e) {
      console.error('Failed to fetch sessions:', e)
    }
  }

  const sendMessage = async () => {
    const text = inputText.value.trim()
    if ((!text && uploadedImages.value.length === 0) || isLoading.value) return

    // Build message content
    let messageContent: any = text
    if (uploadedImages.value.length > 0) {
      const parts: any[] = text ? [{ type: 'text', text }] : []
      for (const img of uploadedImages.value) {
        parts.push({ type: 'image_url', image_url: { url: img.dataUrl } })
      }
      messageContent = parts
    }

    // Add user message
    const userMsg: Message = { 
      role: 'user', 
      content: messageContent, 
      timestamp: Date.now() 
    }
    if (uploadedImages.value.length > 0) {
      userMsg.images = uploadedImages.value.map(img => img.preview)
    }
    messages.value.push(userMsg)

    // Update session name
    const currentS = sessions.value.find(s => s.key === currentSession.value || s.id === currentSession.value)
    if (currentS && currentS.name === '新對話') {
      currentS.name = text.substring(0, 30) || '圖片訊息'
      currentS.preview = currentS.name
    }

    inputText.value = ''
    uploadedImages.value = []
    isLoading.value = true

    try {
      // 使用 session 的 key 後綴作為 user
      const currentSessionData = sessions.value.find(s => s.key === currentSession.value || s.id === currentSession.value)
      const keySuffix = currentSessionData?.key ? currentSessionData.key.split(':').pop() : currentSession.value
      console.log('[sendMessage] using key suffix as userId:', keySuffix)
      
      const response = await fetch(`/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: `openclaw:${selectedAgent.value.id}`,
          messages: [{ role: 'user', content: messageContent }],
          stream: true,
          user: keySuffix
        })
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)

      const assistantMsg: Message = { role: 'assistant', content: '', timestamp: Date.now() }
      messages.value.push(assistantMsg)

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') continue

            try {
              const chunk = JSON.parse(data)
              if (chunk.type === 'response.output_text.delta') {
                assistantMsg.content += chunk.delta || ''
              } else {
                const delta = chunk.choices?.[0]?.delta
                if (delta?.content) {
                  const items = delta.content
                  if (Array.isArray(items)) {
                    for (const item of items) {
                      if (item.type === 'thinking') assistantMsg.thinking += item.thinking || ''
                      else if (item.type === 'text') assistantMsg.content += item.text || ''
                    }
                  } else {
                    assistantMsg.content += items
                  }
                }
              }
              messages.value = [...messages.value]
            } catch {}
          }
        }
      }
    } catch (error: any) {
      messages.value.push({ 
        role: 'assistant', 
        content: '抱歉，發生錯誤：' + error.message,
        error: error.message,
        timestamp: Date.now()
      })
    } finally {
      isLoading.value = false
      if (currentSession.value) {
        const currentSessionData = sessions.value.find(s => s.key === currentSession.value || s.id === currentSession.value)
        const agentId = currentSessionData?.agentId || selectedAgent.value.id
        saveSessionMessages(currentSession.value, agentId, messages.value)
      }
    }
  }

  const clearChat = () => {
    if (currentSession.value) {
      const currentSessionData = sessions.value.find(s => s.key === currentSession.value || s.id === currentSession.value)
      const agentId = currentSessionData?.agentId || selectedAgent.value.id
      saveSessionMessages(currentSession.value, agentId, messages.value)
    }
    messages.value = []
  }

  return {
    // State
    agents,
    models,
    selectedAgent,
    selectedModel,
    messages,
    inputText,
    isLoading,
    currentView,
    currentSession,
    sessions,
    displayedSessions,
    uploadedImages,
    toasts,
    isDarkMode,
    isChatMode,
    showNewChatModal,
    showAgentDropdown,
    showModelDropdown,
    selectedFilterAgent,
    boardContent,
    boardLoading,
    boardAutoRefresh,
    schedules,
    cronJobs,
    scheduleLoading,
    expandedJob,
    systemStatus,
    manageAgents,
    manageChannels,
    manageSessions,
    showFileBrowser,
    fileBrowserLoading,
    fileBrowserFiles,
    fileBrowserPath,
    // Computed
    selectedModelName,
    // Actions
    selectAgent,
    selectModel,
    showToast,
    toggleTheme,
    loadTheme,
    formatTime,
    saveSessions,
    getSessionMessages,
    saveSessionMessages,
    createNewSession,
    switchSession,
    handleImageUpload,
    removeImage,
    fetchSessions,
    sendMessage,
    clearChat,
    toggleFileBrowser,
    fileBrowserNavigate,
    formatFileSize,
    openFile,
    closeFilePreview,
    filePreviewContent,
    filePreviewPath,
    filePreviewImage,
    isImageFile,
    isMarkdownFile,
  }
})
