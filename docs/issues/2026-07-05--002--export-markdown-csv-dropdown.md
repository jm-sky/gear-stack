# Eksport do Markdown / CSV z dropdownu nic nie robi

**Status:** `done`  
**Created:** 2026-07-05  
**Updated:** 2026-07-06

**Strona:** `/gear` (dropdown „more actions")

## Objaw

Pozycje „Eksport do Markdown" i „Eksport do CSV" w menu rozwijanym nie reagują.
Przycisk eksportu obok dropdownu (poza menu) działa i otwiera dialog.

## Przyczyna

Niezgodność nazw eventów między komponentem a stroną:

- Dropdown emituje `exportAllToMarkdown`, a strona nasłuchuje `@export-all-to-prompt` — inne nazwy.
- Dropdown emituje `exportAllToCSV`, a strona nasłuchuje `@export-all-to-csv` — `CSV`
  (kolejne wielkie litery) kebab-uje się do `export-all-to-c-s-v`, więc też nie pasuje.

## Poprawka

Ujednolicono nazwy eventów (`exportAllToMarkdown` / `exportAllToCsv` /
`exportAllToJson`) i podpięto poprawne listenery na stronie
(`@export-all-to-markdown`, `@export-all-to-csv`, `@export-all-to-json`). Dodatkowo
dropdown czyta teraz listę kontenerów z V2 (`useGearV2()`), spójnie ze stroną.

## Pliki

- `src/modules/gear/components/ContainersListPageDropdown.vue`
- `src/modules/gear/pages/ContainersListPage.vue`
