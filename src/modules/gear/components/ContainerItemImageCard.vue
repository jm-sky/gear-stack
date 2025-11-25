<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import type { IGearItem } from '../types/gear.types'
import type { IItemImage } from '../types/itemImage.types'
import { GearRoutePath } from '../routes'

const props = defineProps<{
  item: IGearItem
  image: IItemImage | null
  containerId: string
  hasError: boolean
}>()

const { t } = useI18n()
const router = useRouter()

function handleImageClick() {
  router.push(GearRoutePath.ItemDetailById(props.containerId, props.item.id))
}
</script>

<template>
  <div class="group relative w-full md:w-[calc(25%-1rem)]">
    <div
      class="relative h-48 cursor-pointer overflow-hidden rounded-lg border border-border shadow-md/5 transition-transform hover:scale-105"
      @click="handleImageClick"
    >
      <img
        v-if="image && !hasError"
        :alt="item.name"
        :src="image.url"
        class="size-full object-cover"
      />
      <div
        v-else
        class="flex h-full items-center justify-center bg-muted"
      >
        <div class="text-center text-sm text-muted-foreground">
          <p>{{ t('common.error') }}</p>
        </div>
      </div>

      <!-- Item name overlay -->
      <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 to-transparent p-2">
        <p class="truncate text-sm font-medium text-white">
          {{ item.name }}
        </p>
      </div>
    </div>
  </div>
</template>

