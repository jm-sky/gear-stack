# UX: strona „Dodaj przedmiot” — layout (marginesy) + research designu formularza

**Status:** `todo`  
**Created:** 2026-07-23  
**Updated:** 2026-07-23  
**Type:** improvement  
**Severity:** medium  
**Related:** [#006](2026-07-05--006--add-existing-item-tab-ux.md), [#021](2026-07-15--021--add-item-form-combobox-labels.md)

**Strona:** `/gear/:containerId/items/new` (`ItemFormPage`)

## Problem

1. **Layout:** treść formularza jest wyśrodkowana na środku karty — po bokach powstają szerokie białe (puste) marginesy; na desktopie marnuje się szerokość viewportu.
2. **Design formularza:** długi, gęsty formularz; warto sprawdzić, czy sekcje / inny układ poprawią skanowalność i tempo wypełniania.

## Oczekiwane zachowanie

- Formularz wykorzystuje dostępną szerokość sensowniej (np. pełniejszy kontener, dwukolumnowy układ pól na `md+`, mniej „wąskiej kolumny na środku”).
- Hierarchia pól czytelna (grupy: tożsamość, waga/ilość, status, opcjonalne…).

## Research (przed implementacją)

- [ ] Screenshots obecnego UI (desktop + mobile).
- [ ] Porównanie z 1–2 wzorcami (LighterPack, inne gear/inventory forms) — sekcje, sticky submit, progressive disclosure.
- [ ] Krótka notatka w `docs/research/` lub w tym issue: rekomendowany układ + co zostaje bez zmian.

## Zakres implementacji (po research)

- [ ] Layout wrapper strony / karty — szerokość, padding, grid.
- [ ] Ewentualne sekcje / collapsible grupy pól (bez zmiany modelu danych).
- [ ] Spójność z edycją przedmiotu (ten sam `ItemFormPage`).

## Weryfikacja

1. Desktop: brak zbędnych szerokich pustych pasów po bokach formularza.
2. Mobile: pola nadal w jednej kolumnie, CTA submit dostępne.
3. A11y: etykiety / focus order bez regresji względem #021.
