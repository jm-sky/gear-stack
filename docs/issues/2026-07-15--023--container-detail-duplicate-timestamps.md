# UX: metadane kontenera — zduplikowany ten sam timestamp

**Status:** `verification needed`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15 — fix w branchu `fix/ux-review-simple-medium` (`hasDistinctUpdate` w `ContainerHeader`)
**Type:** improvement  
**Severity:** medium  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Strona:** `/gear/:id`

## Problem

Pod tytułem kontenera wyświetlane są **dwa identyczne** znaczniki czasu (np. „1/21/2026 03:47 PM” dwa razy) — prawdopodobnie created i updated bez etykiet, gdy wartości są równe.

## Oczekiwane zachowanie

- Gdy created === updated: jeden wpis „Created” (lub względny czas).
- Gdy różne: „Created … · Updated …” lub tooltip na względnym czasie.

## Zakres

- [x] Komponent metadanych nagłówka kontenera.
- [x] i18n: etykiety Created / Updated.

## Weryfikacja

1. Nowy kontener — jeden timestamp lub jawne etykiety.
2. Po edycji — Updated różni się od Created gdy data się zmieniła.
