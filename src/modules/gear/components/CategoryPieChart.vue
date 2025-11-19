<script setup lang="ts">
import { Donut } from '@unovis/ts'
import { VisDonut, VisSingleContainer } from '@unovis/vue'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  componentToString,
} from '@/components/ui/chart'
import type { IGearContainer, IGearItem } from '../types/gear.types'
import { useGear } from '../composables/useGear'
import { usePieChartGeometry } from '../composables/usePieChartGeometry'
import { getAllNestedContainers } from '../utils/containerNesting'
import CategoryPieChartLabels from './CategoryPieChartLabels.vue'
import CategoryPieChartLegend from './CategoryPieChartLegend.vue'
import type { ChartConfig } from '@/components/ui/chart'

type ChartMode = 'weight' | 'quantity'

interface CategoryData {
  category: string
  weight: number
  quantity: number
  percentage: number
  value: number // The value to display in the chart
}

const props = withDefaults(defineProps<{
  container: IGearContainer
  includeNested?: boolean
}>(), {
  includeNested: false,
})

const { t } = useI18n()
const { containers } = useGear()

const chartMode = ref<ChartMode>('weight')

const categoryData = computed<CategoryData[]>(() => {
  const categoryMap = new Map<string, { weight: number; quantity: number }>()

  // Get all items including nested containers if enabled
  let allItems: IGearItem[] = [...props.container.items]

  if (props.includeNested) {
    const nestedContainers = getAllNestedContainers(props.container.id, containers.value)
    for (const nestedContainer of nestedContainers) {
      allItems = allItems.concat(nestedContainer.items)
    }
  }

  // Calculate totals
  let totalWeight = 0
  let totalQuantity = 0

  for (const item of allItems) {
    const itemWeight = item.weight * item.quantity
    totalWeight += itemWeight
    totalQuantity += item.quantity

    const category = item.category || 'other'
    const existing = categoryMap.get(category) || { weight: 0, quantity: 0 }
    categoryMap.set(category, {
      weight: existing.weight + itemWeight,
      quantity: existing.quantity + item.quantity,
    })
  }

  // Convert to array and calculate percentages
  const data: CategoryData[] = Array.from(categoryMap.entries()).map(([category, values]) => {
    const value = chartMode.value === 'weight' ? values.weight : values.quantity
    const total = chartMode.value === 'weight' ? totalWeight : totalQuantity
    const percentage = total > 0 ? (value / total) * 100 : 0

    return {
      category,
      weight: values.weight,
      quantity: values.quantity,
      percentage,
      value,
    }
  })

  // Sort by percentage descending
  return data.sort((a, b) => b.percentage - a.percentage)
})

const totalValue = computed(() => {
  if (chartMode.value === 'weight') {
    return categoryData.value.reduce((sum, item) => sum + item.weight, 0)
  }
  return categoryData.value.reduce((sum, item) => sum + item.quantity, 0)
})

// Build chart config from category data
const chartConfig = computed<ChartConfig>(() => {
  const config: ChartConfig = {}
  const colors = [
    'var(--chart-1)',
    'var(--chart-2)',
    'var(--chart-3)',
    'var(--chart-4)',
    'var(--chart-5)',
    'var(--primary)',
    'var(--secondary)',
    'var(--accent)',
  ]

  categoryData.value.forEach((data, index) => {
    config[data.category] = {
      label: t(`gear.item.categories.${data.category}`, data.category),
      color: colors[index % colors.length] ?? 'var(--muted-foreground)',
    }
  })

  return config
})

// Use composable for chart geometry calculations
const { chartGeometry, calculateLabelPositions } = usePieChartGeometry({
  svgWidth: 430,
  svgHeight: 300,
  margin: 30,
  arcWidth: 60, // Must match :arc-width in VisDonut
  padAngle: 0.02, // Must match :pad-angle in VisDonut
  labelDistance: 50, // Distance from arc middle to label (increase to move labels further out)
})

