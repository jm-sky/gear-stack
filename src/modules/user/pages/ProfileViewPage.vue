<script setup lang="ts">
import { Edit, ExternalLink, Mail, Shield } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Avatar from '@/components/ui/avatar/Avatar.vue'
import AvatarFallback from '@/components/ui/avatar/AvatarFallback.vue'
import AvatarImage from '@/components/ui/avatar/AvatarImage.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { useSettings } from '@/modules/settings/composables/useSettings'
import AuthenticationRequiredAlert from '../components/AuthenticationRequiredAlert.vue'
import { useUser } from '../composables/useUser'
import { UserRoutePaths } from '../routes'

const router = useRouter()
const { t } = useI18n()
const { profile } = useUser()
const { settings } = useSettings()
const { isAuthenticated } = useAuth()

const handleEdit = () => {
  router.push(UserRoutePaths.profileEdit)
}

const isProfilePublic = computed(() => settings.value?.profilePublic ?? false)
const publicProfileUrl = computed(() => {
  if (profile.value?.id && isProfilePublic.value) {
    return `/users/${profile.value.id}/public`
  }
  return null
})

// Generate initials from name or email
const initials = computed(() => {
  if (profile.value?.name) {
    return profile.value.name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2)
  }
  if (profile.value?.email) {
    return profile.value.email.substring(0, 2).toUpperCase()
  }
  return 'U'
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="space-y-1">
          <div class="flex items-center gap-2 flex-wrap">
            <h1 class="text-3xl font-bold tracking-tight">
              {{ t('user.profile.title') }}
            </h1>
            <Badge v-if="profile?.isAdmin" variant="default" class="gap-1">
              <Shield class="size-3" />
              {{ t('user.profile.admin_badge', 'Admin') }}
            </Badge>
          </div>
          <p class="text-sm text-muted-foreground">
            {{ t('user.profile.subtitle') }}
          </p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <Button
            v-if="publicProfileUrl"
            variant="outline"
            class="flex-1 sm:flex-none"
            @click="router.push(publicProfileUrl)"
          >
            <ExternalLink class="size-4 mr-2" />
            {{ t('user.edit.show_public_profile') }}
          </Button>
          <Button
            v-if="isAuthenticated"
            variant="outline"
            class="flex-1 sm:flex-none"
            @click="handleEdit"
          >
            <Edit class="size-4 mr-2" />
            {{ t('user.profile.edit_button') }}
          </Button>
        </div>
      </div>

      <div v-if="profile" class="bg-card border rounded-lg p-6 space-y-6">
        <div class="flex items-center space-x-6">
          <Avatar class="size-24 ring-1 ring-border">
            <AvatarImage :src="profile.avatarUrl ?? ''" :alt="profile.name" />
            <AvatarFallback class="bg-muted text-muted-foreground text-2xl font-semibold">
              {{ initials }}
            </AvatarFallback>
          </Avatar>
          <div class="flex-1">
            <div class="flex items-center gap-2 flex-wrap">
              <h2 class="text-2xl font-semibold">
                {{ profile.name }}
              </h2>
              <Badge v-if="profile.isAdmin" variant="default" class="gap-1">
                <Shield class="size-3" />
                {{ t('user.profile.admin_badge', 'Admin') }}
              </Badge>
            </div>
            <div class="flex items-center mt-2 text-muted-foreground">
              <Mail class="size-4 mr-2 shrink-0" />
              <span class="break-all">{{ profile.email }}</span>
            </div>
          </div>
        </div>

        <div class="border-t pt-4 space-y-4">
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-1">
              <label class="text-xs uppercase tracking-wide text-muted-foreground">
                {{ t('user.profile.user_id_label') }}
              </label>
              <p class="text-sm font-mono">
                {{ profile.id }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="bg-card border rounded-lg p-6 text-center">
        <p class="text-muted-foreground">
          {{ t('user.profile.no_profile') }}
        </p>
      </div>

      <AuthenticationRequiredAlert v-if="!isAuthenticated" />
    </div>
  </AuthenticatedLayout>
</template>

