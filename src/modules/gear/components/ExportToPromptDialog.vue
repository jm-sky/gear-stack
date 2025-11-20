<script setup lang="ts">
import { Check, Copy, Info } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
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
import { Label } from '@/components/ui/label'
import { useSettings } from '@/modules/settings/composables/useSettings'
import type { IGearContainer } from '../types/gear.types'
import { useGear } from '../composables/useGear'
import { guidelinesTemplate } from '../services/markdownImportService'
import { exportContainersToPrompt, exportContainerToPrompt } from '../utils/exportToPrompt'

const props = defineProps<{
  open: boolean
  container?: IGearContainer
  containers?: IGearContainer[]
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { t } = useI18n()
const { getContainerById, calculateTotalWeight } = useGear()
const { customContainerTypes } = useSettings()
const copied = ref(false)
const copiedGuidelines = ref(false)
const showUuid = ref(true)
const showWeight = ref(true)
const showColor = ref(true)
const showBrand = ref(true)
const showNestedContainer = ref(true)
const showLegend = ref(true)

// Get container type label helper
const getContainerTypeLabel = (typeKey: string): string => {
  const customType = customContainerTypes.value.find(t => t.key === typeKey)
  if (customType) {
    return customType.label
  }
  return t(`gear.container.types.${typeKey}`)
}

// Generate markdown based on current options
const markdown = computed<string>(() => {
  const exportOptions = {
    t,
    getContainerTypeLabel,
    getContainerById,
    calculateTotalWeight,
    showUuid: showUuid.value,
    showWeight: showWeight.value,
    showColor: showColor.value,
    showBrand: showBrand.value,
    showNestedContainer: showNestedContainer.value,
    showLegend: showLegend.value,
  }

  if (props.container) {
    return exportContainerToPrompt(props.container, exportOptions)
  } else if (props.containers && props.containers.length > 0) {
    return exportContainersToPrompt(props.containers, exportOptions)
  }
  return ''
})

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(markdown.value)
    copied.value = true
    toast.success(t('gear.actions.exportToPromptSuccess'))
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error copying to clipboard:', error)
  }
}

const handleCopyGuidelines = async () => {
  try {
    await navigator.clipboard.writeText(guidelinesTemplate)
    copiedGuidelines.value = true
    toast.success(t('gear.export.guidelinesCopied', 'Guidelines copied to clipboard'))
    setTimeout(() => {
      copiedGuidelines.value = false
    }, 2000)
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error copying guidelines:', error)
  }
}

const handleOpenChange = (value: boolean) => {
  emit('update:open', value)
}
</script>

<template>
  <Dialog :open="open" @update:open="handleOpenChange">
    <DialogContent class="min-w-full md:min-w-3xl max-w-screen md:max-w-6xl max-h-[90vh] flex flex-col">
      <DialogHeader>
        <DialogTitle>
          {{ t('gear.actions.exportToPrompt') }}
        </DialogTitle>
        <DialogDescription>
          {{ t('gear.actions.exportToPromptDescription', 'Skopiuj poniższą treść i wklej do ChatGPT lub innego AI') }}
        </DialogDescription>
      </DialogHeader>

      <!-- Export Options -->
      <div class="space-y-3 border-b pb-4">
        <div class="text-sm font-medium">
          {{ t('gear.export.options', 'Export Options') }}
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="flex items-center space-x-2">
            <Checkbox id="showUuid" v-model="showUuid" />
            <Label for="showUuid" class="text-sm font-normal cursor-pointer">
              {{ t('gear.export.showUuid', 'Show UUID in export') }}
            </Label>
          </div>
          <div class="flex items-center space-x-2">
            <Checkbox id="showWeight" v-model="showWeight" />
            <Label for="showWeight" class="text-sm font-normal cursor-pointer">
              {{ t('gear.export.showWeight', 'Show weight') }}
            </Label>
          </div>
          <div class="flex items-center space-x-2">
            <Checkbox id="showColor" v-model="showColor" />
            <Label for="showColor" class="text-sm font-normal cursor-pointer">
              {{ t('gear.export.showColor', 'Show color') }}
            </Label>
          </div>
          <div class="flex items-center space-x-2">
            <Checkbox id="showBrand" v-model="showBrand" />
            <Label for="showBrand" class="text-sm font-normal cursor-pointer">
              {{ t('gear.export.showBrand', 'Show brand') }}
            </Label>
          </div>
          <div class="flex items-center space-x-2">
            <Checkbox id="showNestedContainer" v-model="showNestedContainer" />
            <Label for="showNestedContainer" class="text-sm font-normal cursor-pointer">
              {{ t('gear.export.showNestedContainer', 'Show nested container reference') }}
            </Label>
          </div>
          <div class="flex items-center space-x-2">
            <Checkbox id="showLegend" v-model="showLegend" />
            <Label for="showLegend" class="text-sm font-normal cursor-pointer">
              {{ t('gear.export.showLegend', 'Show legend') }}
            </Label>
          </div>
        </div>
      </div>

      <div class="flex-1 max-w-[calc(100vw-2rem)] md:max-w-full overflow-auto">
        <pre class="whitespace-pre-wrap text-sm font-mono bg-muted p-4 rounded-md border overflow-x-auto">{{ markdown }}</pre>
      </div>

      <DialogFooter class="flex-col sm:flex-row gap-2">
        <Button variant="secondary" class="sm:mr-auto" @click="handleCopyGuidelines">
          <Info v-if="!copiedGuidelines" class="size-4" />
          <Check v-else class="size-4" />
          {{ copiedGuidelines ? t('common.copyToClipboard.copied') : t('gear.export.guidelines', 'Guidelines') }}
        </Button>
        <div class="flex gap-2">
          <Button class="flex-1" variant="outline" @click="handleOpenChange(false)">
            {{ t('common.close') }}
          </Button>
          <Button class="flex-1" @click="handleCopy">
            <Copy v-if="!copied" class="size-4" />
            <Check v-else class="size-4" />
            {{ copied ? t('common.copyToClipboard.copied') : t('common.copyToClipboard.copy') }}
          </Button>
        </div>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

