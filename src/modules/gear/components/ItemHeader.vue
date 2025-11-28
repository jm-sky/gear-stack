<script setup lang="ts">
import { ArrowLeftIcon, PencilIcon } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import type { IGearItem } from '../types/gear.types'
import CategoryIcon from '../components/CategoryIcon.vue'
import ItemHeaderName from '../components/ItemHeaderName.vue'
import ItemPriorityBadge from '../components/ItemPriorityBadge.vue'
import ItemStatusBadge from '../components/ItemStatusBadge.vue'
import { useCategoryLabel } from '../composables/useCategoryLabel'
import { useExpiration } from '../composables/useExpiration'
import { GearRoutePath } from '../routes'
import { createNavigationQuery, getFrom } from '../utils/navigationParams'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { getCategoryLabel } = useCategoryLabel()

const { containerId, itemId, item } = defineProps<{
  containerId: string
  itemId: string
  item: IGearItem
}>()

const { isExpired, isExpiringSoon } = useExpiration(item)

const backTo = computed<string>(() => {
  const from = getFrom(route)
  if (from === 'all-items') {
    return GearRoutePath.AllItems
  }
  return GearRoutePath.ContainerDetailById(containerId)
})

const handleEdit = () => {
  const from = getFrom(route)
  router.push({
    path: GearRoutePath.ItemEditById(containerId, itemId),
    query: createNavigationQuery('detail', from),
  })
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-4">
      <ButtonLink :to="backTo" variant="ghost" size="sm">
        <ArrowLeftIcon class="size-4" />
        {{ t('common.back') }}
      </ButtonLink>

      <Button size="sm" @click="handleEdit">
        <PencilIcon class="size-4" />
        {{ t('common.edit') }}
      </Button>
    </div>

    <div class="flex flex-col gap-2">
      <ItemHeaderName :item />
      <div class="flex flex-wrap items-center gap-2">
        <Badge variant="outline" class="flex items-center gap-2">
          <CategoryIcon :category="item.category" :size="14" />
          {{ getCategoryLabel(item.category) }}
        </Badge>
        <ItemPriorityBadge :priority="item.priority" />
        <ItemStatusBadge :status="item.status" />
        <Badge v-if="isExpired" variant="destructive" class="text-xs">
          {{ t('gear.item.expiration.expired') }}
        </Badge>
        <Badge v-if="isExpiringSoon" variant="outline" class="text-xs border-yellow-600 text-yellow-600">
          {{ t('gear.item.expiration.expiringSoon') }}
        </Badge>
        <Badge v-if="item.wearable" variant="outline" class="text-xs">
          {{ t('gear.item.wearable') }}
        </Badge>
        <Badge v-if="item.consumable" variant="outline" class="text-xs">
          {{ t('gear.item.consumable') }}
        </Badge>
      </div>
    </div>
  </div>
</template>
