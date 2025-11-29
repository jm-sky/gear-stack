<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { IGearContainer, TRatingType, TRatingValue } from '../types/gear.types'
import RatingStars from './RatingStars.vue'

interface Props {
  container: IGearContainer
  isOwner?: boolean
  isPublic?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isOwner: false,
  isPublic: false,
  loading: false
})

const emit = defineEmits<{
  'rate': [rating: TRatingValue, type: TRatingType]
  'delete-rating': [type: TRatingType]
}>()

const { t } = useI18n()

const ownerRating = computed(() => props.container.ownerRating)
const userRating = computed(() => props.container.userRating)
const averageUserRating = computed(() => props.container.averageUserRating)
const userRatingCount = computed(() => props.container.userRatingCount ?? 0)

function handleOwnerRatingChange(rating: TRatingValue | null) {
  if (rating === null) {
    emit('delete-rating', 'owner')
  } else {
    emit('rate', rating, 'owner')
  }
}

function handleUserRatingChange(rating: TRatingValue | null) {
  if (rating === null) {
    emit('delete-rating', 'user')
  } else {
    emit('rate', rating, 'user')
  }
}
</script>

<template>
  <div class="space-y-4">
    <!-- Owner Rating Section -->
    <div v-if="isOwner" class="space-y-2">
      <div class="flex items-center justify-between">
        <label class="text-sm font-medium">
          {{ t('gear.container.ownerRating') }}
        </label>
      </div>
      <RatingStars
        :rating="ownerRating"
        :interactive="true"
        :disabled="loading"
        @update:rating="handleOwnerRatingChange"
      />
      <p class="text-xs text-gray-500 dark:text-gray-400">
        {{ t('gear.container.ownerRatingDescription') }}
      </p>
    </div>

    <!-- User Rating Section -->
    <div v-if="isPublic && !isOwner" class="space-y-2">
      <div class="flex items-center justify-between">
        <label class="text-sm font-medium">
          {{ t('gear.container.yourRating') }}
        </label>
      </div>
      <RatingStars
        :rating="userRating"
        :interactive="true"
        :disabled="loading"
        @update:rating="handleUserRatingChange"
      />
    </div>

    <!-- Average User Rating Display -->
    <div v-if="isPublic && userRatingCount > 0" class="space-y-2">
      <div class="flex items-center justify-between">
        <label class="text-sm font-medium">
          {{ t('gear.container.averageUserRating') }}
        </label>
        <span class="text-sm text-gray-500 dark:text-gray-400">
          ({{ userRatingCount }} {{ t('gear.container.ratings') }})
        </span>
      </div>
      <RatingStars
        :rating="averageUserRating"
        :show-number="true"
        :interactive="false"
      />
    </div>
  </div>
</template>

