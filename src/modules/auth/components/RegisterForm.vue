<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { AuthRouteNames } from '@/modules/auth/config/routes'
import { registerSchema } from '@/modules/auth/validation/register.schema'
import { isValidationError } from '@/shared/utils/typeGuards'
import type { RegisterCredentials } from '@/modules/auth/types/user.type'

const { t } = useI18n()
const router = useRouter()
const { register, isRegistering } = useAuth()

const { handleSubmit, setErrors } = useForm({
  validationSchema: toTypedSchema(registerSchema),
  initialValues: {
    name: import.meta.env.VITE_DEFAULT_USER_EMAIL?.split('@')[0]?.replaceAll('.', ' ') ?? '',
    email: import.meta.env.VITE_DEFAULT_USER_EMAIL ?? '',
    password: import.meta.env.VITE_DEFAULT_USER_PASSWORD ?? '',
    passwordConfirmation: import.meta.env.VITE_DEFAULT_USER_PASSWORD ?? '',
  },
})

const onSubmit = handleSubmit(async (values: RegisterCredentials) => {
  try {
    const response = await register(values)
    toast.success(response.message ?? t('auth.register_success'))
    await router.push({ name: AuthRouteNames.verifyEmail, query: { email: values.email } })
  } catch (err: unknown) {
    if (isValidationError(err)) {
      setErrors(err.response.data.errors)
    } else {
      // TODO: add toast/sonner notification from shadcn-vue
      toast.error(t('errors.generic'))
      console.error('Register error:', err)
    }
  }
})
</script>

<template>
  <form class="space-y-4" @submit="onSubmit">
    <FormField v-slot="{ componentField }" name="name">
      <FormItem>
        <FormLabel required>
          {{ t('auth.form.name') }}
        </FormLabel>
        <FormControl>
          <Input type="text" :placeholder="t('auth.form.name_placeholder')" v-bind="componentField" />
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <FormField v-slot="{ componentField }" name="email">
      <FormItem>
        <FormLabel required>
          {{ t('auth.email') }}
        </FormLabel>
        <FormControl>
          <Input type="email" :placeholder="t('auth.form.email_placeholder')" v-bind="componentField" />
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <FormField v-slot="{ componentField }" name="password">
      <FormItem>
        <FormLabel required>
          {{ t('auth.password') }}
        </FormLabel>
        <FormControl>
          <Input type="password" :placeholder="t('auth.form.password_placeholder')" v-bind="componentField" />
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <FormField v-slot="{ componentField }" name="passwordConfirmation">
      <FormItem>
        <FormLabel required>
          {{ t('auth.password_confirm') }}
        </FormLabel>
        <FormControl>
          <Input type="password" :placeholder="t('auth.form.password_confirm_placeholder')" v-bind="componentField" />
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <Button type="submit" class="w-full" :loading="isRegistering">
      {{ t('auth.form.submit_register') }}
    </Button>
  </form>
</template>
