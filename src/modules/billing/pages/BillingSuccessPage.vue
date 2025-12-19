<script setup lang="ts">
import { CheckCircle } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { useSubscription } from '../composables/useSubscription'

const router = useRouter()
const { refetchSubscription } = useSubscription()

const handleContinue = async () => {
  await refetchSubscription()
  router.push('/billing')
}
</script>

<template>
  <div class="container mx-auto flex min-h-[60vh] items-center justify-center py-8">
    <Card class="w-full max-w-md">
      <CardHeader class="text-center">
        <div class="mx-auto mb-4 flex size-16 items-center justify-center rounded-full bg-green-100">
          <CheckCircle class="size-10 text-green-600" />
        </div>
        <CardTitle class="text-2xl">
          Subscription Activated!
        </CardTitle>
        <CardDescription>
          Your payment was successful and your subscription is now active.
        </CardDescription>
      </CardHeader>

      <CardContent class="text-center text-sm text-muted-foreground">
        <p>
          You now have access to all premium features. Thank you for your purchase!
        </p>
      </CardContent>

      <CardFooter class="flex justify-center">
        <Button @click="handleContinue">
          Continue to Billing
        </Button>
      </CardFooter>
    </Card>
  </div>
</template>
