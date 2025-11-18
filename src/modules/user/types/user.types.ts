import type { TUUID } from '@/shared/types/base.type'

export interface IUser {
  id: TUUID
  name: string
  email: string
  avatar?: string
  createdAt: string
  updatedAt: string
}

export interface IUpdateUserDto {
  name?: string
  email?: string
}

