# Po dodaniu przedmiotu lista w kontenerze się nie odświeża

**Status:** `todo`  
**Created:** 2026-07-05  
**Updated:** 2026-07-06  
**Related:** V1→V2 migration ([migration-v1-to-v2.md](../archive/v2-unified-model/migration-v1-to-v2.md))

**Strona:** `/gear/:id` (szczegóły kontenera) → `/gear/:id/items/new` → zapis nowego przedmiotu

## Objaw

Po dodaniu przedmiotu i powrocie na stronę kontenera nowy element nie pojawia się
na liście. Trzeba ręcznie odświeżyć stronę (lub użyć akcji refresh), żeby go zobaczyć.

## Przyczyna (prawdopodobna)

Rozjazd V1/V2 — ten sam wzorzec co w bugach delete-all i import-markdown.
`ContainerDetailPage.vue` przy zalogowanym użytkowniku (`shouldUseAPI`) renderuje dzieci
z TanStack Query (`useContainerWithChildren` → `childrenFromAPI`), a `ItemFormPage.vue`
po zapisie woła `useGearV2().createItem()`, które aktualizuje tylko store V2
(`store.upsertItem`) **bez** inwalidacji cache (`gearQueryKeys.all`). Po nawigacji wstecz
strona pokazuje stare dane z cache do ręcznego odświeżenia.

## Sugerowana poprawka

Po `createItem` inwalidować cache V2
(`queryClient.invalidateQueries({ queryKey: gearQueryKeys.all })`) albo użyć
`useGearMutations().createItem()` (jak w innych miejscach na stronie kontenera — komentarz
w `ContainerDetailPage.vue` wskazuje, że mutacje z tego composable same inwalidują cache).

## Pliki

- `src/modules/gear/pages/ItemFormPage.vue`
- `src/modules/gear/composables/useGearV2.ts`
- `src/modules/gear/pages/ContainerDetailPage.vue`
