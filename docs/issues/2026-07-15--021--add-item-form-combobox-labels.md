# A11y: formularz dodawania przedmiotu — comboboxy Brand/Color bez labeli

**Status:** `todo`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15  
**Type:** bug (accessibility)  
**Severity:** medium  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Strona:** `/gear/:id/items/new` (sekcja Additional Information)

## Problem

Comboboxy **Brand** i **Color** w accessibility snapshot nie mają accessible name (puste `combobox` refs). Inne pola formularza (Name, Category, …) są poprawnie oznaczone.

## Oczekiwane zachowanie

Każdy Combobox ma `<Label>` + `id` / `aria-labelledby` jak pozostałe pola.

## Zakres

- [ ] `ItemForm` / komponenty pól Brand i Color.
- [ ] Audyt pozostałych comboboxów w tym formularzu (Currency, Quality tier — sprawdzić).

## Weryfikacja

1. Snapshot add item — Brand i Color mają nazwy.
2. Edycja przedmiotu — ten sam wzorzec jeśli współdzielony formularz.
