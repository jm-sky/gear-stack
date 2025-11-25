<script setup lang="ts">
import { GripVertical, Star, Trash2 } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import type { IItemImage } from '../types/itemImage.types'
import type { TUUID } from '@/shared/types/base.type'

const props = defineProps<{
  image: IItemImage
}>()

const emit = defineEmits<{
  setPrimary: [imageId: TUUID]
  delete: [imageId: TUUID]
}>()

const { t } = useI18n()

function handleSetPrimary() {
  emit('setPrimary', props.image.id)
}

function handleDelete() {
  emit('delete', props.image.id)
}
</script>

<template>
  <div class="absolute inset-0 flex items-center justify-center gap-2 rounded-lg bg-black/50 opacity-0 transition-opacity group-hover:opacity-100">
    <Button
      v-tooltip.bottom="t('fileUpload.imageGallery.tooltips.setPrimary')"
      :aria-label="t('fileUpload.imageGallery.tooltips.setPrimary')"
      class="text-white"
      size="icon"
      variant="ghost"
      @click="handleSetPrimary"
    >
      <Star :class="{ 'fill-yellow-400': image.isPrimary }" class="size-4" />
    </Button>

    <Button
      v-tooltip.bottom="t('fileUpload.imageGallery.tooltips.dragToReorder')"
      :aria-label="t('fileUpload.imageGallery.tooltips.dragToReorder')"
      class="cursor-move text-white"
      size="icon"
      variant="ghost"
    >
      <GripVertical class="size-4" />
    </Button>

    <Button
      v-tooltip.bottom="t('fileUpload.imageGallery.tooltips.deleteImage')"
      :aria-label="t('fileUpload.imageGallery.tooltips.deleteImage')"
      class="text-white"
      size="icon"
      variant="ghost"
      @click="handleDelete"
    >
      <Trash2 class="size-4" />
    </Button>
  </div>
</template>

