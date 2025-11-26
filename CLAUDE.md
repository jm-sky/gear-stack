# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gear Stack is a lightweight front-end Vue 3 application for managing survival gear and bug-out bag equipment. The app runs fully client-side using `localStorage` for persistence.

## Commands

### Development
```bash
pnpm dev              # Start development server (default port: 5176)
pnpm build            # Build for production (runs type-check + build-only)
pnpm build-only       # Build without type checking
pnpm preview          # Preview production build
```

### Code Quality
```bash
pnpm type-check       # Run TypeScript compiler check
pnpm lint             # Run ESLint with auto-fix and cache
```

### Package Manager
This project uses **pnpm** (version 10.18.3+). Always use `pnpm` instead of `npm` or `yarn`.

## Architecture

### Module-Based Structure

The application follows a **modular architecture** where each feature is self-contained in `src/modules/`. Each module contains:

- `pages/` - Vue page components
- `components/` - Module-specific components
- `store/` - Pinia stores for state management
- `services/` - Business logic layer (e.g., `gearService.ts`)
- `composables/` - Reusable composition functions
- `types/` - TypeScript type definitions
- `routes.ts` - Module route definitions
- `i18n/` - Module-specific translations

Current modules:
- `gear` - Core gear/container management
- `user` - User profile management
- `settings` - Application settings
- `dashboard` - Dashboard views

### Core Directories

- `src/components/` - Shared UI components
  - `ui/` - shadcn-vue components
  - `data-table/` - Table components
  - `layout/` - Layout-related components
- `src/layouts/` - Layout wrappers (authenticated, guest, public)
- `src/shared/` - Shared utilities, types, composables, and i18n infrastructure
- `src/router/` - Vue Router configuration
- `src/i18n/` - Application i18n instance (merges module translations)

### State Management Pattern

**Pinia stores** handle state persistence, while **service classes** contain business logic:

- **Store** (`src/modules/gear/store/useGearStore.ts`): Simple CRUD operations + localStorage sync
- **Service** (`src/modules/gear/services/gearService.ts`): Business logic, validation, calculations

Example:
```typescript
// Service creates/validates, store persists
const container = gearService.createContainer(data)
// Service handles weight calculations
const totalWeight = gearService.calculateTotalWeight(containerId)
```

### Data Persistence

All data is stored in `localStorage` with automatic sync:
- Gear containers: `gear-stack:containers`
- Settings: `gear-stack:settings`
- The stores handle load/save operations automatically

### Routing & Layouts

Routes are defined per-module and merged in `src/router/routes.ts`. Each route specifies a layout via `meta.layout`:

```typescript
{
  path: '/gear',
  component: () => import('@/modules/gear/pages/ContainersListPage.vue'),
  meta: { layout: 'authenticated' }
}
```

Available layouts: `authenticated`, `guest`, `public`

### Internationalization (i18n)

The app uses **vue-i18n** with a registry pattern:

1. Each module defines translations in `i18n/locales/` (en, pl)
2. Module translations are exported from `i18n/index.ts`
3. App-level `src/i18n/index.ts` merges all module translations + shared registry
4. Shared i18n utilities are in `src/shared/i18n/`

Locale is persisted in localStorage and synced via `useLocale()` composable.

## Tech Stack & Configuration

### Core Technologies
- **Vue 3.5+** with `<script setup>` and Composition API
- **TypeScript** (strict mode)
- **Pinia** for state management
- **Vue Router** for navigation
- **Vite** as build tool

### UI & Styling
- **Tailwind CSS v4** (via `@tailwindcss/vite`)
- **shadcn-vue** components (based on reka-ui)
- **lucide-vue-next** for icons
- **vue-sonner** for toast notifications
- **floating-vue** for tooltips (registered as `v-tooltip` directive)

### Form Handling
- **vee-validate** + **@vee-validate/zod** for form validation
- **zod** for schema validation

### Development Tools
- **ESLint** with Vue, TypeScript, and Perfectionist plugins
- **vue-tsc** for TypeScript type checking
- **vite-plugin-vue-devtools** for Vue DevTools

## Code Style & Conventions

### ESLint Configuration (eslint.config.ts)

- **No semicolons** (`semi: never`)
- **Single quotes** with escape avoidance
- **Import sorting** (Perfectionist plugin) - alphabetical order with specific groups
- **Self-closing tags** required for all HTML/SVG/Vue components
- **Max attributes per line**: 3 for single-line, 1 for multi-line
- Unused variables starting with `_` are allowed
- **No line breaks before `else`, `catch`, `finally`** - Keep control flow keywords on the same line as closing brace
  - ✅ Use: `} else {`, `} catch (error) {`, `} finally {`
  - ❌ Avoid: Line breaks before these keywords

### TypeScript Conventions

- Use `@/` alias for absolute imports from `src/`
- Create **dedicated union types** instead of inline definitions (per global CLAUDE.md)
- Prefer interfaces for object shapes, types for unions/primitives
- All types are defined in module-specific `types/` directories

### Vue Component Patterns

- Use `<script setup lang="ts">` for all components
- Import order: external packages → internal modules (alphabetical, enforced by ESLint)
- Use composables for reusable logic (e.g., `useGearStore`, `useLocale`)
- Layouts are rendered via `<RouterView />` in App.vue

### Vue 3.5+ Best Practices

**v-model with defineModel:**
- ✅ Use: `const open = defineModel<boolean>('open', { required: true })`
- ❌ Avoid: `defineProps<{ open: boolean }>()` + `emit('update:open')`
- Benefits: Simpler syntax, automatic reactivity, less boilerplate

