<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import Button from '@/components/ui/button/Button.vue'
import { Input } from '@/components/ui/input'
import { itemImageApiService } from '@/modules/gear/services/itemImageApiService'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IItemImage } from '../types/itemImage.types'
import type { TUUID } from '@/shared/types/base.type'

const { t } = useI18n()
const { handleError } = useHandleError()

const images = defineModel<IItemImage[]>('images', { required: true })
const imageLoadErrors = defineModel<Set<TUUID>>('imageLoadErrors', { required: true })

const { itemId } = defineProps<{
  itemId: TUUID
}>()

const imageUrl = ref('')
const isSubmittingUrl = ref(false)

const emit = defineEmits<{
  hide: []
}>()

async function handleAddFromUrl() {
  const url = imageUrl.value.trim()
  if (!url) {
    toast.error(t('gear.fileUpload.imageGallery.messages.urlRequired'))
    return
  }

  try {
    // Basic URL validation

    new URL(url)
  } catch {
    toast.error(t('gear.fileUpload.imageGallery.messages.urlInvalid'))
    return
  }

  try {
    isSubmittingUrl.value = true
    const hasPrimary = images.value.some(img => img.isPrimary)
    const newImage = await itemImageApiService.uploadImageFromUrl(itemId, url, !hasPrimary)
    images.value.push(newImage)
    imageLoadErrors.value.delete(newImage.id)
    toast.success(t('gear.fileUpload.imageGallery.messages.uploadSuccess'))
    imageUrl.value = ''
    emit('hide')
  } catch (error: unknown) {
    handleError(error, { fallbackMessage: t('gear.fileUpload.imageGallery.messages.uploadFailed') })
  } finally {
    isSubmittingUrl.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-2 rounded-lg border bg-muted/40 p-3 sm:flex-row sm:items-center">
    <Input
      :model-value="imageUrl"
      :placeholder="t('gear.fileUpload.imageGallery.urlPlaceholder')"
      type="url"
      autocomplete="off"
      class="flex-1"
      @update:model-value="value => (imageUrl = (value as string))"
    />
    <div class="flex gap-2 justify-end pt-2 sm:pt-0">
      <Button
        variant="outline"
        size="sm"
        :disabled="isSubmittingUrl"
        @click="emit('hide')"
      >
        {{ t('common.cancel', 'Cancel') }}
      </Button>
      <Button
        size="sm"
        :disabled="isSubmittingUrl"
        @click="handleAddFromUrl"
      >
        {{ t('gear.fileUpload.imageGallery.addFromUrl') }}
      </Button>
    </div>
  </div>
</template>
