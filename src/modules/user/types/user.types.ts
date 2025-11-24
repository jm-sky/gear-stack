import type { TUUID } from '@/shared/types/base.type'

export interface IUser {
  id: TUUID
  name: string
  email: string
  avatarUrl?: string
  isAdmin?: boolean
  emailPublic?: boolean // Whether email is public (for public profiles)
  createdAt: string
  updatedAt: string
}

export interface IUpdateUserDto {
  name?: string
  email?: string
  avatarUrl?: string
}

