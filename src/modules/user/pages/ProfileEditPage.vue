<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { ArrowLeft, Shield, Sparkles } from 'lucide-vue-next'
import { useField, useForm } from 'vee-validate'
import { onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { z } from 'zod'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import { FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useBackend } from '@/shared/composables/useBackend'
import { useHandleError } from '@/shared/composables/useHandleError'
import { useUser } from '../composables/useUser'
import { UserRoutePaths } from '../routes'
import { generateGravatarUrl } from '../utils/generateGravatarUrl'
import { validateAvatarUrl } from '../utils/validateAvatarUrl'

const router = useRouter()
const { t } = useI18n()
const { profile, updateProfile } = useUser()
const { shouldUseAPI: _shouldUseAPI } = useBackend()
const { handleError } = useHandleError()

const profileSchema = z.object({
  name: z.string().min(1, t('user.edit.name_required')),
  email: z.string().email(t('user.edit.email_invalid')),
  avatarUrl: z
    .string()
    .optional()
    .refine(
      (val) => !val || validateAvatarUrl(val),
      { message: t('user.edit.avatar_invalid') }
    ),
})

const { handleSubmit, setValues, setErrors } = useForm({
  validationSchema: toTypedSchema(profileSchema),
  initialValues: {
    name: '',
    email: '',
    avatarUrl: '',
  },
})

const { value: emailValue } = useField('email')
const { value: avatarUrlValue } = useField('avatarUrl')


// Populate form with current profile data
onMounted(() => {
  if (profile.value) {
    setValues({
      name: profile.value.name,
      email: profile.value.email,
      avatarUrl: profile.value.avatarUrl || '',
    })
  }
})

// Watch for profile data changes
watch(() => profile.value, (newProfile) => {
  if (newProfile) {
    setValues({
      name: newProfile.name,
      email: newProfile.email,
      avatarUrl: newProfile.avatarUrl ?? '',
    })
  }
})

const onSubmit = handleSubmit(
  async (values) => {
    try {
      const updateData = {
        name: values.name,
        email: values.email,
        avatarUrl: values.avatarUrl && values.avatarUrl.trim() ? values.avatarUrl.trim() : undefined,
      }

      await updateProfile(updateData)
      toast.success(t('common.success'))
      router.push(UserRoutePaths.profile)
    } catch (error) {
      console.error('Profile update failed:', error)
      handleError(error, { setErrors })
    }
  },
  () => {
    toast.error(t('user.edit.validation_error') || 'Validation failed')
  }
)

const handleCancel = () => {
  router.push(UserRoutePaths.profile)
}

const handleGenerateGravatar = () => {
  const email = emailValue.value as string | undefined
  if (!email || typeof email !== 'string' || !email.trim()) {
    toast.error(t('user.edit.email_required_for_gravatar') || 'Email is required to generate Gravatar URL')
    return
  }

  try {
    const gravatarUrl = generateGravatarUrl(email)
    avatarUrlValue.value = gravatarUrl
    toast.success(t('user.edit.gravatar_generated') || 'Gravatar URL generated')
  } catch (error) {
    console.error('Gravatar generation failed:', error)
    toast.error(t('user.edit.gravatar_generation_failed') || 'Failed to generate Gravatar URL')
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <Button
            variant="ghost"
            size="icon"
            @click="handleCancel"
          >
            <ArrowLeft class="size-4" />
          </Button>
          <div class="space-y-1">
            <div class="flex items-center gap-2 flex-wrap">
              <h1 class="text-3xl font-bold tracking-tight">
                {{ t('user.edit.title') }}
              </h1>
              <Badge v-if="profile?.isAdmin" variant="default" class="gap-1">
                <Shield class="size-3" />
                {{ t('user.profile.admin_badge', 'Admin') }}
              </Badge>
            </div>
            <p class="text-sm text-muted-foreground">
              {{ t('user.edit.subtitle') }}
            </p>
          </div>
        </div>
      </div>

      <form v-if="profile" class="max-w-2xl mx-auto bg-card border rounded-lg p-6 space-y-8" @submit.prevent="onSubmit">
        <div class="flex flex-col gap-6">
          <FormField v-slot="{ componentField }" name="name">
            <FormItem>
              <FormLabel required>
                {{ t('user.edit.name_label') }}
              </FormLabel>
              <FormControl>
                <Input
                  type="text"
                  :placeholder="t('user.edit.name_placeholder')"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <FormField v-slot="{ componentField }" name="email">
            <FormItem>
              <FormLabel required>
                {{ t('user.edit.email_label') }}
              </FormLabel>
              <FormControl>
                <Input
                  type="email"
                  :placeholder="t('user.edit.email_placeholder')"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <FormField v-slot="{ componentField }" name="avatarUrl">
            <FormItem>
              <FormLabel>
                {{ t('user.edit.avatar_label') }}
              </FormLabel>
              <FormControl>
                <div class="flex gap-2">
                  <Input
                    type="url"
                    :placeholder="t('user.edit.avatar_placeholder')"
                    class="flex-1"
                    v-bind="componentField"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    :title="t('user.edit.generate_gravatar') || 'Generate Gravatar URL from email'"
                    @click="handleGenerateGravatar"
                  >
                    <Sparkles class="size-4" />
                  </Button>
                </div>
              </FormControl>
              <FormDescription>
                {{ t('user.edit.avatar_help') }}
              </FormDescription>
              <FormMessage />
            </FormItem>
          </FormField>
        </div>

        <div class="flex justify-end space-x-4">
          <Button type="button" variant="outline" @click="handleCancel">
            {{ t('user.edit.cancel') }}
          </Button>
          <Button type="submit">
            {{ t('user.edit.save_changes') }}
          </Button>
        </div>
      </form>
    </div>
  </AuthenticatedLayout>
</template>

