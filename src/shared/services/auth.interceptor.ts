import type { InternalAxiosRequestConfig } from 'axios'

import { JWT_STORE_KEY } from '@/shared/config/config'

export function authInterceptor(config: InternalAxiosRequestConfig): InternalAxiosRequestConfig {
  const token = localStorage.getItem(JWT_STORE_KEY)

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
}
