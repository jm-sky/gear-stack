# UX: nawigacja — redundancja top bar vs sidebar

**Status:** `done`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15 — decyzja produktowa: zachować linki w top bar na dużym ekranie (wayfinding)
**Type:** improvement (design decision)  
**Severity:** low  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Obszar:** layout authenticated

## Problem

Te same linki (**Gear containers**, **All Items**, **Shopping**, **Public containers**) występują w top navigation i w sidebarze „My Gear” / „Public”. Na desktopie może to być zamierzone; na mobile zwiększa szum i scroll w sidebarze.

## Decyzja

**Zachować oba** na desktopie (`md+`) — top bar + sidebar. Użytkownik preferuje szybki dostęp z górnego paska na dużym ekranie.

Na mobile (`<md`) top nav pozostaje ukryty; nawigacja przez sidebar (off-canvas).

## Zakres

- [x] Decyzja produktowa — bez ukrywania top nav od `lg`.
- [x] `AppHeader` — `hidden md:flex` (linki od tablet/desktop w górze).

## Weryfikacja

1. Desktop — linki widoczne w top bar i w sidebarze.
2. Mobile — top nav ukryty; ścieżka przez sidebar.
