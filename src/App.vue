<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { Toaster } from '@/components/ui/sonner'
import { useCoreSettingsStore } from '@/modules/settings/store/useCoreSettingsStore'
import { useDarkMode } from '@/shared/composables/useDarkMode'
import { useLocale } from '@/shared/i18n'
import 'vue-sonner/style.css'

const coreSettingsStore = useCoreSettingsStore()
const { isDark, setDark } = useDarkMode()
const { setLocale } = useLocale()

// Sync settings store with composables on mount
onMounted(() => {
  // Sync dark mode
  if (isDark.value !== coreSettingsStore.darkMode) {
    setDark(coreSettingsStore.darkMode)
  }

  // Sync locale
  if (setLocale) {
    setLocale(coreSettingsStore.locale)
  }
})

// Watch for changes in store and sync with composables
watch(() => coreSettingsStore.darkMode, (newValue) => {
  if (isDark.value !== newValue) {
    setDark(newValue)
  }
})

watch(() => coreSettingsStore.locale, (newValue) => {
  if (setLocale) {
    setLocale(newValue)
  }
})
</script>

<template>
  <RouterView />
  <Toaster rich-colors />
</template>

<style scoped></style>
