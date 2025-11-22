<script setup lang="ts">
import { ShoppingCart, Trash2, Download, Plus } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import type { IGearItem } from '../types/gear.types'
import type { TGearItemCategory, TGearItemPriority } from '../types/gear.types'
import CategoryIcon from '../components/CategoryIcon.vue'
import { useGear } from '../composables/useGear'
import { useGearSettings } from '../composables/useGearSettings'
import { getPriorityVariant } from '../utils/badgeVariants'
import { EXPIRATION_WARNING_DAYS, MILLISECONDS_PER_DAY } from '../utils/constants'
import { formatWeightWithPreferredUnit } from '../utils/formatWeight'

const { t } = useI18n()
const { containers } = useGear()
const { customCategories, settings: gearSettings } = useGearSettings()
const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

// Filters
const selectedCategories = ref<TGearItemCategory[]>([])
const budget = ref<number | null>(null)
const includeExpiringSoon = ref(true)

// Shopping list (items selected for shopping)
const shoppingList = ref<IGearItem[]>([])

// Helper to check if item is expiring soon
function isExpiringSoon(item: IGearItem, days: number = EXPIRATION_WARNING_DAYS): boolean {
  if (!item.expirationDate) return false
  const expirationDate = new Date(item.expirationDate)
  const now = new Date()
  const daysUntilExpiration = Math.ceil((expirationDate.getTime() - now.getTime()) / MILLISECONDS_PER_DAY)
  return daysUntilExpiration > 0 && daysUntilExpiration <= days
}

// Get available items (toBuy + optionally expiring soon)
const availableItems = computed<IGearItem[]>(() => {
  const items: IGearItem[] = []
  
  containers.value.forEach(container => {
    container.items.forEach(item => {
      // Include items with status "toBuy"
      if (item.status === 'toBuy') {
        items.push(item)
      }
      // Optionally include items expiring soon
      else if (includeExpiringSoon.value && isExpiringSoon(item)) {
        items.push(item)
      }
    })
  })
  
  return items
})

// Get all available categories
const allCategories = computed<TGearItemCategory[]>(() => {
  const categories = new Set<TGearItemCategory>()
  availableItems.value.forEach(item => {
    categories.add(item.category)
  })
  return Array.from(categories).sort()
})

// Helper to get category label
const getCategoryLabel = (categoryValue: string): string => {
  const customCategory = customCategories.value.find(c => c.value === categoryValue)
  if (customCategory) {
    return customCategory.value
  }
  return t(`gear.item.categories.${categoryValue}`)
}

// Priority order for sorting
const priorityOrder: Record<TGearItemPriority, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
}

// Filtered and sorted items
const filteredItems = computed<IGearItem[]>(() => {
  let items = [...availableItems.value]
  
  // Filter by categories
  if (selectedCategories.value.length > 0) {
    items = items.filter(item => selectedCategories.value.includes(item.category))
  }
  
  // Filter by budget (if set)
  if (budget.value !== null && budget.value > 0) {
    items = items.filter(item => {
      const itemPrice = item.price ?? 0
      const totalPrice = itemPrice * item.quantity
      return totalPrice <= budget.value!
    })
  }
  
  // Sort by priority
  items.sort((a, b) => {
    return priorityOrder[a.priority] - priorityOrder[b.priority]
  })
  
  return items
})

// Calculate total price
const totalPrice = computed(() => {
  return shoppingList.value.reduce((sum, item) => {
    const itemPrice = item.price ?? 0
    return sum + (itemPrice * item.quantity)
  }, 0)
})

// Check if item is in shopping list
const isInShoppingList = (item: IGearItem): boolean => {
  return shoppingList.value.some(i => i.id === item.id)
}

// Add item to shopping list
const addToShoppingList = (item: IGearItem) => {
  if (!isInShoppingList(item)) {
    shoppingList.value.push(item)
    toast.success(t('gear.shopping.addedToCart', 'Added to shopping list'))
  }
}

// Remove item from shopping list
const removeFromShoppingList = (item: IGearItem) => {
  const index = shoppingList.value.findIndex(i => i.id === item.id)
  if (index !== -1) {
    shoppingList.value.splice(index, 1)
    toast.success(t('gear.shopping.removedFromCart', 'Removed from shopping list'))
  }
}

