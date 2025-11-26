<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IGearContainer } from '../types/gear.types'
import { useGear } from '../composables/useGear'
import FavoriteStarIcon from './FavoriteStarIcon.vue'

const { t } = useI18n()
const { updateContainer } = useGear()
const { handleError } = useHandleError()

const { container } = defineProps<{
  container: IGearContainer
}>()

const handleToggleFavorite = async () => {
  try {
    const newFavoriteStatus = !container.favorite
    await updateContainer(container.id, {
      favorite: newFavoriteStatus,
    })
    toast.success(
      newFavoriteStatus
        ? t('gear.container.favoriteAdded')
        : t('gear.container.favoriteRemoved'),
    )
  } catch (error) {
    console.error('Failed to update favorite status:', error)
    handleError(error)
  }
}
</script>

<template>
  <Button
    v-tooltip.bottom="container.favorite ? t('gear.container.removeFavorite') : t('gear.container.addFavorite')"
    variant="ghost"
    size="sm"
    :aria-label="container.favorite ? t('gear.container.removeFavorite') : t('gear.container.addFavorite')"
    @click.stop="handleToggleFavorite"
  >
    <FavoriteStarIcon :favorite="container.favorite" />
  </Button>
</template>
