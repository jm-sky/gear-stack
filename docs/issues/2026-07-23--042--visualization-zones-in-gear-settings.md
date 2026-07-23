# UX: własne obszary wizualizacji — sekcja w `/gear/settings`

**Status:** `todo`  
**Created:** 2026-07-23  
**Updated:** 2026-07-23  
**Type:** improvement  
**Severity:** low  
**Related:** [plan: visualization DnD + zones](../plans/2026-07-22-visualization-dnd-zones.md)

**Strona:** `/gear/settings` (`GearSettingsPage`)

## Problem

W ustawieniach gear są już karty: **Własne typy kontenerów**, **Własne kategorie**, **Własne marki**. Własne obszary wizualizacji (`visualizationCustomZones`) zarządza się głównie ze strony wizualizacji — brak spójnej sekcji w settings, mimo że dane siedzą w tych samych `gear_settings`.

## Oczekiwane zachowanie

- W `/gear/settings` pojawia się karta/sekcja **Własne obszary wizualizacji** (CRUD: nazwa, ikona; usuwanie z potwierdzeniem).
- Zachowanie zgodne z istniejącym API / store (`addVisualizationZone` / `update` / `remove`).
- Opcjonalnie krótki link „Otwórz wizualizację” do mapy kontenerów.

## Zakres

- [ ] Nowa karta settings (wzór: `ContainerTypesSettingsCard` / `CategoriesSettingsCard`).
- [ ] Podpięcie pod `useGearSettings` / dual-path persistence.
- [ ] i18n PL/EN.
- [ ] Edge case: usunięcie strefy używanej w `visualizationPlacements` — komunikat / fallback do default zone (jak na stronie wizualizacji).

## Weryfikacja

1. `/gear/settings` — sekcja widoczna obok typów/kategorii/marek.
2. Dodanie / edycja / usunięcie strefy synchronizuje się ze stroną wizualizacji.
3. Offline (localStorage) i online (API) bez rozjazdu.
