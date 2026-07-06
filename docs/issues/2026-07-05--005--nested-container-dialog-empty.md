# Dialog „Dodaj kontener" (nesting) pokazuje „Brak dostępnych kontenerów"

**Status:** `todo`  
**Created:** 2026-07-05  
**Updated:** 2026-07-06  
**Related:** V1→V2 migration ([migration-v1-to-v2.md](../migration-v1-to-v2.md))

**Strona:** `/gear/:id` (np. `/gear/01KAP9SZH1X1F460J6FN06C822` – „Bagażnik") → dialog „Dodaj kontener"

## Objaw

Próba zagnieżdżenia istniejącego kontenera (np. „Plecak Helikon EDC Cordura")
w „Bagażniku" – dialog pokazuje „Brak dostępnych kontenerów do zagnieżdżenia", mimo że
ten kontener jest na liście `/gear`.

## Przyczyna

Rozjazd V1/V2. `AddNestedContainerDialog.vue` czyta `containers` z `useGear()`
(store V1), a `ContainerDetailPage` jest już zmigrowany na V2 i **nie zasila store'a V1**.
Gdy wchodzi się prosto na stronę kontenera, store V1 jest pusty → lista dostępnych
kontenerów jest pusta. Dialog używa też V1-owego pola `container.type` i `getAllNestedContainers`
operującego na typach V1.

## Sugerowana poprawka

Zmigrować dialog na V2 (`useGearV2()`/store V2, `containerType`,
V2-owa wersja wykluczania zagnieżdżeń). Część Kroku 1 migracji V1→V2
(`docs/migration-v1-to-v2.md`).

## Pliki

- `src/modules/gear/components/AddNestedContainerDialog.vue`
- `src/modules/gear/utils/containerNesting.ts`
