<script setup lang="ts">
import { Check, Copy } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'

const { t } = useI18n()
const copied = ref(false)

const aiContextMarkdown = computed(() => {
  return `# Gear Stack - AI Context

## Overview
Gear Stack is a full-stack web application for managing survival gear, bug-out bags, and outdoor equipment. It's designed for outdoor enthusiasts, preppers, and survival gear collectors.

## Key Capabilities
- **Multi-User Platform** - Secure user accounts with authentication and authorization
- **Hybrid Architecture** - Works offline with localStorage, syncs with cloud when online
- **Advanced Organization** - Hierarchical container system with nested items and weight tracking
- **Rich Metadata** - Track weight, expiration dates, priorities, brands, and custom categories
- **Data Portability** - Import/export functionality with AI-ready markdown format

## Core Features

### Container System
- Multiple container types (Bug-out bags, EDC kits, get-home bags, medical kits, camping gear, custom)
- Hierarchical organization - containers can contain other containers (nested packs, pouches in bags)
- Visual distinction - assign colors to containers (10+ colors)
- Container metadata - type, description, base weight, color coding
- Cycle detection - prevents circular references

### Item Management
- Rich item data: name, quantity, weight (g, kg, oz, lb), category, priority, status (owned/missing/to buy), brand, notes, expiration date
- Smart categorization - automatic category recognition (water, fire, food, shelter, first aid, tools, navigation, communication, clothing, hygiene, light, other)
- Status tracking - owned, missing, or to buy
- Priority levels - low, medium, high, critical
- Expiration tracking for consumables

### Analytics & Insights
- Weight calculations - total pack weight with recursive calculation for nested containers
- Category-based weight distribution
- Base weight vs. consumables tracking
- Readiness indicators - kit completeness percentage
- Donut charts - visual breakdown by category
- Item statistics by status, category, or priority

### Search & Filtering
- Smart search - find items by name, brand, or notes across all containers
- Multi-criteria filtering - by category, status, priority, or container
- Sorting options - by name, weight, expiration date, or priority
- Highlight expired items - visual warnings

### Import/Export
- JSON export/import - full data backup and restore
- AI-ready markdown export - structured format with metadata, nested container support, calculated weights
- CSV export - for spreadsheet applications
- Cross-device transfer

## Business Features

### User Management & Security
- Email/password authentication with secure password hashing
- OAuth social login (Google, GitHub planned)
- Email verification
- Two-factor authentication (2FA) - TOTP and WebAuthn (passkeys)
- Password management - reset and change
- reCAPTCHA v3 protection
- JWT tokens with automatic refresh
- GDPR-compliant account deletion

### User Profile
- Profile management - name, email, preferences
- Avatar support from OAuth providers
- Preferred settings - weight units, language, theme
- Security settings - manage 2FA methods

### Multi-Language Support
- English and Polish fully supported
- Automatic locale detection
- Manual language switching
- All UI text, validation messages, and emails localized

### Theming
- Dark mode with system preference detection
- Theme persistence per user account

## Technical Stack

### Frontend
- Vue 3.5+ with TypeScript & Composition API
- Pinia for state management
- Vue Router for navigation
- TailwindCSS v4 + shadcn-vue components
- VeeValidate + Zod for form validation
- TanStack Query for server state management
- vue-i18n for internationalization

### Backend
- FastAPI (Python) with async/await
- PostgreSQL database
- SQLAlchemy ORM with async support
- JWT authentication with refresh tokens
- Rate limiting and reCAPTCHA protection
- Modular architecture (auth, two-factor, email)

## Architecture
- **Hybrid Persistence**: Client-side localStorage for offline-first, server-side PostgreSQL for multi-device sync
- **Automatic Synchronization** - Changes sync to cloud when online
- **Conflict Resolution** - Smart merging of offline changes
- **Module-Based Frontend** - Each feature is self-contained in modules
- **Backend Modules** - FastAPI modular pattern with routers, services, repositories`
})

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(aiContextMarkdown.value)
    copied.value = true
    toast.success(t('aiContext.copied', 'Context copied to clipboard'))
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error copying to clipboard:', error)
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6">
      <div class="space-y-2">
        <h1 class="text-3xl font-bold tracking-tight">
          {{ t('aiContext.title', 'AI Context') }}
        </h1>
        <p class="text-muted-foreground">
          {{ t('aiContext.subtitle', 'Short description of Gear Stack in Markdown format for AI assistants like ChatGPT') }}
        </p>
      </div>

      <Card>
        <CardHeader>
          <div class="flex items-center justify-between">
            <div>
              <CardTitle>
                {{ t('aiContext.card.title', 'Copy Context to Clipboard') }}
              </CardTitle>
              <CardDescription>
                {{ t('aiContext.card.description', 'Click the button below to copy the context description. You can then paste it into ChatGPT or other AI assistants to provide context about Gear Stack.') }}
              </CardDescription>
            </div>
            <Button @click="handleCopy">
              <Copy v-if="!copied" class="size-4" />
              <Check v-else class="size-4" />
              {{ copied ? t('common.copyToClipboard.copied') : t('common.copyToClipboard.copy') }}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <pre class="whitespace-pre-wrap text-sm font-mono bg-muted p-4 rounded-md border overflow-x-auto max-h-[600px] overflow-y-auto">{{ aiContextMarkdown }}</pre>
        </CardContent>
      </Card>
    </div>
  </AuthenticatedLayout>
</template>

