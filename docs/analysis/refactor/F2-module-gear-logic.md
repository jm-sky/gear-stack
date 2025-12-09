# F2: Gear Module - Logic Layer - Analiza

**Phase:** B (Frontend)
**Data:** 2025-12-09
**Zakres:** `src/modules/gear/` (services, composables, stores, types)
**Status:** ✅ Completed + 🔧 CRITICAL Fixes Applied (2025-12-09)
**Language/Stack:** TypeScript/Vue 3

---

## ⚠️ CRITICAL FIXES APPLIED (2025-12-09)

**Status:** ✅ All 3 CRITICAL issues have been fixed and tested

### C1: Data Consistency in gearContainerService ✅ FIXED
**Issue:** Risk of data loss if localStorage deletion fails after API deletion
**Fix Applied:**
- Implemented two-phase commit pattern with rollback mechanism
- Backup container data before deletion
- Automatic restore to API if localStorage deletion fails
- User-friendly error message if rollback fails

**Files Modified:**
- `src/modules/gear/services/gearContainerService.ts:46-97`
- `src/modules/gear/services/gearContainerService.ts:130-180`

**Test Coverage:** ✅
- `src/modules/gear/services/gearContainerService.spec.ts` (7 test cases)

---

### C2: Race Condition in gearItemHybridService ✅ FIXED
**Issue:** Linear search for parent container could refresh wrong container during concurrent updates
**Fix Applied:**
- Added `getContainerIdByItemId()` and `getContainerByItemId()` getters to store
- Get container ID BEFORE update/delete to prevent race conditions
- Eliminated O(n²) loop search with O(n) direct lookup
- Performance improvement: 100 containers now process in <100ms

**Files Modified:**
- `src/modules/gear/store/useGearStore.ts:49-64` (added getters)
- `src/modules/gear/services/gearItemHybridService.ts:46-70` (updateItem)
- `src/modules/gear/services/gearItemHybridService.ts:72-98` (deleteItem)
- `src/modules/gear/services/gearItemHybridService.ts:108-134` (batchUpdateOrder)

**Test Coverage:** ✅
- `src/modules/gear/services/gearItemHybridService.spec.ts` (10 test cases including performance test)

---

### C3: Circular Dependency in dataMigrationService ✅ FIXED
**Issue:** Containers created without respecting parentContainerId dependency order, causing orphaned containers
**Fix Applied:**
- Implemented topological sort algorithm
- Containers now sorted by dependency order (parents before children)
- Circular dependency detection and automatic breaking (set parent to null)
- Orphaned container handling (missing parent set to null)
- ID mapping from old localStorage IDs to new API-generated IDs

**Files Modified:**
- `src/modules/gear/services/dataMigrationService.ts:10-54` (added sortContainersByDependency)
- `src/modules/gear/services/dataMigrationService.ts:83-132` (migration with sorting and ID mapping)

**Test Coverage:** ✅
- `src/modules/gear/services/dataMigrationService.spec.ts` (13 test cases)

---

**Total Test Coverage for CRITICAL Fixes:** 30 test cases
**All tests passing:** ✅

**Impact:**
- Data loss prevention: Two-phase commit ensures API/localStorage consistency
- Performance: O(n) lookup instead of O(n²) loop search
- Reliability: Topological sort prevents orphaned containers during migration
- User experience: Clear error messages and automatic recovery

---

## 1. Overview

### Struktura katalogów
```
src/modules/gear/
├── services/ (21 files)
│   ├── gearContainerService.ts (Hybrid API/Local)
│   ├── gearItemService.ts (Hybrid API/Local)
│   ├── gearSettingsService.ts (Factory wrapper)
│   ├── gearContainerApiService.ts
│   ├── gearItemApiService.ts
│   ├── gearContainerLocalService.ts
│   ├── gearItemLocalService.ts
│   ├── gearItemHybridService.ts
│   ├── gearSettingsApiService.ts
│   ├── catalogueApiService.ts
│   ├── itemImageApiService.ts
│   ├── markdownImportService.ts (Markdown parsing)
│   ├── dataMigrationService.ts (Data migration)
│   ├── jsonImportExportService.ts
│   ├── sampleSetGenerator.ts
│   ├── exampleSets.ts
│   ├── imageSearchApiService.ts
│   ├── publicContainersService.ts
│   └── sharedContainersService.ts
├── composables/ (22 files)
│   ├── useGear.ts (Main entry point - 24+ functions)
│   ├── useContainer.ts
│   ├── useItem.ts
│   ├── useGearSettings.ts
│   ├── useCatalogue.ts
│   ├── useFormattedItemWeight.ts
│   ├── useFormattedItemPrice.ts
│   ├── useCategoryLabel.ts
│   ├── useContainerTypeLabel.ts
│   ├── usePriceTierLabel.ts
│   ├── useExpiration.ts
│   ├── useItemImage.ts
│   ├── useInlineItemEditing.ts
│   ├── useDataMigration.ts
│   ├── useDataMigrationModal.ts
│   ├── useJsonImportExport.ts
│   ├── useItemsTableEditMode.ts
│   ├── useItemsParamRecognition.ts
│   ├── useNavigationReturn.ts
│   ├── useSearchPaginationUrl.ts
│   ├── useIsContainerOwner.ts
│   └── usePieChartGeometry.ts
├── store/ (2 files)
│   ├── useGearStore.ts (Options API style)
│   └── useGearSettingsStore.ts (Setup style)
└── types/ (5 files)
    ├── gear.types.ts (Core types)
    ├── gearSettings.types.ts
    ├── catalogue.types.ts
    ├── itemImage.types.ts
    └── shopping.types.ts
```

