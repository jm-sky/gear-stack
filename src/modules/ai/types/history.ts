/**
 * AI History types
 */

import type { AiOperationType } from './chat'
import type { IAiCost, IAiTokenUsage } from './chat'

export interface IAiHistoryItem {
  id: string
  operation_type: AiOperationType
  final_prompt: string
  context_data?: Record<string, unknown>
  response_data: Record<string, unknown>
  model: string
  provider: string
  tokens: IAiTokenUsage
  cost: IAiCost
  duration_ms?: number
  used_own_token: boolean
  created_at: string
}

export interface IAiHistoryListResponse {
  items: IAiHistoryItem[]
  total: number
  limit: number
  offset: number
}

export interface IAiHistoryDetail extends IAiHistoryItem {
  response_preview?: string
}

export interface IAiHistoryQuery {
  limit?: number
  offset?: number
  operationType?: AiOperationType
}

