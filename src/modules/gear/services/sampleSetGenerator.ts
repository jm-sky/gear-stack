import type { ICreateItemDto } from '../types/gear.types'
import { gearService } from './gearService'
import type { TUUID } from '@/shared/types/base.type'

interface ISampleSetItem {
  nameKey: string
  category: ICreateItemDto['category']
  weight: number
  weightUnit: ICreateItemDto['weightUnit']
  quantity?: number
  priority?: ICreateItemDto['priority']
  status?: ICreateItemDto['status']
}

/**
 * Generates a sample gear set with containers and items
 * @param t - Translation function from vue-i18n
 * @returns Array of created container IDs
 */
export async function generateSampleSet(t: (key: string) => string): Promise<TUUID[]> {
  const backpack = await gearService.createContainer({
    name: t('gear.sampleSet.backpack'),
    type: 'backpack',
    description: t('gear.sampleSet.generate'),
  })
  const backpackId = backpack.id

  // Create pouch container (will be added as nested container item)
  const pouch = await gearService.createContainer({
    name: t('gear.sampleSet.pouch'),
    type: 'pouch',
  })
  const pouchId = pouch.id

  // Items in backpack
  const backpackItems: ISampleSetItem[] = [
    {
      nameKey: 'knife',
      category: 'tools',
      weight: 150,
      weightUnit: 'g',
      priority: 'critical',
      status: 'owned',
    },
    {
      nameKey: 'multiTool',
      category: 'tools',
      weight: 200,
      weightUnit: 'g',
      priority: 'high',
      status: 'owned',
    },
    {
      nameKey: 'flashlight',
      category: 'light',
      weight: 100,
      weightUnit: 'g',
      priority: 'critical',
      status: 'owned',
    },
    {
      nameKey: 'firstAidKit',
      category: 'firstAid',
      weight: 300,
      weightUnit: 'g',
      priority: 'critical',
      status: 'owned',
    },
    {
      nameKey: 'paracord',
      category: 'tools',
      weight: 50,
      weightUnit: 'g',
      quantity: 1,
      priority: 'medium',
      status: 'owned',
    },
  ]

  // Items in pouch
  const pouchItems: ISampleSetItem[] = [
    {
      nameKey: 'ferroRod',
      category: 'fire',
      weight: 30,
      weightUnit: 'g',
      priority: 'high',
      status: 'owned',
    },
    {
      nameKey: 'tinder',
      category: 'fire',
      weight: 20,
      weightUnit: 'g',
      priority: 'high',
      status: 'owned',
    },
    {
      nameKey: 'lighter',
      category: 'fire',
      weight: 15,
      weightUnit: 'g',
      priority: 'medium',
      status: 'owned',
    },
  ]

  // Create items in backpack
  for (const item of backpackItems) {
    await gearService.createItem(backpackId, {
      name: t(`gear.sampleSet.${item.nameKey}`),
      category: item.category,
      weight: item.weight,
      weightUnit: item.weightUnit,
      quantity: item.quantity ?? 1,
      priority: item.priority ?? 'medium',
      status: item.status ?? 'owned',
    })
  }

  // Create pouch as nested container item in backpack
  await gearService.createItem(backpackId, {
    name: t('gear.sampleSet.pouch'),
    category: 'tools',
    weight: 50,
    weightUnit: 'g',
    quantity: 1,
    priority: 'high',
    status: 'owned',
    containerId: pouchId,
  })

  // Create items in pouch
  for (const item of pouchItems) {
    await gearService.createItem(pouchId, {
      name: t(`gear.sampleSet.${item.nameKey}`),
      category: item.category,
      weight: item.weight,
      weightUnit: item.weightUnit,
      quantity: item.quantity ?? 1,
      priority: item.priority ?? 'medium',
      status: item.status ?? 'owned',
    })
  }

  return [backpackId]
}
