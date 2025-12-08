# FEATURE-028: Nawigacja przycisku "Wróć"

**Status:** ✅ Completed  
**Priority:** High  
**Complexity:** Small  
**Related:** [FEATURE-026-query-params-refactoring.md](./FEATURE-026-query-params-refactoring.md), [query-params-analysis.md](../analysis/query-params-analysis.md)

## 📋 Opis

Dokumentacja zachowania przycisku "Wróć" w różnych komponentach aplikacji, wyjaśniająca jak działa nawigacja w różnych scenariuszach i dlaczego używa parametru `from` zamiast `router.back()`.

## 🎯 Problem

Po commit d7ce6d2f5d142f318050496b470771a20082413a zmieniono przyciski "Wróć" na użycie `router.back()`, co powodowało nieprawidłowe zachowanie:

1. Użytkownik: ContainersList → ContainerDetails → ItemDetails
2. Użytkownik klika "Edytuj" → ItemEdit
3. Po zapisie `navigateBackAndClean()` nawiguje do ItemDetails (dodaje wpis do historii)
4. Historia przeglądarki: ItemDetails → ItemEdit → ItemDetails (po zapisie)
5. Kliknięcie "Wróć" w ItemDetails używa `router.back()` → wraca do ItemEdit zamiast ContainerDetails ❌

## ✅ Rozwiązanie

Przywrócenie logiki nawigacji opartej na parametrze `from` z query string zamiast polegania na historii przeglądarki. Parametr `from` jest zachowywany podczas nawigacji, co zapewnia poprawną nawigację wstecz niezależnie od historii przeglądarki.

## 📋 Lista wszystkich komponentów z przyciskiem "Wróć"

Poniżej znajduje się pełna lista wszystkich komponentów i stron w aplikacji, które zawierają przycisk "Wróć":

| # | Komponent/Strona | Lokalizacja | Metoda nawigacji | Użycie |
|---|------------------|-------------|------------------|--------|
| 1 | **ItemHeader.vue** | `src/modules/gear/components/ItemHeader.vue` | Parametr `from` z query string | `ItemDetailPage` |
| 2 | **ContainerHeader.vue** | `src/modules/gear/components/ContainerHeader.vue` | `router.back()` | `ContainerDetailPage` |
| 3 | **PublicContainerHeader.vue** | `src/modules/gear/components/PublicContainerHeader.vue` | Prop `backPath` lub emit `back` | `PublicContainerDetailPage`, `SharedContainerDetailPage` |
| 4 | **PublicItemDetailPage.vue** | `src/modules/gear/pages/PublicItemDetailPage.vue` | Explicit navigation | Strona szczegółów publicznego przedmiotu |
| 5 | **ContainerShareTokensPage.vue** | `src/modules/gear/pages/ContainerShareTokensPage.vue` | Explicit navigation | Strona zarządzania tokenami udostępniania |
| 6 | **ProfileEditPage.vue** | `src/modules/user/pages/ProfileEditPage.vue` | Explicit navigation | Strona edycji profilu użytkownika |
| 7 | **TwoFactorSetupPage.vue** | `src/modules/auth/pages/TwoFactorSetupPage.vue` | `ButtonLink` | Strona konfiguracji 2FA |
| 8 | **CatalogueItemDetailPage.vue** | `src/modules/gear/pages/catalogue/CatalogueItemDetailPage.vue` | Explicit navigation | Strona szczegółów przedmiotu z katalogu |

## 🔍 Jak działa nawigacja "Wróć"

### Parametr `from`

Parametr `from` określa źródło nawigacji do strony i jest używany przez przycisk "Wróć" do określenia, dokąd powinien nawigować.

**Możliwe wartości:**
- `'all-items'` - nawigacja z `AllItemsPage`
- `'container'` - nawigacja z `ContainerDetailPage` (przez `ItemsTable` lub `ContainerItemImageCard`)
- `undefined` - domyślnie nawigacja do kontenera

### Komponenty z przyciskiem "Wróć"

Poniżej znajduje się pełna lista wszystkich komponentów w aplikacji, które zawierają przycisk "Wróć":

#### 1. ItemHeader.vue

**Lokalizacja:** `src/modules/gear/components/ItemHeader.vue`  
**Użycie:** Wyświetlany na stronie `ItemDetailPage`  
**Metoda nawigacji:** Parametr `from` z query string

