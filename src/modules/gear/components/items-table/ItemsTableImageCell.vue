<script setup lang="ts">
import { ImageIcon } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { type RouteLocationRaw, RouterLink } from 'vue-router'
import { GearRoutePath } from '@/modules/gear/routes'
import { itemImageApiService } from '@/modules/gear/services/itemImageApiService'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IItemImage } from '@/modules/gear/types/itemImage.types'

const props = defineProps<{
  itemId: string
  containerId?: string
  publicMode?: boolean
}>()

const { handleError } = useHandleError()

const image = ref<IItemImage | null>(null)
const isLoading = ref(false)
const hasError = ref(false)

async function loadPrimaryImage() {
  if (isLoading.value || image.value || hasError.value) return

  try {
    isLoading.value = true
    const images = await itemImageApiService.getImages(props.itemId)
    if (!images.length) {
      image.value = null
      return
    }

    const primary = images.find(img => img.isPrimary) ?? images[0]
    image.value = primary ?? null
  } catch (error: unknown) {
    console.error('Failed to load item image', error)
    hasError.value = true
    handleError(error)
  } finally {
    isLoading.value = false
  }
}

const routeTo = computed<RouteLocationRaw | undefined>(() => {
  if (!image.value || !props.containerId) return undefined

  if (props.publicMode) {
    return GearRoutePath.PublicItemDetailById(props.containerId, props.itemId)
  }
  return {
      path: GearRoutePath.ItemDetailById(props.containerId, props.itemId),
      query: { from: 'container' },
    }
})

onMounted(() => {
  void loadPrimaryImage()
})
</script>

<template>
  <div class="flex items-center justify-center">
    <!-- Loading skeleton -->
    <div
      v-if="isLoading"
      class="size-10 rounded-md bg-muted animate-pulse"
    />

    <!-- Image thumbnail -->
    <component
      :is="routeTo ? RouterLink : 'button'"
      v-else-if="image && !hasError"
      :to="routeTo"
      class="-my-1 group block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-md overflow-hidden"
    >
      <img
        :src="image.url"
        :alt="image.fileName"
        loading="lazy"
        class="size-12 rounded-md object-cover border border-border group-hover:border-primary/50 transition-colors"
      />
    </component>

    <!-- No image -->
    <span v-else class="flex items-center justify-center size-10 text-muted-foreground">
      <ImageIcon class="size-4" />
    </span>
  </div>
</template>


