<script setup lang="ts">
import { FileInput, MoreVertical, Plus, Sparkles, Trash2 } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useGear } from '../composables/useGear'

const router = useRouter()
const { t } = useI18n()
const { containers, deleteAllContainers } = useGear()

const emit = defineEmits<{
  exportAllToPrompt: [],
  import: [],
}>()

const handleCreate = () => {
  router.push('/gear/new')
}

const handleImport = () => {
  emit('import')
}

const handleDeleteAll = () => {
  if (confirm(t('gear.container.deleteAllConfirm'))) {
    try {
      deleteAllContainers()
      toast.success(t('gear.container.deleteAllSuccess'))
    } catch {
      toast.error(t('common.error'))
    }
  }
}

const handleExportAllToPrompt = () => {
  emit('exportAllToPrompt')
}
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button
        variant="outline"
        class="sm:shrink-0"
        :aria-label="$t('gear.actions.moreActions')"
      >
        <MoreVertical class="size-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <DropdownMenuItem @click="handleCreate">
        <Plus class="size-4 mr-2" />
        {{ t('gear.container.create.new') }}
      </DropdownMenuItem>
      <DropdownMenuItem @click="handleImport">
        <FileInput class="size-4 mr-2" />
        {{ t('gear.import.fromMarkdown') }}
      </DropdownMenuItem>
      <DropdownMenuSeparator v-if="containers.length > 0" />
      <DropdownMenuItem
        v-if="containers.length > 0"
        @click="handleExportAllToPrompt"
      >
        <Sparkles class="size-4 mr-2" />
        {{ t('gear.export.allToPrompt') }}
      </DropdownMenuItem>
      <DropdownMenuSeparator v-if="containers.length > 0" />
      <DropdownMenuItem
        v-if="containers.length > 0"
        class="text-destructive focus:text-destructive"
        @click="handleDeleteAll"
      >
        <Trash2 class="size-4 mr-2" />
        {{ t('gear.container.deleteAll') }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

