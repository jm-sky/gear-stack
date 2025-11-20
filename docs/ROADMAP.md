# Roadmap - Gear Stack (Front-end Only)

Lista planowanych funkcjonalności i ulepszeń aplikacji - **front-end only** (działające z localStorage, bez potrzeby backendu, bazy danych lub autoryzacji).

> 📋 **Zobacz też:** 
> - [ROADMAP_V2.md](./ROADMAP_V2.md) - funkcjonalności wymagające backendu/DB/auth
> - [Features Implementation Plans](./features/README.md) - szczegółowe plany implementacji

---

## 📊 Status Overview

- ✅ **Completed** - Zaimplementowane i przetestowane
- 🚧 **In Progress** - W trakcie implementacji
- 🔄 **Planned** - Zaplanowane, nie rozpoczęte
- ⏸️ **On Hold** - Tymczasowo wstrzymane
- ❌ **Cancelled** - Anulowane

---

## 🌐 Internacjonalizacja

### ✅ Wykrywanie języka (locale) z ustawień przeglądarki
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** [FEATURE-001](./features/FEATURE-001-locale-detection.md)

- ✅ Automatyczne wykrywanie języka użytkownika na podstawie ustawień przeglądarki
- ✅ Fallback do domyślnego języka (np. polski)
- ✅ Możliwość ręcznej zmiany języka w ustawieniach
- ✅ HTML lang attribute automatycznie ustawiany na podstawie wykrytego języka
- ✅ Wykryty język zapisywany w localStorage

### ✅ Preferowana jednostka wagi
**Status:** ✅ Completed | **Priority:** Medium

- ✅ Użytkownik może ustawić preferowaną jednostkę wagi w ustawieniach (g lub kg)
- ✅ Wszystkie wyświetlane wagi na dashboard, w tabelach i kartach będą konwertowane do preferowanej jednostki
- ✅ Formularze nadal mogą używać różnych jednostek, ale wyświetlanie będzie spójne
- ✅ Ustawienie zapisywane w localStorage i synchronizowane w całej aplikacji

### ✅ Dodatkowe jednostki wagi (oz, lb)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Dodanie jednostek imperialnych: uncje (oz) i funty (lb)
- ✅ Rozszerzenie typu `TGearWeightUnit` o `'oz'` i `'lb'`
- ✅ Aktualizacja funkcji konwersji w `formatWeight.ts`:
  - ✅ Konwersja oz → g (1 oz = 28.3495 g)
  - ✅ Konwersja lb → g (1 lb = 453.592 g)
  - ✅ Konwersja g → oz i g → lb
- ✅ Aktualizacja formularzy (ItemFormFields, ContainerFormFields) - dodanie opcji oz i lb
- ✅ Aktualizacja preferowanej jednostki wagi w ustawieniach - dodanie oz i lb jako opcji
- ✅ Aktualizacja tłumaczeń (PL/EN) dla nowych jednostek
- ✅ Aktualizacja parsera markdown import - rozpoznawanie oz i lb w eksporcie/impocie
- ✅ Aktualizacja walidacji (zod schemas) - dodanie oz i lb do enum
- ✅ Wszystkie wyświetlane wagi będą konwertowane do preferowanej jednostki (w tym oz/lb)

---

## 🎨 UI/UX Ulepszenia

### ✅ Strona z listą wszystkich przedmiotów
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

- ✅ Nowa strona wyświetlająca listę wszystkich przedmiotów ze wszystkich kontenerów
- ✅ Dostępna jako kolejna pozycja w topbar navigation (obok "Kontenery")
- ✅ Tabela przedmiotów z kolumnami:
  - ✅ Kategoria (z ikoną)
  - ✅ Nazwa przedmiotu
  - ✅ Kontener (nazwa kontenera, z którego pochodzi przedmiot, z wizualizacją koloru)
  - ✅ Ilość
  - ✅ Waga
  - ✅ Status
  - ✅ Priorytet
  - ✅ Marka (opcjonalnie, ukryta domyślnie)
  - ✅ Kolor (opcjonalnie, ukryty domyślnie)
- ✅ Możliwość filtrowania i sortowania:
  - ✅ Filtrowanie po kategorii, statusie, priorytecie
  - ✅ Filtrowanie po kontenerze (przez wyszukiwarkę)
  - ✅ Sortowanie po dowolnej kolumnie
