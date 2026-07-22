# UX: layout strony kontenera na mobile — pusta przestrzeń, wąska treść

**Status:** `verification needed`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15 — fix w branchu `fix/ux-review-phase-2-items` (layout + toolbar mobile)
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
- [ ] Test manualny: 375px, 768px, 1920px.

## Weryfikacja

1. Otwórz `/gear/:id` na mobile — brak pustego panelu po prawej.
2. Wszystkie primary CTA (Add Item, Back) dostępne bez poziomego scrolla całej strony.
3. Accessibility snapshot: sensowna kolejność focusu w nagłówku.
