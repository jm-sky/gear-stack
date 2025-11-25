<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import ButtonGroup from '../ui/button-group/ButtonGroup.vue'
import Button from '../ui/button/Button.vue'

const { t } = useI18n()

const filterType = defineModel<string>('filterType', { default: 'all' })
</script>

<template>
  <ButtonGroup>
    <Button
      :variant="filterType === 'all' ? 'default' : 'outline'"
      @click="filterType = 'all'"
    >
      {{ t('gear.allItems.filter.all', 'All') }}
    </Button>
    <Button
      :variant="filterType === 'containers' ? 'default' : 'outline'"
      @click="filterType = 'containers'"
    >
      {{ t('gear.allItems.filter.containers', 'Containers') }}
    </Button>
    <Button
      :variant="filterType === 'items' ? 'default' : 'outline'"
      @click="filterType = 'items'"
    >
      {{ t('gear.allItems.filter.items', 'Items') }}
    </Button>
  </ButtonGroup>
</template>