- ✅ Możliwość szybkiego przejścia do kontenera, w którym znajduje się przedmiot (kliknięcie w nazwę kontenera)
- ✅ Wyszukiwarka przedmiotów (globalne filtrowanie)
- ✅ Zarządzanie widocznością kolumn z zapisem w localStorage

### ✅ Dedykowane ikony dla kategorii
**Status:** ✅ Completed | **Priority:** High | **Feature:** [FEATURE-002](./features/FEATURE-002-category-icons.md)

- ✅ Na liście przedmiotów - dedykowana ikona do każdej kategorii
- ✅ Ikony dla kategorii: woda, ogień, jedzenie, schronienie, pierwsza pomoc, narzędzia, nawigacja, komunikacja, odzież, higiena, światło, inne
- ✅ Spójny system ikon (Lucide Icons)
- ✅ Ikony wyświetlane w tabelach i selektorach kategorii

### ✅ Kolorowanie kontenerów
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** [FEATURE-003](./features/FEATURE-003-container-colors.md)

- ✅ Możliwość przypisania koloru do kontenera
- ✅ 10 dostępnych kolorów do wyboru (default, blue, green, red, yellow, purple, orange, pink, teal, indigo)
- ✅ Wizualne rozróżnienie kontenerów na liście (kolorowa kropka i ramka)
- ✅ Kolor wyświetlany w kartach kontenerów i rozwiniętych wierszach zagnieżdżonych kontenerów

### Wybór primary color (brand color)
**Status:** ⏸️ On Hold | **Priority:** Low | **Complexity:** Small

- Obecny kolor "dark orange" jest zadowalający, zadanie wstrzymane
- **Uwaga:** Warianty kolorów są już przygotowane w `src/css/style.css` jako zakomentowany kod (na wypadek potrzeby zmiany w przyszłości)

---

## 🔗 Relacje i Nesting

### ✅ Relacja parent-children (nesting kontenerów)
**Status:** ✅ Completed | **Priority:** High | **Feature:** [FEATURE-008](./features/FEATURE-008-container-nesting.md)

- ✅ Kontener może zawierać na liście przedmiotów inny kontener
  - Przykład: W plecaku może być Pouch, a w Pouch może być Latarka
- ✅ Kontener, który ma rodzica lub jest używany jako item, można ukryć z głównej listy kontenerów
- ✅ Opcja wyświetlania tylko kontenerów głównych (bez zagnieżdżonych)
- ✅ Wizualne oznaczenie kontenerów zagnieżdżonych (ikona, badge, klikalna nazwa)
- ✅ Rekurencyjne obliczanie wagi (waga kontenera + waga jego zawartości)
- ✅ Rozwijane wiersze w tabeli przedmiotów - możliwość zobaczenia zawartości zagnieżdżonego kontenera
- ✅ Walidacja cyklicznych referencji - zapobieganie nieskończonym pętlom
- ✅ Osobne akcje "Dodaj Przedmiot" i "Dodaj Kontener" w interfejsie

> **Uwaga:** Ta funkcjonalność jest już zaimplementowana i działa z localStorage. W przyszłości może być rozszerzona o synchronizację z backendem (zobacz [ROADMAP_V2.md](./ROADMAP_V2.md)).

---

## 📝 Rozszerzone pola

### ✅ Dodatkowe pola dla przedmiotów i kontenerów
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** FEATURE-006 | **Complexity:** Medium

**Dla przedmiotów:**
- ✅ **Cena** - cena zakupu przedmiotu
- ✅ **Link URL** - link do produktu, recenzji, itp.
- ✅ **Półka cenowa / jakość** - niska półka, średnia półka, wyższa półka
- ✅ **Firma** - producent/marka przedmiotu (z ComboBox i sugerowanymi wartościami)
- ✅ **Kolor** - kolor przedmiotu (z ComboBox i sugerowanymi wartościami)

**Dla kontenerów:**
- ✅ **Firma** - producent/marka kontenera
- ✅ **Cena** - cena zakupu kontenera

**Ujednolicenie modelu:**
- ✅ Wspólne pola (firma, cena) zaimplementowane w modelu danych
- ✅ Wizualizacja kolorów w tabelach (kolorowa kropka)
- ✅ Zarządzanie widocznością kolumn (marka, kolor) w tabelach

> **Uwaga:** Ta funkcjonalność jest już zaimplementowana i działa z localStorage. W przyszłości może być rozszerzona o synchronizację z backendem (zobacz [ROADMAP_V2.md](./ROADMAP_V2.md)).

