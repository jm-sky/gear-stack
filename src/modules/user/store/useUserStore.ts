import { defineStore } from 'pinia'
import type { IUpdateUserDto, IUser } from '../types/user.types'

const STORAGE_KEY = 'gear-stack:user'

function loadFromStorage(): IUser | null {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) {
    try {
      return JSON.parse(stored)
    } catch (error) {
      console.error('Error loading user from storage:', error)
    }
  }
  return null
}

export const useUserStore = defineStore('user', {
  state: (): { user: IUser | null } => {
    const loaded = loadFromStorage()
    // Initialize default user if none exists
    if (!loaded) {
      const now = new Date().toISOString()
      const defaultUser: IUser = {
        id: crypto.randomUUID(),
        name: 'User',
        email: 'user@example.com',
        createdAt: now,
        updatedAt: now,
      }
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultUser))
      } catch (error) {
        console.error('Error saving default user to storage:', error)
      }
      return { user: defaultUser }
    }
    return { user: loaded }
  },

  getters: {
    getProfile: (state): IUser | null => {
      return state.user
    },
  },

  actions: {
    setUser(user: IUser): void {
      this.user = user
      this.saveToStorage()
    },

    initializeDefaultUser(): void {
      if (this.user) return // User already exists

      const now = new Date().toISOString()
      const defaultUser: IUser = {
        id: crypto.randomUUID(),
        name: 'User',
        email: 'user@example.com',
        createdAt: now,
        updatedAt: now,
      }
      this.setUser(defaultUser)
    },

    updateUser(data: IUpdateUserDto): void {
      if (!this.user) {
        // If no user exists, initialize with default and update
        this.initializeDefaultUser()
      }

      if (!this.user) return

      this.user = {
        ...this.user,
        ...data,
        updatedAt: new Date().toISOString(),
      }
      this.saveToStorage()
    },

    loadFromStorage(): void {
      this.user = loadFromStorage()
    },

    saveToStorage(): void {
      try {
        if (this.user) {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(this.user))
        } else {
          localStorage.removeItem(STORAGE_KEY)
        }
      } catch (error) {
        console.error('Error saving user to storage:', error)
      }
    },
  },
})