**Reactive Destructured Props:**
- Destructured props are reactive in Vue 3.5+ (no need for `toRefs`)
- ✅ Use: `const { item } = defineProps<{ item: IGearItem }>()`
- Props can be used directly in computed/watch without losing reactivity

**Prop Shortcuts:**
- When passing a prop with the same name as the variable
- ✅ Use: `<Dialog :open />` instead of `<Dialog :open="open" />`

**TypeScript Generics:**
- Always provide explicit types for `ref<T>`, `computed<T>`, `reactive<T>`
- ✅ Use: `const count = ref<number>(0)`, `const label = computed<string>(() => ...)`
- ❌ Avoid: `const count = ref(0)` (implicit types)

**Declaration Order in `<script setup>`:**
1. Composables (e.g., `useI18n()`, `useRouter()`)
2. `defineProps()`
3. `defineModel()`
4. `defineEmits()`
5. Computed properties and reactive state
6. Functions and methods

**Routing:**
- Use route helper functions from `routes.ts` instead of hardcoded paths
- ✅ Use: `GearRoutePath.ItemEditById(containerId, itemId)`
- ❌ Avoid: `` `/gear/${containerId}/items/${itemId}/edit` ``

## Environment & Configuration

### Environment Variables
- `VITE_PORT` - Development server port (default: 5176)
- `VITE_API_PROXY_URL` - API proxy target (default: http://localhost:8000)

The Vite config proxies `/api` requests to the configured backend URL.

### Node.js Requirements
- Node.js `^20.19.0` or `>=22.12.0` (specified in package.json)

## Key Features

1. **Gear Container Management** - Create/edit multiple gear lists (bug-out bags, EDC, etc.)
2. **Item Tracking** - Track items with status (owned/missing/toBuy), priority, weight, expiration
3. **Weight Calculations** - Automatic total pack weight calculation (supports g/kg units)
4. **Readiness Indicators** - Kit completeness tracking
5. **Data Import/Export** - JSON import/export for backup/restore
6. **Dark Mode** - Synced via settings store and `useDarkMode` composable
7. **Multi-language** - English and Polish (extensible)

## Important Notes

- **No backend** - This is a fully client-side application
- **Data persistence** - All data in localStorage; clearing browser data = data loss
- **Module independence** - Modules should be self-contained and reusable
- **Service layer** - Business logic belongs in service classes, not in stores or components
- **Type safety** - All data structures have TypeScript interfaces in `types/` directories

## UI Component Notes

### Action Icons

**CRITICAL:** Action icons must use the centralized mapping from `src/modules/gear/utils/actionIcons.ts`. This is the single source of truth for all action icons.

✅ **Correct usage:**
```vue
<script setup>
import { getActionIcon } from '@/modules/gear/utils/actionIcons'

const ExportIcon = getActionIcon('exportToPrompt')
const CreateIcon = getActionIcon('create')
</script>

<template>
  <Button>
    <ExportIcon class="size-4" />
    Export to Prompt
  </Button>
</template>
```

❌ **Incorrect usage:**
```vue
<!-- DO NOT import icons directly -->
<script setup>
import { MessageSquare, Sparkles } from 'lucide-vue-next'
</script>

<template>
  <Button>
    <MessageSquare class="size-4" />
    Export to Prompt
  </Button>
</template>
```

**Notes:**
- Always use `getActionIcon(actionKey)` instead of importing icons directly
- This ensures consistency across the application (e.g., `exportToPrompt` always uses `Sparkles`, not `MessageSquare`)
- Available action keys: `back`, `moreActions`, `create`, `addItem`, `addContainer`, `edit`, `delete`, `deleteAll`, `export`, `import`, `importFromMarkdown`, `exportToPrompt`, `exportAllToPrompt`, `recognizeParameters`, `recognizeParametersAll`
- Similar pattern exists for category icons in `src/modules/gear/utils/categoryIcons.ts`

### Reka-ui / shadcn-vue Checkbox

**CRITICAL:** In Reka-ui (shadcn-vue), Checkbox uses standard `v-model`, **NOT** `v-model:checked`.

✅ **Correct usage:**
```vue
<script setup>
const checked = ref(true)
</script>

<template>
  <Checkbox v-model="checked" />
</template>
```

❌ **Incorrect usage:**
```vue
<!-- DOES NOT WORK -->
<Checkbox v-model:checked="checked" />
<Checkbox :checked="checked" @update:checked="..." />
```

**Notes:**
- `v-model:checked` only works with `defineModel()` (as in `ContainersFilters.vue`)
- For regular `ref`, use standard `v-model`
- Checkbox in Reka-ui uses `modelValue` and `@update:model-value` under the hood

## TailwindCSS Best Practices

**Sizing:**
- Prefer `size-{value}` utility class instead of separate `w-{value} h-{value}` when width and height are the same
- ✅ **Correct:** `size-4`, `size-8`, `size-12`
- ❌ **Avoid:** `w-4 h-4`, `w-8 h-8`, `w-12 h-12`

**Button Component Spacing:**
- The Button component already includes `flex` and `gap-2` classes
- Icons inside buttons do **NOT** need `mr-2` or similar margin utilities
- ✅ **Correct:** `<Button><Icon />Label</Button>` (gap handled automatically)
- ❌ **Avoid:** `<Button><Icon class="mr-2" />Label</Button>`

## Responsive Design

**Always consider mobile-first responsive design:**
- Start with mobile styles (base classes)
- Add desktop variants using Tailwind breakpoint prefixes (eg. `sm:`)
- Example: `text-sm sm:text-base lg:text-lg` (small on mobile, base on tablet, large on desktop)
- Consider spacing, typography, layout, and visibility across breakpoints
