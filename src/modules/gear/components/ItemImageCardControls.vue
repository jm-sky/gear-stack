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
  <div
    class="absolute inset-0 flex items-center justify-center gap-2 rounded-lg bg-black/50 opacity-100 md:opacity-0 transition-opacity md:group-hover:opacity-100 pointer-events-none"
  >
    <Button
      v-tooltip.bottom="t('gear.fileUpload.imageGallery.tooltips.setPrimary')"
      :aria-label="t('gear.fileUpload.imageGallery.tooltips.setPrimary')"
      class="pointer-events-auto text-white"
      size="icon"
      variant="ghost"
      :disabled="image.isPrimary"
      @click.stop="handleSetPrimary"
    >
      <Star :class="{ 'fill-yellow-400': image.isPrimary }" class="size-4" />
    </Button>

    <Button
      v-tooltip.bottom="t('gear.fileUpload.imageGallery.tooltips.dragToReorder')"
      :aria-label="t('gear.fileUpload.imageGallery.tooltips.dragToReorder')"
      class="pointer-events-auto cursor-move text-white"
      size="icon"
      variant="ghost"
      @click.stop
    >
      <GripVertical class="size-4" />
    </Button>

    <Button
      v-tooltip.bottom="t('gear.fileUpload.imageGallery.tooltips.deleteImage')"
      :aria-label="t('gear.fileUpload.imageGallery.tooltips.deleteImage')"
      class="pointer-events-auto text-white hover:text-destructive"
      size="icon"
      variant="ghost"
      @click.stop="handleDelete"
    >
      <Trash2 class="size-4" />
    </Button>
  </div>
</template>

