<script setup lang="ts">
import { AlertCircle, Check, FileText, Info } from 'lucide-vue-next'
import { computed, ref } from 'vue'
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
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import type { IGearContainer } from '../types/gear.types'
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
const { createContainer, updateContainer, createItem, updateItem, getContainerById } = useGear()

const markdownContent = ref('')
const importing = ref(false)
const importMode = ref<'create' | 'update'>('update') // Default to update mode
const previewResult = ref<ReturnType<typeof markdownImportService.parseMarkdown> | null>(null)
const copiedGuidelines = ref(false)

// Markdown template for AI guidelines
const guidelinesTemplate = `# Gear List Formatting Guidelines

When generating or updating gear lists, use this format:

## Standard Format
\`\`\`markdown
## [Container Name] [#container-id] ([Container Type])
- **[Item Name]** x[qty] ([Brand], [Color]) [#nested-id] ([Status]) <URL> - [weight]g
\`\`\`

## Format Rules

### Item Name (Required)
- **Bold formatting** using \`**Item Name**\`
- Always at the start of the line after \`- \`

### Quantity (Optional)
- Format: \`x[number]\` (e.g., x2, x10, x100)
- Can appear anywhere before weight, but typically after item name
- If omitted, quantity = 1

### Brand and Color (Optional)
- First parentheses: \`([Brand], [Color])\`
- Brand comes first, color second
- Both are optional, can have just brand or just color
- Examples: \`(Victorinox)\`, \`(Red)\`, \`(Petzl, Black)\`

### Status (Optional)
- Second parentheses for status or expiration
- Status values: \`Missing\`, \`To Buy\` (omit if Owned)
- Expiration: \`Expiration: DD.MM.YYYY\`
- Can combine: \`(Missing, Expiration: 31.12.2025)\`

### Container ID (Required for containers)
- Format: \`[#slug-id]\` in header and nested item reference
- ID is generated from container name as slug
- Examples: \`Bug-Out Bag\` → \`[#bug-out-bag]\`, \`EDC Pouch\` → \`[#edc-pouch]\`
- If item references container \`[#id]\`, it creates nested relationship

### URL (Optional)
- Format: \`<URL>\` in angle brackets or plain URL
- Recognized by \`http://\`, \`https://\`, or \`www.\`
- Examples: \`<https://example.com>\`, \`https://example.com\`, \`www.example.com\`
- Automatically adds \`https://\` to \`www.\` links

### Weight (Optional)
- Format: \`- [number]g\` or \`- [number]kg\`
- Always at the end after a dash
- Examples: \`- 150g\`, \`- 2.5kg\`, \`- 1200g\`
- If omitted, default weight will be assigned (100g)

## Examples

### Minimal Format
\`\`\`markdown
- **Flashlight** - 150g
- **Rope** - 500g
\`\`\`

### With Quantity
\`\`\`markdown
- **AA Battery** x4 - 96g
- **Energy Bar** x10 - 400g
\`\`\`

### With Brand and Color
\`\`\`markdown
- **Tactical Knife** (Victorinox, Black) - 200g
- **Headlamp** (Petzl, Red) - 90g
- **Water Bottle** (Nalgene) - 150g
\`\`\`

### With Status
\`\`\`markdown
- **First Aid Kit** (Missing) - 500g
- **Water Filter** (To Buy) - 200g
- **Compass** (Suunto) (Missing) - 45g
\`\`\`

### With Expiration
\`\`\`markdown
- **Emergency Food** (Expiration: 31.12.2025) - 400g
- **Water Purification Tablets** (Katadyn) (Expiration: 15.06.2026) - 50g
\`\`\`

### With URL
\`\`\`markdown
- **Tactical Knife** (Victorinox) <https://example.com/knife> - 200g
- **Headlamp** (Petzl) www.petzl.com/headlamp - 90g
- **Water Filter** <https://store.com/filter> (To Buy) - 200g
\`\`\`

### Complete Examples
\`\`\`markdown
- **Headlamp** x2 (Petzl, Red) <https://petzl.com> - 180g
- **Multi-tool** (Leatherman, Silver) (Missing) - 250g
- **Emergency Blanket** x3 (Mylar) <www.example.com> - 180g
\`\`\`

## Container Example
\`\`\`markdown
## Bug-Out Bag [#bug-out-bag] (Backpack)
- **Water Bottle** x2 (Nalgene) - 300g
- **Emergency Food** x5 (Expiration: 31.12.2025) - 1000g
- **Tactical Knife** (Victorinox, Black) - 200g
- **Headlamp** (Petzl, Red) - 90g
- **First Aid Pouch** (Pouch) [#first-aid-pouch] - 350g
- **Fire Starter** x2 - 50g

## First Aid Pouch [#first-aid-pouch] (Pouch)
- **Bandages** x5 - 100g
- **Pain Pills** (Expiration: 31.12.2025) - 50g
- **Antiseptic** - 100g
\`\`\`

## Nested Containers
When a container is inside another container:
1. Add item with container name and \`[#id]\` reference
2. Define the nested container separately with same \`[#id]\`
3. Parser will create the relationship automatically

Example:
\`\`\`markdown
## Main Backpack [#main] (Backpack)
- **EDC Pouch** (Pouch) [#edc] - 500g
- **Water Bottle** - 150g

## EDC Pouch [#edc] (Pouch)
- **Multi-tool** - 250g
- **Flashlight** - 90g
\`\`\`

## Container Types
Backpack, Bag, Pouch, Box, Cabinet, Vehicle, Shelf, Drawer, Case, Trunk, Other

## Important Notes
1. **Only item name is required** (bold \`**text**\`)
2. Container headers must have \`[#id]\` for proper identification
3. Nested containers: item with \`[#id]\` + separate container definition
4. Weight should end with \`g\` or \`kg\` (if omitted, 100g default)
5. Quantity can be anywhere but typically after name
6. Parentheses order: (Brand, Color) then (Status/Expiration)
7. URL can be in angle brackets \`<url>\` or plain (http://, https://, www.)
8. All fields except item name are optional
9. Use metric units (grams/kilograms)
10. Parser is flexible and will guess missing fields
`

