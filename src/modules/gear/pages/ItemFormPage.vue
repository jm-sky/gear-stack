<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import { nextTick, onMounted, ref, watch, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Label } from '@/components/ui/label'
import Tabs from '@/components/ui/tabs/Tabs.vue'
import TabsContent from '@/components/ui/tabs/TabsContent.vue'
import TabsList from '@/components/ui/tabs/TabsList.vue'
import TabsTrigger from '@/components/ui/tabs/TabsTrigger.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useBackend } from '@/shared/composables/useBackend'
import { useHandleError } from '@/shared/composables/useHandleError'
import { usePageTitle } from '@/shared/composables/usePageTitle'
import { config } from '@/shared/config/config'
import type { ICreateItemDto, IGearItem, IUpdateItemDto } from '../types/gear.types'
import type { IItemWithContainer } from '../utils/allItemsColumns'
import ItemCatalogSelector from '../components/ItemCatalogSelector.vue'
import ItemFormFields from '../components/ItemFormFields.vue'
import { useContainer } from '../composables/useContainer'
import { useGear } from '../composables/useGear'
import { useNavigationReturn } from '../composables/useNavigationReturn'
import { GearRoutePath } from '../routes'
import { gearItemService } from '../services/gearItemService'
import { useGearStore } from '../store/useGearStore'
import { recognizeCategory } from '../utils/categoryRecognition'
import { getDefaultItemValues } from '../utils/defaultValues'
import { recognizeParameters } from '../utils/parameterRecognition'
import { type ItemFormData, itemSchema } from '../utils/validation'

const router = useRouter()
const route = useRoute()
const store = useGearStore()
const { t } = useI18n()
const { createItem, updateItem } = useGear()
const { shouldUseAPI } = useBackend()
const { handleError } = useHandleError()
const { setTitle } = usePageTitle()

const containerId = route.params.containerId as string
const itemId = route.params.itemId as string | undefined
const isEditMode: boolean = !!itemId

const { container } = useContainer(containerId)
const { navigateBackAndClean } = useNavigationReturn(containerId, itemId)

// Local state for item (loaded explicitly, not from computed)
const item = ref<IGearItem | null>(null)

// Set dynamic page title
watchEffect(() => {
  if (isEditMode && item.value?.name) {
    setTitle('gear.item.edit', { name: item.value.name })
  } else if (!isEditMode && container.value?.name) {
    setTitle('gear.item.create', { name: container.value.name })
  }
})
const isLoading = ref(isEditMode) // Only show loading when editing

// Redirect if container not found
if (!container.value) {
  router.push(GearRoutePath.Containers)
}

// Tabs mode - only show tabs when creating new item (not editing)
const tabMode = ref<'new' | 'catalog'>('new')
const selectedCatalogItemId = ref<string>('')

const getInitialValues = (): ItemFormData => {
  if (item.value) {
    return {
      name: item.value.name,
      category: item.value.category,
      quantity: item.value.quantity,
      weight: item.value.weight,
      weightUnit: item.value.weightUnit ?? config.defaults.preferredWeightUnit,
      notes: item.value.notes ?? '',
      expirationDate: item.value.expirationDate ?? '',
      priority: item.value.priority,
      status: item.value.status,
      price: item.value.price ?? undefined,
      currency: item.value.currency ?? undefined,
      url: item.value.url ?? '',
      brand: item.value.brand ?? '',
      color: item.value.color ?? '',
      quality: item.value.quality ?? undefined,
      wearable: item.value.wearable ?? false,
      consumable: item.value.consumable ?? false,
      showOnContainer: item.value.showOnContainer ?? false,
    }
  }
  return {
    ...getDefaultItemValues(),
  } as ItemFormData
}

const form = useForm({
  validationSchema: toTypedSchema(itemSchema),
  initialValues: getInitialValues(),
})

const { handleSubmit, isSubmitting, setFieldValue, setValues, values, resetForm, setErrors } = form

// Load item data for edit mode
const loadItem = async () => {
  if (!isEditMode || !itemId) {
    isLoading.value = false
    return
  }

  try {
    const service = gearItemService()

    if (shouldUseAPI.value && 'getItem' in service) {
      item.value = await service.getItem(itemId)
    } else {
      const containerData = store.getContainerById(containerId)
      const foundItem = containerData?.items.find(i => i.id === itemId)

      if (!foundItem) {
        toast.error(t('common.error'))
        router.push(GearRoutePath.ContainerDetailById(containerId))
        return
      }

      item.value = foundItem
    }
  } catch (error) {
    console.error('Failed to load item:', error)
    toast.error(t('common.error'))
    router.push(GearRoutePath.ContainerDetailById(containerId))
  } finally {
    // First: show the form
    isLoading.value = false

    // Then: wait for Vue to render the form fields, then set values
    if (item.value) {
      await nextTick()

      const loadedItem = item.value
      setValues({
        name: loadedItem.name,
        category: loadedItem.category,
        quantity: loadedItem.quantity,
        weight: loadedItem.weight,
        weightUnit: loadedItem.weightUnit ?? 'g',
        notes: loadedItem.notes ?? '',
        expirationDate: loadedItem.expirationDate ?? '',
        priority: loadedItem.priority,
        status: loadedItem.status,
        price: loadedItem.price ?? undefined,
        currency: loadedItem.currency ?? undefined,
        url: loadedItem.url ?? '',
        brand: loadedItem.brand ?? '',
        color: loadedItem.color ?? '',
        quality: loadedItem.quality ?? undefined,
        wearable: loadedItem.wearable ?? false,
        consumable: loadedItem.consumable ?? false,
      })
    }
  }
}

onMounted(async () => {
  await loadItem()
})

