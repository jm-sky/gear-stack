# A11y: baner premium — przycisk zamknięcia bez nazwy

**Status:** `todo`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15  
**Type:** bug (accessibility)  
**Severity:** low  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Strony:** `/dashboard`, `/gear`, `/gear/:id` (baner „Unlock Premium Features”)

## Problem

Przycisk zamknięcia (X) obok „View Plans” nie ma accessible name w snapshot — icon-only bez `aria-label`.

## Oczekiwane zachowanie

`aria-label="Dismiss premium banner"` (+ i18n PL).

## Zakres

- [ ] Komponent premium upsell banner (billing lub shared).
- [ ] Wzorzec jak inne icon-only buttons (`getActionIcon` / Button variant).

## Weryfikacja

1. Snapshot — nazwany przycisk dismiss.
2. Zamknięcie banera — stan zapisany (jeśli dismiss jest persistent).
