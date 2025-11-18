<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import type { ICreateItemDto, IUpdateItemDto } from '../types/gear.types'
import ItemFormFields from '../components/ItemFormFields.vue'
import { useContainer } from '../composables/useContainer'
import { useGear } from '../composables/useGear'
import { useItem } from '../composables/useItem'
import { getDefaultItemValues } from '../utils/defaultValues'
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
    }
  }
  return {
    ...getDefaultItemValues(),
  } as ItemFormData
}

const { handleSubmit, isSubmitting } = useForm({
  validationSchema: toTypedSchema(itemSchema),
  initialValues: getInitialValues(),
})

// Submit handler
const onSubmit = handleSubmit(async (data: ICreateItemDto | IUpdateItemDto) => {
  try {
    if (isEditMode && itemId) {
      updateItem(containerId, itemId, data as IUpdateItemDto)
      toast.success(t('common.success'))
      router.push(`/gear/${containerId}`)
    } else {
      createItem(containerId, data as ICreateItemDto)
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
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="container" class="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 class="text-3xl font-bold">
          {{ isEditMode ? t('gear.item.edit') : t('gear.item.create') }}
        </h1>
        <p class="text-muted-foreground mt-1">
          {{ container.name }}
        </p>
      </div>

      <div class="bg-card rounded-lg border p-6">
        <form @submit="onSubmit">
          <ItemFormFields
            :item="item"
            :loading="isSubmitting"
            @cancel="handleCancel"
          />
        </form>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

