# A11y: niespójne aria-label przycisków sidebar toggle

**Status:** `verification needed`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15 — fix w branchu `fix/ux-review-simple-medium` (`SidebarRail` → `common.toggleSidebar`)
**Type:** bug (accessibility)  
**Severity:** low  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Obszar:** layout authenticated (global chrome)

## Problem

W accessibility snapshot występują dwa przyciski: **„Toggle Sidebar”** i **„Toggle sidebar”** (różna wielkość liter). Prawdopodobnie duplikat kontrolki lub niespójne i18n.

## Oczekiwane zachowanie

Jedna kontrolka toggle lub spójny `aria-label` z jednego klucza tłumaczenia.

## Zakres

- [x] Sidebar trigger w layout + ewentualny duplikat w headerze.
- [x] i18n `navigation.toggleSidebar` (lub equivalent).

## Weryfikacja

1. Snapshot — jeden toggle lub identyczne labele.
2. Klawiatura — jedna ścieżka do otwarcia/zamknięcia sidebar.
