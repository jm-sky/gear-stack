<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ChartConfig } from '@/components/ui/chart'

interface CategoryData {
  category: string
  weight: number
  quantity: number
  percentage: number
  value: number
}

interface Props {
  categoryData: CategoryData[]
  chartConfig: ChartConfig
  chartMode: 'weight' | 'quantity'
  totalValue: number
}

defineProps<Props>()

const { t } = useI18n()
</script>

<template>
  <div class="flex-1 space-y-2">
    <div class="text-sm font-medium">
      {{ t('gear.chart.legend', 'Legenda') }}
    </div>
    <div class="space-y-2">
      <div
        v-for="data in categoryData"
        :key="data.category"
        class="flex items-center justify-between gap-4 p-2 rounded hover:bg-muted transition-colors"
      >
        <div class="flex items-center gap-2 flex-1 min-w-0">
          <div
            class="size-4 rounded shrink-0"
            :style="{
              backgroundColor: chartConfig[data.category]?.color || 'transparent',
            }"
          />
          <span class="text-sm font-medium truncate">
            {{ t(`gear.item.categories.${data.category}`, data.category) }}
          </span>
        </div>
        <div class="text-sm text-muted-foreground shrink-0">
          <span class="font-semibold">{{ data.percentage.toFixed(1) }}%</span>
          <span class="ml-2">
            ({{ chartMode === 'weight' ? `${data.weight.toFixed(2)} g` : `${data.quantity}` }})
          </span>
        </div>
      </div>
    </div>
    <div class="pt-4 px-2 border-t text-sm text-muted-foreground">
      <div class="flex flex-row items-center justify-between gap-2">
        {{ t('gear.chart.total', 'Łącznie') }}:
        <span class="font-semibold">
          {{ chartMode === 'weight' ? `${totalValue.toFixed(2)} g` : `${totalValue}` }}
        </span>
      </div>
    </div>
  </div>
</template>

