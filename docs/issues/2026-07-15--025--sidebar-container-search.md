# UX: sidebar — brak wyszukiwania przy długiej liście kontenerów

**Status:** `todo`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15  
**Type:** improvement  
**Severity:** medium  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md), [#018](2026-07-15--018--sidebar-duplicate-container-names.md)

**Obszar:** sidebar „Containers”

## Problem

Przy 30+ kontenerach lista w sidebarze wymaga długiego scrolla bez wyszukiwania ani filtrowania. Ulubione (favorites) są na kartach listy `/gear`, ale nie w sidebarze.

## Oczekiwane zachowanie

Szybki dostęp do kontenera po nazwie lub z sekcji „Pinned / Favorites”.

## Propozycje

- Mini search w sekcji Containers (debounced).
- Sekcja „Favorites” na górze listy sidebar.
- Collapse grup rarely-used (opcjonalnie).

## Zakres

- [ ] Layout sidebar gear module.
- [ ] Persist pinned/favorites jeśli już istnieje w store — reuse.

## Weryfikacja

1. 20+ kontenerów — znalezienie po 2–3 znakach nazwy.
2. Mobile — search nie psuje off-canvas sidebar.