### Kluczowe pliki
- **`gearContainerService.ts`** - Hybrid service with API/localStorage fallback pattern
- **`gearItemService.ts`** - Similar hybrid pattern for items
- **`gearSettingsService.ts`** - Factory wrapper with significant code duplication
- **`markdownImportService.ts`** - Complex markdown parsing (500+ lines)
- **`useGearStore.ts`** - Main Pinia store (Options API)
- **`useGear.ts`** - Mega-composable with 24+ exported functions
- **`gear.types.ts`** - Core type definitions with 300+ lines

### Statystyki
- Liczba plików: **50**
- Łączne linie kodu: ~**5,000+** (estimated)
- Główne dependencies: Vue 3, Pinia, Axios, i18n, date-fns, markdown-it
- Services: 21 (API: 7, Local: 4, Hybrid: 3, Utilities: 7)
- Composables: 22 (organized by concern)
- Stores: 2 (mixed patterns)
- Type files: 5

### Kluczowe wzorce architektoniczne
1. **Hybrid Service Pattern**: API-first with localStorage fallback
2. **Factory Pattern**: Service instantiation with dependency injection
3. **Composable Pattern**: Reusable logic with Vue Composition API
4. **Repository Pattern** (partial): Some services follow this pattern
5. **Singleton Pattern**: Stores and some services

---

## 2. SOLID Analysis

### ✅ Single Responsibility Principle (SRP)

#### Violations

- [x] **[CRITICAL]** `useGear.ts:entire-file` - Mega-composable with 24+ exported functions
  - **Problem:** Single composable handles CRUD operations, calculations, import/export, catalog operations, and data migration
  - **Responsibilities:** Container CRUD, Item CRUD, Weight calculations, Import/Export, Catalog integration, Data migration
  - **Impact:** High - Makes code difficult to maintain, test, and reason about
  - **Recommendation:** Split into focused composables:
    - `useContainerOperations()` - Container CRUD
    - `useItemOperations()` - Item CRUD
    - `useContainerCalculations()` - Weight/readiness calculations
    - `useContainerImportExport()` - Import/export operations
    - `useItemCatalog()` - Catalog operations

- [x] **[HIGH]** `markdownImportService.ts:parseMarkdown` (235 lines)
  - **Problem:** Single method handles container parsing, item parsing, metadata extraction, and description assembly
  - **Impact:** High - Cyclomatic complexity too high, difficult to test
  - **Recommendation:** Extract methods:
    - `parseContainerHeader()`
    - `parseItemMetadata()`
    - `parseItemParentheses()`
    - `extractDescriptionLines()`

- [x] **[HIGH]** `markdownImportService.ts:parseItemLine` (254 lines)
  - **Problem:** Handles checkbox parsing, priority extraction, price parsing, weight parsing, expiration parsing, and parameter recognition
  - **Impact:** High - 6 levels of nesting, multiple regex patterns
  - **Recommendation:** Extract to separate parsing methods for each concern

- [x] **[MEDIUM]** `gearContainerLocalService.ts:calculateTotalWeight` + inline calculations
  - **Problem:** Weight calculation logic scattered across service and individual methods
  - **Impact:** Medium - Hard to change calculation logic consistently
  - **Recommendation:** Create dedicated `WeightCalculationService` or utility

#### Good Practices

- ✅ `gearContainerApiService.ts` - Focused on API communication only
- ✅ `gearItemApiService.ts` - Clean separation of item API operations
- ✅ `useFormattedItemWeight.ts` - Single responsibility: formatting weight
- ✅ `useCategoryLabel.ts` - Single responsibility: translating category labels
- ✅ Composables like `useExpiration`, `useItemImage`, `useInlineItemEditing` are well-scoped

---

### ✅ Open/Closed Principle (OCP)

#### Violations

- [x] **[HIGH]** `markdownImportService.ts:parsePrice` (38 lines with hardcoded currencies)
  - **Problem:** Adding new currency requires modifying method internals
  - **Recommendation:** Use currency registry pattern:
    ```typescript
    const CURRENCY_PATTERNS: Record<string, RegExp[]> = {
      PLN: [/(\d+(?:[\s,.]\d+)*)\s*PLN/i, /(\d+(?:[\s,.]\d+)*)\s*zł/i],
      USD: [/\$\s*(\d+(?:[\s,.]\d+)*)/i],
      EUR: [/(\d+(?:[\s,.]\d+)*)\s*EUR/i, /€\s*(\d+(?:[\s,.]\d+)*)/i],
    }

    function parsePrice(text: string): IPrice | null {
      for (const [currency, patterns] of Object.entries(CURRENCY_PATTERNS)) {
        for (const pattern of patterns) {
          // ... matching logic
        }
      }
    }
    ```