**Logika nawigacji:**
```typescript
const backTo = computed<string>(() => {
  const from = getFrom(route)
  if (from === 'all-items') {
    return GearRoutePath.AllItems
  }
  return GearRoutePath.ContainerDetailById(containerId)
})

const handleBack = () => {
  router.push(backTo.value)
}
```

**Scenariusze:**

1. **ContainersList → ContainerDetails → ItemDetails**
   - Parametr `from`: `'container'` (ustawiany przez `ItemsTable.navigateToItem()`)
   - Przycisk "Wróć" → `ContainerDetailById(containerId)` ✅

2. **AllItemsPage → ItemDetails**
   - Parametr `from`: `'all-items'` (ustawiany przez `AllItemsPage`)
   - Przycisk "Wróć" → `AllItemsPage` ✅

3. **ContainersList → ContainerDetails → ItemDetails → Edit → Save**
   - Parametr `from`: `'container'` (zachowywany przez `navigateBackAndClean()`)
   - Po zapisie: nawigacja do `ItemDetails` z `from=container`
   - Przycisk "Wróć" → `ContainerDetailById(containerId)` ✅

4. **AllItemsPage → ItemDetails → Edit → Save**
   - Parametr `from`: `'all-items'` (zachowywany przez `navigateBackAndClean()`)
   - Po zapisie: nawigacja do `ItemDetails` z `from=all-items`
   - Przycisk "Wróć" → `AllItemsPage` ✅

#### 2. ContainerHeader.vue

**Lokalizacja:** `src/modules/gear/components/ContainerHeader.vue`  
**Użycie:** Wyświetlany na stronie `ContainerDetailPage`  
**Metoda nawigacji:** `router.back()` ⚠️ **Wymaga poprawki**

**Obecna logika nawigacji:**
```typescript
@click="router.back()"
```

**Problemy z obecnym podejściem:**
- `ContainerDetailPage` może być otwarty z różnych miejsc:
  - `ContainersList` (główna lista)
  - `AllItemsPage` (kliknięcie w kontener)
  - `ContainerFormPage` (po zapisie edycji)
  - `ContainerShareTokensPage` (po zarządzaniu tokenami)
  - Bezpośrednie linki (zakładki, emaile)
- `router.back()` może nie działać poprawnie w niektórych scenariuszach
- Po zapisie edycji kontenera, historia przeglądarki może być skomplikowana

**Proponowana poprawka:**
```typescript
const handleBack = () => {
  router.push(GearRoutePath.Containers)
}
```

**Uzasadnienie poprawki:**
- Explicit navigation do `ContainersList` jest bardziej przewidywalne
- Użytkownik zawsze wie, dokąd trafi po kliknięciu "Wróć"
- Działa poprawnie niezależnie od źródła nawigacji
- Spójne z innymi komponentami używającymi explicit navigation

**Scenariusze po poprawce:**

1. **ContainersList → ContainerDetails**
   - Przycisk "Wróć" → `ContainersList` ✅

2. **AllItemsPage → ContainerDetails**
   - Przycisk "Wróć" → `ContainersList` ✅

3. **ContainerDetails → Edit → Save → ContainerDetails**
   - Po zapisie: nawigacja do `ContainerDetails` (nowy wpis w historii)
   - Przycisk "Wróć" → `ContainersList` ✅ (zamiast powrotu do formularza edycji)

#### 3. PublicContainerHeader.vue

**Lokalizacja:** `src/modules/gear/components/PublicContainerHeader.vue`  
**Użycie:** Wyświetlany na stronach `PublicContainerDetailPage` i `SharedContainerDetailPage`  
**Metoda nawigacji:** Prop `backPath` lub emit `back`

**Logika nawigacji:**
```typescript
const handleBack = () => {
  if (props.backPath) {
    router.push(props.backPath)
  } else {
    emit('back')
  }
}
```

**Uzasadnienie:** Komponent przyjmuje opcjonalny prop `backPath`, który określa dokąd nawigować. Jeśli nie jest podany, emituje event `back`, który jest obsługiwany przez komponent rodzica.

**Scenariusze:**

1. **PublicContainers → PublicContainerDetail**
   - Prop `backPath`: `GearRoutePath.PublicContainers`
   - Przycisk "Wróć" → `PublicContainers` ✅

