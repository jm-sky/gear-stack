<script setup lang="ts">
import { isAxiosError } from 'axios'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import FileDropZone from '@/components/ui/FileDropZone.vue'
import { itemImageApiService } from '@/modules/gear/services/itemImageApiService'
import ItemImageCard from './ItemImageCard.vue'
import ItemImageGalleryEmptyState from './ItemImageGalleryEmptyState.vue'
import type { IItemImage } from '@/modules/gear/types/itemImage.types'
import type { TUUID } from '@/shared/types/base.type'

const props = defineProps<{
  itemId: TUUID
  editable: boolean
}>()

const { t } = useI18n()

const images = ref<IItemImage[]>([])
const draggedImages = ref<IItemImage[]>([]) // Separate state for drag operations
const isLoading = ref(false)
const isDragging = ref(false)
const draggedIndex = ref(-1)
const dragOverIndex = ref<number | null>(null) // Track which index we're hovering over
const imageLoadErrors = ref<Set<TUUID>>(new Set())

const sortedImages = computed(() => {
  const source = isDragging.value ? draggedImages.value : images.value
  return [...source].sort((a, b) => a.order - b.order)
})

async function loadImages() {
  try {
    isLoading.value = true
    images.value = await itemImageApiService.getImages(props.itemId)
    imageLoadErrors.value.clear()
  }
  catch (error: unknown) {
    toast.error(t('fileUpload.imageGallery.messages.loadFailed'))
    console.error(error)
  }
  finally {
    isLoading.value = false
  }
}

async function handleFilesSelected(files: File[]) {
  if (files.length === 0) return

  // Upload all files sequentially
  await uploadImages(files)
}

function handleDropZoneError(message: string) {
  toast.error(message)
}

async function uploadImages(files: File[]) {
  if (files.length === 0) return

  try {
    isLoading.value = true
    const hasPrimary = images.value.some(img => img.isPrimary)
    const uploadedImages: IItemImage[] = []
    const errors: string[] = []

    // Upload files sequentially
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      if (!file) continue

      try {
        // First image should be primary if there's no primary yet
        const isPrimary = !hasPrimary && i === 0
        const newImage = await itemImageApiService.uploadImage(props.itemId, file, isPrimary)
        uploadedImages.push(newImage)
        images.value.push(newImage)
      }
      catch (error: unknown) {
        const message = isAxiosError(error) ? error.response?.data?.detail : null
        const errorMessage = message ?? t('fileUpload.imageGallery.messages.uploadFailed')
        errors.push(`${file.name}: ${errorMessage}`)
        console.error(`Failed to upload ${file.name}:`, error)
      }
    }

    // Show success/error messages
    if (uploadedImages.length > 0) {
      if (uploadedImages.length === 1) {
        toast.success(t('fileUpload.imageGallery.messages.uploadSuccess'))
      }
      else {
        toast.success(t('fileUpload.imageGallery.messages.uploadSuccessMultiple', { count: uploadedImages.length }))
      }
    }

    if (errors.length > 0) {
      toast.error(errors.join(', '))
    }
  }
  catch (error: unknown) {
    toast.error(t('fileUpload.imageGallery.messages.uploadFailed'))
    console.error(error)
  }
  finally {
    isLoading.value = false
  }
}

async function deleteImage(imageId: TUUID) {
  if (!confirm(t('fileUpload.imageGallery.confirmDelete'))) {
    return
  }

  try {
    await itemImageApiService.deleteImage(imageId)
    images.value = images.value.filter(img => img.id !== imageId)
    imageLoadErrors.value.delete(imageId)
    toast.success(t('fileUpload.imageGallery.messages.deleteSuccess'))
  }
  catch (error: unknown) {
    toast.error(t('fileUpload.imageGallery.messages.deleteFailed'))
    console.error(error)
  }
}

async function setPrimary(imageId: TUUID) {
  try {
    await itemImageApiService.setPrimaryImage(props.itemId, imageId)
    images.value = images.value.map(img => ({
      ...img,
      isPrimary: img.id === imageId,
    }))
    toast.success(t('fileUpload.imageGallery.messages.primarySuccess'))
  }
  catch (error: unknown) {
    toast.error(t('fileUpload.imageGallery.messages.primaryFailed'))
    console.error(error)
  }
}

// Drag and drop reordering with proper state management
const initialDragIndex = ref(-1) // Store initial index to compare later

function handleDragStart(index: number) {
  draggedIndex.value = index
  initialDragIndex.value = index
  // Initialize dragged state with current sorted images BEFORE setting isDragging
  // We need to use images.value directly and sort it, not sortedImages computed
  // because sortedImages depends on isDragging which we're about to set
  const currentSorted = [...images.value].sort((a, b) => a.order - b.order)
  draggedImages.value = currentSorted
  isDragging.value = true
}

