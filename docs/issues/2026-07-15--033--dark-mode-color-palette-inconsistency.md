# UX: dark mode — niespójna temperatura koloru (slate tło vs neutralne tokeny)

**Status:** `todo`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15  
**Type:** improvement (visual design)  
**Severity:** medium  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Obszar:** dark mode — layout authenticated, tokeny CSS, sidebar

## Problem

W dark mode UI wygląda **monochromatycznie** (karty, sidebar, header na neutralnych szarościach), podczas gdy **tło głównej treści** ma wyraźny **niebieskawy** podton. Efekt: brak spójności temperatury barw i wrażenie „dwóch palet naraz”.

## Przyczyny (z kodu)

1. **`AuthenticatedLayout.vue`** — radial gradient kończy na `dark:to-slate-800` (Tailwind slate = blue-gray), podczas gdy `from-card` pochodzi z neutralnego tokena.
2. **`src/css/style.css`** — tokeny `.dark` (`--background`, `--card`, `--sidebar`) mają chroma ≈ 0 (czyste szarości oklch).
3. **`--sidebar-primary` w dark** — `oklch(… 264°)` (niebieski), podczas gdy brand `--primary` to pomarańcz (~41°). W light mode `sidebar-primary` jest neutralny.
4. **Mieszanka tokenów i hardcoded Tailwind** — np. `PageCard.vue` (`dark:bg-gray-800`), guest layouty (`dark:via-gray-800`), `--color-surface: slate-300`.

## Oczekiwane zachowanie

Jedna spójna oś kolorystyczna w dark mode: albo **neutralna** (zinc/gray, bez blue shift), albo **świadomy slate** — ale wtedy karty, sidebar i tło z tej samej rodziny. Pomarańcz (`--primary`) jako główny akcent kolorowy.

## Propozycje rozwiązania

**Opcja A (rekomendowana): neutralne tokeny wszędzie**
- Usunąć `to-slate-300` / `dark:to-slate-800` z `AuthenticatedLayout` → `to-muted` lub flat `bg-background`.
- Zastąpić `bg-surface` / hardcoded `gray-*` / `slate-*` tokenami `--background`, `--muted`, `--card`.
- W dark: `--sidebar-primary` wrócić do neutralnego (jak w light) lub ustawić na `--primary` (pomarańcz).

**Opcja B: świadomy slate theme**
- Przesunąć tokeny `.dark` na jedną rodzinę slate (np. wszystkie z hue ~250–260).
- Wymaga audytu kontrastu i chart colors.

## Zakres

- [ ] `src/layouts/AuthenticatedLayout.vue` — gradient tła
- [ ] `src/css/style.css` — `.dark` tokeny (`sidebar-primary`, ewentualnie `--muted`)
- [ ] `src/components/layout/PageCard.vue` i inne hardcoded `dark:bg-gray-*` / `slate-*`
- [ ] Guest/landing layouty — spójność z authenticated (opcjonalnie, osobny scope)
- [ ] Wizualna weryfikacja: dashboard, `/gear`, settings, login (dark)

## Weryfikacja

1. Dark mode na `/gear` i `/dashboard` — tło, karty i sidebar w jednej temperaturze barw (brak „niebieskiego” tła przy szarych panelach).
2. Aktywny element sidebar / primary CTA — spójny z brandem (pomarańcz), bez przypadkowego niebieskiego `sidebar-primary`.
3. Porównanie light ↔ dark — oba tryby równie spójne wewnętrznie.

## Notatki

Finding zidentyfikowany po review (sesja 1) na podstawie obserwacji użytkownika + analizy `style.css` i layoutów. Nie był wpisany w pierwotnej tabeli findings review.
