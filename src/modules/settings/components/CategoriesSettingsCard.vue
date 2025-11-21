<script setup lang="ts">
import { Edit, InfoIcon, Plus, Trash2 } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useGearSettings } from '@/modules/gear/composables/useGearSettings'
import type { IUserCategory } from '@/modules/gear/types/gearSettings.types'

const { t } = useI18n()
const { customCategories, addCategory, updateCategory, removeCategory } = useGearSettings()

const editingId = ref<string | null>(null)
const newCategoryKey = ref('')
const newCategoryLabel = ref('')

const isAdding = computed(() => editingId.value === null && (newCategoryKey.value || newCategoryLabel.value))

const handleAdd = () => {
  if (!newCategoryKey.value.trim() || !newCategoryLabel.value.trim()) {
    return
  }

  const now = new Date().toISOString()
  const category: IUserCategory = {
    id: crypto.randomUUID(),
    key: newCategoryKey.value.trim().toLowerCase().replace(/\s+/g, '_'),
    label: newCategoryLabel.value.trim(),
    createdAt: now,
    updatedAt: now,
  }

  addCategory(category)

  // Reset form
  newCategoryKey.value = ''
  newCategoryLabel.value = ''
}

const handleEdit = (category: IUserCategory) => {
  editingId.value = category.id
  newCategoryKey.value = category.key
  newCategoryLabel.value = category.label
}

const handleSave = (id: string) => {
  const category = customCategories.value.find(c => c.id === id)
  if (!category) return

  const updated: IUserCategory = {
    ...category,
    key: newCategoryKey.value.trim().toLowerCase().replace(/\s+/g, '_'),
    label: newCategoryLabel.value.trim(),
    updatedAt: new Date().toISOString(),
  }

  updateCategory(updated)
  editingId.value = null
  newCategoryKey.value = ''
  newCategoryLabel.value = ''
}

const handleCancel = () => {
  editingId.value = null
  newCategoryKey.value = ''
  newCategoryLabel.value = ''
}

const handleDelete = (id: string) => {
  if (confirm(t('settings.categories.deleteConfirm'))) {
    removeCategory(id)
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ t('settings.categories.title') }}</CardTitle>
      <CardDescription>
        {{ t('settings.categories.description') }}
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
      <!-- Add New Category Form -->
      <div class="border rounded-lg p-4 space-y-3">
        <h4 class="font-medium text-sm">
          {{ editingId ? t('settings.categories.edit') : t('settings.categories.add') }}
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Input
            v-model="newCategoryKey"
            :placeholder="t('settings.categories.keyPlaceholder')"
            :disabled="!!editingId"
            @keydown.enter="handleAdd"
          />
          <Input
            v-model="newCategoryLabel"
            :placeholder="t('settings.categories.labelPlaceholder')"
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
            {{ editingId ? t('settings.categories.save') : t('settings.categories.add') }}
          </Button>
          <Button
            v-if="editingId"
            size="sm"
            variant="outline"
            @click="handleCancel"
          >
            {{ t('settings.categories.cancel') }}
          </Button>
        </div>
      </div>

      <!-- Categories List -->
      <div v-if="customCategories.length > 0" class="space-y-2">
        <div
          v-for="category in customCategories"
          :key="category.id"
          class="flex flex-col sm:flex-row sm:items-center justify-between p-3 border rounded-lg gap-3"
        >
          <div class="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <div class="text-xs text-muted-foreground">
                {{ t('settings.categories.key') }}
              </div>
              <div class="font-mono text-sm">
                {{ category.key }}
              </div>
            </div>
            <div>
              <div class="text-xs text-muted-foreground">
                {{ t('settings.categories.label') }}
              </div>
              <div class="text-sm">
                {{ category.label }}
              </div>
            </div>
          </div>
          <div class="flex gap-2 sm:shrink-0">
            <Button
              size="sm"
              variant="outline"
              @click="handleEdit(category)"
            >
              <Edit class="size-4" />
            </Button>
            <Button
              size="sm"
              variant="destructive"
              @click="handleDelete(category.id)"
            >
              <Trash2 class="size-4" />
            </Button>
          </div>
        </div>
      </div>
      <div v-else class="flex items-center justify-center gap-2 text-sm py-8 text-muted-foreground">
        <InfoIcon class="size-4 inline" />
        {{ t('settings.categories.empty') }}
      </div>
    </CardContent>
  </Card>
</template>

