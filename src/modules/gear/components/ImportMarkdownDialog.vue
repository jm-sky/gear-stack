<script setup lang="ts">
import { AlertCircle, FileText } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { useGear } from '../composables/useGear'
import { markdownImportService } from '../services/markdownImportService'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'import-complete': []
}>()

const { t } = useI18n()
const { createContainer } = useGear()

const markdownContent = ref('')
const importing = ref(false)
const previewResult = ref<ReturnType<typeof markdownImportService.parseMarkdown> | null>(null)

const handleClose = () => {
  markdownContent.value = ''
  previewResult.value = null
  emit('update:open', false)
}

const handlePreview = () => {
  if (!markdownContent.value.trim()) {
    toast.error(t('gear.import.emptyContent'))
    return
  }

  const result = markdownImportService.parseMarkdown(markdownContent.value)
  previewResult.value = result

  if (result.containers.length === 0) {
    toast.warning(t('gear.import.noContainersFound'))
  } else {
    toast.success(t('gear.import.previewSuccess', { count: result.containers.length }))
  }
}

const handleImport = async () => {
  if (!previewResult.value || previewResult.value.containers.length === 0) {
    toast.error(t('gear.import.noPreview'))
    return
  }

  importing.value = true

  try {
    let importedCount = 0
    let itemCount = 0

    for (const containerData of previewResult.value.containers) {
      const container = createContainer({
        name: containerData.name,
        type: 'other',
        description: t('gear.import.importedDescription'),
      })

      // Import items
      for (const itemData of containerData.items) {
        const { createItem } = useGear()
        createItem(container.id, itemData)
        itemCount++
      }

      importedCount++
    }

    toast.success(
      t('gear.import.success', {
        containers: importedCount,
        items: itemCount,
      }),
    )

    emit('import-complete')
    handleClose()
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Import error:', error)
  } finally {
    importing.value = false
  }
}
</script>

<template>
  <Dialog :open="props.open" @update:open="handleClose">
    <DialogContent class="max-w-4xl max-h-[90vh] flex flex-col">
      <DialogHeader>
        <DialogTitle>{{ t('gear.import.title') }}</DialogTitle>
        <DialogDescription>
          {{ t('gear.import.description') }}
        </DialogDescription>
      </DialogHeader>

      <div class="flex-1 overflow-y-auto space-y-4">
        <!-- Markdown Input -->
        <div>
          <label class="text-sm font-medium mb-2 block">
            {{ t('gear.import.markdownContent') }}
          </label>
          <textarea
            v-model="markdownContent"
            :placeholder="t('gear.import.placeholder')"
            rows="12"
            class="flex min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 font-mono"
          />
        </div>

        <!-- Preview Button -->
        <div class="flex justify-start">
          <Button type="button" variant="outline" @click="handlePreview">
            <FileText class="size-4" />
            {{ t('gear.import.preview') }}
          </Button>
        </div>

        <!-- Preview Result -->
        <div v-if="previewResult" class="space-y-4">
          <!-- Errors -->
          <Alert v-if="previewResult.errors.length > 0" variant="destructive">
            <AlertCircle class="h-4 w-4" />
            <AlertTitle>{{ t('gear.import.errors') }}</AlertTitle>
            <AlertDescription>
              <ul class="list-disc list-inside text-xs">
                <li v-for="(error, idx) in previewResult.errors" :key="idx">
                  {{ error }}
                </li>
              </ul>
            </AlertDescription>
          </Alert>

          <!-- Preview Summary -->
          <div v-if="previewResult.containers.length > 0" class="border rounded-lg p-4 space-y-3">
            <h3 class="font-semibold">
              {{ t('gear.import.previewTitle') }}
            </h3>

            <div class="space-y-2 text-sm">
              <div v-for="(container, idx) in previewResult.containers" :key="idx" class="border-l-2 pl-3">
                <div class="font-medium">
                  {{ container.name }} ({{ container.items.length }} {{ t('gear.import.items') }})
                </div>
                <ul class="text-xs text-muted-foreground mt-1 space-y-0.5">
                  <li v-for="(item, itemIdx) in container.items.slice(0, 5)" :key="itemIdx">
                    {{ item.name }}
                    <span v-if="item.brand" class="text-primary">{{ item.brand }}</span>
                    <span v-if="item.quantity > 1">x{{ item.quantity }}</span>
                  </li>
                  <li v-if="container.items.length > 5" class="italic">
                    {{ t('gear.import.andMore', { count: container.items.length - 5 }) }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" @click="handleClose">
          {{ t('gear.actions.cancel') }}
        </Button>
        <Button
          type="button"
          :disabled="!previewResult || previewResult.containers.length === 0 || importing"
          :loading="importing"
          @click="handleImport"
        >
          {{ t('gear.import.import') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
