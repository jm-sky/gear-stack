<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useBackend } from '@/shared/composables/useBackend'
import type { IGearContainer, TRatingType, TRatingValue } from '../types/gear.types'
import { useGear } from '../composables/useGear'
import { useIsContainerOwner } from '../composables/useIsContainerOwner'
import { gearContainerApiService } from '../services/gearContainerApiService'
import ContainerRatingCard from './ContainerRatingCard.vue'

const { t } = useI18n()
const { shouldUseAPI } = useBackend()
const { getContainerById } = useGear()

const props = defineProps<{
  container: IGearContainer
}>()

// Rating state
const isRatingLoading = ref(false)

const isOwner = useIsContainerOwner(props.container, true)
const isPublic = computed(() => props.container?.isPublic ?? false)

const handleRate = async (rating: TRatingValue, type: TRatingType) => {
  if (!props.container) return

  isRatingLoading.value = true
  try {
    await gearContainerApiService.rateContainer(
      props.container.id,
      rating,
      type
    )
    // Refresh container data
    if (shouldUseAPI.value) {
      await getContainerById(props.container.id)
    }
    toast.success(t('gear.container.ratingUpdated'))
  } catch (error) {
    console.error('Failed to rate container:', error)
    toast.error(t('gear.errors.ratingFailed'))
  } finally {
    isRatingLoading.value = false
  }
}

const handleDeleteRating = async (type: TRatingType) => {
  if (!props.container) return

  isRatingLoading.value = true
  try {
    await gearContainerApiService.deleteContainerRating(
      props.container.id,
      type
    )
    // Refresh container data
    if (shouldUseAPI.value) {
      await getContainerById(props.container.id)
    }
    toast.success(t('gear.container.ratingDeleted'))
  } catch (error) {
    console.error('Failed to delete rating:', error)
    toast.error(t('gear.errors.deleteRatingFailed'))
  } finally {
    isRatingLoading.value = false
  }
}
</script>

<template>
  <Card v-if="container && shouldUseAPI" class="gap-4">
    <CardHeader>
      <CardTitle>{{ t('gear.container.averageUserRating') }}</CardTitle>
    </CardHeader>
    <CardContent>
      <ContainerRatingCard
        :container
        :is-owner
        :is-public
        :loading="isRatingLoading"
        @rate="handleRate"
        @delete-rating="handleDeleteRating"
      />
    </CardContent>
  </Card>
</template>
