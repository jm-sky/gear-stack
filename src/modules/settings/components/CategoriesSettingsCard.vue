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
const newCategoryValue = ref('')

const isAdding = computed(() => editingId.value === null && !!newCategoryValue.value.trim())

const handleAdd = () => {
  if (!newCategoryValue.value.trim()) {
    return
  }

  const now = new Date().toISOString()
  const category: IUserCategory = {
    id: crypto.randomUUID(),
    value: newCategoryValue.value.trim(),
    createdAt: now,
    updatedAt: now,
  }

  addCategory(category)

  // Reset form
  newCategoryValue.value = ''
}

const handleEdit = (category: IUserCategory) => {
  editingId.value = category.id
  newCategoryValue.value = category.value
}

const handleSave = (id: string) => {
  const category = customCategories.value.find(c => c.id === id)
  if (!category) return

  const updated: IUserCategory = {
    ...category,
    value: newCategoryValue.value.trim(),
    updatedAt: new Date().toISOString(),
  }

  updateCategory(updated)
  editingId.value = null
  newCategoryValue.value = ''
}

const handleCancel = () => {
  editingId.value = null
  newCategoryValue.value = ''
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
        <Input
          v-model="newCategoryValue"
          :placeholder="t('settings.categories.valuePlaceholder')"
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
          <div class="flex-1">
            <div class="text-sm">
              {{ category.value }}
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

