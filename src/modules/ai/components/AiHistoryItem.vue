<script setup lang="ts">
import { Clock, MessageSquare, Trash2 } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { IAiHistoryItem } from '../types/history'
import AiCostDisplay from './AiCostDisplay.vue'

const { t } = useI18n()

const props = defineProps<{
  item: IAiHistoryItem
}>()

const emit = defineEmits<{
  restore: [item: IAiHistoryItem]
  delete: [id: string]
  viewDetails: [item: IAiHistoryItem]
}>()

const formattedDate = computed(() => {
  const date = new Date(props.item.created_at)
  return date.toLocaleString()
})

const preview = computed(() => {
  const prompt = props.item.finalPrompt
  if (prompt.length > 150) {
    return prompt.substring(0, 150) + '...'
  }
  return prompt || t('ai.history.noPreview')
})

const handleRestore = (): void => {
  emit('restore', props.item)
}

const handleDelete = (): void => {
  emit('delete', props.item.id)
}

const handleViewDetails = (): void => {
  emit('viewDetails', props.item)
}
</script>

<template>
  <Card class="hover:shadow-md transition-shadow">
    <CardHeader class="pb-3">
      <div class="flex items-start justify-between gap-2">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-2">
            <MessageSquare class="size-4 text-muted-foreground shrink-0" />
            <CardTitle class="text-base truncate">
              {{ item.model }}
            </CardTitle>
            <Badge variant="outline" class="text-xs">
              {{ item.operationType }}
            </Badge>
          </div>
          <CardDescription class="text-xs text-muted-foreground">
            <div class="flex items-center gap-2 flex-wrap">
              <span>{{ item.provider }}</span>
              <span v-if="item.durationMs" class="flex items-center gap-1">
                <Clock class="size-3" />
                {{ item.durationMs }}ms
              </span>
            </div>
          </CardDescription>
        </div>
      </div>
    </CardHeader>

    <CardContent class="pt-0 space-y-3">
      <!-- Preview -->
      <div class="text-sm text-muted-foreground line-clamp-2">
        {{ preview }}
      </div>

      <!-- Cost and Tokens -->
      <AiCostDisplay
        :tokens="item.tokens"
        :cost="item.cost"
        class="text-xs"
      />

      <!-- Actions -->
      <div class="flex items-center justify-between gap-2 pt-2 border-t">
        <div class="text-xs text-muted-foreground">
          {{ formattedDate }}
        </div>
        <div class="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            @click="handleViewDetails"
          >
            {{ t('ai.history.details') }}
          </Button>
          <Button
            variant="outline"
            size="sm"
            @click="handleRestore"
          >
            {{ t('ai.history.restore') }}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            @click="handleDelete"
          >
            <Trash2 class="size-4" />
          </Button>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

