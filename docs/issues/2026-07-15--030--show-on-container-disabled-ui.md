# UX: checkbox „Show on Container” — widoczny disabled z notką dev

**Status:** `todo`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15  
**Type:** improvement  
**Severity:** low  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Strona:** `/gear/:id/items/new` (i edit item jeśli ten sam formularz)

## Problem

Checkbox **Show on Container** jest disabled z opisem *„Implementation postponed”* — mylące w UI produkcyjnym; sugeruje niedokończoną funkcję.

## Oczekiwane zachowanie

Ukryć pole do czasu implementacji lub oznaczyć jako „Coming soon” bez surowej notki technicznej.

## Zakres

- [ ] Item form — warunek feature flag / usuń z UI.
- [ ] Roadmap — link do planu galerii obrazków jeśli istnieje.

## Weryfikacja

1. Formularz add/edit item — brak disabled pola z dev copy (lub czytelny premium/soon badge).
