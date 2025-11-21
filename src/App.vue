<script setup lang="ts">
import { Toaster } from '@/components/ui/sonner'
import 'vue-sonner/style.css'
import LoginModal from './shared/components/LoginModal.vue'
import { useAppInitialization } from './shared/composables/useAppInitialization'

const { isInitialized } = useAppInitialization()
</script>

<template>
  <RouterView :is-initialized />
  <LoginModal />
  <Toaster rich-colors />
</template>

<style scoped></style>