// Toggle item in shopping list
const toggleShoppingList = (item: IGearItem) => {
  if (isInShoppingList(item)) {
    removeFromShoppingList(item)
  } else {
    addToShoppingList(item)
  }
}

// Generate markdown export
const generateMarkdown = (): string => {
  if (shoppingList.value.length === 0) {
    return t('gear.shopping.emptyList', 'Shopping list is empty')
  }
  
  let markdown = `# ${t('gear.shopping.title', 'Shopping List')}\n\n`
  markdown += `${t('gear.shopping.generatedAt', 'Generated at')}: ${new Date().toLocaleString()}\n\n`
  
  // Group by priority
  const byPriority: Record<TGearItemPriority, IGearItem[]> = {
    critical: [],
    high: [],
    medium: [],
    low: [],
  }
  
  shoppingList.value.forEach(item => {
    byPriority[item.priority].push(item)
  })
  
  // Output by priority
  Object.entries(byPriority).forEach(([priority, items]) => {
    if (items.length > 0) {
      markdown += `## ${t(`gear.item.priorities.${priority}`)}\n\n`
      items.forEach(item => {
        const categoryLabel = getCategoryLabel(item.category)
        const price = item.price ? ` - ${item.price} ${t('gear.shopping.currency', 'PLN')}` : ''
        const quantity = item.quantity > 1 ? ` x${item.quantity}` : ''
        const brand = item.brand ? ` **${item.brand}**` : ''
        const expiration = item.expirationDate ? ` (${t('gear.item.expiration.expiringSoon')}: ${new Date(item.expirationDate).toLocaleDateString()})` : ''
        
        markdown += `- ${item.name}${brand}${quantity}${price}${expiration} [${categoryLabel}]\n`
      })
      markdown += '\n'
    }
  })
  
  if (totalPrice.value > 0) {
    markdown += `\n**${t('gear.shopping.totalPrice', 'Total')}**: ${totalPrice.value.toFixed(2)} ${t('gear.shopping.currency', 'PLN')}\n`
  }
  
  return markdown
}

// Export dialog
const exportDialogOpen = ref(false)
const markdownContent = computed(() => generateMarkdown())