---

## 🚀 Import/Export i Markdown

### ✅ Eksport i import markdown (AI-friendly format)
**Status:** ✅ Completed | **Priority:** High | **Feature:** FEATURE-009, FEATURE-011 | **Complexity:** Large

**Eksport do markdown:**
- ✅ Przycisk "Eksport do prompt (AI)" w dropdown menu kontenera
- ✅ Przycisk "Eksport do prompt (AI) - Wszystkie" dla wszystkich kontenerów na liście
- ✅ Eksport tworzy markdown z kontenerem i jego zawartością w ujednoliconym formacie
- ✅ Dialog z markdownem i przyciskiem do kopiowania
- ✅ Przycisk "Guidelines" w dialogu - kopiuje szablon formatowania dla AI
- ✅ Legenda/opis dla AI wyjaśniająca strukturę danych

**Format markdown (ujednolicony dla import/export):**
```markdown
## [Container Name] [#container-id] ([Container Type])
- **[Item Name]** x[qty] ([Brand], [Color]) [#nested-id] ([Status]) <URL> - [weight]g
```

**Cechy formatu:**
- ✅ **Nazwa przedmiotu** (bold `**text**`) - wymagane
- ✅ **Ilość** (format: `x2`, `x10`) - opcjonalne, może być wszędzie w linii
- ✅ **Marka i kolor** w pierwszych nawiasach: `(Marka, Kolor)` - opcjonalne
- ✅ **Status i expiration** w drugich nawiasach: `(Status, Expiration: DD.MM.YYYY)` - opcjonalne
- ✅ **Container ID** w formacie `[#slug-id]` - dla identyfikacji kontenerów
  - ID generowane jako slug z nazwy: "Bug-Out Bag" → `#bug-out-bag`
  - Użyte w nagłówku kontenera i referencjach do zagnieżdżonych kontenerów
- ✅ **URL** w nawiasach kątowych lub plain: `<https://example.com>` lub `https://...` lub `www...` - opcjonalne
  - Automatyczne dodawanie `https://` do linków zaczynających się od `www.`
- ✅ **Waga** na końcu: `- 500g` lub `- 2.5kg` - opcjonalne (domyślnie 100g)
- ✅ **Zagnieżdżone kontenery**:
  - Item z `[#id]` w linii przedmiotu
  - Osobna definicja kontenera z tym samym `[#id]` w nagłówku
  - Parser automatycznie tworzy relację

**Import z markdown:**
- ✅ Przycisk "Import z markdown" w dropdown menu na liście kontenerów
- ✅ Dialog z textarea do wklejenia markdown i przyciskiem "Preview"
- ✅ Elastyczny parser:
  - ✅ Rozpoznaje pola w dowolnej kolejności (nazwa, ilość, waga, marka, kolor, status, expiration, URL, container ID)
  - ✅ Inteligentne dopasowywanie marek (fuzzy matching z SUGGESTED_BRANDS)
  - ✅ Inteligentne dopasowywanie kolorów (z SUGGESTED_COLORS)
  - ✅ Automatyczne rozpoznawanie kategorii po słowach kluczowych
  - ✅ Domyślne wartości dla brakujących pól (waga: 100g, ilość: 1, status: owned)
  - ✅ Wyciąganie `[#id]` z nagłówków kontenerów
  - ✅ Wyciąganie `[#id]` z linii przedmiotów (dla relacji zagnieżdżonych kontenerów)
  - ✅ Obsługa różnych formatów dat expiration
  - ✅ Obsługa URL w nawiasach kątowych lub plain
- ✅ Obsługa błędów - wyświetlanie błędów parsowania z numerami linii
- ✅ Preview przed importem - podgląd kontenerów i przedmiotów przed zapisaniem

**Szablon Guidelines:**
- ✅ Kompletny szablon formatowania w markdown
- ✅ Szczegółowe zasady dla każdego pola
- ✅ Przykłady dla wszystkich możliwych formatów
- ✅ Instrukcje dla AI jak rozpoznawać i formatować dane
- ✅ Dokumentacja zagnieżdżonych kontenerów
- ✅ Przycisk kopiowania szablonu do schowka