// Reset form when switching tabs
watch(tabMode, () => {
  resetForm({
    values: getDefaultItemValues() as ItemFormData,
  })
  selectedCatalogItemId.value = ''
})

// Auto-detect category from name on blur (only for new items, not when editing)
const handleNameBlur = () => {
  if (!isEditMode && values.name && values.category === 'other') {
    const detectedCategory = recognizeCategory(values.name)
    if (detectedCategory) {
      setFieldValue('category', detectedCategory)
    }
  }
}

// Auto-set consumable/wearable based on category (only for new items, not when editing)
watch(
  () => values.category,
  (newCategory) => {
    if (!isEditMode && newCategory) {
      if (newCategory === 'food') {
        setFieldValue('consumable', true)
      } else if (newCategory === 'clothing') {
        setFieldValue('wearable', true)
      }
    }
  },
)

// Handle catalog item selection
const handleCatalogItemSelect = (selectedItem: IItemWithContainer) => {
  // Pre-fill form with selected item data
  setFieldValue('name', selectedItem.name)
  setFieldValue('category', selectedItem.category)
  setFieldValue('quantity', selectedItem.quantity)
  setFieldValue('weight', selectedItem.weight)
  setFieldValue('weightUnit', selectedItem.weightUnit)
  setFieldValue('notes', selectedItem.expirationDate ? '' : '') // Reset notes for linked items
  setFieldValue('expirationDate', selectedItem.expirationDate ?? '')
  setFieldValue('priority', selectedItem.priority)
  setFieldValue('status', selectedItem.status)
  setFieldValue('brand', selectedItem.brand ?? '')
  setFieldValue('color', selectedItem.color ?? '')
  // Note: We don't copy price, url, quality, wearable, consumable as these may differ per container
}

// Submit handler
const onSubmit = handleSubmit(async (data: ICreateItemDto | IUpdateItemDto) => {
  try {
    if (isEditMode && itemId) {
      await updateItem(itemId, data as IUpdateItemDto)
      toast.success(t('common.success'))
      await navigateBackAndClean()
    } else {
      // Add linkedItemId if selecting from catalog
      const createData: ICreateItemDto = {
        ...data as ICreateItemDto,
        linkedItemId: tabMode.value === 'catalog' && selectedCatalogItemId.value ? selectedCatalogItemId.value : undefined,
      }
      await createItem(containerId, createData)
      toast.success(t('common.success'))
      await navigateBackAndClean()
    }
  } catch (error) {
    console.error(error)
    handleError(error, { setErrors })
  }
})

// Cancel handler
const handleCancel = async () => {
  await navigateBackAndClean()
}

// Recognize parameters handler
const handleRecognizeParameters = () => {
  if (!values.name) {
    toast.error(t('gear.item.name'))
    return
  }

  try {
    const params = recognizeParameters(values.name)

    if (!params.brand && !params.color) {
      toast.info(t('gear.actions.noParametersFound'))
      return
    }

    if (params.brand && !values.brand) {
      setFieldValue('brand', params.brand)
    }
    if (params.color && !values.color) {
      setFieldValue('color', params.color)
    }

    toast.success(t('gear.actions.parametersRecognized'))
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error recognizing parameters:', error)
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="container" class="max-w-2xl mx-auto space-y-6">
      <!-- Header - always visible -->
      <div>
        <h1 class="text-3xl font-bold">
          {{ isEditMode ? t('gear.item.edit') : t('gear.item.create') }}
        </h1>
        <p class="text-muted-foreground mt-1">
          <RouterLink
            :to="GearRoutePath.ContainerDetailById(container.id)"
            class="hover:text-primary hover:underline transition-colors"
          >
            {{ container.name }}
          </RouterLink>
        </p>
      </div>

      <!-- Loading state for form -->
      <div v-if="isLoading" class="h-96 animate-pulse rounded-lg bg-muted" />

      <div v-else class="bg-card rounded-lg border p-6">
        <!-- Tabs - only show when creating new item (not editing) -->
        <Tabs v-if="!isEditMode" v-model="tabMode">
          <TabsList class="mb-6">
            <TabsTrigger value="new">
              {{ t('gear.item.catalog.tabNew') }}
            </TabsTrigger>
            <TabsTrigger value="catalog">
              {{ t('gear.item.catalog.tabExisting') }}
            </TabsTrigger>
          </TabsList>

          <form @submit="onSubmit">
            <!-- Catalog mode - show selector first -->
            <TabsContent
              value="catalog"
              class="mt-0 mb-6"
            >
              <div class="space-y-2">
                <Label required>
                  {{ t('gear.item.catalog.selectItem') }}
                </Label>
                <ItemCatalogSelector
                  :container-id="containerId"
                  :model-value="selectedCatalogItemId"
                  @update:model-value="selectedCatalogItemId = $event"
                  @select="handleCatalogItemSelect"
                />
              </div>
            </TabsContent>

            <TabsContent value="new" class="mt-0">
              <div />
            </TabsContent>

            <ItemFormFields
              :item="item ?? undefined"
              :loading="isSubmitting"
              :hide-name="!isEditMode && tabMode === 'catalog' && !selectedCatalogItemId"
              @cancel="handleCancel"
              @name-blur="handleNameBlur"
              @recognize-parameters="handleRecognizeParameters"
            />
          </form>
        </Tabs>

        <!-- No tabs when editing -->
        <form v-else @submit="onSubmit">
          <ItemFormFields
            :item="item ?? undefined"
            :loading="isSubmitting"
            @cancel="handleCancel"
            @name-blur="handleNameBlur"
            @recognize-parameters="handleRecognizeParameters"
          />
        </form>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
