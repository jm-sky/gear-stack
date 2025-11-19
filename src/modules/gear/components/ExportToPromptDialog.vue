<script setup lang="ts">
import { Check, Copy, Info } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

const props = defineProps<{
  open: boolean
  markdown: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { t } = useI18n()
const copied = ref(false)
const copiedGuidelines = ref(false)

// Markdown template for AI guidelines
const guidelinesTemplate = `# Gear List Formatting Guidelines

When generating or updating gear lists, use this format:

## Standard Format
\`\`\`markdown
## [Container Name] [#container-id] [uuid:container-uuid] ([Container Type])
- **[Item Name]** [uuid:item-uuid] x[qty] ([Brand], [Color]) [#nested-id] ([Status]) <URL> - [weight]g
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

### UUID (Optional but recommended)
- Format: \`[uuid:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx]\`
- Appears after item name or after container ID in header
- Used for stable references when updating existing items/containers
- If UUID is present during import, the item/container will be updated instead of created
- If UUID is missing, a new item/container will be created

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
## Bug-Out Bag [#bug-out-bag] [uuid:abc-123] (Backpack)
- **Water Bottle** [uuid:item-1] x2 (Nalgene) - 300g
- **Emergency Food** [uuid:item-2] x5 (Expiration: 31.12.2025) - 1000g
- **Tactical Knife** [uuid:item-3] (Victorinox, Black) - 200g
- **Headlamp** [uuid:item-4] (Petzl, Red) - 90g
- **First Aid Pouch** [uuid:item-5] (Pouch) [#first-aid-pouch] - 350g
- **Fire Starter** [uuid:item-6] x2 - 50g

## First Aid Pouch [#first-aid-pouch] [uuid:def-456] (Pouch)
- **Bandages** [uuid:item-7] x5 - 100g
- **Pain Pills** [uuid:item-8] (Expiration: 31.12.2025) - 50g
- **Antiseptic** [uuid:item-9] - 100g
\`\`\`

## Nested Containers
When a container is inside another container:
1. Add item with container name and \`[#id]\` reference
2. Define the nested container separately with same \`[#id]\`
3. Parser will create the relationship automatically

Example:
\`\`\`markdown
## Main Backpack [#main] [uuid:main-123] (Backpack)
- **EDC Pouch** [uuid:edc-item-1] (Pouch) [#edc] - 500g
- **Water Bottle** [uuid:water-1] - 150g

## EDC Pouch [#edc] [uuid:edc-456] (Pouch)
- **Multi-tool** [uuid:tool-1] - 250g
- **Flashlight** [uuid:light-1] - 90g
\`\`\`

## Container Types
Backpack, Bag, Pouch, Box, Cabinet, Vehicle, Shelf, Drawer, Case, Trunk, Other

## Important Notes
1. **Only item name is required** (bold \`**text**\`)
2. Container headers must have \`[#id]\` for proper identification
3. **UUID support** - \`[uuid:...]\` enables update workflow:
   - If UUID exists in import: item/container will be **updated**
   - If UUID missing in import: new item/container will be **created**
   - Always include UUIDs when re-importing edited lists
4. Nested containers: item with \`[#id]\` + separate container definition
5. Weight should end with \`g\` or \`kg\` (if omitted, 100g default)
6. Quantity can be anywhere but typically after name
7. Parentheses order: (Brand, Color) then (Status/Expiration)
8. URL can be in angle brackets \`<url>\` or plain (http://, https://, www.)
9. All fields except item name are optional
10. Use metric units (grams/kilograms)
11. Parser is flexible and will guess missing fields
`

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(props.markdown)
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
    <DialogContent class="w-[95vw] max-w-6xl max-h-[90vh] flex flex-col">
      <DialogHeader>
        <DialogTitle>
          {{ t('gear.actions.exportToPrompt') }}
        </DialogTitle>
        <DialogDescription>
          {{ t('gear.actions.exportToPromptDescription', 'Skopiuj poniższą treść i wklej do ChatGPT lub innego AI') }}
        </DialogDescription>
      </DialogHeader>

      <div class="flex-1 overflow-auto">
        <pre class="whitespace-pre-wrap text-sm font-mono bg-muted p-4 rounded-md border overflow-x-auto">{{ markdown }}</pre>
      </div>

      <DialogFooter class="flex-col sm:flex-row gap-2">
        <Button variant="secondary" class="sm:mr-auto" @click="handleCopyGuidelines">
          <Info v-if="!copiedGuidelines" class="size-4" />
          <Check v-else class="size-4" />
          {{ copiedGuidelines ? t('common.copyToClipboard.copied') : t('gear.export.guidelines', 'Guidelines') }}
        </Button>
        <div class="flex gap-2">
          <Button variant="outline" @click="handleOpenChange(false)">
            {{ t('common.close') }}
          </Button>
          <Button @click="handleCopy">
            <Copy v-if="!copied" class="size-4" />
            <Check v-else class="size-4" />
            {{ copied ? t('common.copyToClipboard.copied') : t('common.copyToClipboard.copy') }}
          </Button>
        </div>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