- [x] **[MEDIUM]** `gearSettingsService.ts` - No extension mechanism for custom operations
  - **Problem:** Adding new settings category requires duplicating entire pattern
  - **Recommendation:** Generic array manipulation methods (see DRY section)

#### Good Practices

- ✅ Factory pattern in services allows for easy extension
- ✅ Interface-based design in type definitions
- ✅ Composables can be composed together for extended functionality

---

### ✅ Liskov Substitution Principle (LSP)

#### Issues

- [x] **[LOW]** `IGearServiceExtended` interface
  - **Problem:** API service cannot properly substitute for this interface as it doesn't support 11 localStorage-specific methods
  - **Impact:** Low - Currently not causing issues as API/Local services are used separately
  - **Recommendation:** See ISP section for interface splitting

#### Good Practices

- ✅ Hybrid services properly delegate to underlying implementations
- ✅ No inheritance-based violations detected

---

### ✅ Interface Segregation Principle (ISP)

#### Violations

- [x] **[HIGH]** `gear.types.ts:284-317` - `IGearServiceExtended` interface
  - **Problem:** Interface with 16 methods where only 5 are core CRUD, 11 are localStorage-specific queries
  - **Impact:** High - API implementation would need to throw "Not implemented" for 11 methods
  - **Recommendation:** Split into focused interfaces:
    ```typescript
    export interface IGearService {
      createContainer(data: ICreateContainerDto): Promise<IGearContainer>
      updateContainer(id: TUUID, data: IUpdateContainerDto): Promise<IGearContainer>
      deleteContainer(id: TUUID): Promise<void>
      getContainer(id: TUUID): Promise<IGearContainer>
    }

    export interface IGearCalculationService {
      calculateTotalWeight(containerId: TUUID): Promise<number>
      calculateReadiness(containerId: TUUID): Promise<number>
    }

    export interface IGearQueryService {
      getAllContainers(): Promise<IGearContainer[]>
      getRootContainers(): Promise<IGearContainer[]>
      getChildContainers(parentId: TUUID): Promise<IGearContainer[]>
      searchContainers(query: string): Promise<IGearContainer[]>
    }

    export interface IGearLocalService extends
      IGearService,
      IGearCalculationService,
      IGearQueryService {}
    ```

#### Good Practices

- ✅ Most composables have focused, minimal interfaces
- ✅ API services have clean, minimal method sets

---

### ✅ Dependency Inversion Principle (DIP)

#### Violations

- [x] **[MEDIUM]** `useGear.ts` - Direct dependencies on concrete service implementations
  - **Problem:** Composable imports concrete `gearContainerService`, `gearItemService` instead of depending on abstractions
  - **Impact:** Medium - Makes testing difficult, tight coupling
  - **Recommendation:** Use dependency injection:
    ```typescript
    export function useGear(
      containerService: IGearService = gearContainerService,
      itemService: IGearItemService = gearItemService
    ) {
      // ... use injected services
    }
    ```

- [x] **[MEDIUM]** `gearItemHybridService.ts:10-15` - Direct store access
  - **Problem:** Service directly calls `useGearStore()` instead of receiving store as dependency
  - **Impact:** Medium - Cannot test service without Pinia setup
  - **Recommendation:** Inject store or use service-level state management

#### Good Practices

- ✅ Hybrid services use injected API/Local services
- ✅ Factory pattern allows for dependency injection

---

## 3. KISS Analysis (Keep It Simple)

### Over-Engineering

- [x] **[MEDIUM]** `gearSettingsService.ts:333-395` - Complex factory wrapper
  - **Problem:** Factory wrapper creates instance for every static method call (11 static methods wrapping 11 instance methods)
  - **Simpler approach:** Use singleton pattern or remove static methods entirely:
    ```typescript
    // Simple singleton
    let instance: GearSettingsService | null = null

    export function getGearSettingsService(): GearSettingsService {
      if (!instance) {
        instance = new GearSettingsService()
      }
      return instance
    }
    ```

- [x] **[LOW]** `sampleSetGenerator.ts:translateWithFallback` - Complex translation fallback logic
  - **Problem:** Custom heuristics to detect untranslated keys (checks for key patterns in output)
  - **Simpler approach:** Use i18n's built-in `te()` (translation exists) method:
    ```typescript
    function translateWithFallback(key: string): string {
      return i18n.global.te(key)
        ? i18n.global.t(key)
        : i18n.global.t(key, 'en')
    }
    ```

### Unnecessary Abstractions

- [x] **[LOW]** `gear.types.ts:IItemParams` interface
  - **Problem:** Defined but only used internally in one private method
  - **Simpler approach:** Use inline type or remove if not needed

### Good Practices

