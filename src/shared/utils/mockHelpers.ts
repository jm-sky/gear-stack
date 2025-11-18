// This file is kept for potential future use but JWT-related functions have been removed
// as the app is now fully client-side with localStorage and doesn't need JWT tokens

// Note: If JWT functionality is needed in the future, reinstall jwt-decode package
// and uncomment the code below

/*
import { JWT_STORE_KEY } from '@/shared/config/config'
import type { JWTPayload, JWTPayloadOptions } from '../types/jwt.type'
import { decodeJWT } from './jwtDecoder'

export const getCurrentUserEmailFromMockJWT = (): string => {
  const token = localStorage.getItem(JWT_STORE_KEY)
  try {
    const payload = decodeJWT(token ?? '')
    return payload.email
  } catch {
    throw new Error('Invalid JWT token')
  }
}
*/

/**
 * Base64URL encoding (JWT-safe base64 encoding)
 */
export function base64UrlEncode(str: string): string {
  return btoa(str)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '')
}

// generateMockJWT removed - not needed for client-side only app
// If JWT functionality is needed in the future, reinstall jwt-decode package
// and implement with proper types

export const createHttpError = (status: number, message: string, errors?: Record<string, string[]>): Error => {
  const error = new Error(message)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ;(error as any).response = {
    status,
    data: {
      message,
      errors,
    },
  }
  return error
}

export const delay = (ms = 500): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms))
}
