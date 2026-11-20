# Frontend rules (src/)

Stack: Vue 3.5 `<script setup lang="ts">`, Pinia, TanStack Query (`@tanstack/vue-query`), vue-router, vue-i18n, Tailwind v4, shadcn-vue (reka-ui), vee-validate + zod, axios (API client + interceptors in `src/shared/services/`), lucide-vue-next, vue-sonner. Architecture: [../docs/claude/architecture.md](../docs/claude/architecture.md).

## ESLint specifics (eslint.config.ts; `pnpm lint` auto-fixes)

- No semicolons, single quotes. Keep `else` / `catch` / `finally` on the same line as the closing brace (`} else {`).
- Vue templates: self-closing tags always (html, components, svg); max 3 attributes per line single-line, 1 per line multi-line.
- Perfectionist import sorting: alphabetical, no blank lines between imports; groups: external, `@/` internal, type imports (parent/sibling/index), then relative. Object keys are NOT sorted. Interface/union sorting off.
- Unused vars/args prefixed `_` are allowed; `any` only warns.

## Vue / TS conventions

- `@/` alias for imports from `src/`. Prefer interfaces for object shapes, `type` for unions. Types live in each module's `types/`.
- `defineModel` instead of props + `update:` emit: `const open = defineModel<boolean>('open', { required: true })`.
- Destructured props are reactive (3.5): `const { item } = defineProps<{ item: IGearItem }>()`. Use prop shorthand `<Dialog :open />`.
- Explicit generics: `ref<number>(0)`, `computed<string>(() => ...)`.
- `<script setup>` order: composables (`useI18n`, `useRouter`...), `defineProps`, `defineModel`, `defineEmits`, computed/state, functions.
- Routes: use helpers from the module `routes.ts` (`GearRoutePath.ItemEditById(containerId, itemId)`), never hardcoded path strings. Layout via `meta.layout`: `authenticated` | `guest` | `public`.
- i18n: every module has `i18n/locales/{en,pl}`; new strings need both.
- Mobile-first responsive (`text-sm sm:text-base`).

## Gotchas

- **Action icons:** never import lucide icons directly for actions; use `getActionIcon('<key>')` from `@/modules/gear/utils/actionIcons` (single source of truth; keys are the object keys in that file, e.g. `create`, `edit`, `delete`, `clone`, `publish`, `export`, `exportToPrompt`, `ai`, `recognizeParameters`). Category icons: `modules/gear/utils/categoryIcons.ts`.
- **Checkbox (reka-ui/shadcn-vue):** plain `v-model`, NOT `v-model:checked` / `:checked` (that only works with `defineModel()` as in `ContainersFilters.vue`).
- **Tailwind:** `size-4` not `w-4 h-4`. `Button` already has `flex gap-2`: no `mr-2` on icons inside it.
- **Offline cache:** `useGearStoreV2` persists to localStorage key `gear-stack:items-v2`; legacy `gear-stack:containers` is a read-only V1 snapshot used only by `v1ToV2Migration` / `dataMigrationService` for local-to-API upload. Server state for API-synced data is TanStack Query.
