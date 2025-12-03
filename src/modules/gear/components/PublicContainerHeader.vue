<script setup lang="ts">
import { ArrowLeft, CalendarPlus } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { smallDateTime } from '@/shared/utils/smallDateTime'
import type { IGearContainer } from '../types/gear.types'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { GearRoutePath } from '../routes'
import { getActionIcon } from '../utils/actionIcons'
import MarkdownRenderer from './MarkdownRenderer.vue'
import PublicContainerAuthorBadge from './PublicContainerAuthorBadge.vue'

const props = defineProps<{
  container: IGearContainer
  backPath?: string
}>()

const emit = defineEmits<{
  back: []
}>()

const router = useRouter()
const { t } = useI18n()
const { user, isAuthenticated } = useAuth()
const { typeLabel } = useContainerTypeLabel(computed(() => props.container.type))

const EditIcon = getActionIcon('edit')

// Check if current user is the author
const isAuthor = computed(() => {
  if (!isAuthenticated.value || !user.value || !props.container.authorId) {
    return false
  }
  return props.container.authorId === user.value.id
})

const handleBack = () => {
  if (props.backPath) {
    router.push(props.backPath)
  } else {
    emit('back')
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-3">
      <Button variant="ghost" size="sm" @click="handleBack">
        <ArrowLeft class="size-4" />
        {{ t('common.back') }}
      </Button>
      <ButtonLink
        v-if="isAuthor"
        :to="GearRoutePath.ContainerEditById(container.id)"
        variant="outline"
        size="sm"
      >
        <EditIcon class="size-4" />
        <span class="hidden sm:inline">{{ t('gear.actions.edit') }}</span>
      </ButtonLink>
    </div>

    <div>
      <h1 class="text-2xl sm:text-3xl font-bold mb-2 wrap-break-word">
        {{ container.name }}
      </h1>
      <div v-if="container.description" class="text-muted-foreground mb-3">
        <MarkdownRenderer
          :content="container.description"
          class="text-sm sm:text-base"
        />
      </div>
      <div class="flex items-center gap-2 flex-wrap">
        <Badge variant="outline">
          {{ typeLabel }}
        </Badge>
        <PublicContainerAuthorBadge
          v-if="container.authorName && container.authorId && isAuthenticated"
          :author-name="container.authorName"
          :author-id="container.authorId"
          as-link
        />
        <PublicContainerAuthorBadge
          v-else-if="container.authorName && !isAuthenticated"
          :author-name="container.authorName"
        />
        <Badge variant="secondary" class="text-xs">
          <CalendarPlus class="size-3" />
          {{ smallDateTime(container.createdAt) }}
        </Badge>
      </div>
    </div>
  </div>
</template>
