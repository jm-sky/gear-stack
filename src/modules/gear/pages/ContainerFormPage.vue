<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useDebounceFn } from '@vueuse/core'
import { useForm } from 'vee-validate'
import { watch, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useSettings } from '@/modules/settings/composables/useSettings'
import { useHandleError } from '@/shared/composables/useHandleError'
import { usePageTitle } from '@/shared/composables/usePageTitle'
import type { ICreateContainerDto, IUpdateContainerDto, TContainerColor } from '../types/gear.types'
import ContainerFormFields from '../components/ContainerFormFields.vue'
import { useContainer } from '../composables/useContainer'
import { useGear } from '../composables/useGear'
import { useGearSettings } from '../composables/useGearSettings'
import { GearRoutePath } from '../routes'
import { CONTAINER_COLORS } from '../utils/containerColors'
import { recognizeContainerType } from '../utils/containerTypeRecognition'
import { recognizeParameters } from '../utils/parameterRecognition'
import { type ContainerFormData, containerSchema } from '../utils/validation'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const { createContainer, updateContainer } = useGear()
const { customBrands } = useGearSettings()
const { settings } = useSettings()
const { handleError } = useHandleError()
const { setTitle } = usePageTitle()

const containerId = route.params.id as string | undefined
const isEditMode: boolean = !!containerId

const { container } = useContainer(containerId)

// Set dynamic page title
watchEffect(() => {
  if (isEditMode && container.value?.name) {
    setTitle('gear.container.edit.title', { name: container.value.name })
  }
})

const getInitialValues = (): ContainerFormData => {
  if (container.value) {
    return {
      name: container.value.name,
      description: container.value.description ?? '',
      type: container.value.type,
      color: container.value.color ?? 'default',
      hideWhenNested: container.value.hideWhenNested ?? false,
      isPublic: container.value.isPublic ?? false,
      brand: container.value.brand ?? '',
      price: container.value.price ?? undefined,
      weight: container.value.weight ?? undefined,
      weightUnit: container.value.weightUnit ?? 'kg',
      maxWeight: container.value.maxWeight ?? undefined,
      maxWeightUnit: container.value.maxWeightUnit ?? 'kg',
      url: container.value.url ?? '',
      showItemImages: container.value.showItemImages ?? false,
    }
  }
  // For new containers, use default from settings (will be updated via watch)
  return {
    name: '',
    description: '',
    type: 'other' as const,
    color: 'default' as const,
    hideWhenNested: false,
    isPublic: false, // Will be updated via watch when settings load
    brand: '',
    price: undefined,
    weight: undefined,
    weightUnit: 'kg' as const,
    maxWeight: undefined,
    maxWeightUnit: 'kg' as const,
    url: '',
    showItemImages: false,
  }
}

const { handleSubmit, isSubmitting, setFieldValue, values, setErrors } = useForm({
  validationSchema: toTypedSchema(containerSchema),
  initialValues: getInitialValues(),
})

// Watch for settings changes and update isPublic field for new containers
watch(() => settings.value?.defaultContainersPublic, (newValue) => {
  if (!isEditMode && newValue !== undefined) {
    // Update isPublic when settings load (only if still at initial false value)
    // This allows user to change it manually without it being overwritten
    const currentValue = values.isPublic
    if (currentValue === false && newValue === true) {
      setFieldValue('isPublic', newValue)
    } else if (currentValue === false && newValue === false) {
      // Keep it false if settings also say false
      setFieldValue('isPublic', false)
    }
  }
}, { immediate: true })

// Map item colors to container colors
const mapItemColorToContainerColor = (itemColor: string): TContainerColor | null => {
  const normalized = itemColor.toLowerCase().trim()

  // Direct matches
  const colorMap: Record<string, TContainerColor> = {
    'green': 'green',
    'blue': 'blue',
    'red': 'red',
    'yellow': 'yellow',
    'purple': 'purple',
    'orange': 'orange',
    'pink': 'pink',
    'teal': 'teal',
    'indigo': 'indigo',
    // Additional mappings
    'navy': 'blue',
    'olive': 'green',
    'gray': 'default',
    'grey': 'default',
    'black': 'default',
    'tan': 'yellow',
    'brown': 'orange',
  }

  // Check direct match
  if (colorMap[normalized]) {
    return colorMap[normalized]
  }

  // Check if container color exists
  if (CONTAINER_COLORS.includes(normalized as TContainerColor)) {
    return normalized as TContainerColor
  }

  return null
}

// Auto-recognize type, color, and brand from name during typing (only for new containers, not when editing)
const autoRecognizeFromName = useDebounceFn(() => {
  if (isEditMode || !values.name || values.name.trim().length === 0) {
    return
  }

  // Recognize container type (only if type is 'other' or not set)
  if (values.type === 'other' || !values.type) {
    const detectedType = recognizeContainerType(values.name)
    if (detectedType) {
      setFieldValue('type', detectedType)
    }
  }

  // Recognize brand and color
  const params = recognizeParameters(
    values.name,
    customBrands.value
  )

  if (params.brand && !values.brand) {
    setFieldValue('brand', params.brand)
  }

  // Map item color to container color
  if (params.color && (!values.color || values.color === 'default')) {
    const containerColor = mapItemColorToContainerColor(params.color)
    if (containerColor) {
      setFieldValue('color', containerColor)
    }
  }
}, 500)

// Watch for name changes and auto-recognize
watch(() => values.name, () => {
  autoRecognizeFromName()
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
      router.push(GearRoutePath.ContainerDetailById(containerId))
    } else {
      const newContainer = await createContainer(data as ICreateContainerDto)
      toast.success(t('common.success'))
      router.push(GearRoutePath.ContainerDetailById(newContainer.id))
    }
  } catch (error) {
    console.error(error)
    handleError(error, { setErrors })
  }
})

// Cancel handler
const handleCancel = () => {
  if (isEditMode && containerId) {
    router.push(GearRoutePath.ContainerDetailById(containerId))
  } else {
    router.push(GearRoutePath.Containers)
  }
}

// Recognize parameters handler
const handleRecognizeParameters = () => {
  if (!values.name) {
    toast.error(t('gear.container.name'))
    return
  }

  try {
    const params = recognizeParameters(
      values.name,
      customBrands.value
    )

    if (!params.brand && !params.color) {
      toast.info(t('gear.actions.noParametersFound'))
      return
    }

    if (params.brand && !values.brand) {
      setFieldValue('brand', params.brand)
    }

    // Map item color to container color
    if (params.color && (!values.color || values.color === 'default')) {
      const containerColor = mapItemColorToContainerColor(params.color)
      if (containerColor) {
        setFieldValue('color', containerColor)
      }
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

