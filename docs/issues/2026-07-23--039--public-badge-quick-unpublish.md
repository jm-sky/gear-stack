# UX: badge `Public` — szybkie cofnięcie publikacji

**Status:** `todo`  
**Created:** 2026-07-23  
**Updated:** 2026-07-23  
**Type:** improvement  
**Severity:** low  

**Strona:** `/gear/:id` (container detail)

## Problem

Gdy kontener jest publiczny, w nagłówku pojawia się badge `Public` (`PublicContainerBadge`). To tylko status — żeby cofnąć publikację trzeba iść w edycję / menu akcji. Brak szybkiej ścieżki „unpublish”.

## Oczekiwane zachowanie

Jedna z opcji (do wyboru przy implementacji):

1. **Dropdown na badge** — klik otwiera menu z akcją „Cofnij publikację” (ew. „Skopiuj link publiczny”).
2. **Hover / focus: `X`** — dyskretny dismiss na badge, z potwierdzeniem lub toastem undo.

Badge nadal komunikuje status; akcja unpublish jest 1–2 kliknięcia od widoku kontenera.

## Zakres

- [ ] `PublicContainerBadge.vue` + nagłówek (`ContainerHeader.vue`) — interakcja badge.
- [ ] Wywołanie istniejącego update `isPublic: false` (API / V2).
- [ ] i18n (PL/EN) dla akcji i ewentualnego potwierdzenia.
- [ ] A11y: klawiatura / `aria-label` na dismiss lub trigger dropdownu.

## Weryfikacja

1. Publiczny kontener — badge widoczny; da się cofnąć publikację bez wchodzenia w Edit.
2. Po unpublish badge znika; kontener nie jest już w `/gear/public`.
3. Mobile: akcja osiągalna (nie tylko hover).
