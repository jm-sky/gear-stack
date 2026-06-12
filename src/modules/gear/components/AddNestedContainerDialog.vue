<script setup lang="ts">
import { Package } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useGearV2 } from '../composables/useGearV2'

const { t } = useI18n()

const props = defineProps<{
  open: boolean
  currentContainerId: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  confirm: [containerId: string]
}>()

// Load the full container list through the active V2 service (API when authenticated,
// localStorage otherwise) into the store. The container detail page only loads the current
// container + its children, so we fetch all containers when the dialog opens.
const { containers, getItems } = useGearV2()

watch(
  () => props.open,
  (open) => {
    if (open) {
      getItems({ itemType: 'container' }).catch(() => {
        // Best-effort; fall back to whatever is already in the store
      })
    }
  },
  { immediate: true },
)

/**
 * Collect a container id and all of its descendants (V2 hierarchy via parentItemId).
 */
const collectSubtreeIds = (rootId: string, all: IGearItemV2[]): Set<string> => {
  const ids = new Set<string>([rootId])
  const walk = (parentId: string) => {
    for (const c of all) {
      if (c.parentItemId === parentId && !ids.has(c.id)) {
        ids.add(c.id)
        walk(c.id)
      }
    }
  }
  walk(rootId)
  return ids
}

// Get available containers for selection (exclude current container and its nested containers)
const availableContainers = computed<IGearItemV2[]>(() => {
  const allContainers = containers.value
  if (!props.currentContainerId) {
    return allContainers
  }

  const excludedIds = collectSubtreeIds(props.currentContainerId, allContainers)
  return allContainers.filter(c => !excludedIds.has(c.id))
})

const selectedContainerId = ref<string>('')

const handleOpenChange = (open: boolean) => {
  emit('update:open', open)
  if (!open) {
    selectedContainerId.value = ''
  }
}

const handleConfirm = () => {
  if (selectedContainerId.value) {
    emit('confirm', selectedContainerId.value)
    handleOpenChange(false)
  }
}

const isOpen = computed({
  get: () => props.open,
  set: (value) => handleOpenChange(value),
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click="handleOpenChange(false)"
    >
      <div
        class="bg-card rounded-lg border shadow-lg w-[95vw] max-w-md mx-4"
        @click.stop
      >
        <div class="p-6 space-y-4">
          <div>
            <h2 class="text-lg font-semibold">
              {{ t('gear.container.addNested') }}
            </h2>
            <p class="text-sm text-muted-foreground mt-1">
              {{ t('gear.container.addNestedDescription') }}
            </p>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium">
              {{ t('gear.container.selectContainer') }}
            </label>
            <Select v-model="selectedContainerId">
              <SelectTrigger>
                <SelectValue :placeholder="t('gear.container.selectContainerPlaceholder')" />
              </SelectTrigger>
              <SelectContent>
                <template v-for="container in availableContainers" :key="container.id">
                  <SelectItem :value="container.id">
                    <div class="flex items-center gap-2">
                      <Package :size="16" class="text-muted-foreground" />
                      <span>{{ container.name }}</span>
                      <span class="text-xs text-muted-foreground">({{ t(`gear.container.types.${container.containerType ?? 'other'}`) }})</span>
                    </div>
                  </SelectItem>
                </template>
              </SelectContent>
            </Select>
          </div>

          <p v-if="availableContainers.length === 0" class="text-sm text-muted-foreground">
            {{ t('gear.container.noContainersAvailable') }}
          </p>

          <div class="flex justify-end gap-2 pt-4">
            <Button variant="outline" @click="handleOpenChange(false)">
              {{ t('gear.actions.cancel') }}
            </Button>
            <Button :disabled="!selectedContainerId" @click="handleConfirm">
              {{ t('gear.actions.add') }}
            </Button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

