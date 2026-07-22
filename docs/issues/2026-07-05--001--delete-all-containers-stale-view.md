# „Delete All Containers" nie usuwa kontenerów z widoku

**Status:** `done`  
**Created:** 2026-07-05  
**Updated:** 2026-07-06  
**Related:** V1→V2 migration ([migration-v1-to-v2.md](../archive/v2-unified-model/migration-v1-to-v2.md))

**Strona:** `/gear` (dropdown „more actions")

## Objaw

Po kliknięciu „Delete all containers" kontenery są dalej widoczne na liście,
ale sama akcja znika z menu.

## Przyczyna

Rozjazd V1/V2. Lista strony (`ContainersListPage.vue`) renderuje dane z
TanStack Query (V2), a dropdown (`ContainersListPageDropdown.vue`) usuwał przez V1
(`useGear()`), który kasował kontenery na backendzie i czyścił store V1 (przez co znikało
menu), ale **nie inwalidował cache V2** — dlatego karty zostawały do odświeżenia strony.
Dodatkowo `deleteAllContainers()` nie był `await`-owany.

## Poprawka

`handleDeleteAll` jest teraz `async`, `await`-uje usunięcie, czyści store V2
(`storeV2.clearAll()`) i inwaliduje cache (`queryClient.invalidateQueries({ queryKey: gearQueryKeys.all })`).

## Pliki

- `src/modules/gear/components/ContainersListPageDropdown.vue`
