<script setup lang="ts">
import { BookIcon, Link2Off, MoreHorizontalIcon, Sparkles } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import type { IGearItem } from '../types/gear.types'
import { useCatalogue } from '../composables/catalogue/useCatalogue'

const { t } = useI18n()
const { updateItemFromCatalogue, unlinkItemFromCatalogue, isUpdatingFromCatalogue, isUnlinking } = useCatalogue()

const matchDialogOpen = defineModel<boolean>('matchDialogOpen', { default: false })

const { item } = defineProps<{
  item: IGearItem
}>()

const emit = defineEmits<{
  itemUpdated: []
}>()

const handleMatchWithCatalogue = () => {
  matchDialogOpen.value = true
}

const handleUpdateFromCatalogue = async () => {
  if (!item.catalogueItemId) return

  try {
    await updateItemFromCatalogue(item.id)
    toast.success(t('gear.catalogue.updatedFromCatalogue'))
    emit('itemUpdated')
  } catch (error) {
    console.error('Failed to update item from catalogue:', error)
    toast.error(t('common.error'))
  }
}

const handleUnlinkFromCatalogue = async () => {
  if (!item.catalogueItemId) return

  try {
    await unlinkItemFromCatalogue(item.id)
    toast.success(t('gear.catalogue.unlinkedSuccess'))
    emit('itemUpdated')
  } catch (error) {
    console.error('Failed to unlink item from catalogue:', error)
    toast.error(t('common.error'))
  }
}

const isCatalogueActionLoading = computed(() => isUpdatingFromCatalogue.value || isUnlinking.value)

const isLinkedToCatalogue = computed(() => !!item.catalogueItemId)
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button size="sm" variant="ghost">
        <MoreHorizontalIcon class="size-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <DropdownMenuItem
        v-if="!isLinkedToCatalogue"
        :disabled="isCatalogueActionLoading"
        @click="handleMatchWithCatalogue"
      >
        <Sparkles class="size-4" />
        {{ t('gear.catalogue.matchWithCatalogue') }}
      </DropdownMenuItem>
      <DropdownMenuItem
        v-if="isLinkedToCatalogue"
        :disabled="isCatalogueActionLoading"
        @click="handleUpdateFromCatalogue"
      >
        <BookIcon class="size-4" />
        {{ t('gear.catalogue.updateFromCatalogue') }}
      </DropdownMenuItem>
      <DropdownMenuItem
        v-if="isLinkedToCatalogue"
        :disabled="isCatalogueActionLoading"
        @click="handleUnlinkFromCatalogue"
      >
        <Link2Off class="size-4" />
        {{ t('gear.catalogue.unlinkFromCatalogue') }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
