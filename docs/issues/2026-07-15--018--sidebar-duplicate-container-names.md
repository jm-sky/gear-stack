# UX: sidebar — identyczne nazwy kontenerów (wayfinding)

**Status:** `verification needed`  
**Created:** 2026-07-15  
**Updated:** 2026-07-15 — fix w branchu `fix/ux-review-simple-medium` (disambiguatory w `SidebarMenuContainerItem`)
**Type:** improvement  
**Severity:** medium  
**Related:** [UX review 2026-07-15](../reviews/2026-07-06-ux.md)

**Obszar:** sidebar „Containers” na wszystkich stronach authenticated

## Problem

W sidebarze wiele kontenerów ma tę samą nazwę (np. **6× „Do zakupu”**, **2× „Legenda dla AI”**). W drzewie dostępności i wizualnie użytkownik nie rozróżnia, który link otwiera — ryzyko pomyłki przy nawigacji klawiaturą i czytnikami ekranu.

## Oczekiwane zachowanie

Każdy wpis w sidebarze jest jednoznaczny bez zgadywania.

## Propozycje rozwiązania

- Dodać disambiguatory: ikona typu, liczba przedmiotów, skrócony parent path, data modyfikacji.
- Tooltip z pełną ścieżką zagnieżdżenia.
- Opcjonalnie: grupowanie kontenerów o tej samej nazwie pod wspólnym nagłówkiem.

## Zakres

- [x] Komponent listy kontenerów w sidebarze (gear module layout).
- [x] i18n — copy dla secondary label jeśli potrzebne.
- [x] Nie psuć skróconych nazw gdy są unikalne.

## Weryfikacja

1. Konto z wieloma kontenerami o tej samej nazwie — każdy wpis odróżnialny.
2. Screen reader / snapshot — unikalne `name` na linkach.
