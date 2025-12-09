<script setup lang="ts">
import { X } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import SearchInput from '@/components/ui/input/SearchInput.vue'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import type { AiOperationType } from '../types/chat'

const { t } = useI18n()

const searchQuery = defineModel<string>('searchQuery', { default: '' })
const operationType = defineModel<AiOperationType | null>('operationType', { default: null })

const emit = defineEmits<{
  clearFilters: []
}>()

const operationTypes: AiOperationType[] = ['chat', 'classify', 'analyze', 'generate']

const hasActiveFilters = computed(() => {
  return searchQuery.value !== '' || operationType.value !== null
})

const handleClearFilters = (): void => {
  searchQuery.value = ''
  operationType.value = null
  emit('clearFilters')
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <!-- Search Filter -->
      <div class="space-y-1.5">
        <Label for="history-search" class="text-xs text-muted-foreground">
          {{ t('ai.history.filters.search') }}
        </Label>
        <SearchInput
          id="history-search"
          v-model="searchQuery"
          name="history-search"
          :placeholder="t('ai.history.filters.search')"
        />
      </div>

      <!-- Operation Type Filter -->
      <div class="space-y-1.5">
        <Label for="operation-type-filter" class="text-xs text-muted-foreground">
          {{ t('ai.history.filters.operationType') }}
        </Label>
        <Select v-model="operationType">
          <SelectTrigger id="operation-type-filter">
            <SelectValue :placeholder="t('ai.history.filters.all')" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem :value="null">
              {{ t('ai.history.filters.all') }}
            </SelectItem>
            <SelectItem v-for="type in operationTypes" :key="type" :value="type">
              {{ type }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>

    <!-- Clear Filters Button -->
    <div v-if="hasActiveFilters" class="flex justify-end">
      <Button variant="outline" size="sm" @click="handleClearFilters">
        <X class="size-4" />
        {{ t('gear.catalogue.clearFilters') }}
      </Button>
    </div>
  </div>
</template>

