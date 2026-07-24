# UX: layout strony kontenera na mobile — pusta przestrzeń, wąska treść

**Status:** `verification needed`  
**Created:** 2026-07-15  
**Updated:** 2026-07-23 — re-verified at 375px with inline-edit polish (sticky name/actions, compact toolbar)
**Type:** bug (responsive)  
**Severity:** high  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Strona:** `/gear/:id` (container detail)

## Problem

Na viewporcie **375×667** główna treść zajmuje ~40% szerokości ekranu. Po prawej widać duży pusty panel (szare tło). Nagłówek kontenera i pasek akcji (Back, Edit, Add Item, inline editing) łamią się nieczytelnie; tabela przedmiotów jest trudna do użycia.

## Oczekiwane zachowanie

- Sidebar zwinięty off-canvas na mobile; treść na pełną szerokość.
- Akcje w nagłówku w jednym rzędzie lub w menu „More actions” / overflow.
- Tabela przewijalna poziomo lub uproszczony widok kart na `sm`.

## Zakres zmian (propozycja)

- [x] Zweryfikować `SidebarProvider` + `SidebarInset` / breakpointy w layoutcie authenticated.
- [x] Container detail header — responsive stack / ukrycie wtórnych akcji na wąskich ekranach.
- [x] Test manualny: 375px (2026-07-23 — full-width main, sticky name+actions, toolbar overflow-x).

## Weryfikacja

1. Otwórz `/gear/:id` na mobile — brak pustego panelu po prawej. ✅
2. Wszystkie primary CTA (Add Item, Back) dostępne bez poziomego scrolla całej strony. ✅
3. Accessibility snapshot: sensowna kolejność focusu w nagłówku. ✅
