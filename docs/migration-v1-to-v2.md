# Plan migracji warstwy danych gear: V1 → V2

Cel: usunąć legacy warstwę „V1" modułu gear i oprzeć wszystko na V2 (unified model).
Nie dbamy o kompatybilność wsteczną z V1.

## Status: ✅ UKOŃCZONE (2026-06-13)

Migracja zakończona — **warstwa V1 całkowicie usunięta**, cały moduł gear działa na V2.
Type-check, ESLint i 359 testów jednostkowych przechodzą; `pnpm build` (PWA) OK.

Usunięto: `useGear` + `internal/*`, serwisy V1 (`gearContainerService`, `gearItemService`,
`gearItemHybridService`, `gearItemLocalService`, `gearContainerLocalService`, `gearItemApiService`,
`migrationV1toV2Service`), `store/useGearStore`, utils V1 (`getAllItems`, `containerCalculations`,
`migrationHelpers`) + ich specy.

Zostawiono (świadomie): `gear.types.ts` (wspólne uniony/enumy), `gearContainerApiService`
(ratingi/raporty kontenerów publicznych — brak odpowiednika V2), `v1ToV2Migration`
(transparentna migracja localStorage V1→V2 przy starcie store'a V2), `dataMigrationService`
(upload danych offline → API, przepisany na V2).

> Historyczny opis planu poniżej — zachowany jako dokumentacja procesu.

---

## (Archiwum) Status w trakcie (2026-06-12)

Aplikacja była w spójnym, działającym stanie hybrydowym — zmigrowane komponenty używały V2,
niezmigrowane działały na V1.

**Zrobione:**
- ✅ Faza 0: `useGearMutations` (keystone — mutacje V2 + inwalidacja cache)
- ✅ Komponenty mutujące: `ItemHeaderName`, `ItemHeaderActions`, `ContainerHeader`,
  `ContainersListPageDropdown` (delete-all → V2), `ContainerDetailPage` (pełny V2:
  mutacje, batchUpdateOrder, re-parenting zagnieżdżonych kontenerów, refresh przez invalidację)
- ✅ Strony formularzy: `ContainerFormPage`, `ItemFormPage`, `ContainerShareTokensPage`
  → `useContainerV2`; `ItemFormPage` ładuje przez `useGearV2().getItemById`
- ✅ Composable: `useItemImage` (primaryImageUrl w store V2 + invalidacja),
  `useItemsParamRecognition` (typy V2 + `useGearMutations`)
- ✅ Eksport JSON (`exportToJsonV2`) z `/gear`

**Zrobione (cd.):**
- ✅ Pickery kontenerów dual-path (API/localStorage): `AddNestedContainerDialog` (fix bug #5),
  `MoveItemDialog`, `AddCatalogueItemToContainerDialog`
- ✅ Wyświetlanie zagnieżdżonych kontenerów: `ItemsTable` dociąga dzieci wnuków i liczy wagę na V2;
  `ItemsTableImageCell` na store V2
- ✅ Luki funkcjonalne na V2 (z testami jednostkowymi): **clone** (`cloneContainerV2`),
  **import/eksport JSON** (`importFromJsonV2` + `exportToJsonV2`), **odczyt katalogu**
  (`getAllItemsForCatalogV2` + `useItemCatalogV2`)
- ✅ `useCatalogue` — usunięto martwą synchronizację store'a V1, polega na inwalidacji cache
- ✅ `AppSidebar` + `SidebarMenuContainerItem` na V2

**Potwierdzone:** `migrateV1ToV2()` uruchamia się przy inicjalizacji store'a V2 → dane offline
(z localStorage V1, klucz `gear-stack:containers`) są transparentnie migrowane do V2
(`gear-stack:items-v2`). Dzięki temu ścieżka offline na V2 (`useGearV2` → serwis lokalny) działa.

**Zrobione (cd. 2):**
- ✅ `ShoppingPlanningPage` (widok V1-shaped z V2 przez konwertery; create/update przez `useGearMutations`)
- ✅ Read-only: `DashboardPage`, `AllItemsPage` (reużywa `getAllItemsForCatalogV2`), `LocalContainersStats`,
  `TotalsStats`, `statsLocalService`, `ai/useAiContext`, `LandingPage`
- ✅ Ścieżka zapisu AI: `ai/useAiActions` → `useGearMutations`
- ✅ Usunięto martwe composable V1: `useItem`, `useContainer`, `useInlineItemEditing`

**Pozostało — jedyny blocker finalnego usunięcia V1: feature „migracja danych lokalnych → API":**
- ⏳ `services/dataMigrationService.ts` (czyta store V1, uploaduje do API) + konsumenci:
  `useDataMigration`, `useDataMigrationModal`, `DataMigrationDialog`
- ⏳ `shared/utils/appInit.ts` — bootstrap store'a V1 (potrzebny tylko przez dataMigrationService;
  migracja localStorage V1→V2 i tak idzie przez `migrateV1ToV2()` w store V2, nie przez appInit)
- ⏳ Po zmigrowaniu powyższego: **Faza 4** — usunąć `useGear`, `internal/*`, serwisy V1
  (`gearContainerService`, `gearItemService`, `gearItemHybridService`, `gearItemLocalService`,
  `gearContainerLocalService`), `store/useGearStore`, `dataMigrationService`, `migrationV1toV2Service`,
  oraz specy V1. **Zostają**: `gear.types.ts` (wspólne uniony), `gearContainerApiService` (ratingi/raporty public).

> Uwaga: feature dataMigration to upload danych offline na backend — wymaga weryfikacji
> (zalogowanie z danymi w localStorage). Robić ostrożnie jako osobne zadanie.

> Główna przyczyna błędów ze „stale UI": mutacje przez V1 (lub przez `useGearV2()`
> bez inwalidacji) nie odświeżają cache TanStack Query (`gearQueryKeys`). Strona `/gear`
> renderuje z tego cache. Patrz [docs/issues/README.md](issues/README.md) (V1/V2 stale UI bugs).

