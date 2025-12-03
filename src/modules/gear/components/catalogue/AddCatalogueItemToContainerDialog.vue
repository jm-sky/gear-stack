<script setup lang="ts">
import { Package } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { IGlobalCatalogueItem } from '../../types/catalogue.types'
import type { TGearItemPriority, TGearItemStatus } from '../../types/gear.types'
import { useCatalogue } from '../../composables/catalogue/useCatalogue'
import { useGear } from '../../composables/useGear'
import { GearRoutePath } from '../../routes'

const { t } = useI18n()
const router = useRouter()

const props = defineProps<{
  open: boolean
  catalogueItem: IGlobalCatalogueItem
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { containers } = useGear()
const { addCatalogueItemToContainer, isAddingToContainer } = useCatalogue()

// Form state
const selectedContainerId = ref<string>('')
const quantity = ref(1)
const status = ref<TGearItemStatus>('owned')
const priority = ref<TGearItemPriority>('medium')

const statuses: TGearItemStatus[] = ['owned', 'missing', 'toBuy']
const priorities: TGearItemPriority[] = ['critical', 'high', 'medium', 'low']

// Reset form when dialog opens
watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      selectedContainerId.value = ''
      quantity.value = 1
      status.value = 'owned'
      priority.value = 'medium'
    }
  },
)

const handleOpenChange = (open: boolean) => {
  emit('update:open', open)
}

const handleConfirm = async () => {
  if (!selectedContainerId.value) return

  try {
    await addCatalogueItemToContainer(
      selectedContainerId.value,
      props.catalogueItem.id,
      {
        quantity: quantity.value,
        status: status.value,
        priority: priority.value,
      },
    )

    toast.success(t('gear.catalogue.addedToContainer'))
    handleOpenChange(false)

    // Navigate to the container detail page
    router.push(GearRoutePath.ContainerDetailById(selectedContainerId.value))
  } catch (error) {
    console.error('Failed to add catalogue item to container:', error)
    toast.error(t('common.error'))
  }
}

const isOpen = computed({
  get: () => props.open,
  set: (value) => handleOpenChange(value),
})

const canSubmit = computed(() => {
  return selectedContainerId.value && quantity.value > 0 && !isAddingToContainer.value
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click="handleOpenChange(false)"
    >
      <div class="mx-4 w-[95vw] max-w-md rounded-lg border bg-card shadow-lg" @click.stop>
        <div class="space-y-4 p-6">
          <!-- Title -->
          <div>
            <h2 class="text-lg font-semibold">
              {{ t('gear.catalogue.addToContainer') }}
            </h2>
            <p class="mt-1 text-sm text-muted-foreground">
              {{ catalogueItem.name }}
            </p>
          </div>

          <!-- Container Selection -->
          <div class="space-y-2">
            <Label>
              {{ t('gear.catalogue.selectContainer') }}
            </Label>
            <Select v-model="selectedContainerId">
              <SelectTrigger>
                <SelectValue :placeholder="t('gear.catalogue.selectContainerPlaceholder')" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="container in containers" :key="container.id" :value="container.id">
                  <div class="flex items-center gap-2">
                    <Package :size="16" class="text-muted-foreground" />
                    <span>{{ container.name }}</span>
                    <span class="text-xs text-muted-foreground">({{ t(`gear.container.types.${container.type}`) }})</span>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Add Options -->
          <div class="space-y-4 rounded-lg border bg-muted/50 p-4">
            <h3 class="text-sm font-medium">
              {{ t('gear.catalogue.addOptions') }}
            </h3>

            <!-- Quantity -->
            <div class="space-y-2">
              <Label for="quantity">
                {{ t('gear.catalogue.quantity') }}
              </Label>
              <Input
                id="quantity"
                v-model.number="quantity"
                type="number"
                min="1"
                :disabled="isAddingToContainer"
              />
            </div>

            <!-- Status -->
            <div class="space-y-2">
              <Label for="status">
                {{ t('gear.catalogue.status') }}
              </Label>
              <Select v-model="status" :disabled="isAddingToContainer">
                <SelectTrigger id="status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="s in statuses" :key="s" :value="s">
                    {{ t(`gear.item.statuses.${s}`) }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <!-- Priority -->
            <div class="space-y-2">
              <Label for="priority">
                {{ t('gear.catalogue.priority') }}
              </Label>
              <Select v-model="priority" :disabled="isAddingToContainer">
                <SelectTrigger id="priority">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="p in priorities" :key="p" :value="p">
                    {{ t(`gear.item.priorities.${p}`) }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <!-- No containers message -->
          <p v-if="containers.length === 0" class="text-sm text-muted-foreground">
            {{ t('gear.container.empty') }}
          </p>

          <!-- Actions -->
          <div class="flex justify-end gap-2 pt-4">
            <Button variant="outline" :disabled="isAddingToContainer" @click="handleOpenChange(false)">
              {{ t('gear.actions.cancel') }}
            </Button>
            <Button :disabled="!canSubmit" :loading="isAddingToContainer" @click="handleConfirm">
              {{ t('gear.actions.add') }}
            </Button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
