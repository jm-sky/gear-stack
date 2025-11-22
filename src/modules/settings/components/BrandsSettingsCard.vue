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
const newBrandValue = ref('')

const isAdding = computed(() => editingId.value === null && !!newBrandValue.value.trim())

const handleAdd = () => {
  if (!newBrandValue.value.trim()) {
    return
  }

  const now = new Date().toISOString()
  const brand: IUserBrand = {
    id: crypto.randomUUID(),
    value: newBrandValue.value.trim(),
    createdAt: now,
    updatedAt: now,
  }

  addBrand(brand)

  // Reset form
  newBrandValue.value = ''
}

const handleEdit = (brand: IUserBrand) => {
  editingId.value = brand.id
  newBrandValue.value = brand.value
}

const handleSave = (id: string) => {
  const brand = customBrands.value.find(b => b.id === id)
  if (!brand) return

  const updated: IUserBrand = {
    ...brand,
    value: newBrandValue.value.trim(),
    updatedAt: new Date().toISOString(),
  }

  updateBrand(updated)
  editingId.value = null
  newBrandValue.value = ''
}

const handleCancel = () => {
  editingId.value = null
  newBrandValue.value = ''
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
        <Input
          v-model="newBrandValue"
          :placeholder="t('settings.brands.valuePlaceholder')"
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
          <div class="flex-1">
            <div class="text-sm">
              {{ brand.value }}
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