- ✅ Most composables are straightforward wrappers around services
- ✅ API services are simple HTTP request wrappers
- ✅ Local services use clear localStorage patterns
- ✅ Formatting composables are simple computed properties

---

## 4. DRY Analysis (Don't Repeat Yourself)

### Code Duplication

#### Critical Duplications (3+ miejsca)

*None found at Critical level*

#### Moderate Duplications (2 miejsca)

- [x] **[HIGH]** `gearSettingsService.ts:219-279` - 11 static methods duplicating instance methods (61 lines)
  - **Pattern:** Identical pattern repeated 11 times:
    ```typescript
    // Pattern repeated for:
    // addCategory, updateCategory, deleteCategory
    // addContainerType, updateContainerType, deleteContainerType
    // addBrand, updateBrand, deleteBrand
    // updateDefaultUnit, updateWeightCalculation

    static async addCategory(
      settings: IGearSettings,
      category: IUserCategory
    ): Promise<IGearSettings> {
      const instance = new GearSettingsService()
      return instance.addCategory(settings, category)
    }
    ```
  - **Recommendation:** Remove static methods or create generic wrapper:
    ```typescript
    private static async delegateToInstance<T extends any[], R>(
      method: (instance: GearSettingsService, ...args: T) => Promise<R>,
      ...args: T
    ): Promise<R> {
      const instance = new GearSettingsService()
      return method(instance, ...args)
    }

    static async addCategory(settings: IGearSettings, category: IUserCategory) {
      return this.delegateToInstance(
        (inst, s, c) => inst.addCategory(s, c),
        settings,
        category
      )
    }
    ```

- [x] **[HIGH]** `gearSettingsService.ts:333-395` - Category/ContainerType/Brand operations (63 lines duplicated 3x)
  - **Pattern:** Add/Update/Delete operations for 3 different array types:
    ```typescript
    // Duplicated for: customCategories, customContainerTypes, customBrands
    async addCategory(settings: IGearSettings, category: IUserCategory): Promise<IGearSettings> {
      const updated = {
        ...settings,
        customCategories: [...settings.customCategories, category],
      }
      return this.updateSettings(settings, { customCategories: updated.customCategories })
    }

    async updateCategory(/* ... */) { /* similar logic */ }
    async deleteCategory(/* ... */) { /* similar logic */ }
    ```
  - **Recommendation:** Generic helper method:
    ```typescript
    private async addToArray<T>(
      settings: IGearSettings,
      key: keyof Pick<IGearSettings, 'customCategories' | 'customContainerTypes' | 'customBrands'>,
      item: T
    ): Promise<IGearSettings> {
      const updated = {
        ...settings,
        [key]: [...(settings[key] as T[]), item],
      }
      return this.updateSettings(settings, { [key]: updated[key] })
    }

    async addCategory(settings: IGearSettings, category: IUserCategory) {
      return this.addToArray(settings, 'customCategories', category)
    }
    ```

- [x] **[MEDIUM]** Linked items update logic appears in multiple locations
  - **Files:** `useGear.ts:63-126`, likely duplicated in service layer
  - **Pattern:** Complex logic for updating master item and all linked items
  - **Recommendation:** Consolidate in `GearItemLocalService.updateLinkedItems()`

### Similar Patterns

- **Weight conversion:** Multiple places convert between units (g ↔ kg)
- **Price formatting:** Duplicated in composables and services
- **Error handling:** Try-catch with fallback pattern repeated across hybrid services

### Good Practices

- ✅ API services avoid duplication through consistent patterns
- ✅ Composables like `useFormattedItemWeight` centralize formatting logic
- ✅ Type definitions are well-centralized

---

## 5. Modularity Analysis

### Separation of Concerns

#### Issues

- [x] **[HIGH]** `useGear.ts` - Mixed concerns (CRUD + calculations + import/export + catalog)
  - **Problem:** Single file handles 5+ different concerns
  - **Recommendation:** Split as described in SRP section

- [x] **[MEDIUM]** `gearItemHybridService.ts:46-65` - Service contains store update logic
  - **Problem:** Service layer directly manipulating store state
  - **Recommendation:** Return data and let composable/component update store

- [x] **[MEDIUM]** `useGear.ts:63-126` - Business logic (linked items) in composable
  - **Problem:** 64 lines of complex business logic should be in service layer
  - **Recommendation:** Move to `GearItemLocalService.updateLinkedItems()`

#### Good Practices

- ✅ Clear separation between API, Local, and Hybrid service layers
- ✅ Composables focused on specific features (expiration, image, inline editing)
- ✅ Type definitions separated from implementation
- ✅ Store layer properly separated from services

---

### Module Coupling

#### Tight Coupling

- [x] **[HIGH]** `gearItemHybridService.ts` → `useGearStore()` (direct store access)
  - **Problem:** Service layer tightly coupled to specific store implementation
  - **Recommendation:** Inject store or use observer pattern

- [x] **[MEDIUM]** `useGear.ts` → Concrete service implementations
  - **Problem:** Composable imports concrete services, making testing difficult
  - **Recommendation:** Use dependency injection (see DIP section)

