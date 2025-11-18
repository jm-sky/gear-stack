<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import CategoriesSettingsCard from '../components/CategoriesSettingsCard.vue'
import ContainerTypesSettingsCard from '../components/ContainerTypesSettingsCard.vue'
import PreferencesSettingsCard from '../components/PreferencesSettingsCard.vue'

const { t } = useI18n()
</script>

<template>
  <AuthenticatedLayout>
    <div class="max-w-4xl mx-auto space-y-6">
      <div class="space-y-1">
        <h1 class="text-3xl font-bold tracking-tight">
          {{ t('settings.page.title') }}
        </h1>
        <p class="text-sm text-muted-foreground">
          {{ t('settings.page.subtitle') }}
        </p>
      </div>

      <div class="space-y-6">
        <!-- Preferences Settings -->
        <PreferencesSettingsCard />

        <!-- Container Types Settings -->
        <ContainerTypesSettingsCard />

        <!-- Categories Settings -->
        <CategoriesSettingsCard />
      </div>
    </div>
  </AuthenticatedLayout>
</template>

