<script setup lang="ts">
import { Search } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const { t } = useI18n()

// Define models using defineModel
const searchQuery = defineModel<string>('searchQuery', { default: '' })
const showOnlyRootContainers = defineModel<boolean>('showOnlyRootContainers', { default: false })
</script>

<template>
  <div class="space-y-4">
    <div class="relative">
      <Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        v-model="searchQuery"
        :placeholder="$t('gear.filters.searchContainers')"
        class="pl-9"
      />
    </div>
    <div class="flex items-center gap-2">
      <Checkbox
        id="root-containers-filter"
        v-model="showOnlyRootContainers"
      />
      <Label
        for="root-containers-filter"
        class="text-sm text-muted-foreground cursor-pointer"
      >
        {{ t('gear.container.showOnlyRootContainers') }}
      </Label>
    </div>
  </div>
</template>

