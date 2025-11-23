<script setup lang="ts">
import { CheckCircle2, Download, Plus, RotateCcw, ShoppingCart, Trash2, X } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute, useRouter } from 'vue-router'
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
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import type { ICreateItemDto, IGearItem } from '../types/gear.types'
import type { TGearItemCategory, TGearItemPriority } from '../types/gear.types'
import CategoryIcon from '../components/CategoryIcon.vue'
import { useGear } from '../composables/useGear'
import { useGearSettings } from '../composables/useGearSettings'
import { getPriorityVariant } from '../utils/badgeVariants'
import { EXPIRATION_WARNING_DAYS, MILLISECONDS_PER_DAY } from '../utils/constants'
import { formatWeightWithPreferredUnit } from '../utils/formatWeight'
import { getDefaultItemValues } from '../utils/defaultValues'
import { itemSchema, type ItemFormData } from '../utils/validation'
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import ItemFormFields from '../components/ItemFormFields.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const { containers, createItem, updateItem } = useGear()
const { customCategories, settings: gearSettings } = useGearSettings()
const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

// Filters
const selectedCategories = ref<TGearItemCategory[]>([])
const budget = ref<number | null>(null)
const includeExpiringSoon = ref(true)

// Category checkbox states - using reactive object for v-model compatibility
const categoryChecked = ref<Record<string, boolean>>({})

// Storage key for shopping list
const SHOPPING_LIST_STORAGE_KEY = 'gear-stack:shopping-list'
const DELETED_ITEMS_STORAGE_KEY = 'gear-stack:shopping-deleted-items'

// Helper to load shopping list from localStorage
function loadShoppingListFromStorage(): IItemWithContainerId[] {
  const stored = localStorage.getItem(SHOPPING_LIST_STORAGE_KEY)
  if (stored) {
    try {
      return JSON.parse(stored) as IItemWithContainerId[]
    } catch (error) {
      console.error('Error loading shopping list from storage:', error)
    }
  }
  return []
}

// Helper to save shopping list to localStorage
function saveShoppingListToStorage(list: IItemWithContainerId[]): void {
  try {
    localStorage.setItem(SHOPPING_LIST_STORAGE_KEY, JSON.stringify(list))
  } catch (error) {
    console.error('Error saving shopping list to storage:', error)
  }
}

// Helper to load deleted items from localStorage
function loadDeletedItemsFromStorage(): IItemWithContainerId[] {
  const stored = localStorage.getItem(DELETED_ITEMS_STORAGE_KEY)
  if (stored) {
    try {
      return JSON.parse(stored) as IItemWithContainerId[]
    } catch (error) {
      console.error('Error loading deleted items from storage:', error)
    }
  }
  return []
}

// Helper to save deleted items to localStorage
function saveDeletedItemsToStorage(items: IItemWithContainerId[]): void {
  try {
    localStorage.setItem(DELETED_ITEMS_STORAGE_KEY, JSON.stringify(items))
  } catch (error) {
    console.error('Error saving deleted items to storage:', error)
  }
}

// Shopping list (items selected for shopping)
const shoppingList = ref<IItemWithContainerId[]>(loadShoppingListFromStorage())

// Deleted items (local to this page)
const deletedItems = ref<IItemWithContainerId[]>(loadDeletedItemsFromStorage())

// Watch shopping list changes and save to localStorage
watch(shoppingList, (newList) => {
  saveShoppingListToStorage(newList)
}, { deep: true })

// Watch deleted items changes and save to localStorage
watch(deletedItems, (newItems) => {
  saveDeletedItemsToStorage(newItems)
}, { deep: true })

// Helper to check if item is expired
function isExpired(item: IGearItem): boolean {
  if (!item.expirationDate) return false
  const expirationDate = new Date(item.expirationDate)
  const now = new Date()
  return expirationDate < now
}

// Helper to check if item is expiring soon (includes expired items)
function isExpiringSoon(item: IGearItem, days: number = EXPIRATION_WARNING_DAYS): boolean {
  if (!item.expirationDate) return false
  const expirationDate = new Date(item.expirationDate)
  const now = new Date()
  const daysUntilExpiration = Math.ceil((expirationDate.getTime() - now.getTime()) / MILLISECONDS_PER_DAY)
  // Include expired items (daysUntilExpiration <= 0) and items expiring soon
  return daysUntilExpiration <= days
}

// Item with container ID for navigation
interface IItemWithContainerId extends IGearItem {
  _containerId: string // Internal field to track container ID
}