**Planowane ulepszenia (front-end only):**
- 🚧 **Opcje konfiguracji eksportu** (częściowo zaimplementowane):
  - ✅ Pokazywanie UUID w eksporcie (opcjonalnie)
  - ✅ Pokazywanie wagi w eksporcie (opcjonalnie)
  - ✅ Pokazywanie koloru w eksporcie (opcjonalnie)
  - ✅ Pokazywanie marki w eksporcie (opcjonalnie)
  - ✅ Pokazywanie powiązania z kontenerem (opcjonalnie)
  - ✅ Pokazywanie legendy (opcjonalnie)
  - 🔄 Pokazywanie cen przedmiotów w eksporcie (opcjonalnie) - planowane
  - 🔄 Dodatkowe podsumowanie "Do kupienia" na końcu eksportu - planowane
  - 🔄 Inne opcje konfiguracji formatu (poziom szczegółowości, metadane, itp.) - planowane

> **Uwaga:** UUID support dla update workflow wymaga backendu/DB - zobacz [ROADMAP_V2.md](./ROADMAP_V2.md)

---

## ⚡ Usprawnienia dodawania przedmiotów

### ✅ Domyślne wartości dla nowych przedmiotów
**Status:** ✅ Completed | **Priority:** High | **Feature:** [FEATURE-004](./features/FEATURE-004-default-values.md)

- ✅ Nowy przedmiot ma większość pól z domyślnymi wartościami
- ✅ Domyślne wartości:
  - ✅ Waga: 0.1 kg
  - ✅ Ilość: 1
  - ✅ Status: "owned"
  - ✅ Priorytet: "medium"
  - ✅ Kategoria: "other" (lub wykryta automatycznie)
  - ✅ Jednostka wagi: kg

### ✅ Rozpoznawanie kategorii po nazwie
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** [FEATURE-005](./features/FEATURE-005-category-recognition.md)

- ✅ Na podstawie słów kluczowych w nazwie dobieramy kategorię
- ✅ Przykłady:
  - ✅ `nóż`, `knife` → kategoria: narzędzia
  - ✅ `woda`, `water` → kategoria: woda
  - ✅ `zapałki`, `matches` → kategoria: ogień
  - ✅ `apteczka`, `first aid` → kategoria: pierwsza pomoc
- ✅ Podobnie dla kontenerów (rozpoznawanie typu kontenera)
- ✅ Słownik słów kluczowych dla każdej kategorii i typu kontenera
- ✅ Rozpoznawanie uruchamiane na zdarzeniu blur (po opuszczeniu pola nazwy)
- ✅ Priorytetyzacja dłuższych słów kluczowych (np. "bagażnik" zamiast "bag")

> **Uwaga:** Uczenie się na podstawie wcześniejszych wyborów użytkownika wymaga backendu/DB - zobacz [ROADMAP_V2.md](./ROADMAP_V2.md)

---

## ✏️ Szybka edycja

### Edycja bezpośrednio na liście
**Status:** 🔄 Planned | **Priority:** High | **Feature:** FEATURE-007 | **Complexity:** Large

- Możliwość szybkiej edycji listy - dodawanie i zmienianie przedmiotów bezpośrednio na liście
- Bez wchodzenia w formularz
- Inline editing dla podstawowych pól (nazwa, ilość, status)
- Szybkie akcje (zmiana statusu, priorytetu) bezpośrednio z listy

### Kolejność przedmiotów w kontenerze
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

- Dodanie pola `order` (lub `sortOrder`) do przedmiotów w kontenerze
- Możliwość ręcznego układania przedmiotów w wybranej kolejności
- Dwa sposoby zmiany kolejności:
  - **Drag & drop** - przeciąganie wierszy w tabeli do zmiany kolejności (preferowane)
  - **Akcje "Do góry" / "Do dołu"** - przyciski w menu akcji przedmiotu (alternatywa, jeśli drag & drop jest zbyt skomplikowane)
- Kolejność zapisywana w localStorage i wyświetlana domyślnie w tabeli przedmiotów
- Opcja sortowania według innych kryteriów (nazwa, waga, kategoria) z możliwością powrotu do kolejności ręcznej
- Wizualne wskaźniki podczas przeciągania (highlight, placeholder)

---

## 📊 Wizualizacje i analityka

### ✅ Wykres kołowy kategorii w kontenerze
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Wykres kołowy (donut chart) pokazujący rozkład kategorii przedmiotów w kontenerze
- ✅ Przełącznik między dwoma trybami wyświetlania:
  - ✅ **Pod względem wagi** - Jak dużo ważą narzędzia względem całości? (procentowy udział wagi każdej kategorii)
  - ✅ **Pod względem ilości** - Jak dużo mam sztuk narzędzi względem wszystkich przedmiotów? (procentowy udział ilości przedmiotów w każdej kategorii)
