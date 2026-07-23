# UX: dialog „Dodaj kontener” — wyszukiwanie i recent / unifikacja z „Dodaj przedmiot”

**Status:** `todo`  
**Created:** 2026-07-23  
**Updated:** 2026-07-23  
**Type:** improvement  
**Severity:** medium  
**Related:** [#006](2026-07-05--006--add-existing-item-tab-ux.md) (zakładka istniejącego przedmiotu/kontenera na stronie dodawania)

**Strona:** `/gear/:id` → dialog `AddNestedContainerDialog` („Dodaj kontener”)

## Problem

Dialog zagnieżdżania istniejącego kontenera jest mało wygodny: ComboBox wymaga otwarcia, brak szybkiego podglądu ostatnio używanych kontenerów. Przy dłuższej liście trudno znaleźć cel.

## Do ustalenia (kierunek)

**A)** Ujednolicić ścieżkę: dodawanie kontenerów i przedmiotów z jednego miejsca — strona „Dodaj przedmiot” (`/gear/:containerId/items/new`), w duchu #006 (zakładka „Mój istniejący…”) — wtedy dialog na stronie kontenera staje się zbędny lub cienkim wrapperem.

**B)** Zostawić dialog, ale go poprawić:

- Wyszukiwarka **widoczna od razu** (nie dopiero po otwarciu ComboBox).
- Sekcja **3 ostatnio dodane / zmienione** kontenery (po `updatedAt` / `createdAt`), klik = wybór.
- Reszta listy poniżej (filtrowana).

## Zakres (po wyborze A lub B)

- [ ] Decyzja produktowa: A vs B (ew. A długoterminowo + B jako quick win).
- [ ] Implementacja wybranej ścieżki.
- [ ] Spójność z #006 (nie dublować dwóch pełnych UI do tej samej akcji).
- [ ] Empty / „brak dostępnych” — powiązane z #005.

## Weryfikacja

1. Z poziomu kontenera da się szybko znaleźć i zagnieździć istniejący kontener.
2. Mobile: wyszukiwanie i recent używalne bez poziomego scrolla.
3. Brak regresji w nesting (cykle / subtree exclusion jak dziś w dialogu).
