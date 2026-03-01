// Types for ClawChat

export interface Agent {
  id: string
  name: string
  identity: {
    emoji: string
    name: string
    theme: string
  }
}

export interface Model {
  id: string
  name: string
  supportsVision?: boolean
}

export interface Message {
  role: 'user' | 'assistant' | 'toolResult'
  content: string | { type: string; text?: string; image_url?: { url: string } }[]
  timestamp?: number
  images?: string[]
  thinking?: string
  error?: string
}

export interface Session {
  id: string
  name: string
  preview?: string
  agentId: string
  source?: string
  isGateway?: boolean
  updatedAt?: number
}

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error'
}

export interface UploadedImage {
  name: string
  type: string
  dataUrl: string
  preview: string
}

export interface FileItem {
  name: string
  path: string
  type: 'file' | 'directory'
  size?: number
}

export interface CronJob {
  id: string
  name: string
  schedule: string
  enabled: boolean
  sessionTarget?: string
  nextRun?: string
  lastRun?: string
  lastStatus?: string
  lastDuration?: string
  lastError?: string
  consecutiveErrors?: number
  message?: string
  messagePreview?: string
}

export interface Schedule {
  workspace: string
  emoji: string
  name: string
  hasSchedule: boolean
  tasks: CronJob[]
}

export interface ChannelInfo {
  enabled: boolean
  accountCount: number
}

export interface SystemStatus {
  status: 'online' | 'offline' | 'loading' | 'error'
  gateway?: {
    port: number
  }
  ngrokUrl?: string
}

export type ViewType = 'chat' | 'board' | 'schedule' | 'manage' | 'backlog'
