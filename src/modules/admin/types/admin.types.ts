import type { TDateTime, TUUID } from '@/shared/types/base.type'

export interface IAdminUser {
  id: TUUID
  name: string
  email: string
  avatarUrl?: string
  isActive: boolean
  isAdmin: boolean
  isEmailVerified: boolean
  emailVerifiedAt?: TDateTime | null
  createdAt: TDateTime
  updatedAt: TDateTime
}

export interface IAdminContainer {
  id: TUUID
  name: string
  description?: string | null
  type: string
  color?: string | null
  isPublic: boolean
  authorId?: TUUID | null
  authorName?: string | null
  createdAt: TDateTime
  updatedAt: TDateTime
  itemCount?: number
}

export interface IAdminItem {
  id: TUUID
  name: string
  category: string
  quantity: number
  weight: number
  weightUnit: string
  status: string
  priority: string
  containerId: TUUID
  containerName?: string
  authorId?: TUUID | null
  authorName?: string | null
  createdAt: TDateTime
  updatedAt: TDateTime
}
