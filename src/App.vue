<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { Toaster } from '@/components/ui/sonner'
import { useSettingsStore } from '@/modules/settings/store/useSettingsStore'
import { useDarkMode } from '@/shared/composables/useDarkMode'
import { useLocale } from '@/shared/i18n'
import 'vue-sonner/style.css'

const settingsStore = useSettingsStore()
const { isDark, setDark } = useDarkMode()
const { setLocale } = useLocale()

// Sync settings store with composables on mount
onMounted(() => {
  // Sync dark mode
  if (isDark.value !== settingsStore.darkMode) {
    setDark(settingsStore.darkMode)
  }

  // Sync locale
  if (setLocale) {
    setLocale(settingsStore.locale)
  }
})

// Watch for changes in store and sync with composables
watch(() => settingsStore.darkMode, (newValue) => {
  if (isDark.value !== newValue) {
    setDark(newValue)
  }
})

watch(() => settingsStore.locale, (newValue) => {
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
