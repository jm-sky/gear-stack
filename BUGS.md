# Lista błędów do poprawy

Bieżąca lista znanych błędów. Status: `TODO` / `IN PROGRESS` / `DONE`.

---

## 1. „Delete All Containers" nie usuwa kontenerów z widoku — `DONE`

**Strona:** `/gear` (dropdown „more actions")

**Objaw:** Po kliknięciu „Delete all containers" kontenery są dalej widoczne na liście,
ale sama akcja znika z menu.

**Przyczyna:** Rozjazd V1/V2. Lista strony (`ContainersListPage.vue`) renderuje dane z
TanStack Query (V2), a dropdown (`ContainersListPageDropdown.vue`) usuwał przez V1
(`useGear()`), który kasował kontenery na backendzie i czyścił store V1 (przez co znikało
menu), ale **nie inwalidował cache V2** — dlatego karty zostawały do odświeżenia strony.
Dodatkowo `deleteAllContainers()` nie był `await`-owany.

**Poprawka:** `handleDeleteAll` jest teraz `async`, `await`-uje usunięcie, czyści store V2
(`storeV2.clearAll()`) i inwaliduje cache (`queryClient.invalidateQueries({ queryKey: gearQueryKeys.all })`).

**Plik:** `src/modules/gear/components/ContainersListPageDropdown.vue`

---

## 2. Eksport do Markdown / CSV z dropdownu nic nie robi — `DONE`

**Strona:** `/gear` (dropdown „more actions")

**Objaw:** Pozycje „Eksport do Markdown" i „Eksport do CSV" w menu rozwijanym nie reagują.
Przycisk eksportu obok dropdownu (poza menu) działa i otwiera dialog.

**Przyczyna:** Niezgodność nazw eventów między komponentem a stroną:
- Dropdown emituje `exportAllToMarkdown`, a strona nasłuchuje `@export-all-to-prompt` — inne nazwy.
- Dropdown emituje `exportAllToCSV`, a strona nasłuchuje `@export-all-to-csv` — `CSV`
  (kolejne wielkie litery) kebab-uje się do `export-all-to-c-s-v`, więc też nie pasuje.

**Poprawka:** ujednolicono nazwy eventów (`exportAllToMarkdown` / `exportAllToCsv` /
`exportAllToJson`) i podpięto poprawne listenery na stronie
(`@export-all-to-markdown`, `@export-all-to-csv`, `@export-all-to-json`). Dodatkowo
dropdown czyta teraz listę kontenerów z V2 (`useGearV2()`), spójnie ze stroną.

**Pliki:** `src/modules/gear/components/ContainersListPageDropdown.vue`,
`src/modules/gear/pages/ContainersListPage.vue`

---

## 3. Brakuje eksportu do JSON — `DONE`

**Strona:** `/gear`

**Objaw:** Dostępny jest eksport do Markdown i CSV, ale nie ma opcji eksportu do JSON.

**Poprawka:** dodano akcję „Eksport do JSON" w dropdownie. Eksport buduje drzewo kontenerów
z zagnieżdżonymi dziećmi (V2) i pobiera plik `.json` bez dodatkowego dialogu.

**Pliki:** `src/modules/gear/utils/exportToJsonV2.ts` (nowy),
`src/modules/gear/components/ContainersListPageDropdown.vue`,
`src/modules/gear/pages/ContainersListPage.vue`,
`src/modules/gear/utils/actionIcons.ts`, `src/modules/gear/i18n/index.ts`

---

## 4. Import z Markdown nie pokazuje nic w kontenerach (zalogowany użytkownik) — `DONE`

**Strona:** `/gear` → dialog „Import z Markdown"

**Objaw:** Po wklejeniu treści jest poprawny podgląd, ale po kliknięciu „Import"
w kontenerach nic się nie pojawia.

**Przyczyna:** `ImportMarkdownDialog.vue` (`handleImport`) zapisuje dane **tylko do lokalnego
store'a V2** (`store.upsertItem(...)`, z fikcyjnym `userId: 'local-user'`). Nie woła w ogóle
API i nie inwaliduje cache TanStack Query. Gdy użytkownik jest zalogowany (`shouldUseAPI`),
strona `/gear` renderuje listę z danych API (`containersFromAPI`), a nie ze store'a — więc
zaimportowane elementy się nie pokazują. Dodatkowo dane nie trafiają na backend, więc po
odświeżeniu i tak ich nie ma. `handleImportComplete` na stronie jest puste
(komentarz „Refresh is automatic via store reactivity" jest nieaktualny dla trybu API).

**Poprawka:** `handleImport` tworzy/aktualizuje teraz elementy przez `useGearV2()`
(`createItem`/`updateItem`), które trafiają do API gdy `shouldUseAPI`, a po zakończeniu
inwaliduje cache (`gearQueryKeys.all`). Zagnieżdżone kontenery są obsłużone natywnie w V2
przez re-parenting (`parentItemId`) zamiast tworzenia „placeholder" itemu. Tryb „update"
(resolucja po UUID) zachowany.

**Pliki:** `src/modules/gear/components/ImportMarkdownDialog.vue`

---

## 5. Dialog „Dodaj kontener" (nesting) pokazuje „Brak dostępnych kontenerów" — `TODO`

**Strona:** `/gear/:id` (np. `/gear/01KAP9SZH1X1F460J6FN06C822` – „Bagażnik") → dialog „Dodaj kontener"

**Objaw:** Próba zagnieżdżenia istniejącego kontenera (np. „Plecak Helikon EDC Cordura")
w „Bagażniku" – dialog pokazuje „Brak dostępnych kontenerów do zagnieżdżenia", mimo że
ten kontener jest na liście `/gear`.

**Przyczyna:** Rozjazd V1/V2. `AddNestedContainerDialog.vue` czyta `containers` z `useGear()`
(store V1), a `ContainerDetailPage` jest już zmigrowany na V2 i **nie zasila store'a V1**.
Gdy wchodzi się prosto na stronę kontenera, store V1 jest pusty → lista dostępnych
kontenerów jest pusta. Dialog używa też V1-owego pola `container.type` i `getAllNestedContainers`
operującego na typach V1.

**Sugerowana poprawka:** zmigrować dialog na V2 (`useGearV2()`/store V2, `containerType`,
V2-owa wersja wykluczania zagnieżdżeń). Część Kroku 1 migracji V1→V2
(`docs/migration-v1-to-v2.md`).

**Pliki:** `src/modules/gear/components/AddNestedContainerDialog.vue`,
`src/modules/gear/utils/containerNesting.ts`

---

## 6. UX: dodawanie istniejącego kontenera/przedmiotu z poziomu „Dodaj przedmiot" — `TODO` (usprawnienie)

**Strona:** `/gear/:id/items/new`

**Obserwacja:** Strona „Dodaj przedmiot" ma 2 zakładki: „Nowy przedmiot" oraz „Z katalogu".
Wygodnie byłoby dodać trzecią zakładkę „Mój istniejący przedmiot/kontener", pozwalającą
zagnieździć istniejący kontener lub dodać/zlinkować istniejący przedmiot bez wchodzenia
do osobnego dialogu na stronie kontenera.

**Do doprecyzowania:** zakładka „Z katalogu" – czy to katalog publiczny, czy katalog
przedmiotów użytkownika? (nazewnictwo do ujednolicenia, by było jednoznaczne).

**Status:** usprawnienie UX, nie błąd. Do zaplanowania osobno (powiązane z migracją katalogu
na V2 – patrz luki w `docs/migration-v1-to-v2.md`).

---

## 7. Po dodaniu przedmiotu lista w kontenerze się nie odświeża — `TODO`

**Strona:** `/gear/:id` (szczegóły kontenera) → `/gear/:id/items/new` → zapis nowego przedmiotu

**Objaw:** Po dodaniu przedmiotu i powrocie na stronę kontenera nowy element nie pojawia się
na liście. Trzeba ręcznie odświeżyć stronę (lub użyć akcji refresh), żeby go zobaczyć.

**Przyczyna (prawdopodobna):** Rozjazd V1/V2 — ten sam wzorzec co w bugach #1 i #4.
`ContainerDetailPage.vue` przy zalogowanym użytkowniku (`shouldUseAPI`) renderuje dzieci
z TanStack Query (`useContainerWithChildren` → `childrenFromAPI`), a `ItemFormPage.vue`
po zapisie woła `useGearV2().createItem()`, które aktualizuje tylko store V2
(`store.upsertItem`) **bez** inwalidacji cache (`gearQueryKeys.all`). Po nawigacji wstecz
strona pokazuje stare dane z cache do ręcznego odświeżenia.

**Sugerowana poprawka:** po `createItem` inwalidować cache V2
(`queryClient.invalidateQueries({ queryKey: gearQueryKeys.all })`) albo użyć
`useGearMutations().createItem()` (jak w innych miejscach na stronie kontenera — komentarz
w `ContainerDetailPage.vue` wskazuje, że mutacje z tego composable same inwalidują cache).

**Pliki:** `src/modules/gear/pages/ItemFormPage.vue`,
`src/modules/gear/composables/useGearV2.ts`,
`src/modules/gear/pages/ContainerDetailPage.vue`

---

## 8. Brak obrazków przedmiotów na liście w kontenerze — `TODO`

**Strona:** `/gear/:id` (szczegóły kontenera) — tabela przedmiotów i/lub galeria „Item Images"

**Objaw:** Na liście przedmiotów w kontenerze nie widać obrazków (kolumna Image / galeria pod
tabelą), mimo że przedmiot ma ustawiony obraz główny (main/primary image) — widoczny np.
na stronie szczegółów przedmiotu lub w edycji obrazków.

**Możliwe przyczyny (do zweryfikowania):**

1. **Brak `primaryImageUrl` w odpowiedzi V2** — `ItemsTableImageCell` renderuje miniaturę z
   `row.original.primaryImageUrl`, ale API V2 (`schemas_v2.py` / `service_v2.py`) prawdopodobnie
   nie zwraca tego pola przy liście dzieci kontenera (w V1 było mapowane w `service.py`).
2. **Kolumna Image ukryta domyślnie** — `ItemsTable.vue` ma w domyślnej widoczności kolumn
   `image: false` (localStorage `ITEMS_TABLE_COLUMN_VISIBILITY_KEY`); użytkownik może nie
   widzieć kolumny mimo że dane są.
3. **Galeria wymaga `showItemImages` na kontenerze** — `ContainerItemImagesGallery` renderuje
   się tylko gdy `container.showItemImages === true`; obrazy pobierane są osobnymi requestami
   (`itemImageApiService.getImages` per item), nie z pola itemu na liście.
4. **Powiązane z bugiem #7** — po dodaniu przedmiotu/obrazka lista może być nieaktualna
   (stary cache TanStack Query) do ręcznego odświeżenia.
5. **Problemy kopiowania obrazów z katalogu** — patrz `docs/BUGS_CATALOGUE_IMAGES.md`
   (FK violation przy `item_images` — obraz może nie trafić do bazy mimo sukcesu API).

**Sugerowana poprawka:** dodać `primaryImageUrl` do odpowiedzi V2 (lista dzieci / batch),
ew. wzbogacić `useContainerWithChildren`; rozważyć domyślną widoczność kolumny Image gdy
kontener ma `showItemImages`; po mutacjach inwalidować cache. Powiązane z migracją V2.

**Pliki:** `src/modules/gear/components/ItemsTable.vue`,
`src/modules/gear/components/items-table/ItemsTableImageCell.vue`,
`src/modules/gear/components/ContainerItemImagesGallery.vue`,
`src/modules/gear/pages/ContainerDetailPage.vue`,
`backend/app/modules/gear/schemas_v2.py`,
`backend/app/modules/gear/service_v2.py`