## Architektura (stan obecny)

- **V1:** `useGear()` (fasada) → `internal/` (`useContainerOperations`, `useItemOperations`,
  `useContainerCalculations`, `useContainerImportExport`, `useItemCatalog`) → serwisy
  (`gearContainerService`, `gearItemService`/`GearItemHybridService`/`GearItemLocalService`,
  `gearContainerApiService`, `gearContainerLocalService`) → Pinia `useGearStore`.
  Typy encji: `IGearContainer`/`IGearItem` w `gear.types.ts`.
- **V2:** `useGearV2()` + hooki TanStack `useGearQueries.ts` → `gearItemApiServiceV2`/
  `gearItemLocalServiceV2` → Pinia `useGearStoreV2`. Typy: `IGearItemV2` w `gear.types.v2.ts`.
  Klucze cache: `gearQueryKeys` w `utils/queryKeys.ts`. Fasady V2: `internal/v2/*`.

**Uwaga o typach:** `gear.types.ts` trzyma też współdzielone uniony/enumy
(`TGearItemCategory`, `TContainerColor`, `TGearItemStatus`, `TGearWeightUnit`,
`TGearContainerType`, `TGearItemQuality`, `IShelfLife`, `GEAR_ITEM_CATEGORIES`, ...),
które są **re-eksportowane przez `gear.types.v2.ts`** i używane w całej apce.
Tego pliku **NIE usuwamy** — V1-specyficzne są tylko encje/DTO
(`IGearContainer`, `IGearItem`, `I*ContainerDto`, `I*ItemDto`, `IGearItemService`).

## Inwentarz użycia V1

