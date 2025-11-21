import { defineStore } from 'pinia'
import type { IGearContainer } from '../types/gear.types'
import type { TUUID } from '@/shared/types/base.type'

interface IGearStoreState {
  containers: IGearContainer[]
}

const STORAGE_KEY = 'gear-stack:containers'

// Helper do ładowania z localStorage
function loadFromStorage(): IGearContainer[] {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) {
    try {
      const containers = JSON.parse(stored) as IGearContainer[]
      // Migration: Add default weightUnit for items that don't have it
      return containers.map(container => ({
        ...container,
        items: container.items.map(item => ({
          ...item,
          weightUnit: item.weightUnit ?? 'g',
        })),
      }))
    } catch (error) {
      console.error('Error loading from storage:', error)
    }
  }
  return []
}

export const useGearStore = defineStore('gear', {
  state: (): IGearStoreState => {
    return {
      containers: loadFromStorage(),
    }
  },
  
  getters: {
    // Proste getters do dostępu do danych
    getContainerById: (state) => (id: TUUID): IGearContainer | undefined => {
      return state.containers.find(c => c.id === id)
    },
    
    getAllContainers: (state): IGearContainer[] => {
      return state.containers
    },
  },
  
  actions: {
    // Tylko operacje na state - bez logiki biznesowej
    setContainers(containers: IGearContainer[]): void {
      this.containers = containers
      this.saveToStorage()
    },
    
    addContainer(container: IGearContainer): void {
      this.containers.push(container)
      this.saveToStorage()
    },
    
    updateContainer(container: IGearContainer): void {
      const index = this.containers.findIndex(c => c.id === container.id)
      if (index !== -1) {
        this.containers[index] = container
        this.saveToStorage()
      }
    },
    
    removeContainer(id: TUUID): void {
      this.containers = this.containers.filter(c => c.id !== id)
      this.saveToStorage()
    },

    clearAllContainers(): void {
      this.containers = []
      this.saveToStorage()
    },

    // Synchronizacja z localStorage
    loadFromStorage(): void {
      this.containers = loadFromStorage()
    },
    
    saveToStorage(): void {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.containers))
      } catch (error) {
        console.error('Error saving to storage:', error)
      }
    },
  },
})

