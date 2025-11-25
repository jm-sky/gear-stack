<script setup lang="ts">
import { Search } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import Button from '@/components/ui/button/Button.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import { type IImageSearchResult, imageSearchApiService } from '../services/imageSearchApiService'
import ImageSearchDialog from './ImageSearchDialog.vue'

const { t } = useI18n()
const { handleError } = useHandleError()

const { itemId } = defineProps<{
  itemId: string
}>()

const isSearchingImages = ref(false)
const showDialog = ref(false)
const searchResults = ref<IImageSearchResult[]>([])

const emit = defineEmits<{
  reload: []
}>()

// Handle image search
const handleSearchImages = async () => {
  try {
    isSearchingImages.value = true

    // Search for images
    const response = await imageSearchApiService.searchImages({
      itemId: itemId,
    })

    if (response.results.length === 0) {
      toast.info(t('gear.imageSearch.noResults', 'No images found'))
      return
    }

    // If only 1 result, add it automatically
    if (response.results.length === 1 && response.results[0]) {
      const result = response.results[0]
      await imageSearchApiService.downloadAndAddImage({
        itemId: itemId,
        imageUrl: result.imageUrl,
        sourceUrl: result.sourceUrl,
        sourceName: result.sourceName,
        searchEngineId: result.searchEngineId,
        isPrimary: false,
      })

      toast.success(t('gear.imageSearch.imageAdded', 'Image added successfully'))
      emit('reload')
      return
    }

    // If multiple results, show dialog
    searchResults.value = response.results
    showDialog.value = true
  } catch (error: unknown) {
    console.error('Failed to search images:', error)
    handleError(error)
  } finally {
    isSearchingImages.value = false
  }
}

const handleImageSelected = () => {
  emit('reload')
}
</script>

<template>
  <div>
    <Button
      :loading="isSearchingImages"
      variant="outline"
      size="sm"
      @click="handleSearchImages"
    >
      <Search class="size-4" />
      {{ isSearchingImages ? t('gear.imageSearch.searching', 'Searching...') : t('gear.imageSearch.searchImages', 'Search Images') }}
    </Button>

    <ImageSearchDialog
      :open="showDialog"
      :item-id="itemId"
      :results="searchResults"
      @update:open="showDialog = $event"
      @image-selected="handleImageSelected"
    />
  </div>
</template>
