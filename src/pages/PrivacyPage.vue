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
          {{ t('privacy.title', 'Polityka prywatności') }}
        </h1>
        <p class="text-muted-foreground">
          {{ t('privacy.subtitle', 'Jak chronimy Twoje dane') }}
        </p>
      </div>

      <div class="space-y-6">
        <section class="space-y-3">
          <h2 class="text-2xl font-semibold">
            {{ t('privacy.dataStorage.title', 'Przechowywanie danych') }}
          </h2>
          <p class="text-muted-foreground">
            {{ t('privacy.dataStorage.description', 'Aplikacja Gear Stack przechowuje wszystkie dane lokalnie w przeglądarce użytkownika za pomocą localStorage. Dane nie są przesyłane na żadne zewnętrzne serwery ani do osób trzecich.') }}
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="text-2xl font-semibold">
            {{ t('privacy.dataAccess.title', 'Dostęp do danych') }}
          </h2>
          <p class="text-muted-foreground">
            {{ t('privacy.dataAccess.description', 'Tylko Ty masz dostęp do swoich danych. Aplikacja nie wymaga rejestracji ani logowania, więc nie ma możliwości, aby ktokolwiek inny uzyskał dostęp do Twoich danych.') }}
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="text-2xl font-semibold">
            {{ t('privacy.dataDeletion.title', 'Usuwanie danych') }}
          </h2>
          <p class="text-muted-foreground">
            {{ t('privacy.dataDeletion.description', 'Możesz w każdej chwili usunąć wszystkie dane z aplikacji poprzez wyczyszczenie localStorage w ustawieniach przeglądarki lub użycie funkcji eksportu/usuwania danych w aplikacji.') }}
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="text-2xl font-semibold">
            {{ t('privacy.changes.title', 'Zmiany w polityce') }}
          </h2>
          <p class="text-muted-foreground">
            {{ t('privacy.changes.description', 'W przypadku wprowadzenia zmian w sposobie przetwarzania danych, ta strona zostanie zaktualizowana, a użytkownicy zostaną poinformowani o istotnych zmianach.') }}
          </p>
        </section>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