2. **SharedContainerDetail (przez token)**
   - Emit `back` → obsługiwany przez `SharedContainerDetailPage`
   - Przycisk "Wróć" → `PublicContainers` ✅

#### 4. PublicItemDetailPage.vue

**Lokalizacja:** `src/modules/gear/pages/PublicItemDetailPage.vue`  
**Użycie:** Strona szczegółów publicznego przedmiotu  
**Metoda nawigacji:** Explicit navigation do `PublicContainerDetailById`

**Logika nawigacji:**
```typescript
const handleBack = () => {
  router.push(GearRoutePath.PublicContainerDetailById(containerId))
}
```

**Uzasadnienie:** Zawsze nawiguje do szczegółów kontenera, z którego pochodzi przedmiot. Nie używa parametru `from`, ponieważ publiczne przedmioty są zawsze wyświetlane w kontekście kontenera.

**Scenariusze:**

1. **PublicContainers → PublicContainerDetail → PublicItemDetail**
   - Przycisk "Wróć" → `PublicContainerDetailById(containerId)` ✅

#### 5. ContainerShareTokensPage.vue

**Lokalizacja:** `src/modules/gear/pages/ContainerShareTokensPage.vue`  
**Użycie:** Strona zarządzania tokenami udostępniania kontenera  
**Metoda nawigacji:** Explicit navigation do `ContainerDetailById`

**Logika nawigacji:**
```typescript
const handleBack = () => {
  router.push(GearRoutePath.ContainerDetailById(containerId))
}
```

**Uzasadnienie:** Zawsze nawiguje z powrotem do szczegółów kontenera, z którego użytkownik przyszedł. Jest to strona pomocnicza, więc zawsze wraca do głównej strony kontenera.

**Scenariusze:**

1. **ContainerDetails → ContainerShareTokens**
   - Przycisk "Wróć" → `ContainerDetailById(containerId)` ✅

#### 6. ProfileEditPage.vue

**Lokalizacja:** `src/modules/user/pages/ProfileEditPage.vue`  
**Użycie:** Strona edycji profilu użytkownika  
**Metoda nawigacji:** Explicit navigation do `UserRoutePaths.profile`

**Logika nawigacji:**
```typescript
const handleCancel = () => {
  router.push(UserRoutePaths.profile)
}
```

**Uzasadnienie:** Zawsze nawiguje z powrotem do strony profilu użytkownika. Nie używa `router.back()`, ponieważ strona może być otwarta z różnych miejsc (np. z linku bezpośredniego).

**Scenariusze:**

1. **Profile → ProfileEdit**
   - Przycisk "Wróć" → `UserRoutePaths.profile` ✅

#### 7. TwoFactorSetupPage.vue

**Lokalizacja:** `src/modules/auth/pages/TwoFactorSetupPage.vue`  
**Użycie:** Strona konfiguracji 2FA  
**Metoda nawigacji:** `ButtonLink` do `SettingsRoutePaths.settings`

**Logika nawigacji:**
```vue
<ButtonLink variant="outline" :to="SettingsRoutePaths.settings">
  {{ t('common.back') }}
</ButtonLink>
```

**Uzasadnienie:** Używa `ButtonLink` zamiast funkcji nawigacji, ponieważ jest to prosty link do strony ustawień. Strona jest zawsze otwierana z ustawień, więc link jest bezpieczny.

**Scenariusze:**

1. **Settings → TwoFactorSetup**
   - Przycisk "Wróć" → `SettingsRoutePaths.settings` ✅

#### 8. CatalogueItemDetailPage.vue

**Lokalizacja:** `src/modules/gear/pages/catalogue/CatalogueItemDetailPage.vue`  
**Użycie:** Strona szczegółów przedmiotu z katalogu  
**Metoda nawigacji:** Explicit navigation do `CatalogueBrowser`

**Logika nawigacji:**
```typescript
const goBack = () => {
  router.push(GearRoutePath.CatalogueBrowser)
}
```

**Uzasadnienie:** Zawsze nawiguje z powrotem do przeglądarki katalogu. Strona jest zawsze otwierana z przeglądarki katalogu, więc explicit navigation jest bezpieczne.

**Scenariusze:**

1. **CatalogueBrowser → CatalogueItemDetail**
   - Przycisk "Wróć" → `CatalogueBrowser` ✅

## 🔧 Implementacja

### ItemHeader.vue

