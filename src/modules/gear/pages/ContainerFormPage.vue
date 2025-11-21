<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import type { ICreateContainerDto, IUpdateContainerDto } from '../types/gear.types'
import ContainerFormFields from '../components/ContainerFormFields.vue'
import { useContainer } from '../composables/useContainer'
import { useGear } from '../composables/useGear'
import { recognizeContainerType } from '../utils/containerTypeRecognition'
import { recognizeParameters } from '../utils/parameterRecognition'
import { type ContainerFormData, containerSchema } from '../utils/validation'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const { createContainer, updateContainer } = useGear()

const containerId = route.params.id as string | undefined
const isEditMode: boolean = !!containerId

const { container } = useContainer(containerId)

const getInitialValues = (): ContainerFormData => {
  if (container.value) {
    return {
      name: container.value.name,
      description: container.value.description ?? '',
      type: container.value.type,
      color: container.value.color ?? 'default',
      hideWhenNested: container.value.hideWhenNested ?? false,
      brand: container.value.brand ?? '',
      price: container.value.price,
      weight: container.value.weight,
      weightUnit: container.value.weightUnit ?? 'kg',
      maxWeight: container.value.maxWeight,
      maxWeightUnit: container.value.maxWeightUnit ?? 'kg',
      url: container.value.url ?? '',
    }
  }
  return {
    name: '',
    description: '',
    type: 'other' as const,
    color: 'default' as const,
    hideWhenNested: false,
    brand: '',
    price: undefined,
    weight: undefined,
    weightUnit: 'kg' as const,
    maxWeight: undefined,
    maxWeightUnit: 'kg' as const,
    url: '',
  }
}

const { handleSubmit, isSubmitting, setFieldValue, values } = useForm({
  validationSchema: toTypedSchema(containerSchema),
  initialValues: getInitialValues(),
})

// Auto-detect container type from name on blur (only for new containers, not when editing)
const handleNameBlur = () => {
  if (!isEditMode && values.name && values.type === 'other') {
    const detectedType = recognizeContainerType(values.name)
    if (detectedType) {
      setFieldValue('type', detectedType)
    }
  }
}

// Submit handler
const onSubmit = handleSubmit(async (data: ContainerFormData) => {
  try {
    if (isEditMode && containerId) {
      updateContainer(containerId, data as IUpdateContainerDto)
      toast.success(t('common.success'))
      router.push(`/gear/${containerId}`)
    } else {
      const newContainer = createContainer(data as ICreateContainerDto)
      toast.success(t('common.success'))
      router.push(`/gear/${newContainer.id}`)
    }
  } catch (error) {
    toast.error(t('common.error'))
    console.error(error)
  }
})

// Cancel handler
const handleCancel = () => {
  if (isEditMode && containerId) {
    router.push(`/gear/${containerId}`)
  } else {
    router.push('/gear')
  }
}

// Recognize parameters handler
const handleRecognizeParameters = () => {
  if (!values.name) {
    toast.error(t('gear.container.name'))
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

    toast.success(t('gear.actions.parametersRecognized'))
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error recognizing parameters:', error)
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 class="text-3xl font-bold">
          {{ isEditMode ? t('gear.container.edit.title') : t('gear.container.create.title') }}
        </h1>
        <p class="text-muted-foreground mt-1">
          {{ isEditMode ? t('gear.container.edit.description') : t('gear.container.create.description') }}
        </p>
      </div>

      <div class="bg-card rounded-lg border p-6">
        <form @submit="onSubmit">
          <ContainerFormFields
            :container="container"
            :loading="isSubmitting"
            @submit="handleSubmit"
            @cancel="handleCancel"
            @name-blur="handleNameBlur"
            @recognize-parameters="handleRecognizeParameters"
          />
        </form>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

