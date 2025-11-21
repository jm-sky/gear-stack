# Funkcjonalności do wdrożenia z ROADMAP

Lista funkcjonalności z ROADMAP.md gotowych do implementacji, uporządkowana według priorytetu i złożoności.

---

## 🎯 Rekomendowane do wdrożenia (w kolejności)

### 1. **Dodawanie własnych marek (brand)** ⭐
**Status:** 🔄 Planned | **Priority:** High | **Complexity:** Medium

**Dlaczego teraz:**
- Wysoki priorytet
- Średnia złożoność (nie za proste, nie za skomplikowane)
- Istnieje już infrastruktura (podobnie jak kategorie)
- Pole `brand` już istnieje w modelu danych

**Co trzeba zrobić:**
- Utworzyć UI w ustawieniach (podobnie jak `CategoriesSettingsCard.vue`)
- Dodać store/composable dla zarządzania markami (podobnie jak `useGearSettings`)
- Rozszerzyć `suggestedValues.ts` o łączenie SUGGESTED_BRANDS + własne marki
- Zintegrować z ComboBox w formularzach
- Zintegrować z rozpoznawaniem parametrów

**Szacowany czas:** 3-5 dni

---

### 2. **Zintegrowany input wagi z wyborem jednostki** ⭐
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Small

**Dlaczego teraz:**
- Mała złożoność (łatwe do zrobienia)
- Poprawia UX (wszystko w jednym miejscu)
- Można zrobić szybko jako "quick win"

**Co trzeba zrobić:**
- Utworzyć komponent `<WeightInputWithUnitPicker>`
- Zastąpić obecne pola wagi w `ItemFormFields.vue`
- Zastąpić pola wagi w `ContainerFormFields.vue` (weight, maxWeight)
- Obsługa wszystkich jednostek: g, kg, oz, lb

**Szacowany czas:** 1-2 dni

---

### 3. **Obsługa waluty (currency)** ⭐
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

**Dlaczego teraz:**
- Uzupełnia istniejące pole `price` (które już jest w modelu)
- Średnia złożoność
- Poprawia użyteczność (cena bez waluty jest niepełna)

**Co trzeba zrobić:**
- Dodać pole `currency` do `IGearItem` i `IGearContainer`
- Dodać domyślną walutę w ustawieniach użytkownika
- Utworzyć funkcję formatowania cen (`formatCurrency.ts`)
- Dodać pole wyboru waluty w formularzach
- Wyświetlać walutę w tabelach i statystykach
- Auto-rozpoznawanie z języka (PL → PLN, inne → EUR)

**Szacowany czas:** 3-5 dni

---

### 4. **Kolejność przedmiotów w kontenerze**
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

**Dlaczego teraz:**
- Średnia złożoność
- Poprawia UX (użytkownik może układać przedmioty jak chce)
- Można zrobić bez drag & drop (przyciski "Do góry" / "Do dołu")

**Co trzeba zrobić:**
- Dodać pole `order` (lub `sortOrder`) do przedmiotów
- Dodać akcje "Do góry" / "Do dołu" w menu akcji przedmiotu
- Opcjonalnie: drag & drop (bardziej skomplikowane)
- Zapisywanie kolejności w localStorage
- Wyświetlanie domyślnie według kolejności ręcznej

**Szacowany czas:** 3-5 dni (z przyciskami) lub 5-7 dni (z drag & drop)

---

### 5. **Oznaczanie kontenerów jako fragmentów rodzica**
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

**Dlaczego teraz:**
- Średnia złożoność
- Przydatne dla zaawansowanych użytkowników
- Wymaga tylko front-end

**Co trzeba zrobić:**
- Dodać pole `isIntegralPart` do `IGearContainer`
- Dodać checkbox w formularzu kontenera (tylko gdy ma rodzica)
- Zaktualizować obliczenia statystyk (nie liczyć fragmentów osobno)
- Wizualne oznaczenie w interfejsie (ikona, badge)
- Aktualizacja logiki wyświetlania (fragmenty nie jako główne kontenery)

**Szacowany czas:** 3-5 dni

---

### 6. **Obsługa Markdown w notatkach**
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

**Dlaczego teraz:**
- Średnia złożoność
- Poprawia użyteczność notatek
- Istnieją już biblioteki do renderowania Markdown

**Co trzeba zrobić:**
- Dodać edytor Markdown (np. `@toast-ui/vue-editor` lub `vue-markdown`)
- Renderowanie Markdown w wyświetlaniu (notatki przedmiotów i opisy kontenerów)
- Podstawowe wsparcie: bold, italic, linki, listy, code
- Opcjonalnie: podgląd na żywo lub split view

**Szacowany czas:** 3-5 dni

---

### 7. **Edycja bezpośrednio na liście**
**Status:** 🔄 Planned | **Priority:** High | **Complexity:** Large

**Dlaczego później:**
- Duża złożoność (1+ tygodnie)
- Wymaga dużo pracy nad UX
- Można zrobić po prostszych funkcjach

**Co trzeba zrobić:**
- Inline editing dla podstawowych pól (nazwa, ilość, status)
- Szybkie akcje bezpośrednio z listy
- Zarządzanie stanem edycji
- Walidacja inline
- Obsługa błędów

**Szacowany czas:** 1-2 tygodnie

---

### 8. **Funkcje AI (podstawowe)**
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium

**Dlaczego później:**
- Niski priorytet
- Wymaga integracji z API
- Można zrobić po podstawowych funkcjach

**Co trzeba zrobić:**
- Integracja z API (np. OpenAI)
- Sugestie sprzętu
- Analiza listy
- Generowanie presetów
- Konwersja: opis → kontener

**Szacowany czas:** 1-2 tygodnie (w zależności od API)

---

## 📊 Podsumowanie - rekomendowana kolejność

### Faza 1: Quick Wins (1-2 tygodnie)
1. ✅ **Zintegrowany input wagi** - Small complexity, szybki efekt
2. ✅ **Dodawanie własnych marek** - High priority, średnia złożoność

### Faza 2: Core Features (2-3 tygodnie)
3. ✅ **Obsługa waluty** - Uzupełnia istniejące funkcje
4. ✅ **Kolejność przedmiotów** - Poprawia UX

### Faza 3: Advanced Features (2-3 tygodnie)
5. ✅ **Oznaczanie fragmentów** - Dla zaawansowanych użytkowników
6. ✅ **Markdown w notatkach** - Poprawia użyteczność

### Faza 4: Complex Features (później)
7. ⏸️ **Edycja bezpośrednio na liście** - Large complexity
8. ⏸️ **Funkcje AI** - Wymaga API, niski priorytet

---

## 🎯 Moja rekomendacja: Zacznij od tego

**Najlepszy wybór na start:**
1. **Zintegrowany input wagi** (1-2 dni) - szybki sukces, poprawia UX
2. **Dodawanie własnych marek** (3-5 dni) - high priority, średnia złożoność

**Dlaczego:**
- Oba są wykonalne w krótkim czasie
- Mają duży wpływ na UX
- Nie wymagają zewnętrznych zależności
- Można zrobić równolegle lub sekwencyjnie

---

## 💡 Uwagi

- Wszystkie funkcjonalności działają z localStorage (front-end only)
- Nie wymagają backendu ani autoryzacji
- Można implementować niezależnie (małe zależności między funkcjami)
- Każda funkcjonalność może być wdrożona osobno


