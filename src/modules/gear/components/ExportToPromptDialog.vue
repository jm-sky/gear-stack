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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { IGearContainer } from '../types/gear.types'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { useGearSettings } from '../composables/useGearSettings'
import { useGearStore } from '../store/useGearStore'
import { calculateTotalWeightSync } from '../utils/containerCalculations'
import { exportContainersToPrompt, exportContainerToPrompt } from '../utils/exportToPrompt'
import GuidelinesDialog from './GuidelinesDialog.vue'

const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  container?: IGearContainer
  containers?: IGearContainer[]
}>()

const { t, locale } = useI18n()
const store = useGearStore()
const { defaultCurrency } = useGearSettings()
const copied = ref(false)
const isGuidelinesDialogOpen = ref(false)
const showUuid = ref(true)
const showWeight = ref(true)
const showColor = ref(true)
const showBrand = ref(true)
const showNestedContainer = ref(true)
const showLegend = ref(true)
const showPrices = ref(false)
const showNotes = ref(true)
const descriptionFormat = ref<'off' | 'inline' | 'newline'>('off')

// Get container type label helper
const { getContainerTypeLabel } = useContainerTypeLabel()

// Sync helpers for computed
const getContainerById = (id: string): IGearContainer | undefined => {
  return store.getContainerById(id)
}

const calculateTotalWeight = (containerId: string): number => {
  const container = store.getContainerById(containerId)
  if (!container) return 0
  return calculateTotalWeightSync(container, store.getAllContainers)
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
    showPrices: showPrices.value,
    showNotes: showNotes.value,
    descriptionFormat: descriptionFormat.value,
    defaultCurrency: defaultCurrency.value,
    locale: locale.value,
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

const handleOpenGuidelines = () => {
  isGuidelinesDialogOpen.value = true
}

</script>

<template>
  <Dialog v-model:open="open">
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
          <div class="flex items-center space-x-2">
            <Checkbox id="showPrices" v-model="showPrices" />
            <Label for="showPrices" class="text-sm font-normal cursor-pointer">
              {{ t('gear.export.showPrices', 'Show prices') }}
            </Label>
          </div>
          <div class="flex items-center space-x-2">
            <Checkbox id="showNotes" v-model="showNotes" />
            <Label for="showNotes" class="text-sm font-normal cursor-pointer">
              {{ t('gear.export.showNotes', 'Show notes/descriptions') }}
            </Label>
          </div>
        </div>
        <div class="space-y-2">
          <Label class="text-sm font-medium">
            {{ t('gear.export.descriptionFormat', 'Item descriptions format') }}
          </Label>
          <Select :model-value="descriptionFormat" @update:model-value="(value) => descriptionFormat = value as 'off' | 'inline' | 'newline'">
            <SelectTrigger class="w-full sm:w-[200px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="off">
                {{ t('gear.export.descriptionFormatOff', 'OFF') }}
              </SelectItem>
              <SelectItem value="inline">
                {{ t('gear.export.descriptionFormatInline', 'Inline') }}
              </SelectItem>
              <SelectItem value="newline">
                {{ t('gear.export.descriptionFormatNewline', 'New Line') }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div class="flex-1 max-w-[calc(100vw-2rem)] md:max-w-full overflow-auto">
        <pre class="whitespace-pre-wrap text-sm font-mono bg-muted p-4 rounded-md border overflow-x-auto">{{ markdown }}</pre>
      </div>

      <DialogFooter class="flex-col sm:flex-row gap-2">
        <Button variant="secondary" class="sm:mr-auto" @click="handleOpenGuidelines">
          <Info class="size-4" />
          {{ t('gear.export.guidelines', 'Guidelines') }}
        </Button>
        <div class="flex gap-2">
          <Button class="flex-1" variant="outline" @click="open = false">
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

  <!-- Guidelines Dialog -->
  <GuidelinesDialog v-model:open="isGuidelinesDialogOpen" />
</template>