```typescript
const backTo = computed<string>(() => {
  const from = getFrom(route)
  if (from === 'all-items') {
    return GearRoutePath.AllItems
  }
  return GearRoutePath.ContainerDetailById(containerId)
})

const handleBack = () => {
  router.push(backTo.value)
}
```

### useNavigationReturn.ts

Funkcja `navigateBackAndClean()` zachowuje parametr `from` przy nawigacji do ItemDetails:

```typescript
async function navigateBackAndClean() {
  const returnToValue = returnTo.value
  const fromValue = from.value

  if (returnToValue === 'detail' && itemId) {
    // Preserve 'from' parameter when navigating back to ItemDetails
    // This ensures the back button in ItemHeader works correctly
    await router.push({
      path: GearRoutePath.ItemDetailById(containerId, itemId),
      query: createNavigationQuery(undefined, fromValue),
    })
  } else if (returnToValue === 'shopping') {
    await router.push(GearRoutePath.ShoppingPlanning)
  } else {
    await router.push({
      path: GearRoutePath.ContainerDetailById(containerId),
      query: {},
    })
  }
}
```

## 📊 Przepływ parametrów

### Scenariusz 1: ContainersList → ContainerDetails → ItemDetails

```
1. ContainersList
   ↓ (kliknięcie w kontener)
2. ContainerDetails
   ↓ (ItemsTable.navigateToItem() z from='container')
3. ItemDetails?from=container
   ↓ (przycisk "Wróć")
4. ContainerDetails ✅
```

### Scenariusz 2: ContainersList → ContainerDetails → ItemDetails → Edit → Save

```
1. ContainersList
   ↓
2. ContainerDetails
   ↓ (ItemsTable.navigateToItem() z from='container')
3. ItemDetails?from=container
   ↓ (kliknięcie "Edytuj" - handleEdit() z returnTo='detail', from='container')
4. ItemEdit?returnTo=detail&from=container
   ↓ (zapis - navigateBackAndClean() zachowuje from='container')
5. ItemDetails?from=container
   ↓ (przycisk "Wróć")
6. ContainerDetails ✅
```

### Scenariusz 3: AllItemsPage → ItemDetails

```
1. AllItemsPage
   ↓ (kliknięcie w przedmiot z from='all-items')
2. ItemDetails?from=all-items
   ↓ (przycisk "Wróć")
3. AllItemsPage ✅
```

### Scenariusz 4: AllItemsPage → ItemDetails → Edit → Save

```
1. AllItemsPage
   ↓
2. ItemDetails?from=all-items
   ↓ (kliknięcie "Edytuj" - handleEdit() z returnTo='detail', from='all-items')
3. ItemEdit?returnTo=detail&from=all-items
   ↓ (zapis - navigateBackAndClean() zachowuje from='all-items')
4. ItemDetails?from=all-items
   ↓ (przycisk "Wróć")
5. AllItemsPage ✅
```

## 🎓 Dlaczego nie `router.back()`?

### Problem z `router.back()`

`router.back()` polega na historii przeglądarki, która może być nieprzewidywalna:

1. **Programatyczna nawigacja** - gdy aplikacja programatycznie nawiguje (np. po zapisie), dodaje nowy wpis do historii, co może zmienić oczekiwane zachowanie `router.back()`

2. **Wielokrotne nawigacje** - jeśli użytkownik nawiguje między stronami wielokrotnie, historia może być skomplikowana i `router.back()` może nie prowadzić tam, gdzie oczekujemy

3. **Brak kontekstu** - `router.back()` nie wie, skąd użytkownik przyszedł w kontekście aplikacji, tylko gdzie był w historii przeglądarki

4. **Bezpośrednie linki** - jeśli użytkownik otworzy stronę przez bezpośredni link (np. z zakładki, emaila), `router.back()` może prowadzić poza aplikację

### Zalety parametru `from` i explicit navigation

1. **Przewidywalność** - zawsze wiemy, dokąd powinien prowadzić przycisk "Wróć"
2. **Kontekst aplikacji** - parametr `from` reprezentuje kontekst aplikacji, nie historię przeglądarki
3. **Niezależność od historii** - działa poprawnie niezależnie od tego, jak skomplikowana jest historia przeglądarki
4. **Spójność** - wszystkie scenariusze nawigacji działają tak samo
5. **Bezpieczeństwo** - explicit navigation zawsze prowadzi do poprawnego miejsca w aplikacji