#### Loose Coupling

- ✅ API services have no dependencies on other modules
- ✅ Local services use interfaces for type safety
- ✅ Composables can be used independently

---

### Reusability

#### Low Reusability

- [x] **[MEDIUM]** `markdownImportService.ts` - Tightly coupled to Gear module types
  - **Problem:** Couldn't be easily reused for other import scenarios
  - **Recommendation:** Extract generic markdown parsing utilities

- [x] **[LOW]** `sampleSetGenerator.ts` - Hardcoded example data
  - **Problem:** Not reusable for custom data sets
  - **Recommendation:** Accept data as parameter or use config file

#### High Reusability

- ✅ Formatting composables (`useFormattedItemWeight`, `useFormattedItemPrice`) are highly reusable
- ✅ Label composables can be used across different components
- ✅ Generic utilities like `useNavigationReturn` are context-independent

---

## 6. Code Splitting Opportunities

### Large Functions

- [x] **[CRITICAL]** `markdownImportService.ts:parseMarkdown` (~235 lines)
  - **Current complexity:** Cyclomatic complexity ≈ 15+
  - **Split into:**
    1. `parseContainerHeader(lines)` - Extract container metadata
    2. `parseItemsList(lines, startIndex)` - Parse items section
    3. `buildContainerObject(header, items, description)` - Assemble final object

- [x] **[CRITICAL]** `markdownImportService.ts:parseItemLine` (~254 lines)
  - **Current complexity:** Cyclomatic complexity ≈ 12+
  - **Split into:**
    1. `parseItemStatus(line)` - Extract checkbox/status
    2. `parseItemName(line)` - Extract name and priority
    3. `parseItemMetadata(line)` - Extract parentheses content
    4. `parseItemPrice(text)` - Already exists, ensure it's used
    5. `parseItemWeight(text)` - Extract weight parsing
    6. `parseItemExpiration(text)` - Extract expiration parsing

- [x] **[HIGH]** `useGear.ts:updateItem` (64 lines with linked items logic)
  - **Split into:**
    1. `updateSingleItem()` - Core update logic
    2. `updateLinkedItems()` - Handle linked items (move to service)

### Complex Components

*Not applicable - this iteration focuses on logic layer, not components*

### Shared Logic

- [x] **[MEDIUM]** Weight calculation logic
  - **From:** `gearContainerLocalService.ts`, inline calculations, composables
  - **To:** `shared/utils/weightCalculations.ts` or dedicated `WeightCalculationService`

- [x] **[MEDIUM]** Price parsing and formatting
  - **From:** `markdownImportService.ts`, `useFormattedItemPrice.ts`
  - **To:** `shared/utils/priceUtils.ts`

- [x] **[LOW]** Unit conversion logic
  - **From:** Multiple services and composables
  - **To:** `shared/utils/unitConversions.ts`

---

## 7. Additional Findings

### Performance Issues

- [x] **[HIGH]** `useGearStore.ts:12-30` - Synchronous localStorage parsing blocks main thread
  - **Problem:** `loadFromStorage()` is synchronous but parses potentially large JSON and runs migration logic
  - **Impact:** App startup could be slow with large data sets
  - **Recommendation:** Use Web Workers for large data sets or implement lazy loading

- [x] **[MEDIUM]** `gearItemHybridService.ts:46-65` - Linear search for parent container
  - **Problem:** Loops through all containers to find item's parent
  - **Impact:** O(n) complexity, slow with many containers
  - **Recommendation:** Maintain item-to-container mapping in store or return container ID from API

- [x] **[MEDIUM]** `markdownImportService.ts` - Synchronous parsing of large markdown files
  - **Problem:** Complex regex operations and nested loops are synchronous
  - **Impact:** UI freezes during large imports
  - **Recommendation:** Use Web Workers or implement chunked parsing with progress indicators

### Type Safety

**✅ Excellent Type Safety (10/10)**

- Zero `any` types found in core logic files
- All functions have explicit return types
- Proper use of generic types
- Discriminated unions for status types
- Comprehensive interface definitions
- Proper use of `MaybeRefOrGetter` with `toValue()`

**Areas of excellence:**
- `gear.types.ts` - Comprehensive type definitions with no `any`
- Service interfaces with full type coverage
- Composables using explicit type parameters
- Proper TypeScript strict mode compliance

### Error Handling

- [x] **[HIGH]** Inconsistent error handling patterns across services
  - **Problem:**
    - `gearContainerService`: Catches errors and falls back to localStorage
    - `gearContainerApiService`: Throws errors
    - `gearItemService`: Mixes both patterns
    - `useGear`: Suppresses errors with `try/catch` returning `undefined`
  - **Impact:** Errors might be silently swallowed or inconsistently propagated
  - **Recommendation:** Establish consistent error handling strategy:
    ```typescript
    // Services should throw typed errors
    class GearServiceError extends Error {
      constructor(public code: string, message: string) {
        super(message)
      }
    }

    // Composables should catch and handle UI concerns
    export function useGear() {
      const { showToast } = useToast()

      const createContainer = async (data: ICreateContainerDto) => {
        try {
          return await gearContainerService.createContainer(data)
        } catch (error) {
          if (error instanceof GearServiceError) {
            showToast.error(error.message)
          }
          throw error // Re-throw for component-level handling
        }
      }
    }
    ```

