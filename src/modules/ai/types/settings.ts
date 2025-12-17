/**
 * AI Settings types
 */

export interface IAiSettings {
  id: string
  user_id: string
  use_own_token: boolean
  has_token: boolean
  selected_model: string
  context_fields: Record<string, any>
  max_tokens: number | null
  temperature: number
  monthly_tokens_used: number
  monthly_cost_used: number
  monthly_token_limit?: number
  monthly_cost_limit?: number
  created_at: string
  updated_at: string
}

export interface IAiUpdateSettings {
  selected_model?: string
  context_fields?: Record<string, any>
  max_tokens?: number
  temperature?: number
}

export interface IAiSetTokenRequest {
  api_token: string
}

export interface IAiSetTokenResponse {
  success: boolean
  message: string
}

