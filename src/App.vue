<script setup lang="ts">
import { Toaster } from '@/components/ui/sonner'
import 'vue-sonner/style.css'
import DataMigrationDialog from '@/modules/gear/components/DataMigrationDialog.vue'
import LoginModal from './shared/components/LoginModal.vue'
import { useAppInitialization } from './shared/composables/useAppInitialization'

const { isInitialized } = useAppInitialization()
</script>

<template>
  <RouterView :is-initialized />
  <LoginModal />
  <DataMigrationDialog />
  <Toaster rich-colors />
</template>

<style scoped></style>