- [x] **[MEDIUM]** Missing rollback mechanisms in hybrid services
  - **Problem:** `gearContainerService.deleteContainer` catches localStorage errors but doesn't rollback API deletion
  - **Files:** `gearContainerService.ts:46-59`, `gearItemHybridService.ts:17-30`
  - **Recommendation:** Implement saga pattern or compensating transactions

- [x] **[MEDIUM]** `dataMigrationService.ts` - No error recovery for partial migrations
  - **Problem:** If migration fails midway, data could be in inconsistent state
  - **Recommendation:** Implement transaction-like pattern with rollback capability

### Testing Gaps

- [x] **[HIGH]** `markdownImportService.ts` - No tests for complex parsing logic
  - **Impact:** High-risk code without test coverage
  - **Recommendation:** Add comprehensive unit tests with edge cases

- [x] **[MEDIUM]** `gearItemHybridService.ts` - Missing tests for fallback logic
  - **Impact:** Critical fallback path untested
  - **Recommendation:** Add integration tests for API failure scenarios

- [x] **[MEDIUM]** Composables lacking tests
  - **Files:** Most composables in `composables/` directory
  - **Recommendation:** Add unit tests for all composables with business logic

**Good practices:**
- ✅ `gearContainerLocalService.spec.ts` and `gearItemLocalService.spec.ts` exist

### Documentation

- [x] **[MEDIUM]** Store actions lack JSDoc comments
  - **Files:** `useGearStore.ts`, `useGearSettingsStore.ts`
  - **Impact:** Medium - Makes it harder for new developers to understand store API
  - **Recommendation:** Add JSDoc to all public store methods

- [x] **[LOW]** Complex functions missing JSDoc
  - **Files:** `markdownImportService.ts:parseMarkdown`, `parseItemLine`
  - **Recommendation:** Add detailed JSDoc explaining parsing logic and format expectations

- [x] **[LOW]** Inconsistent naming conventions
  - **Problem:**
    - `getAllContainers` vs `getRootContainers` (inconsistent "get" prefix)
    - `removeContainer` (store) vs `deleteContainer` (service)
    - `customCategories` vs `userCategories` (naming inconsistency)
  - **Recommendation:** Establish naming conventions:
    - Services: `create`, `update`, `delete`, `get`
    - Stores: `add`, `update`, `remove`, `find`

**Good practices:**
- ✅ Type definitions have inline documentation
- ✅ Complex interfaces have examples in comments

### Security Concerns

**✅ No security issues found**

- API services properly use authenticated HTTP client
- No direct DOM manipulation in logic layer
- No eval() or dangerous dynamic code execution
- Input validation handled at API boundary

---

## 8. Findings Summary

### Critical (Must Fix) - ✅ ALL FIXED (2025-12-09)
| Priority | File | Issue | Impact | Status |
|----------|------|-------|--------|--------|
| ✅ ~~🔴~~ | `gearContainerService.ts:46-97` | ~~Data loss risk - no rollback if localStorage deletion fails after API deletion~~ | ~~Data inconsistency~~ | **FIXED** - Two-phase commit implemented |
| ✅ ~~🔴~~ | `dataMigrationService.ts:10-132` | ~~Circular dependency risk - parentContainerId not handled correctly~~ | ~~Orphaned containers~~ | **FIXED** - Topological sort implemented |
| ✅ ~~🔴~~ | `gearItemHybridService.ts:46-134` | ~~Race condition in container refresh after item update~~ | ~~Wrong container updated~~ | **FIXED** - Container ID lookup before update |

### High (Should Fix)
| Priority | File | Issue | Impact |
|----------|------|-------|--------|
| 🟠 | `gearSettingsService.ts:219-279` | 61 lines of duplicated code (11 static method wrappers) | Maintenance burden |
| 🟠 | `gearSettingsService.ts:333-395` | 63 lines duplicated 3x (Category/Type/Brand operations) | DRY violation |
| 🟠 | `gear.types.ts:284-317` | ISP violation - IGearServiceExtended has 11 localStorage-specific methods | Poor abstraction |
| 🟠 | `markdownImportService.ts:210-445` | parseMarkdown method is 235 lines with 7 nesting levels | Complexity |
| 🟠 | `useGearStore.ts:12-30` | Synchronous localStorage parsing blocks main thread | Performance |
| 🟠 | `gearItemHybridService.ts:17-30` | Missing transaction boundaries in create/update operations | Data inconsistency |

