# UX: strona „Dodaj przedmiot” — layout (marginesy) + research designu formularza

**Status:** `done`  
**Created:** 2026-07-23  
**Updated:** 2026-07-23  
**Type:** improvement  
**Severity:** medium  
**Related:** [#006](2026-07-05--006--add-existing-item-tab-ux.md), [#021](2026-07-15--021--add-item-form-combobox-labels.md)

**Strona:** `/gear/:containerId/items/new` (`ItemFormPage`)

## Problem

1. **Layout:** treść formularza jest wyśrodkowana na środku karty — po bokach powstają szerokie białe (puste) marginesy; na desktopie marnuje się szerokość viewportu.
2. **Design formularza:** długi, gęsty formularz; warto sprawdzić, czy sekcje / inny układ poprawią skanowalność i tempo wypełniania.

## Research

- [x] Diagnoza + rekomendacja: [`docs/research/2026-07-23-item-form-layout.md`](../research/2026-07-23-item-form-layout.md)
- [x] Porównanie z wzorcami (LighterPack / inventory) — sekcje, 2-col, bez collapsible w v1

## Zakres implementacji

- [x] Layout wrapper strony / karty — `max-w-4xl`, sekcje, sticky CTA.
- [x] Sekcje pól (bez zmiany modelu danych).
- [x] Spójność z edycją przedmiotu (ten sam `ItemFormPage` / `ItemFormFields`).

## Weryfikacja

1. Desktop: brak zbędnych szerokich pustych pasów po bokach formularza.
2. Mobile: pola nadal w jednej kolumnie, CTA submit dostępne.
3. A11y: etykiety / focus order bez regresji względem #021.
