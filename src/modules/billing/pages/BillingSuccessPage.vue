<script setup lang="ts">
import { CheckCircle } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useSubscription } from '../composables/useSubscription'
import { BillingRoutePaths } from '../routes'

const { t } = useI18n()
const router = useRouter()
const { refetchSubscription } = useSubscription()

const handleContinue = async () => {
  await refetchSubscription()
  router.push(BillingRoutePaths.billing)
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full">
      <div class="flex min-h-[60vh] items-center justify-center">
        <Card class="w-full max-w-md">
          <CardHeader class="text-center">
            <div class="mx-auto mb-4 flex size-16 items-center justify-center rounded-full bg-green-100">
              <CheckCircle class="size-10 text-green-600" />
            </div>
            <CardTitle class="text-2xl">
              {{ t('billing.success.title') }}
            </CardTitle>
            <CardDescription>
              {{ t('billing.success.description') }}
            </CardDescription>
          </CardHeader>

          <CardContent class="text-center text-sm text-muted-foreground">
            <p>
              {{ t('billing.success.message') }}
            </p>
          </CardContent>

          <CardFooter class="flex justify-center">
            <Button @click="handleContinue">
              {{ t('billing.success.continue') }}
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
