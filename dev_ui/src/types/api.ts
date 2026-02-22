export type EmailType = 'inbox' | 'debug' | 'testcase' | 'eml'

export interface EmailInfo {
  id: string
  subject: string
  sender: string
  date: string
  dateTimestamp: number
  source: 'gmail' | 'eml'
  isStarred: boolean
  emailType: EmailType
}

export interface EmailListResponse {
  gmail: EmailInfo[]
  eml: EmailInfo[]
}

export interface ContentSection {
  index: number
  contentType: string
  originalHtml: string
  ssmlTags: string[]
  descriptionHtml: string
  descriptionContentType: string
  isRemoved: boolean
  removalReason: string | null
  debugInfo: Record<string, unknown>
}

export interface SsmlChunk {
  index: number
  ssml: string
  sectionIndices: number[]
}

export interface ParseResult {
  success: boolean
  emailInfo: {
    subject: string
    sender: string
    recipient: string
    date: string
  }
  parserName: string
  voice: string
  voiceReason: string
  sections: ContentSection[]
  ssmlChunks: SsmlChunk[]
  error: string | null
  errorTraceback: string | null
}

export interface AudioGenerationResult {
  success: boolean
  cached: boolean
  audioUrl?: string
  error?: string
}
