<script setup lang="ts">
import { Package, Search } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
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

const sortByRecency = (a: IGearItemV2, b: IGearItemV2): number => {
  const aTime = new Date(a.updatedAt || a.createdAt).getTime()
  const bTime = new Date(b.updatedAt || b.createdAt).getTime()
  return bTime - aTime
}

const availableContainers = computed<IGearItemV2[]>(() => {
  const allContainers = containers.value
  if (!props.currentContainerId) {
    return [...allContainers].sort(sortByRecency)
  }

  const excludedIds = collectSubtreeIds(props.currentContainerId, allContainers)
  return allContainers.filter(c => !excludedIds.has(c.id)).sort(sortByRecency)
})

const searchQuery = ref<string>('')
const selectedContainerId = ref<string>('')

const normalizedQuery = computed<string>(() => searchQuery.value.trim().toLowerCase())

const filteredContainers = computed<IGearItemV2[]>(() => {
  const query = normalizedQuery.value
  if (!query) {
    return availableContainers.value
  }
  return availableContainers.value.filter((c) => {
    const name = c.name.toLowerCase()
    const typeLabel = t(`gear.container.types.${c.containerType ?? 'other'}`).toLowerCase()
    return name.includes(query) || typeLabel.includes(query)
  })
})

const recentContainers = computed<IGearItemV2[]>(() => {
  if (normalizedQuery.value) {
    return []
  }
  return availableContainers.value.slice(0, 3)
})

const recentIds = computed<Set<string>>(() => new Set(recentContainers.value.map(c => c.id)))

const remainingContainers = computed<IGearItemV2[]>(() => {
  if (normalizedQuery.value) {
    return filteredContainers.value
  }
  return filteredContainers.value.filter(c => !recentIds.value.has(c.id))
})

const containerTypeLabel = (container: IGearItemV2): string => {
  return t(`gear.container.types.${container.containerType ?? 'other'}`)
}

const selectContainer = (id: string): void => {
  selectedContainerId.value = id
}

const handleOpenChange = (open: boolean): void => {
  emit('update:open', open)
  if (!open) {
    selectedContainerId.value = ''
    searchQuery.value = ''
  }
}

const handleConfirm = (): void => {
  if (selectedContainerId.value) {
    emit('confirm', selectedContainerId.value)
    handleOpenChange(false)
  }
}
</script>

<template>
  <Dialog :open="props.open" @update:open="handleOpenChange">
    <DialogContent class="w-full sm:max-w-lg">
      <DialogHeader>
        <DialogTitle>{{ t('gear.container.addNested') }}</DialogTitle>
        <DialogDescription>
          {{ t('gear.container.addNestedDescription') }}
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-4">
        <div class="relative">
          <Search class="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            v-model="searchQuery"
            class="pl-9"
            :placeholder="t('gear.container.searchContainers')"
            :aria-label="t('gear.container.searchContainers')"
            :disabled="availableContainers.length === 0"
          />
        </div>

        <p
          v-if="availableContainers.length === 0"
          class="text-sm text-muted-foreground"
        >
          {{ t('gear.container.noContainersAvailable') }}
        </p>

        <div
          v-else
          class="max-h-72 space-y-4 overflow-y-auto"
        >
          <div
            v-if="recentContainers.length > 0"
            class="space-y-2"
          >
            <h4 class="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              {{ t('gear.container.recentContainers') }}
            </h4>
            <div class="space-y-1">
              <button
                v-for="container in recentContainers"
                :key="`recent-${container.id}`"
                type="button"
                :class="cn(
                  'flex w-full items-center gap-2 rounded-md border px-3 py-2 text-left text-sm transition-colors hover:bg-accent',
                  selectedContainerId === container.id && 'border-primary bg-primary/10',
                )"
                @click="selectContainer(container.id)"
              >
                <Package class="size-4 shrink-0 text-muted-foreground" />
                <span class="min-w-0 truncate font-medium">{{ container.name }}</span>
                <span class="shrink-0 text-xs text-muted-foreground">
                  ({{ containerTypeLabel(container) }})
                </span>
              </button>
            </div>
          </div>

          <div
            v-if="remainingContainers.length > 0"
            class="space-y-2"
          >
            <h4
              v-if="!normalizedQuery"
              class="text-xs font-medium uppercase tracking-wide text-muted-foreground"
            >
              {{ t('gear.container.allContainers') }}
            </h4>
            <div class="space-y-1">
              <button
                v-for="container in remainingContainers"
                :key="container.id"
                type="button"
                :class="cn(
                  'flex w-full items-center gap-2 rounded-md border px-3 py-2 text-left text-sm transition-colors hover:bg-accent',
                  selectedContainerId === container.id && 'border-primary bg-primary/10',
                )"
                @click="selectContainer(container.id)"
              >
                <Package class="size-4 shrink-0 text-muted-foreground" />
                <span class="min-w-0 truncate font-medium">{{ container.name }}</span>
                <span class="shrink-0 text-xs text-muted-foreground">
                  ({{ containerTypeLabel(container) }})
                </span>
              </button>
            </div>
          </div>

          <p
            v-else-if="normalizedQuery && filteredContainers.length === 0"
            class="text-sm text-muted-foreground"
          >
            {{ t('gear.container.noContainersAvailable') }}
          </p>
        </div>
      </div>

      <DialogFooter class="flex-col-reverse gap-2 sm:flex-row">
        <Button
          variant="outline"
          class="w-full sm:w-auto"
          @click="handleOpenChange(false)"
        >
          {{ t('gear.actions.cancel') }}
        </Button>
        <Button
          class="w-full sm:w-auto"
          :disabled="!selectedContainerId"
          @click="handleConfirm"
        >
          {{ t('gear.actions.add') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