// Prepare data for VisDonut
// Format: { [category]: value } to match chartConfig keys for tooltip
// Also calculate label positions for percentage labels
const chartData = computed(() => {
  const mode = chartMode.value
  const dataWithLabels = calculateLabelPositions(categoryData.value, mode)

  return dataWithLabels.map((data) => ({
    [data.category]: mode === 'weight' ? data.weight : data.quantity,
    category: data.category,
    value: data.value,
    percentage: data.percentage,
    weight: data.weight,
    quantity: data.quantity,
    labelX: data.labelX,
    labelY: data.labelY,
  }))
})

type Data = typeof chartData.value[number]

const hasData = computed<boolean>(() => categoryData.value.length > 0 && totalValue.value > 0)

const chartTooltipTriggers = computed(() => {
  const config = chartConfig.value as ChartConfig
  const mode = chartMode.value
  return {
    [Donut.selectors.segment]: (d: Data & { data?: Data }) => {
      // Unovis passes {data: Data, index, value, ...} structure
      const data = (d.data || d) as Data
      const template = componentToString(config, ChartTooltipContent, {
        hideLabel: true,
        valueFormatter,
      })
      if (!template) return ''
      // Pass raw numeric value - ChartTooltipContent will format it
      // The key must match the category in chartConfig for proper label translation
      const rawValue = (mode === 'weight' ? data.weight : data.quantity) ?? 0
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const payload: Record<string, any> = {
        [data.category]: rawValue,
      }
      return template(payload, data.value)
    },
  }
})

const valueFormatter = (value: number) => {
  if (chartMode.value === 'weight') return `${value.toFixed(2)} g`
  return `${value.toLocaleString()} ${t('gear.item.units.piece', 'szt.')}`
}
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex items-center justify-between">
        <div>
          <CardTitle>
            {{ t('gear.chart.title', 'Rozkład kategorii') }}
          </CardTitle>
          <CardDescription>
            {{ t('gear.chart.description', 'Wizualizacja kategorii przedmiotów w kontenerze') }}
          </CardDescription>
        </div>
        <div class="flex gap-2">
          <Button
            :variant="chartMode === 'weight' ? 'default' : 'outline'"
            size="sm"
            @click="chartMode = 'weight'"
          >
            {{ t('gear.chart.byWeight', 'Waga') }}
          </Button>
          <Button
            :variant="chartMode === 'quantity' ? 'default' : 'outline'"
            size="sm"
            @click="chartMode = 'quantity'"
          >
            {{ t('gear.chart.byQuantity', 'Ilość') }}
          </Button>
        </div>
      </div>
    </CardHeader>
    <CardContent>
      <div v-if="!hasData" class="flex items-center justify-center py-12 text-muted-foreground">
        {{ t('gear.chart.noData', 'Brak danych do wyświetlenia') }}
      </div>
      <div v-else class="flex flex-col md:flex-row gap-6">
        <!-- Pie Chart - Left side -->
        <div class="shrink-0 md:w-1/2 relative">
          <ChartContainer :config="chartConfig" class="mx-auto aspect-square max-h-[300px] w-full">
            <VisSingleContainer
              :data="chartData"
              :margin="{ top: 30, bottom: 30, left: 30, right: 30 }"
            >
              <VisDonut
                :value="(d: Data) => d.value"
                :color="(d: Data) => chartConfig[d.category as keyof typeof chartConfig]?.color"
                :arc-width="60"
                :pad-angle="0.02"
              />
              <ChartTooltip :triggers="chartTooltipTriggers" />
            </VisSingleContainer>
            <!-- Labels for segments with percentages - rendered outside VisSingleContainer -->
            <CategoryPieChartLabels
              :chart-data
              :center-x="chartGeometry.centerX"
              :center-y="chartGeometry.centerY"
              :label-radius="chartGeometry.labelRadius"
            />
          </ChartContainer>
        </div>

        <!-- Legend - Right side -->
        <CategoryPieChartLegend
          :category-data="categoryData"
          :chart-config="chartConfig"
          :chart-mode="chartMode"
          :total-value="totalValue"
        />
      </div>
    </CardContent>
  </Card>
</template>
