/**
 * AI History types
 */

import type { AiOperationType } from './chat'
import type { IAiCost, IAiTokenUsage } from './chat'

export interface IAiHistoryItem {
  id: string
  operationType: AiOperationType
  finalPrompt: string
  contextData?: Record<string, unknown>
  responseData: Record<string, unknown>
  model: string
  provider: string
  tokens: IAiTokenUsage
  cost: IAiCost
  durationMs?: number
  usedOwnToken: boolean
  created_at: string
}

export interface IAiHistoryListResponse {
  items: IAiHistoryItem[]
  total: number
  limit: number
  offset: number
}

export interface IAiHistoryDetail extends IAiHistoryItem {
  responsePreview?: string
}

export interface IAiHistoryQuery {
  limit?: number
  offset?: number
  operationType?: AiOperationType
}

export interface LoadHistoryParams {
  limit?: number
  offset?: number
  operationType?: AiOperationType
}
