<script setup lang="ts">
import { Check } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { useHandleError } from '@/shared/composables/useHandleError'
import { type IImageSearchResult, imageSearchApiService } from '../services/imageSearchApiService'

const { t } = useI18n()
const { handleError } = useHandleError()

const props = defineProps<{
  open: boolean
  itemId: string
  results: IImageSearchResult[]
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'image-selected': [image: IImageSearchResult]
}>()

const selectedImage = ref<IImageSearchResult | null>(null)
const isAdding = ref(false)

const handleOpenChange = (value: boolean) => {
  emit('update:open', value)
  if (!value) {
    selectedImage.value = null
  }
}

const handleSelectImage = async (image: IImageSearchResult) => {
  if (isAdding.value) return

  try {
    isAdding.value = true
    selectedImage.value = image

    await imageSearchApiService.downloadAndAddImage({
      itemId: props.itemId,
      imageUrl: image.imageUrl,
      sourceUrl: image.sourceUrl,
      sourceName: image.sourceName,
      searchEngineId: image.searchEngineId,
      isPrimary: false,
    })

    toast.success(t('gear.imageSearch.imageAdded', 'Image added successfully'))
    emit('image-selected', image)
    handleOpenChange(false)
  } catch (error: unknown) {
    console.error('Failed to add image:', error)
    handleError(error)
    selectedImage.value = null
  } finally {
    isAdding.value = false
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="handleOpenChange">
    <DialogContent class="max-w-4xl max-h-[90vh] flex flex-col">
      <DialogHeader>
        <DialogTitle>
          {{ t('gear.imageSearch.selectImage', 'Select Image') }}
        </DialogTitle>
        <DialogDescription>
          {{ t('gear.imageSearch.selectImageDescription', 'Choose an image to add to this item') }}
        </DialogDescription>
      </DialogHeader>

      <div class="flex-1 overflow-y-auto">
        <div v-if="results.length === 0" class="text-center py-8 text-muted-foreground">
          {{ t('gear.imageSearch.noResults', 'No images found') }}
        </div>

        <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          <button
            v-for="(image, index) in results"
            :key="index"
            type="button"
            class="group relative aspect-square rounded-lg overflow-hidden border-2 transition-all hover:border-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
            :class="{
              'border-primary': selectedImage?.imageUrl === image.imageUrl,
              'border-border': selectedImage?.imageUrl !== image.imageUrl,
            }"
            :disabled="isAdding"
            @click="handleSelectImage(image)"
          >
            <img
              :src="image.thumbnailUrl || image.imageUrl"
              :alt="`Image ${index + 1}`"
              class="w-full h-full object-cover"
              loading="lazy"
            />

            <!-- Selected indicator -->
            <div
              v-if="selectedImage?.imageUrl === image.imageUrl"
              class="absolute inset-0 bg-primary/20 flex items-center justify-center"
            >
              <div class="bg-primary text-primary-foreground rounded-full p-2">
                <Check class="size-4" />
              </div>
            </div>

            <!-- Source badge -->
            <div
              v-if="image.sourceName"
              class="absolute bottom-2 left-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded truncate"
            >
              {{ t('gear.imageSearch.source', 'Source') }}: {{ image.sourceName }}
            </div>

            <!-- Loading overlay -->
            <div
              v-if="isAdding && selectedImage?.imageUrl === image.imageUrl"
              class="absolute inset-0 bg-background/80 flex items-center justify-center"
            >
              <div class="text-sm text-muted-foreground">
                {{ t('gear.imageSearch.adding', 'Adding...') }}
              </div>
            </div>
          </button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>