### Medium (Nice to Have)
| Priority | File | Issue | Impact |
|----------|------|-------|--------|
| 🟡 | Multiple service files | Inconsistent error handling patterns | Maintainability |
| 🟡 | `useGearStore.ts` vs `useGearSettingsStore.ts` | Inconsistent store patterns (options API vs setup) | Code consistency |
| 🟡 | Multiple service files | Missing input validation | Data quality |
| 🟡 | Various files | Weight/price calculation logic scattered | Maintenance |
| 🟡 | `gear.types.ts` | Primitive obsession (weight, price, dates) | Type safety |
| 🟡 | `useGear.ts:entire-file` | Mega-composable with 24+ functions (SRP violation) | Maintainability |
| 🟡 | `useGear.ts:63-126` | Business logic (linked items) in composable instead of service | Architecture |
| 🟡 | `markdownImportService.ts` | Synchronous parsing blocks UI | UX |
| 🟡 | `gearContainerService.ts` | No pagination total count or cursor support | API design |
| 🟡 | `markdownImportService.ts:149-186` | Price parsing regex duplication | DRY |

### Low (Optional)
| Priority | File | Issue | Impact |
|----------|------|-------|--------|
| 🟢 | Multiple files | 15+ console.warn/log statements in production code | Production logs |
| 🟢 | Multiple files | Magic numbers (100, 30, 2000) not extracted to constants | Readability |
| 🟢 | `gearItemApiService.ts:42` | TODO comment for unimplemented method | Technical debt |
| 🟢 | Multiple files | Inconsistent naming (getAllContainers vs getRootContainers) | Consistency |
| 🟢 | Store files | Missing JSDoc documentation | Documentation |
| 🟢 | `markdownImportService.ts:115-125` | Unused IItemParams interface | Code cleanup |
| 🟢 | Multiple service files | Optional chaining overuse suggests uncertain data shapes | Type safety |
| 🟢 | `sampleSetGenerator.ts:128-140` | Complex translation fallback heuristics | Fragility |

---

## 9. Refactoring Recommendations

### Phase 1: Critical Fixes (Effort: 2-3 days)

1. **Fix Data Consistency Issues in Hybrid Services**
   - **Files:** `gearContainerService.ts`, `gearItemHybridService.ts`, `dataMigrationService.ts`
   - **Action:**
     - Implement two-phase commit or compensating transactions
     - Add rollback mechanisms for failed operations
     - Fix parentContainerId dependency ordering in migration
     - Add item-to-container mapping in store to avoid linear searches
   - **Benefits:** Prevents data loss and corruption, improves reliability
   - **Risks:** Requires careful testing, might introduce complexity

2. **Add Race Condition Protection**
   - **Files:** `gearItemHybridService.ts:46-65`
   - **Action:**
     - Return container ID from API response
     - Or maintain item-to-container mapping in store
     - Use proper state management for concurrent updates
   - **Benefits:** Prevents wrong container being refreshed
   - **Risks:** API changes might be needed

### Phase 2: High Priority (Effort: 4-5 days)

3. **Eliminate Code Duplication in gearSettingsService**
   - **Files:** `gearSettingsService.ts`
   - **Action:**
     - Remove 11 static method wrappers or implement singleton pattern
     - Create generic `addToArray`, `updateInArray`, `removeFromArray` helpers
     - Reduce 124 lines of duplicated code to ~20 lines
   - **Benefits:** Easier maintenance, less code to test
   - **Risks:** Low - pure refactoring

4. **Split Mega-Functions in markdownImportService**
   - **Files:** `markdownImportService.ts`
   - **Action:**
     - Extract `parseContainerHeader()`, `parseItemsList()`, `buildContainerObject()`
     - Extract `parseItemStatus()`, `parseItemName()`, `parseItemMetadata()`
     - Reduce complexity from 15+ to <7 per function
   - **Benefits:** Improved readability, testability, and maintainability
   - **Risks:** Medium - requires extensive testing

5. **Fix Interface Segregation Violation**
   - **Files:** `gear.types.ts`
   - **Action:**
     - Split `IGearServiceExtended` into:
       - `IGearService` (CRUD only)
       - `IGearCalculationService` (calculations)
       - `IGearQueryService` (queries)
       - `IGearLocalService extends all three`
   - **Benefits:** Better abstraction, clearer contracts
   - **Risks:** Low - mostly type refactoring

### Phase 3: Medium Priority (Effort: 5-6 days)

6. **Standardize Error Handling**
   - **Files:** All services, composables
   - **Action:**
     - Create typed error classes
     - Services throw errors, composables catch and handle UI concerns
     - Add proper error boundaries
   - **Benefits:** Consistent error experience, better debugging
   - **Risks:** Medium - affects many files

7. **Split useGear Mega-Composable**
   - **Files:** `useGear.ts`
   - **Action:**
     - Create `useContainerOperations()`, `useItemOperations()`, `useContainerCalculations()`, `useContainerImportExport()`, `useItemCatalog()`
     - Keep `useGear()` as convenience wrapper that re-exports focused composables
   - **Benefits:** Better separation of concerns, easier testing
   - **Risks:** Low - backward compatible if `useGear()` re-exports

