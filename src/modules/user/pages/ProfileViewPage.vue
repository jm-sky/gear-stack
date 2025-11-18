<script setup lang="ts">
import { Edit, Mail, User as UserIcon } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useUser } from '../composables/useUser'

const router = useRouter()
const { t } = useI18n()
const { profile } = useUser()

const handleEdit = () => {
  router.push('/profile/edit')
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div class="space-y-1">
          <h1 class="text-3xl font-bold tracking-tight">
            {{ t('user.profile.title') }}
          </h1>
          <p class="text-sm text-muted-foreground">
            {{ t('user.profile.subtitle') }}
          </p>
        </div>
        <Button variant="outline" @click="handleEdit">
          <Edit class="size-4 mr-2" />
          {{ t('user.profile.edit_button') }}
        </Button>
      </div>

      <div v-if="profile" class="bg-card border rounded-lg p-6 space-y-6">
        <div class="flex items-center space-x-6">
          <div
            v-if="profile.avatar"
            class="size-24 rounded-full bg-muted ring-1 ring-border flex items-center justify-center overflow-hidden"
          >
            <img :src="profile.avatar" :alt="profile.name" class="size-full object-cover" />
          </div>
          <div
            v-else
            class="size-24 rounded-full bg-muted ring-1 ring-border flex items-center justify-center"
          >
            <UserIcon class="size-12 text-muted-foreground" />
          </div>
          <div>
            <h2 class="text-2xl font-semibold">
              {{ profile.name }}
            </h2>
            <div class="flex items-center mt-2 text-muted-foreground">
              <Mail class="size-4 mr-2" />
              <span>{{ profile.email }}</span>
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
    </div>
  </AuthenticatedLayout>
</template>

