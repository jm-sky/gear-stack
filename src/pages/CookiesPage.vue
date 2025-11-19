<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'

const { t } = useI18n()
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6">
      <div class="space-y-2">
        <h1 class="text-3xl font-bold tracking-tight">
          {{ t('cookies.title', 'Informacja o ciasteczkach') }}
        </h1>
        <p class="text-muted-foreground">
          {{ t('cookies.subtitle', 'Informacje o wykorzystaniu danych w aplikacji') }}
        </p>
      </div>

      <div class="space-y-6">
        <section class="space-y-3">
          <h2 class="text-2xl font-semibold">
            {{ t('cookies.localStorage.title', 'LocalStorage') }}
          </h2>
          <p class="text-muted-foreground">
            {{ t('cookies.localStorage.description', 'Aplikacja Gear Stack wykorzystuje localStorage przeglądarki do przechowywania danych użytkownika. Wszystkie dane są przechowywane lokalnie na Twoim urządzeniu i nie są przesyłane na żadne zewnętrzne serwery.') }}
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="text-2xl font-semibold">
            {{ t('cookies.whatWeStore.title', 'Co przechowujemy') }}
          </h2>
          <ul class="list-disc list-inside space-y-2 text-muted-foreground">
            <li>{{ t('cookies.whatWeStore.items', 'Dane kontenerów i przedmiotów (nazwy, opisy, wagi, statusy)') }}</li>
            <li>{{ t('cookies.whatWeStore.profile', 'Dane profilu użytkownika (nazwa, email)') }}</li>
            <li>{{ t('cookies.whatWeStore.settings', 'Ustawienia aplikacji (język, preferencje)') }}</li>
          </ul>
        </section>

        <section class="space-y-3">
          <h2 class="text-2xl font-semibold">
            {{ t('cookies.privacy.title', 'Prywatność') }}
          </h2>
          <p class="text-muted-foreground">
            {{ t('cookies.privacy.description', 'Wszystkie dane są przechowywane wyłącznie w Twojej przeglądarce. Nie zbieramy, nie przetwarzamy ani nie udostępniamy Twoich danych osobom trzecim. Aplikacja działa w pełni po stronie klienta (client-side).') }}
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="text-2xl font-semibold">
            {{ t('cookies.future.title', 'Przyszłość') }}
          </h2>
          <p class="text-muted-foreground">
            {{ t('cookies.future.description', 'W przyszłości aplikacja może wykorzystywać cookies do dodatkowych funkcji (np. synchronizacja między urządzeniami). W takim przypadku ta strona zostanie zaktualizowana o szczegółowe informacje.') }}
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="text-2xl font-semibold">
            {{ t('cookies.rodo.title', 'RODO') }}
          </h2>
          <p class="text-muted-foreground">
            {{ t('cookies.rodo.description', 'Zgodnie z Rozporządzeniem Ogólnym o Ochronie Danych (RODO), informujemy, że aplikacja nie przetwarza danych osobowych w sposób wymagający zgody użytkownika, ponieważ wszystkie dane są przechowywane lokalnie na urządzeniu użytkownika.') }}
          </p>
        </section>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

