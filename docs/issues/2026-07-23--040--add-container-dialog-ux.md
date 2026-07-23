# UX: dialog „Dodaj kontener” — wyszukiwanie i recent / unifikacja z „Dodaj przedmiot”

**Status:** `done`  
**Created:** 2026-07-23  
**Updated:** 2026-07-23  
**Type:** improvement  
**Severity:** medium  
**Related:** [#006](2026-07-05--006--add-existing-item-tab-ux.md) (zakładka istniejącego przedmiotu/kontenera na stronie dodawania)

**Strona:** `/gear/:id` → dialog `AddNestedContainerDialog` („Dodaj kontener”)

## Problem

Dialog zagnieżdżania istniejącego kontenera jest mało wygodny: ComboBox wymaga otwarcia, brak szybkiego podglądu ostatnio używanych kontenerów. Przy dłuższej liście trudno znaleźć cel.

## Decyzja

**B)** Zostawiony dialog, poprawiony UX (quick win). Unifikacja A / zakładka kontenerów na `ItemFormPage` zostaje przy #006.

## Zakres

- [x] Decyzja produktowa: B (quick win); A długoterminowo przy #006.
- [x] Wyszukiwarka widoczna od razu + sekcja 3 ostatnie + lista filtrowana.
- [x] Spójność z #006 (nie dublować pełnego UI — dialog pozostaje ścieżką nest).
- [x] Empty / „brak dostępnych” — zachowane `noContainersAvailable` + subtree exclusion.

## Weryfikacja

1. Z poziomu kontenera da się szybko znaleźć i zagnieździć istniejący kontener.
2. Mobile: wyszukiwanie i recent używalne bez poziomego scrolla.
3. Brak regresji w nesting (cykle / subtree exclusion jak dziś w dialogu).