## 🎯 Rekomendowane podejście do nawigacji "Wróć"

### Zasady ogólne

1. **Użyj parametru `from`** gdy strona może być otwarta z różnych miejsc w aplikacji
   - Przykład: `ItemHeader` - może być otwarty z `AllItemsPage` lub `ContainerDetailPage`

2. **Użyj explicit navigation** gdy strona jest zawsze otwarta z jednego miejsca lub gdy chcemy zawsze wracać do głównej strony
   - Przykład: `ContainerShareTokensPage` - zawsze wraca do `ContainerDetailPage`
   - Przykład: `ProfileEditPage` - zawsze wraca do `ProfilePage`

3. **Unikaj `router.back()`** gdy:
   - Strona może być otwarta z różnych miejsc
   - Strona może być otwarta przez bezpośredni link
   - Po zapisie/akcji następuje programatyczna nawigacja (dodaje wpis do historii)

4. **Możesz użyć `router.back()`** tylko gdy:
   - Strona jest zawsze otwarta z jednego miejsca
   - Nie ma programatycznej nawigacji po akcjach
   - Historia przeglądarki jest przewidywalna

### Proponowane poprawki

#### 1. ContainerHeader.vue - zmiana z `router.back()` na explicit navigation

**Obecne zachowanie:**
```typescript
@click="router.back()"
```

**Proponowane zachowanie:**
```typescript
const handleBack = () => {
  router.push(GearRoutePath.Containers)
}
```

**Uzasadnienie:**
- `ContainerDetailPage` może być otwarty z różnych miejsc:
  - `ContainersList` (główna lista)
  - `AllItemsPage` (kliknięcie w kontener z listy wszystkich przedmiotów)
  - `ContainerFormPage` (po zapisie edycji)
  - `ContainerShareTokensPage` (po zarządzaniu tokenami)
  - Bezpośrednie linki (zakładki, emaile)
- Explicit navigation do `ContainersList` jest bardziej przewidywalne i spójne
- Użytkownik zawsze wie, dokąd trafi po kliknięciu "Wróć"

**Alternatywa:** Można też użyć parametru `from` podobnie jak w `ItemHeader`, ale dla `ContainerHeader` explicit navigation do głównej listy jest prostsze i bardziej intuicyjne.

#### 2. PublicContainerHeader.vue - już dobrze zaimplementowane

**Obecne zachowanie:** Używa prop `backPath` lub emit `back` ✅

**Status:** Nie wymaga zmian - elastyczne podejście z prop/emit jest odpowiednie dla komponentu używanego w różnych kontekstach.

#### 3. Inne komponenty - sprawdzenie spójności

Wszystkie pozostałe komponenty używają explicit navigation, co jest poprawne:
- ✅ `PublicItemDetailPage` - explicit navigation do `PublicContainerDetailById`
- ✅ `ContainerShareTokensPage` - explicit navigation do `ContainerDetailById`
- ✅ `ProfileEditPage` - explicit navigation do `UserRoutePaths.profile`
- ✅ `TwoFactorSetupPage` - `ButtonLink` do `SettingsRoutePaths.settings`
- ✅ `CatalogueItemDetailPage` - explicit navigation do `CatalogueBrowser`

## ✅ Kryteria akceptacji

- ✅ Przycisk "Wróć" w `ItemHeader` nawiguje poprawnie we wszystkich scenariuszach
- ✅ Parametr `from` jest zachowywany podczas nawigacji po zapisie edycji
- ✅ `navigateBackAndClean()` zachowuje parametr `from` przy nawigacji do ItemDetails
- ✅ Wszystkie scenariusze nawigacji działają poprawnie

## 📝 Pliki związane

- `src/modules/gear/components/ItemHeader.vue` - implementacja przycisku "Wróć"
- `src/modules/gear/components/ContainerHeader.vue` - implementacja przycisku "Wróć" (używa `router.back()`)
- `src/modules/gear/composables/useNavigationReturn.ts` - logika nawigacji po zapisie
- `src/modules/gear/utils/navigationParams.ts` - helper functions do zarządzania parametrami

## 🔗 Powiązane dokumenty

- [FEATURE-026: Refaktoryzacja systemu query parametrów](./FEATURE-026-query-params-refactoring.md)
- [Analiza query parametrów](../analysis/query-params-analysis.md)

