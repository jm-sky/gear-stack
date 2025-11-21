<script setup lang="ts">
import { Edit, InfoIcon, Plus, Trash2 } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useGearSettings } from '@/modules/gear/composables/useGearSettings'
import type { IUserBrand } from '@/modules/gear/types/gearSettings.types'

const { t } = useI18n()
const { customBrands, addBrand, updateBrand, removeBrand } = useGearSettings()

const editingId = ref<string | null>(null)
const newBrandKey = ref('')
const newBrandLabel = ref('')

const isAdding = computed(() => editingId.value === null && (newBrandKey.value || newBrandLabel.value))

const handleAdd = () => {
  if (!newBrandKey.value.trim() || !newBrandLabel.value.trim()) {
    return
  }

  const now = new Date().toISOString()
  const brand: IUserBrand = {
    id: crypto.randomUUID(),
    key: newBrandKey.value.trim().toLowerCase().replace(/\s+/g, '_'),
    label: newBrandLabel.value.trim(),
    createdAt: now,
    updatedAt: now,
  }

  addBrand(brand)

  // Reset form
  newBrandKey.value = ''
  newBrandLabel.value = ''
}

const handleEdit = (brand: IUserBrand) => {
  editingId.value = brand.id
  newBrandKey.value = brand.key
  newBrandLabel.value = brand.label
}

const handleSave = (id: string) => {
  const brand = customBrands.value.find(b => b.id === id)
  if (!brand) return

  const updated: IUserBrand = {
    ...brand,
    key: newBrandKey.value.trim().toLowerCase().replace(/\s+/g, '_'),
    label: newBrandLabel.value.trim(),
    updatedAt: new Date().toISOString(),
  }

  updateBrand(updated)
  editingId.value = null
  newBrandKey.value = ''
  newBrandLabel.value = ''
}

const handleCancel = () => {
  editingId.value = null
  newBrandKey.value = ''
  newBrandLabel.value = ''
}

const handleDelete = (id: string) => {
  if (confirm(t('settings.brands.deleteConfirm'))) {
    removeBrand(id)
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ t('settings.brands.title') }}</CardTitle>
      <CardDescription>
        {{ t('settings.brands.description') }}
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
      <!-- Add New Brand Form -->
      <div class="border rounded-lg p-4 space-y-3">
        <h4 class="font-medium text-sm">
          {{ editingId ? t('settings.brands.edit') : t('settings.brands.add') }}
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Input
            v-model="newBrandKey"
            :placeholder="t('settings.brands.keyPlaceholder')"
            :disabled="!!editingId"
            @keydown.enter="handleAdd"
          />
          <Input
            v-model="newBrandLabel"
            :placeholder="t('settings.brands.labelPlaceholder')"
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
            {{ editingId ? t('settings.brands.save') : t('settings.brands.add') }}
          </Button>
          <Button
            v-if="editingId"
            size="sm"
            variant="outline"
            @click="handleCancel"
          >
            {{ t('settings.brands.cancel') }}
          </Button>
        </div>
      </div>

      <!-- Brands List -->
      <div v-if="customBrands.length > 0" class="space-y-2">
        <div
          v-for="brand in customBrands"
          :key="brand.id"
          class="flex flex-col sm:flex-row sm:items-center justify-between p-3 border rounded-lg gap-3"
        >
          <div class="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <div class="text-xs text-muted-foreground">
                {{ t('settings.brands.key') }}
              </div>
              <div class="font-mono text-sm">
                {{ brand.key }}
              </div>
            </div>
            <div>
              <div class="text-xs text-muted-foreground">
                {{ t('settings.brands.label') }}
              </div>
              <div class="text-sm">
                {{ brand.label }}
              </div>
            </div>
          </div>
          <div class="flex gap-2 sm:shrink-0">
            <Button
              size="sm"
              variant="outline"
              @click="handleEdit(brand)"
            >
              <Edit class="size-4" />
            </Button>
            <Button
              size="sm"
              variant="destructive"
              @click="handleDelete(brand.id)"
            >
              <Trash2 class="size-4" />
            </Button>
          </div>
        </div>
      </div>
      <div v-else class="flex items-center justify-center gap-2 text-sm py-8 text-muted-foreground">
        <InfoIcon class="size-4 inline" />
        {{ t('settings.brands.empty') }}
      </div>
    </CardContent>
  </Card>
</template>

