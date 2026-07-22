# Import z Markdown nie pokazuje nic w kontenerach (zalogowany użytkownik)

**Status:** `done`  
**Created:** 2026-07-05  
**Updated:** 2026-07-06  
**Related:** V1→V2 migration ([migration-v1-to-v2.md](../archive/v2-unified-model/migration-v1-to-v2.md))

**Strona:** `/gear` → dialog „Import z Markdown"

## Objaw

Po wklejeniu treści jest poprawny podgląd, ale po kliknięciu „Import"
w kontenerach nic się nie pojawia.

## Przyczyna

`ImportMarkdownDialog.vue` (`handleImport`) zapisuje dane **tylko do lokalnego
store'a V2** (`store.upsertItem(...)`, z fikcyjnym `userId: 'local-user'`). Nie woła w ogóle
API i nie inwaliduje cache TanStack Query. Gdy użytkownik jest zalogowany (`shouldUseAPI`),
strona `/gear` renderuje listę z danych API (`containersFromAPI`), a nie ze store'a — więc
zaimportowane elementy się nie pokazują. Dodatkowo dane nie trafiają na backend, więc po
odświeżeniu i tak ich nie ma. `handleImportComplete` na stronie jest puste
(komentarz „Refresh is automatic via store reactivity" jest nieaktualny dla trybu API).

## Poprawka

`handleImport` tworzy/aktualizuje teraz elementy przez `useGearV2()`
(`createItem`/`updateItem`), które trafiają do API gdy `shouldUseAPI`, a po zakończeniu
inwaliduje cache (`gearQueryKeys.all`). Zagnieżdżone kontenery są obsłużone natywnie w V2
przez re-parenting (`parentItemId`) zamiast tworzenia „placeholder" itemu. Tryb „update"
(resolucja po UUID) zachowany.

## Pliki

- `src/modules/gear/components/ImportMarkdownDialog.vue`
