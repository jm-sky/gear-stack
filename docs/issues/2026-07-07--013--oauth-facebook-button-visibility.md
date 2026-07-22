# OAuth Facebook — widoczność przycisku niezależnie od Google

**Status:** `done`  
**Created:** 2026-07-07  
**Moduł:** `auth` (shared core)  
**Backport:** [backport-progress.md](../../../.docs/backport-progress.md) — po fixie w gear-stack propagować do core_family

## Problem

W formularzach logowania i rejestracji sekcja OAuth jest warunkowana wyłącznie `config.oauth.google.enabled`. Gdy Google jest skonfigurowany, renderowany jest też `OAuthFacebookButton` — nawet bez `VITE_FACEBOOK_OAUTH_CLIENT_ID`.

Dotyczy:

- `src/modules/auth/components/LoginForm.vue` (linia ~112)
- `src/modules/auth/components/RegisterForm.vue` (linia ~108)

```vue
<template v-if="config.oauth.google.enabled">
  ...
  <OAuthGoogleButton />
  <OAuthFacebookButton />
</template>
```

`useOAuth.ts` ma już `isFacebookEnabled` (`config.oauth.facebook.enabled`), ale nie jest używany w szablonach.

## Oczekiwane zachowanie

| Warunek | Efekt |
|---------|--------|
| Tylko Google skonfigurowany | Separator OAuth + przycisk Google |
| Tylko Facebook skonfigurowany | Separator OAuth + przycisk Facebook |
| Oba skonfigurowane | Separator + oba przyciski |
| Żaden | Brak sekcji OAuth |

Każdy przycisk zależy wyłącznie od własnego providera:

- `OAuthGoogleButton` → `v-if="config.oauth.google.enabled"`
- `OAuthFacebookButton` → `v-if="config.oauth.facebook.enabled"`

Sekcja (separator „or continue with”):

```vue
v-if="config.oauth.google.enabled || config.oauth.facebook.enabled"
```

## Wzorzec (już częściowo w zbory-chwz)

`zbory-chwz/src/modules/auth/components/LoginForm.vue` ma poprawny wzorzec — użyć go w gear-stack i pozostałych formularzach.

## Zakres zmian

- [ ] `LoginForm.vue` — warunek sekcji + `v-if` na przyciskach
- [ ] `RegisterForm.vue` — j.w.
- [ ] Backport do: AI-workspace, family-recipes, ops-monitor, zbory-chwz (`RegisterForm` nadal ma błąd)

## Weryfikacja

1. Tylko `VITE_GOOGLE_OAUTH_CLIENT_ID` — widoczny tylko Google
2. Tylko `VITE_FACEBOOK_OAUTH_CLIENT_ID` — widoczny tylko Facebook
3. Oba — oba przyciski
4. Żaden — brak sekcji OAuth na `/login` i `/register`
