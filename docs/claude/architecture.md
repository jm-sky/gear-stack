# Architecture (on-demand reference for agents)

Read only when you need structural context. Rules/gotchas are in [../../CLAUDE.md](../../CLAUDE.md) and [../../src/CLAUDE.md](../../src/CLAUDE.md).

## Frontend modules (`src/modules/`)

`gear`, `user`, `settings`, `auth` (WebAuthn/passkeys, JWT auto-refresh), `ai`, `admin`, `stats`, `billing`. Each module: `pages/`, `components/`, `store/` (Pinia), `services/` (business logic + API services), `composables/`, `types/`, `routes.ts`, `i18n/`. Modules should stay self-contained.

Shared: `src/components/ui` (shadcn-vue), `src/components/{data-table,layout}`, `src/layouts` (authenticated/guest/public), `src/pages` (Landing, Privacy, Cookies, Contact, NotFound, Dashboard, Settings), `src/shared/{components,composables,config,i18n,services,store,types,utils}`, `src/router`, `src/i18n` (merges module translations + shared registry).

## State and persistence

- **Server state:** TanStack Query for auth, gear (V2, keys in `gearQueryKeys`), AI, admin, billing. Mutations must invalidate the relevant keys.
- **Client state:** Pinia stores. `useGearStoreV2` keeps an offline cache in localStorage (`gear-stack:items-v2`); settings in `gear-stack:settings`; AI chat history/context also local. Locale persisted in localStorage via `useLocale()`.
- **Backend (source of truth for signed-in users):** gear in `gear_items_v2`, users, sessions, admin data, billing (Stripe), AI. API via axios, `/api` proxied by Vite.
- Legacy V1 local key `gear-stack:containers` is read only for local-to-API upload (`readV1LocalDataAsV2Items`).

## Routing

Routes per module, merged in `src/router/routes.ts`; `meta.layout` selects layout. Guards: auth guard (session), admin guard (`modules/admin/guards/adminGuard.ts`); composable.

## i18n

vue-i18n; modules export translations from `i18n/index.ts` (en, pl); `src/i18n/index.ts` merges them with the shared registry.

## Other

- PWA: `vite-plugin-pwa` + workbox, config in `pwa.config.ts`.
- Charts: `@unovis`; tables: `@tanstack/vue-table`; Markdown: `markdown-it`; icons per CLAUDE rules via `getActionIcon`.
- Testing: vitest (happy-dom), Playwright (e2e + integration).
- Backend: see [../../backend/CLAUDE.md](../../backend/CLAUDE.md); deployment: [../deployment/README.md](../deployment/README.md).
