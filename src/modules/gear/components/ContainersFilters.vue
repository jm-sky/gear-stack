<script setup lang="ts">
import { RefreshCcw, Search } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const { t } = useI18n()

defineProps<{
  loading?: boolean
  rootContainersFilter?: boolean
}>()

// Define models using defineModel
const searchQuery = defineModel<string>('searchQuery', { default: '' })
const showOnlyRootContainers = defineModel<boolean>('showOnlyRootContainers', { default: false })

const emit = defineEmits<{
  refresh: []
}>()
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-row items-center gap-2">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          v-model="searchQuery"
          :placeholder="$t('gear.filters.searchContainers')"
          class="pl-9"
        />
      </div>
      <Button
        variant="ghost"
        size="sm"
        :loading
        @click="emit('refresh')"
      >
        <RefreshCcw v-if="!loading" class="size-4" />
      </Button>
    </div>
    <div v-if="rootContainersFilter" class="flex items-center gap-2">
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

