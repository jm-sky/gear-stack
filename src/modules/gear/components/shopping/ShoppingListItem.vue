<script setup lang="ts">
import { CheckCircle2, Minus, Plus, X } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import type { IItemWithContainerId } from '../../types/shopping.types'
import { useCategoryLabel } from '../../composables/useCategoryLabel'
import { useGearSettings } from '../../composables/useGearSettings'
import { GearRoutePath } from '../../routes'
import { getPriorityVariant } from '../../utils/badgeVariants'
import { EXPIRATION_WARNING_DAYS, MILLISECONDS_PER_DAY } from '../../utils/constants'
import { formatCurrency, getCurrency } from '../../utils/currencyFormatter'
import { formatWeightWithPreferredUnit } from '../../utils/formatWeight'
import CategoryIcon from '../CategoryIcon.vue'

const { t } = useI18n()

const { item } = defineProps<{
  item: IItemWithContainerId
  isBeingPurchased?: boolean
}>()

const emit = defineEmits<{
  purchase: []
  increment: []
  decrement: []
  delete: []
}>()

const { settings: gearSettings, defaultCurrency } = useGearSettings()
const { getCategoryLabel } = useCategoryLabel()
const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

// Helper to check if item is expired
function isExpired(): boolean {
  if (!item.expirationDate) return false
  const expirationDate = new Date(item.expirationDate)
  const now = new Date()
  return expirationDate < now
}

// Helper to check if item is expiring soon (includes expired items)
function isExpiringSoon(days: number = EXPIRATION_WARNING_DAYS): boolean {
  if (!item.expirationDate) return false
  const expirationDate = new Date(item.expirationDate)
  const now = new Date()
  const daysUntilExpiration = Math.ceil((expirationDate.getTime() - now.getTime()) / MILLISECONDS_PER_DAY)
  // Include expired items (daysUntilExpiration <= 0) and items expiring soon
  return daysUntilExpiration <= days
}
</script>

<template>
  <div
    class="flex items-center gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
    :class="{ 'opacity-90 grayscale blur-[1px]': isBeingPurchased }"
  >
    <!-- Category icon -->
    <CategoryIcon :category="item.category" :size="20" class="text-muted-foreground shrink-0" />

    <!-- Item info -->
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 flex-wrap">
        <RouterLink
          :to="`${GearRoutePath.ItemEditById(item._containerId, item.id)}?returnTo=shopping`"
          class="font-medium hover:text-primary hover:underline transition-colors"
        >
          {{ item.name }}
        </RouterLink>
        <Badge
          :variant="getPriorityVariant(item.priority)"
          class="text-xs"
        >
          {{ t(`gear.item.priorities.${item.priority}`) }}
        </Badge>
        <Badge
          v-if="item.status === 'toBuy'"
          variant="outline"
          class="text-xs"
        >
          {{ t('gear.item.statuses.toBuy') }}
        </Badge>
        <Badge
          v-else-if="isExpiringSoon()"
          variant="outline"
          :class="[
            'text-xs',
            isExpired() ? 'text-red-600 border-red-600' : 'text-yellow-600 border-yellow-600'
          ]"
        >
          {{ isExpired() ? t('gear.item.expiration.expired') : t('gear.item.expiration.expiringSoon') }}
        </Badge>
      </div>
      <div class="flex items-center gap-4 mt-1 text-sm text-muted-foreground flex-wrap">
        <span>{{ getCategoryLabel(item.category) }}</span>
        <span v-if="item.brand">{{ item.brand }}</span>
        <span>{{ t('gear.item.quantity') }}: {{ item.quantity }}</span>
        <span>
          {{ formatWeightWithPreferredUnit(item.weight * item.quantity, item.weightUnit, settings.preferredWeightUnit) }}
        </span>
        <span v-if="item.price">
          {{ formatCurrency(item.price * item.quantity, getCurrency(item.currency, defaultCurrency)) }}
        </span>
        <span v-if="item.expirationDate" :class="isExpired() ? 'text-red-600' : 'text-yellow-600'">
          {{ isExpired() ? t('gear.item.expiration.expired') : t('gear.item.expiration.expiringSoon') }}: {{ new Date(item.expirationDate).toLocaleDateString() }}
        </span>
      </div>
    </div>

    <!-- Quantity controls -->
    <div class="flex items-center gap-2 shrink-0">
      <Button
        variant="outline"
        size="sm"
        :disabled="item.quantity <= 1"
        @click="emit('decrement')"
      >
        <Minus class="size-4" />
      </Button>
      <span class="text-sm font-medium min-w-[2ch] text-center">
        {{ item.quantity }}
      </span>
      <Button
        variant="outline"
        size="sm"
        @click="emit('increment')"
      >
        <Plus class="size-4" />
      </Button>
    </div>

    <!-- Actions -->
    <div class="flex items-center gap-2 shrink-0">
      <Button
        variant="default"
        size="sm"
        :loading="isBeingPurchased"
        @click="emit('purchase')"
      >
        <CheckCircle2 class="size-4" />
        <span class="hidden sm:inline">{{ t('gear.shopping.purchased', 'Purchased') }}</span>
      </Button>
      <Button
        variant="outline"
        size="sm"
        @click="emit('delete')"
      >
        <X class="size-4" />
      </Button>
    </div>
  </div>
</template>