- ✅ Wykres wyświetlany na stronie szczegółów kontenera
- ✅ Kolorowe segmenty odpowiadające kolorom kategorii (lub dedykowanym kolorom)
- ✅ Legenda z nazwami kategorii i wartościami procentowymi
- ✅ Uwzględnienie zagnieżdżonych kontenerów w obliczeniach (opcjonalnie)

---

## 📄 Informacje prawne i footer

### ✅ Strona "Informacja o ciasteczkach" i Footer
**Status:** ✅ Completed | **Priority:** Low | **Feature:** FEATURE-010 | **Complexity:** Small

**Strona "Informacja o ciasteczkach":**
- ✅ Strona `/cookies` z informacją o wykorzystaniu localStorage
- ✅ Sekcje: LocalStorage, Co przechowujemy, Prywatność, Przyszłość, RODO
- ✅ Zgodność z RODO - informacje o lokalnym przechowywaniu danych
- ✅ Tłumaczenia PL/EN

**Footer:**
- ✅ Footer z informacją `© [rok] DEV Made IT`
- ✅ Linki do:
  - ✅ Informacji o ciasteczkach (`/cookies`)
  - ✅ Polityki prywatności (`/privacy`)
  - ✅ Kontaktu (`/contact`)
  - ✅ GitHub/repozytorium
- ✅ Footer wyświetlany w `AuthenticatedLayout`

---

## 🤖 Funkcje AI (front-end only)

### Funkcje AI z API calls (bez auth)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium

- Sugestie sprzętu (na podstawie pogody, aktywności itp.) - przez API calls
- Analiza listy (co dodać, co usunąć, alternatywy) - przez API calls
- Generowanie gotowych presetów (UL, bushcraft, EDC) - przez API calls
- Konwersja: opis → gotowy kontener - przez API calls

> **Uwaga:** Podstawowe funkcje AI mogą działać przez API calls bez autoryzacji. Zaawansowane funkcje wymagające personalizacji i uczenia się na podstawie historii użytkownika wymagają backendu/DB - zobacz [ROADMAP_V2.md](./ROADMAP_V2.md)

---

## 📈 Priorytetyzacja

### High Priority (Następne do zrobienia)
1. ✅ **Strona z listą wszystkich przedmiotów** - High priority, Medium complexity (Completed in v0.10.0)
2. **Edycja bezpośrednio na liście** - High priority, Large complexity
3. **Kolejność przedmiotów w kontenerze** - Medium priority, Medium complexity

### Medium Priority
1. **Preferowana jednostka wagi** - Medium priority, Small complexity
2. ✅ **Rozszerzone pola** - Medium priority, Medium complexity (Completed in v0.8.0)

### Low Priority (Polish/Enhancement)
1. ⏸️ **Wybór primary color** - Low priority, Small complexity (On Hold - obecny kolor zadowalający)
2. ✅ **Footer i strony prawne** - Low priority, Small complexity (Completed)
3. **Funkcje AI (podstawowe)** - Low priority, Medium complexity

---

## 📝 Uwagi dotyczące funkcjonalności wymagających backendu

Wszystkie funkcjonalności wymagające backendu, bazy danych lub autoryzacji zostały przeniesione do [ROADMAP_V2.md](./ROADMAP_V2.md), w tym:
- Synchronizacja między urządzeniami
- Wersjonowanie danych
- Udostępnianie i współpraca
- Globalny katalog itemów (multi-user)
- Linkowanie przedmiotów (multi-user)
- Zaawansowane funkcje AI z personalizacją
- Szablony kontenerów (z udostępnianiem)
- Statystyki i raporty (multi-user)

---

## 📝 Notatki

- Wszystkie funkcjonalności w tym pliku działają z localStorage (front-end only)
- Wszystkie zaimplementowane features mają dokumentację w `docs/features/`
- Statusy są aktualizowane na bieżąco
- Priorytety mogą się zmieniać w zależności od potrzeb użytkowników
- Complexity: Small (1-2 dni), Medium (3-5 dni), Large (1+ tygodnie)
- Funkcjonalności wymagające backendu/DB/auth znajdują się w [ROADMAP_V2.md](./ROADMAP_V2.md)
