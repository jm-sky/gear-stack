# UX: checkbox „Show on Container” — widoczny disabled z notką dev

**Status:** `verification needed`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15 — fix w branchu `fix/ux-review-simple-medium` (pole usunięte z `ItemFormFields`)
**Type:** improvement  
**Severity:** low  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Strona:** `/gear/:id/items/new` (i edit item jeśli ten sam formularz)

## Problem

Checkbox **Show on Container** jest disabled z opisem *„Implementation postponed”* — mylące w UI produkcyjnym; sugeruje niedokończoną funkcję.

## Oczekiwane zachowanie

Ukryć pole do czasu implementacji lub oznaczyć jako „Coming soon” bez surowej notki technicznej.

## Zakres

- [x] Item form — warunek feature flag / usuń z UI.
- [ ] Roadmap — link do planu galerii obrazków jeśli istnieje.

## Weryfikacja

1. Formularz add/edit item — brak disabled pola z dev copy (lub czytelny premium/soon badge).
