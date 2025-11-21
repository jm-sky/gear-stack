<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import Tabs from '@/components/ui/tabs/Tabs.vue'
import TabsContent from '@/components/ui/tabs/TabsContent.vue'
import TabsList from '@/components/ui/tabs/TabsList.vue'
import TabsTrigger from '@/components/ui/tabs/TabsTrigger.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import type { ICreateItemDto, IUpdateItemDto } from '../types/gear.types'
import type { IItemWithContainer } from '../utils/allItemsColumns'
import ItemCatalogSelector from '../components/ItemCatalogSelector.vue'
import ItemFormFields from '../components/ItemFormFields.vue'
import { useContainer } from '../composables/useContainer'
import { useGear } from '../composables/useGear'
import { useItem } from '../composables/useItem'
import { recognizeCategory } from '../utils/categoryRecognition'
import { getDefaultItemValues } from '../utils/defaultValues'
import { recognizeParameters } from '../utils/parameterRecognition'
import { type ItemFormData, itemSchema } from '../utils/validation'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const { createItem, updateItem } = useGear()

const containerId = route.params.containerId as string
const itemId = route.params.itemId as string | undefined
const isEditMode: boolean = !!itemId

const { container } = useContainer(containerId)
const { item } = useItem(containerId, itemId)

// Redirect if container not found
if (!container.value) {
  router.push('/gear')
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
      weightUnit: item.value.weightUnit ?? 'g',
      notes: item.value.notes ?? '',
      expirationDate: item.value.expirationDate ?? '',
      priority: item.value.priority,
      status: item.value.status,
      price: item.value.price,
      url: item.value.url ?? '',
      brand: item.value.brand ?? '',
      color: item.value.color ?? '',
      quality: item.value.quality,
      wearable: item.value.wearable ?? false,
      consumable: item.value.consumable ?? false,
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

const { handleSubmit, isSubmitting, setFieldValue, values, resetForm } = form

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
      updateItem(containerId, itemId, data as IUpdateItemDto)
      toast.success(t('common.success'))
      router.push(`/gear/${containerId}`)
    } else {
      // Add linkedItemId if selecting from catalog
      const createData: ICreateItemDto = {
        ...data as ICreateItemDto,
        linkedItemId: tabMode.value === 'catalog' && selectedCatalogItemId.value ? selectedCatalogItemId.value : undefined,
      }
      createItem(containerId, createData)
      toast.success(t('common.success'))
      router.push(`/gear/${containerId}`)
    }
  } catch (error) {
    toast.error(t('common.error'))
    console.error(error)
  }
})

// Cancel handler
const handleCancel = () => {
  router.push(`/gear/${containerId}`)
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
      <div>
        <h1 class="text-3xl font-bold">
          {{ isEditMode ? t('gear.item.edit') : t('gear.item.create') }}
        </h1>
        <p class="text-muted-foreground mt-1">
          <RouterLink
            :to="`/gear/${container.id}`"
            class="hover:text-primary hover:underline transition-colors"
          >
            {{ container.name }}
          </RouterLink>
        </p>
      </div>

      <div class="bg-card rounded-lg border p-6">
        <!-- Tabs - only show when creating new item (not editing) -->
        <Tabs
          v-if="!isEditMode"
          v-model="tabMode"
        >
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
                <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  {{ t('gear.item.catalog.selectItem') }}
                  <span class="text-destructive">*</span>
                </label>
                <ItemCatalogSelector
                  :container-id="containerId"
                  :model-value="selectedCatalogItemId"
                  @update:model-value="selectedCatalogItemId = $event"
                  @select="handleCatalogItemSelect"
                />
              </div>
            </TabsContent>

            <TabsContent
              value="new"
              class="mt-0"
            >
              <div />
            </TabsContent>

            <ItemFormFields
              :item="item"
              :loading="isSubmitting"
              :hide-name="!isEditMode && tabMode === 'catalog' && !selectedCatalogItemId"
              @cancel="handleCancel"
              @name-blur="handleNameBlur"
              @recognize-parameters="handleRecognizeParameters"
            />
          </form>
        </Tabs>

        <!-- No tabs when editing -->
        <form
          v-else
          @submit="onSubmit"
        >
          <ItemFormFields
            :item="item"
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

