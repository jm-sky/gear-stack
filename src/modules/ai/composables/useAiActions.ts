/**
 * AI Actions Composable
 * Handles executing actions from AI structured output
 */

import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { gearContainerService } from '@/modules/gear/services/gearContainerService'
import { gearItemService } from '@/modules/gear/services/gearItemService'
import { useGearStore } from '@/modules/gear/store/useGearStore'
import type { IAiStructuredOutput } from '../types'
import type { ICreateContainerDto, ICreateItemDto, IGearItem, IUpdateItemDto } from '@/modules/gear/types/gear.types'

export function useAiActions() {
  const { t } = useI18n()
  const gearStore = useGearStore()

  const executeAction = async (
    structuredOutput: IAiStructuredOutput | null,
    containerId?: string,
  ): Promise<boolean> => {
    if (!structuredOutput || !structuredOutput.action || structuredOutput.action === 'None') {
      return false
    }

    const { action, data } = structuredOutput

    try {
      switch (action) {
        case 'create_container':
          return await handleCreateContainer(data)

        case 'create_item':
          return await handleCreateItem(data, containerId)

        case 'delete_item':
          return await handleDeleteItem(data, containerId)

        case 'update_item':
          return await handleUpdateItem(data, containerId)

        default:
          console.warn(`Unknown AI action: ${action}`)
          return false
      }
    } catch (error) {
      console.error('Error executing AI action:', error)
      toast.error(t('ai.actions.error'))
      return false
    }
  }

  const handleCreateItem = async (
    data: Record<string, unknown>,
    containerId?: string,
  ): Promise<boolean> => {
    if (!containerId) {
      toast.error(t('ai.actions.noContainer'))
      return false
    }

    // Build item from AI data
    const newItem: Partial<IGearItem> = {
      name: data.name as string,
      category: data.category as string | undefined,
      weight: data.weight as number | undefined,
      quantity: data.quantity as number | undefined,
      price: data.price as number | undefined,
      url: data.url as string | undefined,
      notes: data.notes as string | undefined,
      brand: data.brand as string | undefined,
      color: data.color as string | undefined,
      wearable: data.wearable as boolean | undefined,
      consumable: data.consumable as boolean | undefined,
    }

    // Validate required fields
    if (!newItem.name) {
      toast.error(t('ai.actions.invalidData'))
      return false
    }

    // Check if container exists
    const container = gearStore.getContainerById(containerId)
    if (!container) {
      toast.error(t('ai.actions.containerNotFound'))
      return false
    }

    // Create item using service (API or localStorage based on backend status)
    await gearItemService().createItem(containerId, newItem as ICreateItemDto)
    toast.success(t('ai.actions.itemCreated', { name: newItem.name }))

    return true
  }

  const handleUpdateItem = async (
    data: Record<string, unknown>,
    containerId?: string,
  ): Promise<boolean> => {
    if (!containerId) {
      toast.error(t('ai.actions.noContainer'))
      return false
    }

    const itemId = data.id as string
    const updates = data.updates as Record<string, unknown>

    if (!itemId || !updates) {
      toast.error(t('ai.actions.invalidData'))
      return false
    }

    // Check if container exists
    const container = gearStore.getContainerById(containerId)
    if (!container) {
      toast.error(t('ai.actions.containerNotFound'))
      return false
    }

    // Update item using service (API or localStorage based on backend status)
    await gearItemService().updateItem(itemId, updates as IUpdateItemDto)
    toast.success(t('ai.actions.itemUpdated'))

    return true
  }

  const handleDeleteItem = async (
    data: Record<string, unknown>,
    containerId?: string,
  ): Promise<boolean> => {
    if (!containerId) {
      toast.error(t('ai.actions.noContainer'))
      return false
    }

    const itemId = data.id as string

    if (!itemId) {
      toast.error(t('ai.actions.invalidData'))
      return false
    }

    // Check if container exists
    const container = gearStore.getContainerById(containerId)
    if (!container) {
      toast.error(t('ai.actions.containerNotFound'))
      return false
    }

    // Delete item using service (API or localStorage based on backend status)
    await gearItemService().deleteItem(itemId)
    toast.success(t('ai.actions.itemDeleted'))

    return true
  }

  const handleCreateContainer = async (data: Record<string, unknown>): Promise<boolean> => {
    const name = data.name as string

    if (!name) {
      toast.error(t('ai.actions.invalidData'))
      return false
    }

    // Create container using service (API or localStorage based on backend status)
    // Note: gearContainerService().createContainer() already handles store updates
    await gearContainerService().createContainer({
      name,
      description: data.description as string,
      type: (data.container_type as string) ?? 'backpack',
    } as ICreateContainerDto)

    toast.success(t('ai.actions.containerCreated', { name }))

    return true
  }

  return {
    executeAction,
  }
}
