# UX: nagłówek strony kontenera — zduplikowany Edit i przeładowany pasek akcji

**Status:** `todo`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15  
**Type:** improvement  
**Severity:** medium  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md), [#017](2026-07-15--017--container-detail-mobile-layout.md)

**Strona:** `/gear/:id`

## Problem

W toolbarze kontenera widać **dwa przyciski Edit** (wariant ikona + tekst). Obok: toggle inline editing, Add Container, Add Item, More actions — duża gęstość, szczególnie na mobile (#017).

## Oczekiwane zachowanie

- Jedna ścieżka do edycji kontenera.
- Secondary actions (export, favorites, delete…) w „More actions”.
- Primary: Add Item; secondary: Edit, Add Container — hierarchia wizualna.

## Zakres

- [ ] Komponent nagłówka container detail (gear pages).
- [ ] Uzgodnić z issue #017 (responsive overflow).

## Weryfikacja

1. Desktop — jeden Edit, czytelna hierarchia CTA.
2. Mobile — primary actions bez duplikatów.
