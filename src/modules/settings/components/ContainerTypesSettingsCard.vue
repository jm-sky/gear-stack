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
const newTypeValue = ref('')

const isAdding = computed(() => editingId.value === null && !!newTypeValue.value.trim())

const handleAdd = () => {
  if (!newTypeValue.value.trim()) {
    return
  }

  const now = new Date().toISOString()
  const containerType: IUserContainerType = {
    id: crypto.randomUUID(),
    value: newTypeValue.value.trim(),
    createdAt: now,
    updatedAt: now,
  }

  addContainerType(containerType)

  // Reset form
  newTypeValue.value = ''
}

const handleEdit = (containerType: IUserContainerType) => {
  editingId.value = containerType.id
  newTypeValue.value = containerType.value
}

const handleSave = (id: string) => {
  const containerType = customContainerTypes.value.find(t => t.id === id)
  if (!containerType) return

  const updated: IUserContainerType = {
    ...containerType,
    value: newTypeValue.value.trim(),
    updatedAt: new Date().toISOString(),
  }

  updateContainerType(updated)
  editingId.value = null
  newTypeValue.value = ''
}

const handleCancel = () => {
  editingId.value = null
  newTypeValue.value = ''
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
        <Input
          v-model="newTypeValue"
          :placeholder="t('settings.containerTypes.valuePlaceholder')"
          @keydown.enter="handleAdd"
        />
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
          <div class="flex-1">
            <div class="text-sm">
              {{ containerType.value }}
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

