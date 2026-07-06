# Brak obrazków przedmiotów na liście w kontenerze

**Status:** `todo`  
**Created:** 2026-07-05  
**Updated:** 2026-07-06  
**Related:** [2026-07-05--009--catalogue-images.md](2026-07-05--009--catalogue-images.md), V1→V2 migration ([migration-v1-to-v2.md](../archive/v2-unified-model/migration-v1-to-v2.md))

**Strona:** `/gear/:id` (szczegóły kontenera) — tabela przedmiotów i/lub galeria „Item Images"

## Objaw

Na liście przedmiotów w kontenerze nie widać obrazków (kolumna Image / galeria pod
tabelą), mimo że przedmiot ma ustawiony obraz główny (main/primary image) — widoczny np.
na stronie szczegółów przedmiotu lub w edycji obrazków.

## Możliwe przyczyny (do zweryfikowania)

1. **Brak `primaryImageUrl` w odpowiedzi V2** — `ItemsTableImageCell` renderuje miniaturę z
   `row.original.primaryImageUrl`, ale API V2 (`schemas_v2.py` / `service_v2.py`) prawdopodobnie
   nie zwraca tego pola przy liście dzieci kontenera (w V1 było mapowane w `service.py`).
2. **Kolumna Image ukryta domyślnie** — `ItemsTable.vue` ma w domyślnej widoczności kolumn
   `image: false` (localStorage `ITEMS_TABLE_COLUMN_VISIBILITY_KEY`); użytkownik może nie
   widzieć kolumny mimo że dane są.
3. **Galeria wymaga `showItemImages` na kontenerze** — `ContainerItemImagesGallery` renderuje
   się tylko gdy `container.showItemImages === true`; obrazy pobierane są osobnymi requestami
   (`itemImageApiService.getImages` per item), nie z pola itemu na liście.
4. **Powiązane z [007 — container-list-not-refreshing-after-add](2026-07-05--007--container-list-not-refreshing-after-add.md)** — po dodaniu przedmiotu/obrazka lista może być nieaktualna
   (stary cache TanStack Query) do ręcznego odświeżenia.
5. **Problemy kopiowania obrazów z katalogu** — patrz [009 — catalogue-images](2026-07-05--009--catalogue-images.md)
   (FK violation przy `item_images` — obraz może nie trafić do bazy mimo sukcesu API).

## Sugerowana poprawka

Dodać `primaryImageUrl` do odpowiedzi V2 (lista dzieci / batch),
ew. wzbogacić `useContainerWithChildren`; rozważyć domyślną widoczność kolumny Image gdy
kontener ma `showItemImages`; po mutacjach inwalidować cache. Powiązane z migracją V2.

## Pliki

- `src/modules/gear/components/ItemsTable.vue`
- `src/modules/gear/components/items-table/ItemsTableImageCell.vue`
- `src/modules/gear/components/ContainerItemImagesGallery.vue`
- `src/modules/gear/pages/ContainerDetailPage.vue`
- `backend/app/modules/gear/schemas_v2.py`
- `backend/app/modules/gear/service_v2.py`
