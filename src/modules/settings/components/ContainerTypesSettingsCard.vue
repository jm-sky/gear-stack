<script setup lang="ts">
import { Edit, InfoIcon, Plus, Trash2 } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useGearSettings } from '@/modules/gear/composables/useGearSettings'
import type { IUserContainerType } from '@/modules/gear/types/gearSettings.types'

const { t } = useI18n()
const { customContainerTypes, addContainerType, updateContainerType, removeContainerType } = useGearSettings()

const editingId = ref<string | null>(null)
const newTypeKey = ref('')
const newTypeLabel = ref('')

const isAdding = computed(() => editingId.value === null && (newTypeKey.value || newTypeLabel.value))

const handleAdd = () => {
  if (!newTypeKey.value.trim() || !newTypeLabel.value.trim()) {
    return
  }

  const now = new Date().toISOString()
  const containerType: IUserContainerType = {
    id: crypto.randomUUID(),
    key: newTypeKey.value.trim().toLowerCase().replace(/\s+/g, '_'),
    label: newTypeLabel.value.trim(),
    createdAt: now,
    updatedAt: now,
  }

  addContainerType(containerType)

  // Reset form
  newTypeKey.value = ''
  newTypeLabel.value = ''
}

const handleEdit = (containerType: IUserContainerType) => {
  editingId.value = containerType.id
  newTypeKey.value = containerType.key
  newTypeLabel.value = containerType.label
}

const handleSave = (id: string) => {
  const containerType = customContainerTypes.value.find(t => t.id === id)
  if (!containerType) return

  const updated: IUserContainerType = {
    ...containerType,
    key: newTypeKey.value.trim().toLowerCase().replace(/\s+/g, '_'),
    label: newTypeLabel.value.trim(),
    updatedAt: new Date().toISOString(),
  }

  updateContainerType(updated)
  editingId.value = null
  newTypeKey.value = ''
  newTypeLabel.value = ''
}

const handleCancel = () => {
  editingId.value = null
  newTypeKey.value = ''
  newTypeLabel.value = ''
}

const handleDelete = (id: string) => {
  if (confirm(t('settings.containerTypes.deleteConfirm'))) {
    removeContainerType(id)
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ t('settings.containerTypes.title') }}</CardTitle>
      <CardDescription>
        {{ t('settings.containerTypes.description') }}
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
      <!-- Add New Container Type Form -->
      <div class="border rounded-lg p-4 space-y-3">
        <h4 class="font-medium text-sm">
          {{ editingId ? t('settings.containerTypes.edit') : t('settings.containerTypes.add') }}
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Input
            v-model="newTypeKey"
            :placeholder="t('settings.containerTypes.keyPlaceholder')"
            :disabled="!!editingId"
            @keydown.enter="handleAdd"
          />
          <Input
            v-model="newTypeLabel"
            :placeholder="t('settings.containerTypes.labelPlaceholder')"
            @keydown.enter="handleAdd"
          />
        </div>
        <div class="flex gap-2">
          <Button
            v-if="isAdding"
            size="sm"
            @click="editingId ? handleSave(editingId) : handleAdd"
          >
            <Plus v-if="!editingId" class="size-4" />
            <Edit v-else class="size-4" />
            {{ editingId ? t('settings.containerTypes.save') : t('settings.containerTypes.add') }}
          </Button>
          <Button
            v-if="editingId"
            size="sm"
            variant="outline"
            @click="handleCancel"
          >
            {{ t('settings.containerTypes.cancel') }}
          </Button>
        </div>
      </div>

      <!-- Container Types List -->
      <div v-if="customContainerTypes.length > 0" class="space-y-2">
        <div
          v-for="containerType in customContainerTypes"
          :key="containerType.id"
          class="flex flex-col sm:flex-row sm:items-center justify-between p-3 border rounded-lg gap-3"
        >
          <div class="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <div class="text-xs text-muted-foreground">
                {{ t('settings.containerTypes.key') }}
              </div>
              <div class="font-mono text-sm">
                {{ containerType.key }}
              </div>
            </div>
            <div>
              <div class="text-xs text-muted-foreground">
                {{ t('settings.containerTypes.label') }}
              </div>
              <div class="text-sm">
                {{ containerType.label }}
              </div>
            </div>
          </div>
          <div class="flex gap-2 sm:shrink-0">
            <Button
              size="sm"
              variant="outline"
              @click="handleEdit(containerType)"
            >
              <Edit class="size-4" />
            </Button>
            <Button
              size="sm"
              variant="destructive"
              @click="handleDelete(containerType.id)"
            >
              <Trash2 class="size-4" />
            </Button>
          </div>
        </div>
      </div>
      <div v-else class="flex items-center justify-center gap-2 text-sm py-8 text-muted-foreground">
        <InfoIcon class="size-4 inline" />
        {{ t('settings.containerTypes.empty') }}
      </div>
    </CardContent>
  </Card>
</template>

