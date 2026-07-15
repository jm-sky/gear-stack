# UX: nawigacja — redundancja top bar vs sidebar

**Status:** `todo`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15  
**Type:** improvement (design decision)  
**Severity:** low  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Obszar:** layout authenticated

## Problem

Te same linki (**Gear containers**, **All Items**, **Shopping**, **Public containers**) występują w top navigation i w sidebarze „My Gear” / „Public”. Na desktopie może to być zamierzone; na mobile zwiększa szum i scroll w sidebarze.

## Do decyzji produktowej

- Zachować oba (wayfinding z różnych miejsc)?
- Ukryć top nav linki gdy sidebar widoczny na `lg+`?
- Top nav tylko na mobile gdy sidebar zamknięty?

## Zakres (po decyzji)

- [ ] Layout authenticated — warunkowe renderowanie nav.
- [ ] Test RWD + keyboard nav.

## Weryfikacja

1. Desktop — brak zbędnej duplikacji lub uzasadniona hierarchia.
2. Mobile — jedna oczywista ścieżka do głównych sekcji.
