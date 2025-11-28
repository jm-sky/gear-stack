<!--
  AI Premium Feature Alert Component
  Shows a premium feature notice for non-premium users
-->
<script setup lang="ts">
import { Crown } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

const { t } = useI18n()

const props = defineProps<{
  title?: string
  description?: string
}>()
</script>

<template>
  <Alert variant="premium">
    <Crown />
    <AlertTitle>
      {{ props.title ?? t('ai.premium.title') }}
    </AlertTitle>
    <AlertDescription>
      {{ props.description ?? t('ai.premium.description') }}
    </AlertDescription>
  </Alert>
</template>