// Get available items (toBuy + optionally expiring soon/expired) with container IDs
const availableItems = computed<IItemWithContainerId[]>(() => {
  const items: IItemWithContainerId[] = []
  
  containers.value.forEach(container => {
    container.items.forEach(item => {
      // Include items with status "toBuy"
      if (item.status === 'toBuy') {
        items.push({ ...item, _containerId: container.id })
      }
      // Optionally include items expiring soon or expired
      else if (includeExpiringSoon.value && isExpiringSoon(item)) {
        items.push({ ...item, _containerId: container.id })
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

// Sync categoryChecked with selectedCategories
watch(
  () => allCategories.value,
  (categories) => {
    categories.forEach(category => {
      if (!(category in categoryChecked.value)) {
        categoryChecked.value[category] = selectedCategories.value.includes(category)
      }
    })
  },
  { immediate: true },
)

// Watch categoryChecked changes and sync to selectedCategories
watch(
  categoryChecked,
  (checked) => {
    const newSelected: TGearItemCategory[] = []
    Object.entries(checked).forEach(([category, isChecked]) => {
      if (isChecked && allCategories.value.includes(category as TGearItemCategory)) {
        newSelected.push(category as TGearItemCategory)
      }
    })
    selectedCategories.value = newSelected
  },
  { deep: true },
)

// Watch selectedCategories changes and sync to categoryChecked
watch(
  selectedCategories,
  (selected) => {
    allCategories.value.forEach(category => {
      categoryChecked.value[category] = selected.includes(category)
    })
  },
  { immediate: true },
)

// Priority order for sorting
const priorityOrder: Record<TGearItemPriority, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
}

// Filtered and sorted items
const filteredItems = computed<IItemWithContainerId[]>(() => {
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

// Calculate total price for shopping list
const totalPrice = computed(() => {
  return shoppingList.value.reduce((sum, item) => {
    const itemPrice = item.price ?? 0
    return sum + (itemPrice * item.quantity)
  }, 0)
})

// Calculate total items count
const totalItemsCount = computed(() => {
  return shoppingList.value.reduce((sum, item) => sum + item.quantity, 0)
})

// Check if item is in shopping list
const isInShoppingList = (item: IItemWithContainerId): boolean => {
  return shoppingList.value.some(i => i.id === item.id)
}

// Add item to shopping list
const addToShoppingList = (item: IItemWithContainerId) => {
  if (!isInShoppingList(item)) {
    shoppingList.value.push(item)
    toast.success(t('gear.shopping.addedToCart', 'Added to shopping list'))
  }
}

// Remove item from shopping list
const removeFromShoppingList = (item: IItemWithContainerId) => {
  const index = shoppingList.value.findIndex(i => i.id === item.id)
  if (index !== -1) {
    shoppingList.value.splice(index, 1)
    toast.success(t('gear.shopping.removedFromCart', 'Removed from shopping list'))
  }
}

// Toggle item in shopping list
const toggleShoppingList = (item: IItemWithContainerId) => {
  if (isInShoppingList(item)) {
    removeFromShoppingList(item)
  } else {
    addToShoppingList(item)
  }
}

// Mark item as purchased (change status to Owned and remove from list)
const markAsPurchased = async (item: IItemWithContainerId) => {
  try {
    await updateItem(item.id, { status: 'owned' })
    removeFromShoppingList(item)
    toast.success(t('gear.shopping.markedAsPurchased', 'Item marked as purchased'))
  } catch (error) {
    console.error('Failed to mark item as purchased:', error)
    toast.error(t('common.error', 'Error'))
  }
}

// Delete item from shopping list (move to deleted section)
const deleteFromShoppingList = (item: IItemWithContainerId) => {
  const index = shoppingList.value.findIndex(i => i.id === item.id)
  if (index !== -1) {
    shoppingList.value.splice(index, 1)
    deletedItems.value.push(item)
    toast.success(t('gear.shopping.deletedFromList', 'Item removed from shopping list'))
  }
}

// Restore item from deleted section
const restoreToShoppingList = (item: IItemWithContainerId) => {
  const index = deletedItems.value.findIndex(i => i.id === item.id)
  if (index !== -1) {
    deletedItems.value.splice(index, 1)
    if (!isInShoppingList(item)) {
      shoppingList.value.push(item)
      toast.success(t('gear.shopping.restoredToList', 'Item restored to shopping list'))
    }
  }
}

// Reset shopping list (reload from available items)
const resetShoppingList = () => {
  shoppingList.value = []
  deletedItems.value = []
  saveShoppingListToStorage([])
  saveDeletedItemsToStorage([])
  toast.success(t('gear.shopping.listReset', 'Shopping list reset'))
}

// Add all filtered items to shopping list
const addAllToShoppingList = () => {
  let addedCount = 0
  filteredItems.value.forEach(item => {
    if (!isInShoppingList(item)) {
      shoppingList.value.push(item)
      addedCount++
    }
  })
  if (addedCount > 0) {
    toast.success(t('gear.shopping.addedAllToCart', { count: addedCount }))
  } else {
    toast.info(t('gear.shopping.allItemsAlreadyInList'))
  }
}

// Generate markdown export (only from shopping list, respecting filters)
const generateMarkdown = (): string => {
  // Filter shopping list items by current filters
  let itemsToExport = [...shoppingList.value]
  
  // Apply category filter
  if (selectedCategories.value.length > 0) {
    itemsToExport = itemsToExport.filter(item => selectedCategories.value.includes(item.category))
  }
  
  // Apply budget filter
  if (budget.value !== null && budget.value > 0) {
    itemsToExport = itemsToExport.filter(item => {
      const itemPrice = item.price ?? 0
      const totalPrice = itemPrice * item.quantity
      return totalPrice <= budget.value!
    })
  }
  
  if (itemsToExport.length === 0) {
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
  
  itemsToExport.forEach(item => {
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
  
  const exportTotalPrice = itemsToExport.reduce((sum, item) => {
    const itemPrice = item.price ?? 0
    return sum + (itemPrice * item.quantity)
  }, 0)
  
  if (exportTotalPrice > 0) {
    markdown += `\n**${t('gear.shopping.totalPrice', 'Total')}**: ${exportTotalPrice.toFixed(2)} ${t('gear.shopping.currency', 'PLN')}\n`
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

// Add new item dialog
const addItemDialogOpen = ref(false)
const firstContainerId = computed(() => containers.value[0]?.id)

const getInitialAddItemValues = (): ItemFormData => {
  return {
    ...getDefaultItemValues(),
    status: 'toBuy', // Default to "To Buy" status
  } as ItemFormData
}

const addItemForm = useForm({
  validationSchema: toTypedSchema(itemSchema),
  initialValues: getInitialAddItemValues(),
})

const { handleSubmit: handleAddItemSubmit, isSubmitting: isAddingItem, resetForm: resetAddItemForm } = addItemForm

const onAddItemSubmit = handleAddItemSubmit(async (data: ICreateItemDto) => {
  if (!firstContainerId.value) {
    toast.error(t('gear.shopping.noContainer', 'No container available'))
    return
  }
  
  try {
    const newItem = await createItem(firstContainerId.value, data)
    // Add to shopping list
    const itemWithContainer: IItemWithContainerId = { ...newItem, _containerId: firstContainerId.value }
    addToShoppingList(itemWithContainer)
    addItemDialogOpen.value = false
    resetAddItemForm({ values: getInitialAddItemValues() })
    toast.success(t('gear.shopping.itemAdded', 'Item added'))
  } catch (error) {
    console.error('Failed to add item:', error)
    toast.error(t('common.error', 'Error'))
  }
})

// Sync shopping list with current container data
// This ensures items in shopping list are up-to-date with container data
function syncShoppingListWithContainers() {
  const updatedList: IItemWithContainerId[] = []
  
  shoppingList.value.forEach(shoppingItem => {
    // Find the item in current containers
    let found = false
    containers.value.forEach(container => {
      const currentItem = container.items.find(item => item.id === shoppingItem.id)
      if (currentItem) {
        // Update item with current data
        updatedList.push({ ...currentItem, _containerId: container.id })
        found = true
      }
    })
    
    // If item not found in containers, it might have been deleted
    // We keep it in the list for now, but it will be filtered out
    if (!found) {
      updatedList.push(shoppingItem)
    }
  })
  
  shoppingList.value = updatedList
}

// Sync deleted items with current container data
function syncDeletedItemsWithContainers() {
  const updatedDeleted: IItemWithContainerId[] = []
  
  deletedItems.value.forEach(deletedItem => {
    // Find the item in current containers
    let found = false
    containers.value.forEach(container => {
      const currentItem = container.items.find(item => item.id === deletedItem.id)
      if (currentItem) {
        // Update item with current data
        updatedDeleted.push({ ...currentItem, _containerId: container.id })
        found = true
      }
    })
    
    // If item not found, keep it as is
    if (!found) {
      updatedDeleted.push(deletedItem)
    }
  })
  
  deletedItems.value = updatedDeleted
}

// Watch containers changes and sync shopping list
watch(containers, () => {
  syncShoppingListWithContainers()
  syncDeletedItemsWithContainers()
}, { deep: true })

// Handle redirect from edit page
onMounted(() => {
  const returnTo = route.query.returnTo as string | undefined
  if (returnTo === 'shopping') {
    // Clear the query param
    router.replace({ query: {} })
  }
  
  // Sync shopping list with current container data on mount
  syncShoppingListWithContainers()
  syncDeletedItemsWithContainers()
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full overflow-hidden">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
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
            variant="default"
            @click="addItemDialogOpen = true"
          >
            <Plus class="size-4" />
            {{ t('gear.shopping.addItem', 'Add') }}
          </Button>
          <Button
            v-if="shoppingList.length > 0"
            variant="outline"
            @click="exportDialogOpen = true"
          >
            <Download class="size-4" />
            {{ t('gear.shopping.exportMarkdown', 'Export Markdown') }}
          </Button>
          <Button
            variant="outline"
            @click="resetShoppingList"
          >
            <RotateCcw class="size-4" />
            {{ t('gear.shopping.reset', 'Reset') }}
          </Button>
        </div>
      </div>

      <!-- Summary above list -->
      <div
        v-if="shoppingList.length > 0"
        class="p-4 border rounded-lg bg-primary/5"
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-semibold">
              {{ t('gear.shopping.summary', 'Summary') }}
            </h3>
            <p class="text-sm text-muted-foreground">
              {{ t('gear.shopping.itemsCount', { count: shoppingList.length }) }}
              ({{ t('gear.shopping.totalQuantity', { count: totalItemsCount }) }})
              <span v-if="totalPrice > 0">
                - {{ totalPrice.toFixed(2) }} {{ t('gear.shopping.currency', 'PLN') }}
              </span>
            </p>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="space-y-4 p-4 border rounded-lg bg-muted/50">
        <h3 class="font-semibold text-sm">
          {{ t('gear.shopping.filters', 'Filters') }}
        </h3>
        
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
                v-model="categoryChecked[category]"
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
              :model-value="budget?.toString() ?? ''"
              type="number"
              :placeholder="t('gear.shopping.budgetPlaceholder', 'Enter budget amount')"
              class="max-w-xs"
              min="0"
              step="0.01"
              @update:model-value="(value) => {
                budget = value === '' ? null : Number(value)
              }"
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

      <!-- Shopping list section -->
      <div
        v-if="shoppingList.length > 0"
        class="space-y-4"
      >
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold">
            {{ t('gear.shopping.shoppingList', 'Shopping List') }}
          </h2>
          <Button
            variant="outline"
            size="sm"
            @click="shoppingList = []"
          >
            {{ t('gear.shopping.clearList', 'Clear List') }}
          </Button>
        </div>
        
        <div class="space-y-2">
          <div
            v-for="item in shoppingList"
            :key="item.id"
            class="flex items-center gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
          >
            <!-- Category icon -->
            <CategoryIcon :category="item.category" :size="20" class="text-muted-foreground shrink-0" />

            <!-- Item info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <RouterLink
                  :to="`/gear/${item._containerId}/items/${item.id}/edit?returnTo=shopping`"
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
                  v-else-if="isExpiringSoon(item)"
                  variant="outline"
                  :class="[
                    'text-xs',
                    isExpired(item) ? 'text-red-600 border-red-600' : 'text-yellow-600 border-yellow-600'
                  ]"
                >
                  {{ isExpired(item) ? t('gear.item.expiration.expired') : t('gear.item.expiration.expiringSoon') }}
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
                <span v-if="item.expirationDate" :class="isExpired(item) ? 'text-red-600' : 'text-yellow-600'">
                  {{ isExpired(item) ? t('gear.item.expiration.expired') : t('gear.item.expiration.expiringSoon') }}: {{ new Date(item.expirationDate).toLocaleDateString() }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2 shrink-0">
              <Button
                variant="default"
                size="sm"
                @click="markAsPurchased(item)"
              >
                <CheckCircle2 class="size-4" />
                {{ t('gear.shopping.purchased', 'Purchased') }}
              </Button>
              <Button
                variant="outline"
                size="sm"
                @click="deleteFromShoppingList(item)"
              >
                <X class="size-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Available items list -->
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold">
            {{ t('gear.shopping.availableItems', 'Available Items') }}
          </h2>
          <Button
            v-if="filteredItems.length > 0"
            variant="outline"
            size="sm"
            @click="addAllToShoppingList"
          >
            <Plus class="size-4" />
            {{ t('gear.shopping.addAll', 'Add All') }}
          </Button>
        </div>
        
        <div class="space-y-2">
          <div
            v-if="filteredItems.length === 0"
            class="text-center py-12 text-muted-foreground"
          >
            <p class="text-lg">
              {{ t('gear.shopping.noItems', 'No items found') }}
            </p>
            <p class="text-sm mt-2">
              {{ t('gear.shopping.noItemsDescription', 'Try adjusting your filters') }}
            </p>
          </div>
          
          <div
            v-for="item in filteredItems"
            :key="item.id"
            class="flex items-center gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
          >
            <!-- Toggle button -->
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
                <RouterLink
                  :to="`/gear/${item._containerId}/items/${item.id}/edit?returnTo=shopping`"
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
                  v-else-if="isExpiringSoon(item)"
                  variant="outline"
                  :class="[
                    'text-xs',
                    isExpired(item) ? 'text-red-600 border-red-600' : 'text-yellow-600 border-yellow-600'
                  ]"
                >
                  {{ isExpired(item) ? t('gear.item.expiration.expired') : t('gear.item.expiration.expiringSoon') }}
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
                <span v-if="item.expirationDate" :class="isExpired(item) ? 'text-red-600' : 'text-yellow-600'">
                  {{ isExpired(item) ? t('gear.item.expiration.expired') : t('gear.item.expiration.expiringSoon') }}: {{ new Date(item.expirationDate).toLocaleDateString() }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary below list -->
      <div
        v-if="shoppingList.length > 0"
        class="p-4 border rounded-lg bg-primary/5"
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-semibold">
              {{ t('gear.shopping.summary', 'Summary') }}
            </h3>
            <p class="text-sm text-muted-foreground">
              {{ t('gear.shopping.itemsCount', { count: shoppingList.length }) }}
              ({{ t('gear.shopping.totalQuantity', { count: totalItemsCount }) }})
              <span v-if="totalPrice > 0">
                - {{ totalPrice.toFixed(2) }} {{ t('gear.shopping.currency', 'PLN') }}
              </span>
            </p>
          </div>
        </div>
      </div>

      <!-- Deleted items section -->
      <div
        v-if="deletedItems.length > 0"
        class="space-y-4"
      >
        <h2 class="text-xl font-semibold text-muted-foreground">
          {{ t('gear.shopping.deletedItems', 'Deleted Items') }}
        </h2>
        
        <div class="space-y-2">
          <div
            v-for="item in deletedItems"
            :key="item.id"
            class="flex items-center gap-4 p-4 border rounded-lg bg-muted/30 opacity-75"
          >
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
              </div>
              <div class="flex items-center gap-4 mt-1 text-sm text-muted-foreground flex-wrap">
                <span>{{ getCategoryLabel(item.category) }}</span>
                <span v-if="item.brand">{{ item.brand }}</span>
                <span>{{ t('gear.item.quantity') }}: {{ item.quantity }}</span>
                <span v-if="item.price">
                  {{ (item.price * item.quantity).toFixed(2) }} {{ t('gear.shopping.currency', 'PLN') }}
                </span>
              </div>
            </div>

            <!-- Restore button -->
            <Button
              variant="outline"
              size="sm"
              @click="restoreToShoppingList(item)"
            >
              {{ t('gear.shopping.restore', 'Restore') }}
            </Button>
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

      <!-- Add Item Dialog -->
      <Dialog v-model:open="addItemDialogOpen">
        <DialogContent class="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{{ t('gear.shopping.addItem', 'Add') }}</DialogTitle>
            <DialogDescription>
              {{ t('gear.shopping.addItemDescription', 'Add a new item to your shopping list') }}
            </DialogDescription>
          </DialogHeader>
          <form @submit="onAddItemSubmit">
            <ItemFormFields
              :item="undefined"
              :loading="isAddingItem"
              @cancel="() => {
                addItemDialogOpen = false
                resetAddItemForm({ values: getInitialAddItemValues() })
              }"
            />
            <DialogFooter>
              <Button
                variant="outline"
                type="button"
                @click="() => {
                  addItemDialogOpen = false
                  resetAddItemForm({ values: getInitialAddItemValues() })
                }"
              >
                {{ t('gear.actions.cancel', 'Cancel') }}
              </Button>
              <Button type="submit" :disabled="isAddingItem">
                {{ t('gear.actions.add', 'Add') }}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  </AuthenticatedLayout>
</template>
