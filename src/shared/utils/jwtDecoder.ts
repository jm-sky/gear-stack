// This file is kept for potential future use but jwt-decode dependency has been removed
// as the app is now fully client-side with localStorage and doesn't need JWT tokens

// Note: If JWT functionality is needed in the future, reinstall jwt-decode package
// and uncomment the code below

/*
import { jwtDecode } from 'jwt-decode'
import type { JWTPayload } from '../types/jwt.type'

export function decodeJWT(token: string): JWTPayload {
  try {
    return jwtDecode<JWTPayload>(token)
  } catch (error) {
    console.error('Error decoding JWT token:', error)
    throw new Error('Invalid JWT token')
  }
}
*/
