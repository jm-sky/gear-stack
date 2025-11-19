# Roadmap - Gear Stack

Lista planowanych funkcjonalności i ulepszeń aplikacji.

> 📋 **Zobacz też:** [Features Implementation Plans](./features/README.md) - szczegółowe plany implementacji

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

### Preferowana jednostka wagi
**Status:** 🔄 Planned | **Priority:** Medium

- Użytkownik może ustawić preferowaną jednostkę wagi w ustawieniach (g lub kg)
- Wszystkie wyświetlane wagi na dashboard, w tabelach i kartach będą konwertowane do preferowanej jednostki
- Formularze nadal mogą używać różnych jednostek, ale wyświetlanie będzie spójne
- Ustawienie zapisywane w localStorage i synchronizowane w całej aplikacji

---

## 🎨 UI/UX Ulepszenia

### Strona z listą wszystkich przedmiotów
**Status:** 🔄 Planned | **Priority:** High | **Complexity:** Medium

- Nowa strona wyświetlająca listę wszystkich przedmiotów ze wszystkich kontenerów
- Dostępna jako kolejna pozycja w topbar navigation (obok "Kontenery")
- Tabela przedmiotów z kolumnami:
  - Kategoria (z ikoną)
  - Nazwa przedmiotu
  - Kontener (nazwa kontenera, z którego pochodzi przedmiot)
  - Ilość
  - Waga
  - Status
  - Priorytet
- Możliwość filtrowania i sortowania:
  - Filtrowanie po kategorii, statusie, priorytecie
  - Filtrowanie po kontenerze
  - Sortowanie po dowolnej kolumnie
- Możliwość szybkiego przejścia do kontenera, w którym znajduje się przedmiot (kliknięcie w nazwę kontenera)
- Wyszukiwarka przedmiotów
- Eksport danych (opcjonalnie)

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
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Small

- Porównanie obecnego "dark orange" z alternatywnymi opcjami
- Rozważenie kolorów: coyote, olive, oraz inne opcje pasujące do tematyki survival/outdoor
- Testowanie różnych wariantów kolorystycznych
- Wybór finalnego brand color, który najlepiej oddaje charakter aplikacji
- Aktualizacja palety kolorów w całej aplikacji po wyborze
- **Uwaga:** Warianty kolorów są już przygotowane w `src/css/style.css` jako zakomentowany kod

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

---

## 📝 Rozszerzone pola

### Dodatkowe pola dla przedmiotów i kontenerów
**Status:** 🔄 Planned | **Priority:** Medium | **Feature:** FEATURE-006 | **Complexity:** Medium

**Dla przedmiotów:**
- **Cena** - cena zakupu przedmiotu
- **Link URL** - link do produktu, recenzji, itp.
- **Półka cenowa / jakość** - niska półka, średnia półka, wyższa półka
- **Firma** - producent/marka przedmiotu
- **Kolor** - kolor przedmiotu

**Dla kontenerów:**
- **Firma** - producent/marka kontenera
- **Cena** - cena zakupu kontenera

**Ujednolicenie modelu:**
- Rozważenie ujednolicenia modelu danych dla kontenerów i przedmiotów
- Wspólne pola (np. firma, cena) w jednym miejscu

---

## 🚀 Funkcjonalności eksportu

### ✅ Eksport do prompt (AI)
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** FEATURE-009 | **Complexity:** Medium

- ✅ Kontener ma przycisk "Eksport do prompt" w dropdown menu
- ✅ Eksport tworzy markdown z kontenerem i jego zawartością
- ✅ Legenda/opis dla AI wyjaśniająca strukturę danych
- ✅ Dialog z markdownem i przyciskiem do kopiowania
- ✅ Format eksportu:
  - ✅ Struktura kontenera z przedmiotami
  - ✅ Metadane (waga, marka, kolor, status, data ważności)
  - ✅ Obsługa zagnieżdżonych kontenerów z wyliczoną wagą zawartości
  - ✅ Kompaktowy format: `x4 **Nazwa** (Marka, Kolor) (Expiration: data, Status) - waga`
  - ✅ Legenda wyjaśniająca strukturę danych dla AI
  - ✅ Tłumaczenia dla wszystkich tekstów eksportu

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
- ⏳ Możliwość uczenia się na podstawie wcześniejszych wyborów użytkownika (zaplanowane, ale nie zaimplementowane)

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
- Kolejność zapisywana w bazie danych i wyświetlana domyślnie w tabeli przedmiotów
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

### Strona "Informacja o ciasteczkach" i Footer
**Status:** 🔄 Planned | **Priority:** Low | **Feature:** FEATURE-010 | **Complexity:** Small

**Strona "Informacja o ciasteczkach":**
- Strona/informacja typu "Informacja o ciasteczkach"
- Informacje o wykorzystaniu localStorage
- Zgodność z RODO (jeśli aplikacja będzie wykorzystywać cookies w przyszłości)

**Footer:**
- Footer z informacją typu `2025 (R) DEV Made IT`
- Linki do:
  - Informacji o ciasteczkach
  - Polityki prywatności (jeśli będzie potrzebna)
  - Kontaktu
  - GitHub/repozytorium (opcjonalnie)

---

## 🔮 Przyszłe rozważenia

**Status:** 🔄 Planned | **Priority:** Low

- Synchronizacja między urządzeniami (cloud storage)
- Wersjonowanie danych (historia zmian)
- Statystyki i raporty
- Szablony kontenerów (predefiniowane zestawy)
- Współdzielenie kontenerów między użytkownikami
- Aplikacja mobilna (PWA)

---

## 📈 Priorytetyzacja

### High Priority (Następne do zrobienia)
1. **Strona z listą wszystkich przedmiotów** - High priority, Medium complexity
2. **Edycja bezpośrednio na liście** - High priority, Large complexity
3. **Kolejność przedmiotów w kontenerze** - Medium priority, Medium complexity

### Medium Priority
1. **Preferowana jednostka wagi** - Medium priority, Small complexity
2. **Rozszerzone pola** - Medium priority, Medium complexity

### Low Priority (Polish/Enhancement)
1. **Wybór primary color** - Low priority, Small complexity (warianty już przygotowane)
2. **Footer i strony prawne** - Low priority, Small complexity

---

## 📝 Notatki

- Wszystkie zaimplementowane features mają dokumentację w `docs/features/`
- Statusy są aktualizowane na bieżąco
- Priorytety mogą się zmieniać w zależności od potrzeb użytkowników
- Complexity: Small (1-2 dni), Medium (3-5 dni), Large (1+ tygodnie)
