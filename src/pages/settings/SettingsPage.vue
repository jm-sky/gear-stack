<script setup lang="ts">
import GearPreferencesCard from '@/modules/gear/components/GearPreferencesCard.vue'
import CategoriesSettingsCard from '@/modules/settings/components/CategoriesSettingsCard.vue'
import ContainerTypesSettingsCard from '@/modules/settings/components/ContainerTypesSettingsCard.vue'
import SettingsPageCore from '@/modules/settings/pages/SettingsPage.vue'
</script>

<template>
  <SettingsPageCore>
    <template #after>
      <!-- Gear Module Settings -->
      <ContainerTypesSettingsCard />
      <CategoriesSettingsCard />
      <GearPreferencesCard />
    </template>
  </SettingsPageCore>
</template>

