# Brakuje eksportu do JSON

**Status:** `done`  
**Created:** 2026-07-05  
**Updated:** 2026-07-06

**Strona:** `/gear`

## Objaw

Dostępny jest eksport do Markdown i CSV, ale nie ma opcji eksportu do JSON.

## Poprawka

Dodano akcję „Eksport do JSON" w dropdownie. Eksport buduje drzewo kontenerów
z zagnieżdżonymi dziećmi (V2) i pobiera plik `.json` bez dodatkowego dialogu.

## Pliki

- `src/modules/gear/utils/exportToJsonV2.ts` (nowy)
- `src/modules/gear/components/ContainersListPageDropdown.vue`
- `src/modules/gear/pages/ContainersListPage.vue`
- `src/modules/gear/utils/actionIcons.ts`
- `src/modules/gear/i18n/index.ts`
