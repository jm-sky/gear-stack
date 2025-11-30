<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'

const { t } = useI18n()
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-8">
      <div class="space-y-2">
        <h1 class="text-3xl font-bold tracking-tight">
          {{ t('about.title', 'About Gear Stack') }}
        </h1>
        <p class="text-muted-foreground">
          {{ t('about.subtitle', 'A comprehensive web application for managing survival gear, bug-out bags, and outdoor equipment') }}
        </p>
      </div>

      <!-- Overview -->
      <section class="space-y-4">
        <h2 class="text-2xl font-semibold">
          {{ t('about.overview.title', 'Overview') }}
        </h2>
        <p class="text-muted-foreground">
          {{ t('about.overview.description', 'Gear Stack is a full-stack application designed for outdoor enthusiasts, preppers, and survival gear collectors. It combines an intuitive front-end interface with a robust backend to provide secure multi-user gear management with cloud synchronization across devices.') }}
        </p>
      </section>

      <!-- Key Capabilities -->
      <section class="space-y-4">
        <h2 class="text-2xl font-semibold">
          {{ t('about.capabilities.title', 'Key Capabilities') }}
        </h2>
        <ul class="list-disc list-inside space-y-2 text-muted-foreground">
          <li>{{ t('about.capabilities.multiUser', 'Multi-User Platform - Secure user accounts with authentication and authorization') }}</li>
          <li>{{ t('about.capabilities.hybrid', 'Hybrid Architecture - Works offline with localStorage, syncs with cloud when online') }}</li>
          <li>{{ t('about.capabilities.organization', 'Advanced Organization - Hierarchical container system with nested items and weight tracking') }}</li>
          <li>{{ t('about.capabilities.metadata', 'Rich Metadata - Track weight, expiration dates, priorities, brands, and custom categories') }}</li>
          <li>{{ t('about.capabilities.portability', 'Data Portability - Import/export functionality with AI-ready markdown format') }}</li>
        </ul>
      </section>

      <!-- Core Features -->
      <section class="space-y-4">
        <h2 class="text-2xl font-semibold">
          {{ t('about.coreFeatures.title', 'Core Features') }}
        </h2>
        <div class="space-y-6">
          <div class="space-y-2">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.containers.title', 'Container System') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.containers.multiple', 'Multiple container types (Bug-out bags, EDC kits, get-home bags, medical kits, camping gear, and custom types)') }}</li>
              <li>{{ t('about.coreFeatures.containers.hierarchical', 'Hierarchical organization - containers can contain other containers (nested packs, pouches in bags)') }}</li>
              <li>{{ t('about.coreFeatures.containers.colors', 'Visual distinction - assign colors to containers for quick identification (10+ colors)') }}</li>
              <li>{{ t('about.coreFeatures.containers.metadata', 'Container metadata - type, description, base weight, color coding') }}</li>
              <li>{{ t('about.coreFeatures.containers.cycle', 'Cycle detection - prevents circular references in nested containers') }}</li>
            </ul>
          </div>

          <div class="space-y-2">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.items.title', 'Item Management') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.items.rich', 'Rich item data: name, quantity, weight (with unit selection: g, kg, oz, lb), category, priority, status (owned/missing/to buy), brand, notes, expiration date') }}</li>
              <li>{{ t('about.coreFeatures.items.categorization', 'Smart categorization - automatic category recognition based on item name (water, fire, food, shelter, first aid, tools, navigation, communication, clothing, hygiene, light, other)') }}</li>
              <li>{{ t('about.coreFeatures.items.status', 'Status tracking - mark items as owned, missing, or to buy') }}</li>
              <li>{{ t('about.coreFeatures.items.priority', 'Priority levels - low, medium, high, critical') }}</li>
              <li>{{ t('about.coreFeatures.items.expiration', 'Expiration tracking - monitor consumables and replace before they expire') }}</li>
            </ul>
          </div>

          <div class="space-y-2">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.analytics.title', 'Analytics & Insights') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.analytics.weight', 'Weight calculations - total pack weight with recursive calculation for nested containers, category-based weight distribution, base weight vs. consumables tracking') }}</li>
              <li>{{ t('about.coreFeatures.analytics.readiness', 'Readiness indicators - kit completeness percentage based on owned vs. missing items') }}</li>
              <li>{{ t('about.coreFeatures.analytics.charts', 'Donut charts - visual breakdown of weight or quantity by category') }}</li>
              <li>{{ t('about.coreFeatures.analytics.statistics', 'Item statistics - count items by status, category, or priority') }}</li>
            </ul>
          </div>

          <div class="space-y-2">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.search.title', 'Search & Filtering') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.search.smart', 'Smart search - find items by name, brand, or notes across all containers') }}</li>
              <li>{{ t('about.coreFeatures.search.filtering', 'Multi-criteria filtering - filter by category, status, priority, or container') }}</li>
              <li>{{ t('about.coreFeatures.search.sorting', 'Sorting options - sort by name, weight, expiration date, or priority') }}</li>
              <li>{{ t('about.coreFeatures.search.expired', 'Highlight expired items - visual warnings for expired or soon-to-expire items') }}</li>
            </ul>
          </div>

          <div class="space-y-2">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.importExport.title', 'Import/Export') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.importExport.json', 'JSON export/import - full data backup and restore') }}</li>
              <li>{{ t('about.coreFeatures.importExport.markdown', 'AI-ready markdown export - export containers to markdown format for AI processing with structured format, nested container support, and calculated weights') }}</li>
              <li>{{ t('about.coreFeatures.importExport.csv', 'CSV export - export data in CSV format for spreadsheet applications') }}</li>
              <li>{{ t('about.coreFeatures.importExport.crossDevice', 'Cross-device transfer - export from one device, import on another') }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Business Features -->
      <section class="space-y-4">
        <h2 class="text-2xl font-semibold">
          {{ t('about.businessFeatures.title', 'Business Features') }}
        </h2>
        <div class="space-y-6">
          <div class="space-y-2">
            <h3 class="text-xl font-semibold">
              {{ t('about.businessFeatures.security.title', 'User Management & Security') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.businessFeatures.security.auth', 'User registration & login - email/password authentication with secure password hashing') }}</li>
              <li>{{ t('about.businessFeatures.security.oauth', 'OAuth social login - sign in with Google (GitHub support planned)') }}</li>
              <li>{{ t('about.businessFeatures.security.email', 'Email verification - confirm email addresses for account security') }}</li>
              <li>{{ t('about.businessFeatures.security.2fa', 'Two-factor authentication (2FA) - TOTP (authenticator apps) and WebAuthn (passkeys/security keys)') }}</li>
              <li>{{ t('about.businessFeatures.security.password', 'Password management - reset forgotten passwords, change password for authenticated users') }}</li>
              <li>{{ t('about.businessFeatures.security.recaptcha', 'reCAPTCHA v3 protection - invisible bot protection on login, registration, and password reset') }}</li>
              <li>{{ t('about.businessFeatures.security.session', 'Session management - JWT tokens with automatic refresh, secure logout') }}</li>
              <li>{{ t('about.businessFeatures.security.deletion', 'Account deletion - GDPR-compliant soft delete with confirmation') }}</li>
            </ul>
          </div>

          <div class="space-y-2">
            <h3 class="text-xl font-semibold">
              {{ t('about.businessFeatures.profile.title', 'User Profile') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.businessFeatures.profile.management', 'Profile management - update name, email, and preferences') }}</li>
              <li>{{ t('about.businessFeatures.profile.avatar', 'Avatar support - OAuth providers automatically provide profile pictures') }}</li>
              <li>{{ t('about.businessFeatures.profile.settings', 'Preferred settings - weight units, language, theme preferences') }}</li>
              <li>{{ t('about.businessFeatures.profile.security', 'Security settings - manage 2FA methods, view security status') }}</li>
            </ul>
          </div>

          <div class="space-y-2">
            <h3 class="text-xl font-semibold">
              {{ t('about.businessFeatures.i18n.title', 'Multi-Language Support') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.businessFeatures.i18n.languages', 'English and Polish fully supported') }}</li>
              <li>{{ t('about.businessFeatures.i18n.detection', 'Automatic locale detection from browser') }}</li>
              <li>{{ t('about.businessFeatures.i18n.switching', 'Manual language switching in settings') }}</li>
              <li>{{ t('about.businessFeatures.i18n.localized', 'All UI text, validation messages, and emails localized') }}</li>
            </ul>
          </div>

          <div class="space-y-2">
            <h3 class="text-xl font-semibold">
              {{ t('about.businessFeatures.theming.title', 'Theming') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.businessFeatures.theming.dark', 'Dark mode - full dark theme support with system preference detection') }}</li>
              <li>{{ t('about.businessFeatures.theming.persistence', 'Theme persistence - settings saved per user account') }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Technical Stack -->
      <section class="space-y-4">
        <h2 class="text-2xl font-semibold">
          {{ t('about.technical.title', 'Technical Stack') }}
        </h2>
        <div class="space-y-4">
          <div class="space-y-2">
            <h3 class="text-xl font-semibold">
              {{ t('about.technical.frontend.title', 'Frontend') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>Vue 3.5+ with TypeScript & Composition API</li>
              <li>Pinia for state management</li>
              <li>Vue Router for navigation</li>
              <li>TailwindCSS v4 + shadcn-vue components</li>
              <li>VeeValidate + Zod for form validation</li>
              <li>TanStack Query for server state management</li>
              <li>vue-i18n for internationalization</li>
            </ul>
          </div>

          <div class="space-y-2">
            <h3 class="text-xl font-semibold">
              {{ t('about.technical.backend.title', 'Backend') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>FastAPI (Python) with async/await</li>
              <li>PostgreSQL database</li>
              <li>SQLAlchemy ORM with async support</li>
              <li>JWT authentication with refresh tokens</li>
              <li>Rate limiting and reCAPTCHA protection</li>
              <li>Modular architecture (auth, two-factor, email)</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  </AuthenticatedLayout>
</template>

