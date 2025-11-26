/**
 * AI Settings types
 */

export interface IAiSettings {
  use_own_token: boolean
  selected_model: string
  context_fields: string[]
  monthly_tokens_used: number
  monthly_cost_used: number
  monthly_token_limit?: number
  monthly_cost_limit?: number
}

export interface IAiUpdateSettings {
  selected_model?: string
  context_fields?: string[]
  monthly_token_limit?: number
  monthly_cost_limit?: number
}

export interface IAiSetTokenRequest {
  api_token: string
}

export interface IAiSetTokenResponse {
  validated: boolean
  message: string
}

