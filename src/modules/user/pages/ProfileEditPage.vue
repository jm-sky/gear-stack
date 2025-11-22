<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { ArrowLeft } from 'lucide-vue-next'
import { useForm } from 'vee-validate'
import { onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useUser } from '../composables/useUser'
import { validateAvatarUrl } from '../utils/validateAvatarUrl'

const router = useRouter()
const { t } = useI18n()
const { profile, updateProfile } = useUser()

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

const { handleSubmit, setValues } = useForm({
  validationSchema: toTypedSchema(profileSchema),
  initialValues: {
    name: '',
    email: '',
    avatarUrl: '',
  },
})

// Populate form with current profile data
onMounted(() => {
  if (profile.value) {
    setValues({
      name: profile.value.name,
      email: profile.value.email,
      avatarUrl: profile.value.avatar || '',
    })
  }
})

// Watch for profile data changes
watch(() => profile.value, (newProfile) => {
  if (newProfile) {
    setValues({
      name: newProfile.name,
      email: newProfile.email,
      avatarUrl: newProfile.avatar || '',
    })
  }
})

const onSubmit = handleSubmit(async (values) => {
  try {
    await updateProfile({
      name: values.name,
      email: values.email,
      avatarUrl: values.avatarUrl || undefined,
    })
    toast.success(t('common.success'))
    router.push('/profile')
  } catch (error) {
    toast.error(t('common.error'))
    console.error(error)
  }
})

const handleCancel = () => {
  router.push('/profile')
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
            <h1 class="text-3xl font-bold tracking-tight">
              {{ t('user.edit.title') }}
            </h1>
            <p class="text-sm text-muted-foreground">
              {{ t('user.edit.subtitle') }}
            </p>
          </div>
        </div>
      </div>

      <form v-if="profile" class="max-w-2xl mx-auto bg-card border rounded-lg p-6 space-y-8" @submit="onSubmit">
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
                <Input
                  type="url"
                  :placeholder="t('user.edit.avatar_placeholder')"
                  v-bind="componentField"
                />
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