const handleCopyMarkdown = async () => {
  try {
    await navigator.clipboard.writeText(markdownContent.value)
    toast.success(t('gear.shopping.markdownCopied', 'Markdown copied to clipboard'))
    exportDialogOpen.value = false
  } catch (error) {
    console.error('Failed to copy markdown:', error)
    toast.error(t('gear.shopping.copyFailed', 'Failed to copy markdown'))
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight flex items-center gap-3">
            <ShoppingCart class="size-8 text-primary" />
            {{ t('gear.shopping.title', 'Shopping Planning') }}
          </h1>
          <p class="text-muted-foreground mt-2">
            {{ t('gear.shopping.subtitle', 'Plan your purchases for items to buy and expiring soon') }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Button
            v-if="shoppingList.length > 0"
            variant="outline"
            @click="exportDialogOpen = true"
          >
            <Download class="size-4 mr-2" />
            {{ t('gear.shopping.exportMarkdown', 'Export Markdown') }}
          </Button>
        </div>
      </div>

      <!-- Filters -->
      <div class="space-y-4 p-4 border rounded-lg bg-muted/50">
        <h3 class="font-semibold text-sm">{{ t('gear.shopping.filters', 'Filters') }}</h3>
        
        <!-- Categories filter -->
        <div class="space-y-2">
          <Label class="text-sm">{{ t('gear.shopping.filterByCategory', 'Filter by Category') }}</Label>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="category in allCategories"
              :key="category"
              class="flex items-center gap-2"
            >
              <Checkbox
                :id="`category-${category}`"
                :checked="selectedCategories.includes(category)"
                @update:checked="(checked) => {
                  if (checked) {
                    if (!selectedCategories.includes(category)) {
                      selectedCategories.push(category)
                    }
                  } else {
                    const index = selectedCategories.indexOf(category)
                    if (index > -1) {
                      selectedCategories.splice(index, 1)
                    }
                  }
                }"
              />
              <Label
                :for="`category-${category}`"
                class="text-sm cursor-pointer flex items-center gap-2"
              >
                <CategoryIcon :category="category" :size="14" />
                {{ getCategoryLabel(category) }}
              </Label>
            </div>
          </div>
        </div>

        <!-- Budget filter -->
        <div class="space-y-2">
          <Label class="text-sm">{{ t('gear.shopping.filterByBudget', 'Filter by Budget') }}</Label>
          <div class="flex items-center gap-2">
            <Input
              v-model.number="budget"
              type="number"
              :placeholder="t('gear.shopping.budgetPlaceholder', 'Enter budget amount')"
              class="max-w-xs"
              min="0"
              step="0.01"
            />
            <span class="text-sm text-muted-foreground">{{ t('gear.shopping.currency', 'PLN') }}</span>
            <Button
              v-if="budget !== null"
              variant="ghost"
              size="sm"
              @click="budget = null"
            >
              {{ t('gear.shopping.clearBudget', 'Clear') }}
            </Button>
          </div>
        </div>

        <!-- Include expiring soon -->
        <div class="flex items-center gap-2">
          <Checkbox
            id="include-expiring"
            v-model="includeExpiringSoon"
          />
          <Label
            for="include-expiring"
            class="text-sm cursor-pointer"
          >
            {{ t('gear.shopping.includeExpiringSoon', 'Include items expiring soon') }}
          </Label>
        </div>
      </div>

      <!-- Shopping list summary -->
      <div
        v-if="shoppingList.length > 0"
        class="p-4 border rounded-lg bg-primary/5"
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-semibold">{{ t('gear.shopping.shoppingList', 'Shopping List') }}</h3>
            <p class="text-sm text-muted-foreground">
              {{ t('gear.shopping.itemsCount', '{count} items', { count: shoppingList.length }) }}
              <span v-if="totalPrice > 0">
                - {{ totalPrice.toFixed(2) }} {{ t('gear.shopping.currency', 'PLN') }}
              </span>
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            @click="shoppingList = []"
          >
            {{ t('gear.shopping.clearList', 'Clear List') }}
          </Button>
        </div>
      </div>

      <!-- Items list -->
      <div class="space-y-2">
        <div
          v-if="filteredItems.length === 0"
          class="text-center py-12 text-muted-foreground"
        >
          <p class="text-lg">{{ t('gear.shopping.noItems', 'No items found') }}</p>
          <p class="text-sm mt-2">{{ t('gear.shopping.noItemsDescription', 'Try adjusting your filters') }}</p>
        </div>
        
        <div
          v-for="item in filteredItems"
          :key="item.id"
          class="flex items-center gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
        >
          <!-- Add/Remove button -->
          <Button
            :variant="isInShoppingList(item) ? 'default' : 'outline'"
            size="sm"
            @click="toggleShoppingList(item)"
          >
            <Plus
              v-if="!isInShoppingList(item)"
              class="size-4"
            />
            <Trash2
              v-else
              class="size-4"
            />
          </Button>

          <!-- Category icon -->
          <CategoryIcon :category="item.category" :size="20" class="text-muted-foreground shrink-0" />

          <!-- Item info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="font-medium">{{ item.name }}</span>
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
                v-else-if="isExpiringSoon(item)"
                variant="outline"
                class="text-xs text-yellow-600 border-yellow-600"
              >
                {{ t('gear.item.expiration.expiringSoon') }}
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
                {{ (item.price * item.quantity).toFixed(2) }} {{ t('gear.shopping.currency', 'PLN') }}
              </span>
              <span v-if="item.expirationDate" class="text-yellow-600">
                {{ t('gear.item.expiration.expiringSoon') }}: {{ new Date(item.expirationDate).toLocaleDateString() }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Export Dialog -->
      <Dialog v-model:open="exportDialogOpen">
        <DialogContent class="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{{ t('gear.shopping.exportMarkdown', 'Export Markdown') }}</DialogTitle>
            <DialogDescription>
              {{ t('gear.shopping.exportDescription', 'Copy the markdown content below') }}
            </DialogDescription>
          </DialogHeader>
          <div class="space-y-4">
            <pre class="p-4 bg-muted rounded-lg text-sm overflow-x-auto whitespace-pre-wrap">{{ markdownContent }}</pre>
          </div>
          <DialogFooter>
            <Button variant="outline" @click="exportDialogOpen = false">
              {{ t('gear.actions.cancel', 'Cancel') }}
            </Button>
            <Button @click="handleCopyMarkdown">
              {{ t('gear.shopping.copyMarkdown', 'Copy to Clipboard') }}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  </AuthenticatedLayout>
</template>