// Check if any containers/items have UUIDs
const hasUuids = computed(() => {
  if (!previewResult.value) return false
  return previewResult.value.containers.some(c => c.uuid || c.items.some(i => i.uuid))
})

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

const handleImport = async () => {
  if (!previewResult.value || previewResult.value.containers.length === 0) {
    toast.error(t('gear.import.noPreview'))
    return
  }

  importing.value = true

  try {
    let importedCount = 0
    let updatedCount = 0
    let itemCount = 0
    let itemUpdatedCount = 0

    // Map to store container slug/id -> container UUID for nested container resolution
    const containerIdMap = new Map<string, string>()

    // Phase 1: Create/update all containers first
    const createdContainers: Array<{ containerData: typeof previewResult.value.containers[0]; container: IGearContainer }> = []

    for (const containerData of previewResult.value.containers) {
      let container

      // Check if we should update existing container (has UUID and mode is update)
      if (importMode.value === 'update' && containerData.uuid) {
        const existing = getContainerById(containerData.uuid)
        if (existing) {
          // Update existing container
          container = updateContainer(existing.id, {
            name: containerData.name,
            // Keep existing type and other fields
          })
          updatedCount++
        } else {
          // UUID provided but container not found - create new with same UUID
          container = createContainer({
            name: containerData.name,
            type: 'other',
            description: t('gear.import.importedDescription'),
          })
          // Note: We can't override the auto-generated UUID in createContainer
          // This is a limitation - we'd need to modify the service to accept UUID
          importedCount++
        }
      } else {
        // Create new container
        container = createContainer({
          name: containerData.name,
          type: 'other',
          description: t('gear.import.importedDescription'),
        })
        importedCount++
      }

      // Store mapping: slug/id -> container UUID
      if (containerData.id) {
        containerIdMap.set(containerData.id, container.id)
      }
      // Also map UUID if available (for update mode)
      if (containerData.uuid) {
        containerIdMap.set(containerData.uuid, container.id)
      }

      createdContainers.push({ containerData, container })
    }

    // Phase 2: Create/update items with nested container resolution
    for (const { containerData, container } of createdContainers) {
      // Import/update items
      for (const itemData of containerData.items) {
        // Extract nestedContainerId before destructuring
        const { uuid: itemUuid, nestedContainerId, ...itemDto } = itemData

        // Resolve nestedContainerId (slug) to actual container UUID
        if (nestedContainerId) {
          const nestedContainerUuid = containerIdMap.get(nestedContainerId)
          if (nestedContainerUuid) {
            itemDto.containerId = nestedContainerUuid
          } else {
            console.warn(`Nested container with id "${nestedContainerId}" not found`)
          }
        }

        if (importMode.value === 'update' && itemUuid) {
          // Try to find existing item by UUID
          const existingItem = container.items.find(i => i.id === itemUuid)
          if (existingItem) {
            // Update existing item
            updateItem(container.id, existingItem.id, itemDto)
            itemUpdatedCount++
          } else {
            // UUID provided but item not found - create new
            createItem(container.id, itemDto)
            itemCount++
          }
        } else {
          // Create new item
          createItem(container.id, itemDto)
          itemCount++
        }
      }
    }

    const message = importMode.value === 'update'
      ? t('gear.import.successWithUpdates', {
          created: importedCount,
          updated: updatedCount,
          items: itemCount,
          itemsUpdated: itemUpdatedCount,
        })
      : t('gear.import.success', {
          containers: importedCount,
          items: itemCount,
        })

    toast.success(message)

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
    <DialogContent class="w-[95vw] max-w-4xl max-h-[90vh] flex flex-col">
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

        <!-- Import Mode Selection (shown only when UUIDs detected) -->
        <div v-if="hasUuids && previewResult" class="border rounded-lg p-4 space-y-3">
          <Label class="text-sm font-medium">{{ t('gear.import.mode') }}</Label>
          <RadioGroup v-model="importMode" class="gap-3">
            <div class="flex items-center space-x-2">
              <RadioGroupItem id="mode-update" value="update" />
              <Label for="mode-update" class="font-normal cursor-pointer">
                {{ t('gear.import.modeUpdate') }}
                <span class="text-xs text-muted-foreground block">
                  {{ t('gear.import.modeUpdateDesc') }}
                </span>
              </Label>
            </div>
            <div class="flex items-center space-x-2">
              <RadioGroupItem id="mode-create" value="create" />
              <Label for="mode-create" class="font-normal cursor-pointer">
                {{ t('gear.import.modeCreate') }}
                <span class="text-xs text-muted-foreground block">
                  {{ t('gear.import.modeCreateDesc') }}
                </span>
              </Label>
            </div>
          </RadioGroup>
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

      <DialogFooter class="flex-col sm:flex-row gap-2">
        <Button variant="secondary" class="sm:mr-auto" @click="handleCopyGuidelines">
          <Info v-if="!copiedGuidelines" class="size-4" />
          <Check v-else class="size-4" />
          {{ copiedGuidelines ? t('common.copyToClipboard.copied') : t('gear.export.guidelines', 'Guidelines') }}
        </Button>
        <div class="flex gap-2">
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
        </div>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