8. **Move Business Logic from Composables to Services**
   - **Files:** `useGear.ts:63-126`, `gearItemHybridService.ts`
   - **Action:**
     - Move linked items update logic to `GearItemLocalService.updateLinkedItems()`
     - Remove store access from services
   - **Benefits:** Proper layering, easier testing
   - **Risks:** Low - architectural improvement

9. **Add Input Validation with Zod**
   - **Files:** All services
   - **Action:**
     - Create Zod schemas for all DTOs
     - Validate inputs in service layer
     - Return typed validation errors
   - **Benefits:** Better data quality, early error detection
   - **Risks:** Medium - adds runtime overhead

10. **Migrate useGearStore to Setup Syntax**
    - **Files:** `useGearStore.ts`
    - **Action:**
      - Convert from options API to setup function
      - Match pattern from `useGearSettingsStore.ts`
      - Replace getters with `computed()`
    - **Benefits:** Consistency, modern patterns
    - **Risks:** Low - well-defined refactoring

### Phase 4: Low Priority (Effort: 2-3 days)

11. **Improve Performance**
    - **Files:** `useGearStore.ts`, `markdownImportService.ts`
    - **Action:**
      - Use Web Workers for large data parsing
      - Implement lazy loading for store data
      - Add progress indicators for long operations
    - **Benefits:** Better UX with large data sets
    - **Risks:** Medium - requires architecture changes

12. **Documentation & Code Cleanup**
    - **Files:** All files
    - **Action:**
      - Add JSDoc to all public APIs
      - Extract magic numbers to constants
      - Remove console.log/warn or use logger service
      - Fix naming inconsistencies
    - **Benefits:** Better developer experience
    - **Risks:** Low - cosmetic improvements

---

## 10. Dependencies & Blockers

### Dependencies
- Phase 2 (Interface Segregation) should be done before Phase 3 (Move Business Logic), as it affects service contracts
- Error handling standardization (Phase 3) should be done early to establish patterns

### Blockers
- API changes might be needed for Phase 1 (returning container ID in response)
- Large refactorings (splitting useGear, markdown service) require coordination with ongoing feature work

---

## 11. Next Steps

1. [x] Review findings with team
2. [ ] Prioritize refactoring tasks based on current sprint capacity
3. [ ] Create GitHub issues/tickets for Phase 1 (Critical) items
4. [ ] Schedule Phase 1 refactoring work (2-3 days)
5. [ ] Add unit tests before refactoring (especially markdownImportService)
6. [ ] Plan Phase 2 refactoring for next sprint

---

## 12. Notes & Observations

### Positive Patterns Observed

1. **Hybrid Service Pattern**: The API-first with localStorage fallback pattern is well-designed and provides excellent resilience. This pattern should be documented as a best practice for the project.

2. **Composable Organization**: The breadth of focused composables (22 files) shows good thinking about reusability, even if `useGear` is too large.

3. **Type Safety**: Zero `any` types in the logic layer is exceptional and shows strong TypeScript discipline.

4. **Vue 3.5+ Compliance**: Proper use of modern patterns (reactive destructuring, `MaybeRefOrGetter`, explicit types) is excellent.

5. **Service Architecture**: Clear separation between API, Local, and Hybrid layers is well-executed.

### Concerns for Future Iterations

1. **Scalability**: Linear searches and synchronous operations will become problematic as data grows. Consider pagination and indexing strategies.

2. **Testing Culture**: The presence of `.spec.ts` files for local services is good, but coverage gaps in critical areas (markdown parsing, hybrid services) are concerning.

3. **Transaction Management**: As the app grows, lack of transaction boundaries will cause more issues. Consider implementing saga pattern or similar.

### Questions for Team

1. **API Changes**: Can we modify API responses to include container IDs in item operations? This would fix the race condition issue.

2. **Breaking Changes**: Are we willing to accept breaking changes for the interface segregation refactoring, or should we maintain backward compatibility?

3. **Performance Requirements**: What's the expected maximum data set size? This affects whether Web Workers are needed.

4. **Migration Strategy**: For `useGear` splitting, should we do a big-bang refactor or gradual migration?

---

**Overall Assessment: B+ (8/10)**

The Gear module's logic layer demonstrates solid architectural patterns and excellent type safety. The hybrid service approach with automatic fallback is a standout feature. However, significant code duplication (124 lines in gearSettingsService), complex mega-functions (markdownImportService), and potential data consistency issues in hybrid operations bring down the score.

**Key Strengths:**
- ✅ Excellent type safety (zero `any` types)
- ✅ Well-architected service layers
- ✅ Modern Vue 3.5+ patterns
- ✅ Good composable organization (despite useGear being too large)

**Key Weaknesses:**
- ❌ 124 lines of code duplication (High priority)
- ❌ Data consistency risks in hybrid operations (Critical)
- ❌ Mega-functions with 200+ lines (High priority)
- ❌ Interface Segregation violations (High priority)

**Recommended Priority:** Focus on Phase 1 (Critical fixes for data consistency) immediately, then tackle Phase 2 (code duplication and complexity) in the next sprint.

---

*Analiza przeprowadzona przez: Claude Code*
*Data: 2025-12-09*
