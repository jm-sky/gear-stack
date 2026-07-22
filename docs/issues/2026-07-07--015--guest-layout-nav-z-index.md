# GuestLayout — pasek locale/dark mode pod logo (z-index)

**Status:** `done`  
**Created:** 2026-07-07  
**Moduł:** `layouts` (shared core)  
**Backport:** wszystkie projekty z rodziny core (patrz tabela poniżej)

## Problem

Na stronie logowania (`GuestLayoutCentered`) pasek z **LocaleToggle** i **DarkModeToggle** (prawy górny róg) renderuje się **pod** logo / treścią `main`. W efekcie:

- kontrolki wyglądają jakby były „za” logo,
- `backdrop-blur-sm` na `<nav>` nie działa poprawnie (tło pod spodem to logo, nie gradient strony).

## Przyczyna

W `GuestLayoutCentered.vue` `<nav class="fixed … backdrop-blur-sm">` **nie ma `z-10`**, podczas gdy w `GuestLayoutCenteredGlass.vue` i `LandingLayout.vue` już jest. Bez `z-index` element `fixed` traci warstwę względem późniejszego `<main>` w DOM.

Plik: `src/layouts/GuestLayoutCentered.vue` (linia ~16).

## Oczekiwane zachowanie

Pasek locale + dark mode zawsze **nad** logo i kartą logowania; `backdrop-blur` rozmywa gradient tła strony.

## Zakres zmian

- [x] `src/layouts/GuestLayoutCentered.vue` — dodać `z-10` do `<nav>` (wzór: `GuestLayoutCenteredGlass.vue`)
- [x] Opcjonalnie: `relative z-0` na `<main>` dla jawnego stacking context (jak w wersji Glass)

## Backport — każde repo core

| Projekt | Issue |
|---------|-------|
| gear-stack | ten plik |
| AI-workspace | [005](../../AI-workspace/docs/issues/2026-07-07--005--guest-layout-nav-z-index.md) |
| family-recipes | [005](../../family-recipes/docs/issues/2026-07-07--005--guest-layout-nav-z-index.md) |
| ops-monitor | [007](../../ops-monitor/docs/issues/2026-07-07--007--guest-layout-nav-z-index.md) |
| zbory-chwz | [005](../../zbory-chwz/docs/issues/2026-07-07--005--guest-layout-nav-z-index.md) |

## Weryfikacja

1. `/auth/login` — pasek w prawym górnym rogu nad logo.
2. Przewiń / zmień rozmiar okna — kontrolki klikalne, blur widoczny na tle gradientu.
3. Porównaj z `GuestLayoutCenteredGlass` / landing — spójne zachowanie.