### Komponenty/strony mutujące przez V1 (źródło widocznych bugów)
- `src/modules/gear/pages/ShoppingPlanningPage.vue` — `createItem`, `updateItem`
- `src/modules/gear/pages/ContainerDetailPage.vue` — miks V1/V2 (`useGear`, `useGearStore`, `gearItemService`)
- `src/modules/gear/components/ItemHeaderActions.vue` — `moveItem`
- `src/modules/gear/components/ItemHeaderName.vue` — `updateItem`
- `src/modules/gear/components/ContainerHeader.vue` — `deleteContainer`/`updateContainer`
- `src/modules/gear/components/ContainersListPageDropdown.vue` — `deleteAllContainers` (już częściowo na V2 po fixie #1–#3)
- `src/modules/gear/components/CloneContainerDialog.vue` — `cloneContainer` (brak V2)
- `src/modules/gear/pages/ItemFormPage.vue` — `gearItemService()` (miks z V2)

### Komponenty/strony czytające przez V1
- `src/pages/DashboardPage.vue`, `src/components/layout/AppSidebar.vue`
- `src/modules/gear/pages/AllItemsPage.vue`
- `MoveItemDialog.vue`, `AddNestedContainerDialog.vue`, `AddCatalogueItemToContainerDialog.vue`
- `ItemsTable.vue` (miks), `items-table/ItemsTableImageCell.vue`
- `ItemCatalogSelector.vue`, `catalogue/GlobalCatalogueSelector.vue`

### Composable wrapujące V1
- `useItem.ts`, `useContainer.ts`, `useItemImage.ts`, `useInlineItemEditing.ts`
  (twin `useInlineItemEditingV2.ts` istnieje), `useItemsParamRecognition.ts`,
  `useJsonImportExport.ts`, `catalogue/useCatalogue.ts`

### Konsumenci spoza modułu gear
- `src/modules/stats/services/statsLocalService.ts` — `useGearStore`
- `src/modules/ai/composables/useAiContext.ts`, `useAiActions.ts` (mutuje przez V1!)
- `src/pages/LandingPage.vue`, `LocalContainersStats.vue`, `TotalsStats.vue`
- `src/shared/utils/appInit.ts` (bootstrap)

## Mapowanie V1 → V2 i luki

| Możliwość V1 | Odpowiednik V2 | Status |
|---|---|---|
| `useGear().containers` | `useGearV2().containers` / `useContainers()` | ✅ |
| CRUD kontenerów | `useContainerOperationsV2()` (inwaliduje `['gear']`) | ✅ |
| CRUD itemów / move | `useGearV2()` / `useItemOperationsV2()` | ✅ (luka: inwalidacja) |
| getContainerById/root/nested | `useContainerOperationsV2()` / `useContainer()` | ✅ |
| Kalkulacje | `useContainerCalculationsV2()` + `utils/containerCalculationsV2.ts` | ✅ |
| `useItem()` / `useContainer()` | `useContainerV2.ts` istnieje; **brak `useItemV2`** | ⚠️ |
| `useInlineItemEditing` | `useInlineItemEditingV2.ts` | ✅ |
| `getAllItemsForCatalog` / `getItemWithContainer` | — | ❌ luka |
| `exportData` / `importData` (JSON) | częściowo: eksport JSON z `/gear` zrobiony (`exportToJsonV2.ts`); **import JSON brak** | ⚠️ |
| `cloneContainer` | — | ❌ luka |
| Sample/example gear (`sampleSetGenerator`) | — | ❌ luka (pisze przez V1) |
| stats/AI czytające `useGearStore` | muszą czytać `useGearStoreV2` | ⚠️ |

### Luki do zbudowania przed usunięciem V1
1. **Import JSON** na V2 (eksport JSON już jest).
2. **Clone container** na V2 (głęboka kopia poddrzewa z nowymi ID).
3. **Czytanie katalogu** (`getAllItemsForCatalog`/`getItemWithContainer`) na V2 store.
4. **Generowanie sample/example gear** przez `useGearV2().createItem`.
5. **Ścieżka zapisu AI** (`useAiActions.ts`) na V2 + inwalidacja.
6. **`useItemV2`** — twin `useItem()`.

## Rekomendowana kolejność migracji

**Faza 0 — `useGearMutations` (zrobić najpierw, keystone).**
Nowy `composables/useGearMutations.ts` opakowujący create/update/delete/move/batchUpdateOrder
z `useGearV2()`, każdy z **celowaną** inwalidacją `gearQueryKeys` (np. `container(parentId)`,
`children(parentId)`, `itemsFiltered({itemType:'container',parentItemId:null})` zamiast
tępego `['gear']`). `useItemOperationsV2`/`useContainerOperationsV2` powinny przez to przechodzić.
Najlepiej `useMutation` z `onSuccess`. To samo w sobie likwiduje klasę bugów ze stale cache.

**Faza 1 — przełączyć komponenty mutujące na V2** (kolejność wg zasięgu):
`useItem.ts`→`useItemV2`, `useContainer.ts`→`useContainerV2`, `ItemHeaderName/Actions`,
`ContainerHeader`, `ContainersListPageDropdown` (delete-all przez `useContainerOperationsV2`),
`useItemImage`/`useItemsParamRecognition`/`useInlineItemEditing`, `ShoppingPlanningPage`,
dokończyć `ContainerDetailPage`, `ItemFormPage`.

**Faza 2 — zbudować luki** (import JSON, clone, katalog, sample gear), potem ich konsumentów.

**Faza 3 — konsumenci read-only na `useGearStoreV2`/queries:**
Dashboard, AppSidebar, AllItemsPage, dialogi list kontenerów, oraz cross-module
(stats, ai, landing, statystyki, appInit).

**Faza 4 — usunąć martwą warstwę V1** (lista niżej), poprawić testy. Zostawić wspólne uniony w `gear.types.ts`.

## Pliki do usunięcia (po migracji)

`composables/useGear.ts`, całe `composables/internal/` (V1), `useItem.ts`, `useContainer.ts`,
`useInlineItemEditing.ts`, `useJsonImportExport.ts` (lub przepisać na V2);
serwisy `gearContainerService.ts`, `gearItemService.ts`, `gearItemHybridService.ts`,
`gearItemLocalService.ts`, `gearContainerLocalService.ts`, `dataMigrationService.ts`,
`migrationV1toV2Service.ts`/`v1ToV2Migration.ts` (po rolloucie); `store/useGearStore.ts`;
specy V1 (`gearContainerService.spec.ts`, `gearItemHybridService.spec.ts`,
`gearContainerLocalService.spec.ts`, `gearItemLocalService.spec.ts`, `containerCalculations.spec.ts`).

**NIE usuwać:**
- `types/gear.types.ts` — źródło współdzielonych unionów (opcjonalnie wyciąć tylko encje/DTO V1).
- `services/gearContainerApiService.ts` — wciąż obsługuje public-container ratings/reports (brak V2).
- `utils/typeConverters.ts` — przydatne w trakcie migracji.
- `sampleSetGenerator.ts`/`exampleSets.ts` — do czasu portu generatora na V2.
