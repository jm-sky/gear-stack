# A11y: paginacja — przycisk „rows per page” bez opisowej nazwy

**Status:** `todo`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15  
**Type:** bug (accessibility)  
**Severity:** medium  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Strony:** `/gear`, `/gear/items`, tabela na `/gear/:id`

## Problem

Trigger wyboru liczby wierszy na stronę jest eksponowany w a11y jako samo **„12”**, **„20”**, **„10”** — bez kontekstu „Rows per page”. Tekst „Rows per page” jest widoczny wizualnie, ale nie w accessible name przycisku.

## Oczekiwane zachowanie

`aria-label="Rows per page: 12"` lub `aria-labelledby` łączący widoczny label z kontrolką.

## Zakres

- [ ] Wspólny komponent paginacji / data-table footer.
- [ ] Wszystkie miejsca używające tego wzorca.

## Weryfikacja

1. Snapshot na `/gear` i `/gear/items` — przycisk ma pełną nazwę.
2. VoiceOver/NVDA — kontekst zrozumiały bez patrzenia na ekran.