function handleDragEnter(event: DragEvent, index: number) {
  event.preventDefault()
  if (draggedIndex.value === index || draggedIndex.value === -1) {
    return
  }
  // Update visual feedback on enter
  dragOverIndex.value = index
}

function handleDragLeave(event: DragEvent, index: number) {
  // Only reset if we're actually leaving this element
  const relatedTarget = event.relatedTarget as HTMLElement | null
  const currentTarget = event.currentTarget as HTMLElement | null

  if (currentTarget && relatedTarget && !currentTarget.contains(relatedTarget)) {
    if (dragOverIndex.value === index) {
      dragOverIndex.value = null
    }
  }
}

function handleDragOver(event: DragEvent, index: number) {
  event.preventDefault()
  if (draggedIndex.value === index || draggedIndex.value === -1) {
    return
  }

  // Update visual feedback (in case dragenter was missed)
  if (dragOverIndex.value !== index) {
    dragOverIndex.value = index
  }

  // Create new array for immutable update
  const newOrder = [...draggedImages.value]
  const draggedItem = newOrder[draggedIndex.value]

  // Guard against undefined draggedItem
  if (!draggedItem) {
    return
  }

  // Remove from old position
  newOrder.splice(draggedIndex.value, 1)
  // Insert at new position
  newOrder.splice(index, 0, draggedItem)

  // Update dragged state
  draggedImages.value = newOrder
  draggedIndex.value = index
}

async function handleDragEnd() {
  isDragging.value = false
  dragOverIndex.value = null

  if (draggedIndex.value === -1 || initialDragIndex.value === -1) {
    draggedIndex.value = -1
    initialDragIndex.value = -1
    draggedImages.value = []
    return
  }

  // Check if order actually changed by comparing initial and final positions
  const orderChanged = initialDragIndex.value !== draggedIndex.value

  // Also check if the order of images changed (in case of multiple reorders)
  const originalOrder = [...images.value].sort((a, b) => a.order - b.order).map(img => img.id)
  const newOrder = draggedImages.value.map(img => img.id)
  const orderChangedByIds = JSON.stringify(originalOrder) !== JSON.stringify(newOrder)

  // Only send request if order actually changed
  if (!orderChanged && !orderChangedByIds) {
    draggedIndex.value = -1
    initialDragIndex.value = -1
    draggedImages.value = []
    return
  }

  // Use draggedImages which has the correct final order, not sortedImages
  // because sortedImages might still be sorting by old order values
  const finalOrder = draggedImages.value.map((img, index) => ({
    id: img.id,
    order: index,
  }))

  try {
    await itemImageApiService.reorderImages(props.itemId, finalOrder)
    // Update main state with new order from draggedImages (which has correct order)
    images.value = draggedImages.value.map((img, index) => ({
      ...img,
      order: index,
    }))
    toast.success(t('fileUpload.imageGallery.messages.reorderSuccess'))
  }
  catch (error: unknown) {
    toast.error(t('fileUpload.imageGallery.messages.reorderFailed'))
    console.error(error)
    // Reset to server state
    await loadImages()
  }
  finally {
    draggedIndex.value = -1
    initialDragIndex.value = -1
    draggedImages.value = []
  }
}

function handleImageError(imageId: TUUID) {
  imageLoadErrors.value.add(imageId)
}

onMounted(() => {
  loadImages()
})
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-row items-center justify-between gap-2">
      <h3 class="text-lg font-semibold">
        {{ t('fileUpload.imageGallery.title') }}
      </h3>
      <div class="flex flex-row gap-2 items-center justify-end">
        <slot name="header-actions" />
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="isLoading && images.length === 0" class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      <div
        v-for="i in 4"
        :key="i"
        class="h-48 animate-pulse rounded-lg bg-muted"
      />
    </div>

    <!-- Image gallery -->
    <div v-else class="flex flex-wrap gap-4">
      <!-- Empty state -->
      <ItemImageGalleryEmptyState v-if="images.length === 0" />

      <ItemImageCard
        v-for="(image, index) in sortedImages"
        :key="image.id"
        :image
        :index
        :editable
        :has-error="imageLoadErrors.has(image.id)"
        :is-drag-over="isDragging && dragOverIndex === index"
        :is-dragging="isDragging && draggedIndex === index"
        class="w-full md:w-[calc(25%-1rem)]"
        @dragend="handleDragEnd"
        @dragenter="handleDragEnter"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @dragstart="handleDragStart"
        @set-primary="setPrimary"
        @delete="deleteImage"
        @image-error="handleImageError"
      />

      <FileDropZone
        v-if="editable"
        :disabled="isLoading"
        :max-files="10"
        accept="image/jpeg,image/png,image/webp,image/gif"
        class="min-h-32 flex-1"
        @error="handleDropZoneError"
        @files-selected="handleFilesSelected"
      />
    </div>
  </div>
</template>
