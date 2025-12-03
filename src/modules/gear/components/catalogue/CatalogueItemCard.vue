<script setup lang="ts">
import { Package } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import ColorDot from '@/modules/gear/components/ColorDot.vue'
import MarkdownRenderer from '@/modules/gear/components/MarkdownRenderer.vue'
import { useCategoryLabel } from '@/modules/gear/composables/useCategoryLabel'
import { usePriceTierLabel } from '@/modules/gear/composables/usePriceTierLabel'
import { GearRoutePath } from '@/modules/gear/routes'
import type { IGlobalCatalogueItem } from '@/modules/gear/types/catalogue.types'
import type { TContainerColor } from '@/modules/gear/types/gear.types'

const { t } = useI18n()
const { getCategoryLabel } = useCategoryLabel()
const { getPriceTierLabel } = usePriceTierLabel()

const { item } = defineProps<{
  item: IGlobalCatalogueItem
}>()

const categoryLabel = computed(() => getCategoryLabel(item.category))

const priceTierLabel = computed(() => {
  if (!item.priceTier) return null
  return getPriceTierLabel(item.priceTier)
})

const qualityLabel = computed(() => {
  if (!item.quality) return null
  return t(`gear.item.qualities.${item.quality}`)
})
</script>

<template>
  <RouterLink v-slot="{ navigate, href }" :to="GearRoutePath.CatalogueItemDetailById(item.id)" custom>
    <Card
      as="a"
      :href
      class="gap-2 transition-all duration-300 cursor-pointer hover:-translate-y-1 hover:scale-102 hover:bg-current/5 hover:shadow-lg"
      @click.stop="navigate"
    >
      <CardHeader class="h-8 flex items-center justify-between text-card-foreground">
        <div class="flex items-center gap-2">
          <ColorDot :color="(item.color as TContainerColor) ?? undefined" />
          <Package class="size-5" />
          <CardTitle>{{ item.name }}</CardTitle>
        </div>
      </CardHeader>

      <CardContent class="flex flex-1 flex-col gap-3 px-6 pb-4 text-card-foreground">
        <!-- Badges Row -->
        <div class="flex flex-wrap gap-2">
          <Badge variant="secondary" class="text-xs">
            {{ categoryLabel }}
          </Badge>
          <Badge v-if="item.brand" variant="outline" class="text-xs">
            {{ item.brand }}
          </Badge>
          <Badge v-if="priceTierLabel" variant="outline" class="text-xs">
            {{ t('gear.catalogue.priceTier') }}: {{ priceTierLabel }}
          </Badge>
          <Badge v-if="qualityLabel" variant="outline" class="text-xs">
            {{ t('gear.catalogue.quality') }}: {{ qualityLabel }}
          </Badge>
        </div>

        <!-- Description -->
        <CardDescription v-if="item.description" class="flex-1">
          <MarkdownRenderer :content="item.description" class="text-sm" />
        </CardDescription>

        <!-- Weight and Model -->
        <div class="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
          <div v-if="item.weight">
            {{ item.weight }}{{ item.weightUnit }}
          </div>
          <div v-if="item.model" class="flex items-center gap-1">
            <span class="text-xs">Model:</span>
            <span>{{ item.model }}</span>
          </div>
        </div>

        <!-- Metadata (hidden for now) -->
        <!-- <div class="-mb-6 mt-2 flex items-center justify-between text-xs text-muted-foreground">
          <span>v{{ item.version }}</span>
          <span v-if="item.createdBy">
            {{ t('gear.catalogue.createdBy') }}: {{ item.createdBy }}
          </span>
        </div> -->
      </CardContent>
    </Card>
  </RouterLink>
</template>
