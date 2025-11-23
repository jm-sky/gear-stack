<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import HoverLink from '@/components/ui/hover-link/HoverLink.vue'
import HoverLinkExternal from '../ui/hover-link/HoverLinkExternal.vue'
import GithubIcon from '../ui/icons/GithubIcon.vue'

const { t } = useI18n()

const currentYear = new Date().getFullYear()
const version = __APP_VERSION__
const buildDate = new Date(__BUILD_DATE__).toLocaleDateString()
</script>

<template>
  <footer class="border-t bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60 mt-auto">
    <div class="mx-auto max-w-screen-2xl px-4 py-6 text-muted-foreground">
      <div class="flex flex-col items-center justify-between gap-4 md:flex-row">
        <div class="text-sm">
          &copy; {{ currentYear }}
          <HoverLinkExternal href="https://dev-made.it">
            DEV Made IT
          </HoverLinkExternal>
          <span class="ml-2 text-xs opacity-70">
            v{{ version }} – {{ buildDate }}
          </span>
        </div>

        <nav class="flex flex-col sm:flex-row flex-wrap items-center justify-center gap-3 sm:gap-6 text-sm">
          <HoverLink to="/cookies">
            {{ t('footer.cookies', 'Informacja o ciasteczkach') }}
          </HoverLink>
          <HoverLink to="/privacy">
            {{ t('footer.privacy', 'Polityka prywatności') }}
          </HoverLink>
          <HoverLink to="/contact">
            {{ t('footer.contact', 'Kontakt') }}
          </HoverLink>
          <HoverLinkExternal href="https://github.com" class="inline-flex items-center gap-1">
            <GithubIcon class="size-4" />
            {{ t('footer.github', 'GitHub') }}
          </HoverLinkExternal>
        </nav>
      </div>
    </div>
  </footer>
</template>

